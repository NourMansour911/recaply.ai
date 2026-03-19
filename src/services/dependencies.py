from fastapi import Depends

from core.settings import Settings, get_settings

from .files.file_storage_service import FileStorageService
from .files.file_detector_service import FileDetectorService
from .files.file_validator_service import FileValidatorService

from .orchestrators.upload_orchestrator import UploadOrchestrator


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
    settings: Settings = Depends(get_settings)
) -> UploadOrchestrator:

    return UploadOrchestrator(
        storage_service=storage,
        detector=detector,
        validator=validator,
        settings=settings
    )