from fastapi import UploadFile
from helpers.logger import get_logger
from core import Settings
from services.files import *

logger = get_logger(__name__)


class UploadOrchestrator:
    def __init__(
        self,
        storage_service: FileStorageService,
        detector: FileDetectorService,
        validator: FileValidatorService,
        settings: Settings ,
        
    ):
        self.storage_service = storage_service
        self.detector = detector
        self.validator = validator
        self.settings = settings
        


    async def execute(
        self,
        file: UploadFile,
        tenant_id: str,
        project_id: str,
    ):
        logger.info("Starting upload flow")

        
        file_type = self.detector.detect(file)

        
        await self.validator.validate(file, file_type)

        
        file_path, original_name = self.storage_service.generate_file_path(
            original_filename=file.filename,
            tenant_id=tenant_id,
            project_id=project_id,
        )

        
        await self.storage_service.save_file(file, file_path)

        logger.info(
            "Upload flow completed",
            extra={
                "file_path": file_path,
                "file_type": file_type,
                "file_size": (file.size / self.settings.TO_BYTES).__round__(2),
            },
        )

        return {
            "file_name": original_name,
            "file_type": file_type,
            "file_size": (file.size / self.settings.TO_BYTES).__round__(2),
            "file_path": file_path,
        }
        
    async def execute_batch(
        self,
        files: list[UploadFile],
        tenant_id: str,
        project_id: str,
    ):
        
        logger.info("Starting batch upload flow", extra={"files_count": len(files)})

        results = []


        for file in files:
            result = await self.execute(file, tenant_id, project_id)
            results.append(result)

        return {
            "tenant_id": tenant_id,
            "project_id": project_id,
            "uploaded_files_count": len(results),
            "files": results,
            
        }