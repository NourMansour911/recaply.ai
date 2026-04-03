from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from models.chunk_model import ChunkMetadata
class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    # Collections
    @abstractmethod
    def is_collection_existed(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def list_all_collections(self) -> List[str]:
        pass

    @abstractmethod
    def create_collection_name(self, project_id: str, tenant_id: str) -> str:
        pass

    @abstractmethod
    def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        do_reset: bool = False
    ) -> bool:
        pass

    @abstractmethod
    async def ensure_collection_exists(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> None:
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        pass

    # Insert
    @abstractmethod
    async def store_batch(
        self,
        collection_name: str,
        batch_size: int,
        texts: List[str],
        vectors: List[List[float]],
        record_ids: List[str],
        metadatas: List[ChunkMetadata]
    ) -> bool:
        pass

    @abstractmethod
    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        record_id: Optional[str] = None
    ) -> bool:
        pass

 
    @abstractmethod
    def get_collection_chunks(
        self,
        collection_name: str,
        page: int = 1,
        limit: int = 10,
        text_limit: Optional[int] = 100
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def search_by_vector(
        self,
        collection_name: str,
        vector: List[float],
        limit: int 
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def search_by_keyword(
        self,
        collection_name: str,
        query_text: str,
        limit: int 
    ) -> List[Dict[str, Any]]:
        pass