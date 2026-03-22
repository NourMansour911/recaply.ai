from fastapi import Depends

from core.settings import Settings, get_settings

from services.files.file_storage_service import FileStorageService
from services.files.file_detector_service import FileDetectorService
from services.files.file_validator_service import FileValidatorService

from orchestrators.upload_orchestrator import UploadOrchestrator
from .repos_dependencies import get_project_repo,get_file_repo
from repos.project_repo import ProjectRepo
from repos.file_repo import FileRepo



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


def get_upload_orchestrator(
    storage: FileStorageService = Depends(get_storage_service),
    detector: FileDetectorService = Depends(get_file_detector),
    validator: FileValidatorService = Depends(get_file_validator),
    settings: Settings = Depends(get_settings),
    project_repo: ProjectRepo = Depends(get_project_repo),
    file_repo: FileRepo = Depends(get_file_repo),
) -> UploadOrchestrator:

    return UploadOrchestrator(
        storage_service=storage,
        detector=detector,
        validator=validator,
        settings=settings,
        project_repo=project_repo,
        file_repo=file_repo,

    )