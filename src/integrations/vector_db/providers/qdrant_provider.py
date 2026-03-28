# integrations/vector_db/providers/qdrant_provider.py
from qdrant_client import models, QdrantClient
from ..vdb_interface import VectorDBInterface
from typing import List, Optional, Dict, Any
from helpers.logger import get_logger
from models.chunk_model import ChunkMetadata
from ..exceptions import (
    VectorDBConnectionError,
    VectorDBCollectionNotFoundError,
    VectorDBInsertError,
    VectorDBBatchInsertError,
    VectorDBFetchError,
    VectorDBSearchError
)

logger = get_logger(__name__)


class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: str, vector_size: int):
        self.client: Optional[QdrantClient] = None
        self.db_path = db_path
        self.vector_size = vector_size
        self.distance_method = {
            "cosine": models.Distance.COSINE,
            "dot": models.Distance.DOT
        }.get(distance_method, models.Distance.COSINE)

    def connect(self):
        try:
            self.client = QdrantClient(path=self.db_path)
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise VectorDBConnectionError(f"Failed to connect to Qdrant: {e}") from e

    def disconnect(self):
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> List[str]:
        return [c.name for c in self.client.get_collections().collections]

    def create_collection_name(self, project_id: str, tenant_id: str) -> str:
        return f"vdb_{tenant_id}_{project_id}".lower().strip()

    def get_collection_info(self, collection_name: str) -> dict:
        try:
            if not self.is_collection_existed(collection_name):
                raise VectorDBCollectionNotFoundError(f"Collection {collection_name} does not exist")
            return self.client.get_collection(collection_name=collection_name)
        except VectorDBCollectionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch collection info: {e}")
            raise VectorDBFetchError(f"Failed to fetch collection info: {e}") from e

    def delete_collection(self, collection_name: str):
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        raise VectorDBCollectionNotFoundError(f"Collection {collection_name} does not exist")

    def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if do_reset and self.is_collection_existed(collection_name):
            self.delete_collection(collection_name)
            logger.info(f"Deleted collection {collection_name} for reset")

        if not self.is_collection_existed(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            logger.info(f"Created collection {collection_name}")
            return True
        return False

    async def _ensure_collection_exists(self, collection_name: str) -> bool:
        try:
            if self.is_collection_existed(collection_name):
                self.delete_collection(collection_name)
                logger.info(f"Deleted existing collection {collection_name}")
            self.create_collection(collection_name, embedding_size=self.vector_size)
            return True
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            raise VectorDBCollectionNotFoundError(f"Failed to ensure collection exists: {e}") from e

    async def store_batch(
        self,
        collection_name: str,
        batch_size: int,
        texts: List[str],
        vectors: List[List[float]],
        record_ids: List[str],
        metadatas: List[ChunkMetadata]
    ) -> bool:
        if not texts or not vectors or not metadatas:
            logger.warning("Skipping empty batch")
            return False
        if not (len(texts) == len(vectors) == len(metadatas) == len(record_ids)):
            raise VectorDBBatchInsertError("Batch size mismatch")

        await self._ensure_collection_exists(collection_name)

        success = self._insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            record_ids=record_ids,
            metadata=metadatas,
            batch_size=batch_size
        )

        if not success:
            raise VectorDBBatchInsertError(f"Failed to insert batch into {collection_name}")
        logger.info(f"Stored batch of {len(texts)} chunks in {collection_name}")
        return True

    def _insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        record_ids: list,
        metadata: list = None,
        batch_size: int = 50
    ):
        if metadata is None:
            metadata = [None] * len(texts)
        if not self.is_collection_existed(collection_name):
            raise VectorDBCollectionNotFoundError(f"Collection {collection_name} does not exist")

        for i in range(0, len(texts), batch_size):
            batch_points = [
                models.PointStruct(
                    id=record_ids[j],
                    vector=vectors[j],
                    payload={"text": texts[j], "metadata": metadata[j]}
                )
                for j in range(i, min(i + batch_size, len(texts)))
            ]
            try:
                self.client.upsert(collection_name=collection_name, points=batch_points)
            except Exception as e:
                logger.error(f"Batch insert failed: {e}")
                raise VectorDBBatchInsertError(f"Batch insert failed: {e}") from e
        return True

    def insert_one(self, collection_name: str, text: str, vector: list,
                   metadata: dict = None, record_id: str = None):
        if not self.is_collection_existed(collection_name):
            raise VectorDBCollectionNotFoundError(f"Collection {collection_name} does not exist")
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[models.PointStruct(id=record_id, vector=vector, payload={"text": text, "metadata": metadata})]
            )
            return True
        except Exception as e:
            logger.error(f"Single insert failed: {e}")
            raise VectorDBInsertError(f"Single insert failed: {e}") from e

    def get_collection_chunks(
        self,
        collection_name: str,
        page: int = 1,
        limit: int = 10,
        text_limit: Optional[int] = 100
    ) -> Dict[str, Any]:
        if page < 1:
            page = 1
        if not self.is_collection_existed(collection_name):
            raise VectorDBCollectionNotFoundError(f"Collection {collection_name} does not exist")

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
                text = payload.get("text", "")
                if text_limit and len(text) > text_limit:
                    text = text[:text_limit]
                chunks.append({"id": str(p.id), "text": text, "metadata": payload.get("metadata", {})})

            total_pages = (total_points + limit - 1) // limit
            return {"collection_name": collection_name, "total_chunks": total_points, "page": page,
                    "total_pages": total_pages, "returned_chunks": len(chunks), "chunks": chunks}
        except Exception as e:
            logger.error(f"Failed fetching chunks: {e}")
            raise VectorDBFetchError(f"Failed fetching chunks: {e}") from e

    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=vector,
                limit=limit,
                with_payload=True
            )
            return results.points
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise VectorDBSearchError(f"Vector search failed: {e}") from e

    async def hybrid_search(self, collection_name: str,
                            query_vector: List[float],
                            query_text: str = None,
                            limit: int = 10,
                            filter_conditions: Dict[str, Any] = None) -> List[Dict]:
        try:
            # Vector search with optional filtering
            search_params = {
                "collection_name": collection_name,
                "query": query_vector,
                "limit": limit,
                "with_payload": True,
                "with_vectors": True
            }
            if filter_conditions:
                must_conditions = [
                    models.FieldCondition(key=f"metadata.{k}", match=models.MatchValue(value=v))
                    for k, v in filter_conditions.items()
                ]
                if must_conditions:
                    search_params["query_filter"] = models.Filter(must=must_conditions)

            results = self.client.query_points(**search_params)
            return results.points
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            raise VectorDBSearchError(f"Hybrid search failed: {e}") from e

    async def keyword_search(self, collection_name: str,
                             query_text: str,
                             limit: int = 10,
                             filter_conditions: Dict[str, Any] = None) -> List[Dict]:
        try:
            search_params = {
                "collection_name": collection_name,
                "query": query_text,
                "limit": limit,
                "with_payload": True
            }
            if filter_conditions:
                must_conditions = [
                    models.FieldCondition(key=f"metadata.{k}", match=models.MatchValue(value=v))
                    for k, v in filter_conditions.items()
                ]
                if must_conditions:
                    search_params["query_filter"] = models.Filter(must=must_conditions)

            results = self.client.query_points(**search_params)
            return results.points
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            raise VectorDBSearchError(f"Keyword search failed: {e}") from e