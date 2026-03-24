from helpers.logger import get_logger
from schemas import SearchRequest
from fastapi import HTTPException, status
from integrations.vector_db import VectorDBInterface
from integrations.llm import LLMInterface, DocumentTypeEnum
from typing import List,Optional
from helpers.enums import Signals
import json
from schemas import CollectionChunksResponse, ChunkResponse
from models import ChunkMetadata
logger = get_logger(__name__)


class VDBService:

    def __init__(
        self,
        vdb_client: VectorDBInterface,
        generation_client: LLMInterface ,
        embedding_client: LLMInterface 
    ):

        self.vdb_client = vdb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client

        logger.info("Vector DB Push Service initialized")

    def get_collection_info(self, project_id: str,tenant_id: str):
        collection_name = self._create_collection_name(project_id,tenant_id)
        info = self.vdb_client.get_collection_info(collection_name=collection_name)
        return json.loads(
            json.dumps(info,default=lambda x: x.__dict__)
        )
    
    def get_chunks(
        self,
        project_id: str,tenant_id: str,
        page: int = 1,
        limit: int = 10,
        text_limit: Optional[int] = 100
    ) -> CollectionChunksResponse:

        
        collection_name = self._create_collection_name(project_id,tenant_id)
        raw_data = self.vdb_client.get_collection_chunks(
            collection_name=collection_name,
            page=page,
            limit=limit,
            text_limit=text_limit
        )

        
        chunks = []
        for chunk_dict in raw_data["chunks"]:
            metadata = ChunkMetadata(**chunk_dict["metadata"])
            chunk = ChunkResponse(
                id=chunk_dict["id"],
                text=chunk_dict["text"],
                metadata=metadata
            )
            chunks.append(chunk)

        
        response = CollectionChunksResponse(
            collection_name=raw_data["collection_name"],
            total_chunks=raw_data["total_chunks"],
            page=raw_data["page"],
            total_pages=raw_data["total_pages"],
            returned_chunks=raw_data["returned_chunks"],
            chunks=chunks
        )

        return response
    
    async def vdb_search(self, project_id: str, request_schema: SearchRequest):

        collection_name = self._create_collection_name(project_id)
        vector = self.embedding_client.embed_text(
                text=request_schema.query,
                document_type=DocumentTypeEnum.QUERY.value
            )
        
        if vector is None or len(vector) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Signals.QUERY_VECTORIZE_FAILED.value
                )
            
        search_results = self.vdb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector.tolist(),
            limit=request_schema.limit
        )
        return search_results

        
    def _create_collection_name(self, project_id: str,tenant_id: str):
        return f"vdb_{tenant_id}_{project_id}"


