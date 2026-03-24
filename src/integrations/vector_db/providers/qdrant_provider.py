from qdrant_client import models, QdrantClient
from ..vdb_interface import VectorDBInterface
from typing import List, Optional, Dict, Any
from helpers.logger import get_logger
from models.chunk_model import ChunkMetadata

logger = get_logger(__name__)
    

class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str,distance_method: str,vector_size: int):
        self.client: Optional[QdrantClient] = None
        self.db_path = db_path
        self.distance_method = None
        self.vector_size =vector_size

        if distance_method == "cosine":
            self.distance_method = models.Distance.COSINE
        elif distance_method == "dot":
            self.distance_method = models.Distance.DOT


    def connect(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List:
        return self.client.get_collections()
    
    def create_collection_name(self, project_id: str,tenant_id: str):
        return f"vdb_{tenant_id}_{project_id}".lower().strip()
    
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)
    
    def get_collection_chunks(
    self,
    collection_name: str,
    page: int = 1,             
    limit: int = 10,          
    text_limit: Optional[int] = 100
    ) -> Dict[str, Any]:

        if page < 1:
            raise ValueError("Page number must be >= 1")

        if not self.is_collection_existed(collection_name):
            logger.error(f"Collection does not exist: {collection_name}")
            raise ValueError(f"Collection {collection_name} does not exist")

        try:
            collection_info = self.client.get_collection(collection_name=collection_name)
            total_points = collection_info.points_count

            
            offset = (page - 1) * limit

            points, _ = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            chunks = []
            for p in points:
                payload = p.payload or {}
                metadata = payload.get("metadata", {})

                text = payload.get("text", "")
                if text_limit is not None and len(text) > text_limit and text_limit > 0:
                    text = text[:text_limit]

                chunks.append({
                    "id": str(p.id),
                    "text": text,
                    "metadata": metadata
                })

            total_pages = (total_points + limit - 1) // limit  

            return {
                "collection_name": collection_name,
                "total_chunks": total_points,
                "page": page,
                "total_pages": total_pages,
                "returned_chunks": len(chunks),
                "chunks": chunks
            }

        except Exception as e:
            logger.error(f"Error fetching chunks: {e}")
            raise
        
    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def create_collection(self, collection_name: str, 
                          embedding_size: int,
                          do_reset: bool = False):
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            return True
        
        return False
    


    async def store_batch(
        self,
        collection_name: str,
        batch_size: int,
        texts: List[str],
        vectors: List[List[float]],
        record_ids: List[str],
        metadatas: List[ChunkMetadata]
    ) -> bool:

        try:
            
            if not texts or not vectors or not metadatas:
                logger.warning("Skipping empty batch")
                return False

            if not (len(texts) == len(vectors) == len(metadatas) == len(record_ids)):
                logger.error("Batch size mismatch")
                return False


            await self._ensure_collection_exists(collection_name)

            
            success = self._insert_many(
                collection_name=collection_name,
                texts=texts,
                vectors=vectors,
                record_ids=record_ids,
                metadata=metadatas,
                batch_size=batch_size
            )

            if success:
                logger.info(f"Stored batch of {len(texts)} chunks")
            else:
                logger.error("Failed to store batch")

            return success

        except Exception as e:
            logger.error(f"Failed to store batch: {str(e)}")
            return False


        
    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        results = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
            with_payload=True
        )
        return results.points
    
    async def hybrid_search(self, collection_name: str, 
                           query_vector: List[float], 
                           query_text: str = None,
                           limit: int = 10,
                           filter_conditions: Dict[str, Any] = None) -> List[Dict]:
        
        try:
            search_params = {
                "collection_name": collection_name,
                "query": query_vector,
                "limit": limit,
                "with_payload": True,
                "with_vectors": True
            }
            
           
            if filter_conditions:
                must_conditions = []
                for key, value in filter_conditions.items():
                    must_conditions.append(
                        models.FieldCondition(
                            key=f"metadata.{key}",
                            match=models.MatchValue(value=value)
                        )
                    )
                
                if must_conditions:
                    search_params["query_filter"] = models.Filter(
                        must=must_conditions
                    )
            
            
            vector_results = self.client.query_points(**search_params)
            
            # If keyword search is also requested, combine results
            if query_text:
                # This would require additional setup for keyword indexing
                # For now, we'll return vector results with keyword scoring
                pass
            
            return vector_results.points
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            raise
    
    async def keyword_search(self, collection_name: str, 
                            query_text: str, 
                            limit: int = 10,
                            filter_conditions: Dict[str, Any] = None) -> List[Dict]:
        """
        Perform keyword-based search
        """
        try:
            search_params = {
                "collection_name": collection_name,
                "query": query_text,
                "limit": limit,
                "with_payload": True
            }
            
            # Add filters if provided
            if filter_conditions:
                must_conditions = []
                for key, value in filter_conditions.items():
                    must_conditions.append(
                        models.FieldCondition(
                            key=f"metadata.{key}",
                            match=models.MatchValue(value=value)
                        )
                    )
                
                if must_conditions:
                    search_params["query_filter"] = models.Filter(
                        must=must_conditions
                    )
            
            # Note: This requires full-text search setup in Qdrant
            # You might need to enable sparse vectors or use payload filtering
            keyword_results = self.client.query_points(**search_params)
            return keyword_results.points
            
        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}")
            raise
    def insert_one(self, collection_name: str, text: str, vector: list,
                   metadata: dict = None, 
                   record_id: str = None):
        
        if not self.is_collection_existed(collection_name):
            logger.error(f"Cannot insert into non-existing collection: {collection_name}")
            return False
        
        try:
            _ = self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id,
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            logger.error(f"Error while inserting record: {e}")
            return False

        return True
    
    
    async def _ensure_collection_exists(
        self,
        collection_name: str,
    ) -> bool:

        try:
            if not self.is_collection_existed(collection_name):

                size = self.vector_size

                self.create_collection(
                    collection_name=collection_name,
                    embedding_size=size
                )

                logger.info(f"Created collection: {collection_name} (dim={size})")

            return True

        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            return False
    def _insert_many(self, collection_name: str, texts: list, 
                    vectors: list, record_ids: list, metadata: list = None, 
                    batch_size: int = 50):
        
        if metadata is None:
            metadata = [None] * len(texts)
        
        if not self.is_collection_existed(collection_name):
            logger.error(f"Cannot insert into non-existing collection: {collection_name}")
            return False

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_ids = record_ids[i:batch_end]

            batch_points = [
                models.PointStruct(
                    id=batch_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]

            try:
                _ = self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points
                )
            except Exception as e:
                logger.error(f"Error while inserting batch: {e}")
                return False

        return True
    
    