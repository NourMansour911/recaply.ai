from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class VectorDBInterface(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def is_collection_existed(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def list_all_collections(self) -> List:
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        pass
    
    @abstractmethod
    def create_collection_name(self, project_id: str,tenant_id: str):
        pass
    
    
    @abstractmethod
    def get_collection_chunks(
    self, collection_name: str, page: int = 1,limit: int = 10,
                text_limit: Optional[int] = 100 ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False):
        pass

    @abstractmethod
    def insert_one(self, collection_name: str, text: str, vector: list,
                         metadata: dict = None, 
                         record_id: str = None):
        pass

    @abstractmethod
    async def store_batch(self, collection_name, batch_size, text, vectors, record_ids, metadatas):
        pass
    

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list, limit: int):
        pass
    