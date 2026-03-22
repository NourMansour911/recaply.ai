from fastapi import UploadFile
from helpers.logger import get_logger
from core.settings import Settings
from services.files import FileDetectorService, FileStorageService, FileValidatorService
from repos import ProjectRepo,FileRepo
from models import FileModel,ProjectModel
from services.files.normalizers import NormalizerFactory

logger = get_logger(__name__)


class UploadOrchestrator:
    def __init__(
        self,
        storage_service: FileStorageService,
        detector: FileDetectorService,
        validator: FileValidatorService,
        settings: Settings ,
        file_repo: FileRepo ,
        project_repo: ProjectRepo 
        
    ):
        self.storage_service = storage_service
        self.detector = detector
        self.validator = validator
        self.settings = settings
        self.file_repo = file_repo
        self.project_repo = project_repo



    async def execute(
        self,
        file: UploadFile,
        tenant_id: str,
        project_id: str,
    ):
        logger.info("Starting upload flow")

        
        file_type = self.detector.detect(file)

        
        await self.validator.validate(file, file_type)

        
        file_path, original_name,unique_name = self.storage_service.generate_file_path(
            original_filename=file.filename,
            tenant_id=tenant_id,
            project_id=project_id,
        )

        
        await self.storage_service.save_file(file, file_path)
        
        
        ### Normalize 
        normalizer = NormalizerFactory.create_normalizer(file_path)
        
        ## Push to MongoDB
        project : ProjectModel= await self.project_repo.get_project_or_create_one(project_id=project_id, tenant_id=tenant_id) 
        
        logger.info(
            f"Using project: {project.project_id} (DB ID: {str(project.iid)})"
        )
        
        file_model = FileModel(
            file_tenant_id=tenant_id,
            file_project_iid=project.iid,
            file_name=original_name,
            file_type=file_type,
            file_size_mb=(file.size / self.settings.TO_BYTES).__round__(2),
            file_path=file_path,
        )
        
        file_iid = await self.file_repo.add_file(file_model)


        logger.info(
            "Upload flow completed",
            extra={
                "file_path": file_path,
                "file_type": file_type,
                "file_size": (file.size / self.settings.TO_BYTES).__round__(2),
            },
        )

        return {
            "project_iid": str(project.iid),
            "file_id": str(file_iid),
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