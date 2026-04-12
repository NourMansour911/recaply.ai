from helpers.logger import get_logger
from schemas.vectordb_schema import CollectionChunksResponse, ChunkResponse
from integrations.vector_db import VectorDBInterface
from integrations.llm import LLMInterface
from typing import Optional
import json
from models import ChunkMetadata


from .vdb_exceptions import (
    VectorDBException,

)
from ..service_exceptions import ProcessingError


logger = get_logger("vectordb_service")


class VDBService:

    def __init__(
        self,
        vdb_client: VectorDBInterface,
        embedding_client: LLMInterface,
        
    ):
        self.vdb_client = vdb_client
        self.embedding_client = embedding_client
        

        logger.info("Vector DB Push Service initialized")

    def get_collection_info(self, project_id: str, tenant_id: str):
        try:
            collection_name = self.vdb_client.create_collection_name(project_id, tenant_id)
            info = self.vdb_client.get_collection_info(collection_name=collection_name)

            return json.loads(
                json.dumps(info, default=lambda x: x.__dict__)
            )

        except Exception as e:
            details = {
                "error": str(e),
                "type": type(e).__name__,
                "context": {
                    "project_id": project_id,
                    "tenant_id": tenant_id
                }
            }
            logger.error("Failed to get collection info", extra=details)
            raise VectorDBException(details=details)

    def get_chunks(
        self,
        project_id: str,
        tenant_id: str,
        page: int = 1,
        limit: int = 10,
        text_limit: Optional[int] = 100
    ) -> CollectionChunksResponse:

        try:
            if page < 1:
                page = 1

            collection_name = self.vdb_client.create_collection_name(project_id, tenant_id)

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

        except Exception as e:
            details = {
                "error": str(e),
                "type": type(e).__name__,
                "context": {
                    "project_id": project_id,
                    "tenant_id": tenant_id,
                    "page": page,
                    "limit": limit
                }
            }
            logger.error("Failed to get chunks", extra=details)
            raise ProcessingError(details=details)

    