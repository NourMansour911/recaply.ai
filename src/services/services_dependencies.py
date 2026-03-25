from fastapi import Depends

from core.settings import Settings, get_settings

from integrations import get_vdb_client, get_embedding_client, get_generation_client
from integrations.llm import LLMInterface
from integrations.vector_db import VectorDBInterface

from .files.file_storage_service import FileStorageService
from .files.file_detector_service import FileDetectorService
from .files.file_validator_service import FileValidatorService
from  .vdb_service.vectordb_service import VDBService
from .chunking import ChunkingService 


def get_storage_service() -> FileStorageService:
    return FileStorageService()



def get_file_detector(
    settings: Settings = Depends(get_settings),
) -> FileDetectorService:
    return FileDetectorService(settings=settings)


def get_file_validator(
    settings: Settings = Depends(get_settings),
) -> FileValidatorService:
    return FileValidatorService(settings=settings)


def get_chunking_service(
   embedding_client  = Depends(get_embedding_client),
   settings: Settings = Depends(get_settings),
) -> ChunkingService:
    return ChunkingService(embedding_client,settings=settings)


def get_vdb_service(
    vdb_client: VectorDBInterface = Depends(get_vdb_client),
    generation_client: LLMInterface = Depends(get_generation_client),
    embedding_client: LLMInterface = Depends(get_embedding_client),
    
):
    return VDBService(

        vdb_client=vdb_client,
        generation_client=generation_client,
        embedding_client=embedding_client,
        
    )
