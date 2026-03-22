from orchestrators.upload_orchestrator import UploadOrchestrator
from repos.repos_dependencies import get_project_repo,get_file_repo
from repos.project_repo import ProjectRepo
from repos.file_repo import FileRepo
from services.services_dependencies import get_storage_service, get_file_detector, get_file_validator
from core.settings import Settings, get_settings
from services.files import FileDetectorService, FileStorageService, FileValidatorService
from fastapi import Depends
from integrations import get_vdb_client, get_embedding_client 
from integrations.vector_db import VectorDBFactory
from integrations.llm import LLMFactory


def get_upload_orchestrator(
    storage: FileStorageService = Depends(get_storage_service),
    detector: FileDetectorService = Depends(get_file_detector),
    validator: FileValidatorService = Depends(get_file_validator),
    settings: Settings = Depends(get_settings),
    project_repo: ProjectRepo = Depends(get_project_repo),
    file_repo: FileRepo = Depends(get_file_repo),
    vdb_client: VectorDBFactory = Depends(get_vdb_client),
    embedding_client: LLMFactory = Depends(get_embedding_client),
) -> UploadOrchestrator:

    return UploadOrchestrator(
        storage_service=storage,
        detector=detector,
        validator=validator,
        settings=settings,
        project_repo=project_repo,
        file_repo=file_repo,
        vdb_client=vdb_client,
        embedding_client=embedding_client

    )