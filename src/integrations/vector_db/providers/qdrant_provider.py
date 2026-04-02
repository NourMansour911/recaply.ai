
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


from .bm25 import BM25Encoder

class QdrantDBProvider(VectorDBInterface):

    def __init__(self,  distance_method: str, vector_size: int):
        self.client: Optional[QdrantClient] = None

        self.vector_size = vector_size
        self.distance_method = None
        if distance_method == "cosine":
            self.distance_method = models.Distance.COSINE
        elif distance_method == "dot":
            self.distance_method = models.Distance.DOT

        self.bm25_map: Dict[str, BM25Encoder] = {}
        
        

    def connect(self) -> None:
        try:
            self.client = QdrantClient(host="localhost", port=6333)
            logger.info("[CONNECT SUCCESS]")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise VectorDBConnectionError(
                f"Failed to connect to Qdrant: {e}"
            ) from e

    def disconnect(self) -> None:
        self.client = None
        logger.info("[DISCONNECT] Client cleared")

    def fit_bm25(self, collection_name: str, texts: List[str]):
        bm25 = BM25Encoder()
        bm25.fit(texts)
        self.bm25_map[collection_name] = bm25
        logger.info(
            f"[BM25] Fitted for '{collection_name}' "
            f"with {len(texts)} documents, "
            f"vocab size: {len(bm25.vocab)}"
        )


    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> List[str]:
        return [c.name for c in self.client.get_collections().collections]

    def create_collection_name(self, project_id: str, tenant_id: str) -> str:
        return f"vdb_{tenant_id}_{project_id}".lower().strip()

    def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        do_reset: bool = False
    ) -> bool:
        if do_reset and self.is_collection_existed(collection_name):
            self.delete_collection(collection_name)
            logger.info(f"Deleted collection {collection_name} for reset")

        if not self.is_collection_existed(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                ),
                sparse_vectors_config={
                    "bm25": models.SparseVectorParams()
                }
            )
            logger.info(f"Created collection {collection_name}")
            return True
        return False

    async def ensure_collection_exists(self, collection_name: str) -> bool:
        try:
            if not self.is_collection_existed(collection_name):
                self.create_collection(
                    collection_name,
                    embedding_size=self.vector_size
                )
                logger.info(f"Created collection {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            raise VectorDBCollectionNotFoundError(
                f"Failed to ensure collection exists: {e}"
            ) from e

    def delete_collection(self, collection_name: str) -> None:
        if self.is_collection_existed(collection_name):

            self.bm25_map.pop(collection_name, None)
            self.client.delete_collection(collection_name=collection_name)
            return
        raise VectorDBCollectionNotFoundError(
            f"Collection {collection_name} does not exist"
        )

    def get_collection_info(self, collection_name: str) -> dict:
        try:
            if not self.is_collection_existed(collection_name):
                raise VectorDBCollectionNotFoundError(
                    f"Collection {collection_name} does not exist"
                )
            return self.client.get_collection(
                collection_name=collection_name
            )
        except VectorDBCollectionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to fetch collection info: {e}")
            raise VectorDBFetchError(
                f"Failed to fetch collection info: {e}"
            ) from e


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
        if not (
            len(texts) == len(vectors)
            == len(metadatas) == len(record_ids)
        ):
            raise VectorDBBatchInsertError("Batch size mismatch")

        await self.ensure_collection_exists(collection_name)


        self.fit_bm25(collection_name, texts)

        success = self._insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            record_ids=record_ids,
            metadata=metadatas,
            batch_size=batch_size
        )

        if not success:
            raise VectorDBBatchInsertError(
                f"Failed to insert batch into {collection_name}"
            )
        logger.info(
            f"Stored batch of {len(texts)} chunks in {collection_name}"
        )
        return True

    def _insert_many(
        self,
        collection_name: str,
        texts: list,
        vectors: list,
        record_ids: list,
        metadata: list = None,
        batch_size: int = 50
    ) -> bool:
        if metadata is None:
            metadata = [None] * len(texts)
        if not self.is_collection_existed(collection_name):
            raise VectorDBCollectionNotFoundError(
                f"Collection {collection_name} does not exist"
            )

        bm25 = self.bm25_map.get(collection_name)

        for i in range(0, len(texts), batch_size):
            batch_points = []

            for j in range(i, min(i + batch_size, len(texts))):

               
                point_vector: Any = vectors[j]

                if bm25:
                    indices, values = bm25.encode(texts[j])
                    if indices and values:
                        point_vector = {
                            "": vectors[j],
                            "bm25": models.SparseVector(
                                indices=indices, values=values
                            )
                        }

                meta = metadata[j]
                if meta is not None and hasattr(meta, "dict"):
                    meta = meta.dict()
                elif meta is None:
                    meta = {}

                batch_points.append(
                    models.PointStruct(
                        id=record_ids[j],
                        vector=point_vector,
                        payload={
                            "text": texts[j],
                            "metadata": meta
                        }
                    )
                )

            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points
                )
            except Exception as e:
                logger.error(f"Batch insert failed: {e}")
                raise VectorDBBatchInsertError(
                    f"Batch insert failed: {e}"
                ) from e

        return True

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        record_id: Optional[str] = None
    ) -> bool:
        if not self.is_collection_existed(collection_name):
            raise VectorDBCollectionNotFoundError(
                f"Collection {collection_name} does not exist"
            )
        try:
            point_vector: Any = vector
            bm25 = self.bm25_map.get(collection_name)

            if bm25:
                indices, values = bm25.encode(text)
                if indices and values:
                    point_vector = {
                        "": vector,
                        "bm25": models.SparseVector(
                            indices=indices, values=values
                        )
                    }

            self.client.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record_id,
                        vector=point_vector,
                        payload={
                            "text": text,
                            "metadata": metadata or {}
                        }
                    )
                ]
            )
            return True
        except Exception as e:
            logger.error(f"Single insert failed: {e}")
            raise VectorDBInsertError(
                f"Single insert failed: {e}"
            ) from e


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
            raise VectorDBCollectionNotFoundError(
                f"Collection {collection_name} does not exist"
            )

        try:
            collection_info = self.client.get_collection(
                collection_name=collection_name
            )
            total_points = collection_info.points_count


            offset = None
            points = []

            for current_page in range(1, page + 1):
                batch, next_offset = self.client.scroll(
                    collection_name=collection_name,
                    limit=limit,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                if current_page == page:
                    points = batch
                    break
                offset = next_offset
                if offset is None:
                    points = []
                    break

            chunks = []
            for p in points:
                payload = p.payload or {}
                text = payload.get("text", "")
                if text_limit and len(text) > text_limit:
                    text = text[:text_limit]
                chunks.append({
                    "id": str(p.id),
                    "text": text,
                    "metadata": payload.get("metadata", {})
                })

            total_pages = (
                (total_points + limit - 1) // limit
                if total_points else 0
            )
            return {
                "collection_name": collection_name,
                "total_chunks": total_points,
                "page": page,
                "total_pages": total_pages,
                "returned_chunks": len(chunks),
                "chunks": chunks
            }
        except Exception as e:
            logger.error(f"Failed fetching chunks: {e}")
            raise VectorDBFetchError(
                f"Failed fetching chunks: {e}"
            ) from e


    def search_by_vector(
        self,
        collection_name: str,
        vector: List[float],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=vector,
                limit=limit,
                with_payload=True
            )
            return [
                {
                    "id": str(p.id),
                    "score": p.score,
                    "text": (p.payload or {}).get("text", ""),
                    "metadata": (p.payload or {}).get("metadata", {})
                }
                for p in results.points
            ]
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            raise VectorDBSearchError(
                f"Vector search failed: {e}"
            ) from e

    async def search_by_keyword(
        self,
        collection_name: str,
        query_text: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        logger.info(f"[BM25] collection: {collection_name} ")
        try:
            bm25 = self.bm25_map.get(collection_name)


            if not bm25:
                
                raise VectorDBCollectionNotFoundError(
                    f"bm25 not found for {collection_name} does not exist (BM25 MAP KEYS: {list(self.bm25_map.keys())})"
                )

            indices, values = bm25.encode(query_text)

            if not indices:
                logger.warning(
                    f"[BM25] No matching terms for: '{query_text}'"
                )
                return []

            results = self.client.query_points(
                collection_name=collection_name,
                query=models.SparseVector(
                    indices=indices, values=values
                ),
                using="bm25",
                limit=limit,
                with_payload=True
            )

            return [
                {
                    "id": str(p.id),
                    "score": p.score,
                    "text": (p.payload or {}).get("text", ""),
                    "metadata": (p.payload or {}).get("metadata", {})
                }
                for p in results.points
            ]

        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            raise VectorDBSearchError(
                f"Keyword search failed: {e}"
            ) from e