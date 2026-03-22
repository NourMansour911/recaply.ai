from fastapi import Depends

from core.settings import Settings, get_settings

from services.files.file_storage_service import FileStorageService
from services.files.file_detector_service import FileDetectorService
from services.files.file_validator_service import FileValidatorService
from services.chunking import ChunkingService
from integrations import get_vdb_client, get_embedding_client
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
   vdb_client = Depends(get_vdb_client),embedding_client  = Depends(get_embedding_client)
) -> ChunkingService:
    return ChunkingService(embedding_client,vdb_client,settings=Depends(get_settings))