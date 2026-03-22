from fastapi import UploadFile,HTTPException
from helpers.logger import get_logger
from core.settings import Settings
from services.files import FileDetectorService, FileStorageService, FileValidatorService
from repos import ProjectRepo,FileRepo
from models import FileModel,ProjectModel
from services.normalizers import NormalizerFactory
from src.schemas.normalized_schemas import NormalizedFileModel
from services import SemanticChunkingCore
from integrations.vector_db import VectorDBFactory
from integrations.llm import LLMFactory
from bson import ObjectId
from schemas import NormalizedFilesSchema,FileResponseSchema

logger = get_logger(__name__)



class UploadOrchestrator:
    def __init__(
        self,
        storage_service: FileStorageService,
        detector: FileDetectorService,
        validator: FileValidatorService,
        settings: Settings ,
        file_repo: FileRepo ,
        project_repo: ProjectRepo ,
        vdb_client: VectorDBFactory ,
        embedding_client: LLMFactory
        
    ):
        self.storage_service = storage_service
        self.detector = detector
        self.validator = validator
        self.settings = settings
        self.file_repo = file_repo
        self.project_repo = project_repo
        self.vdb_client = vdb_client
        self.embedding_client = embedding_client



    async def _execute(
        self,
        file: UploadFile,
        project: ProjectModel,
        tenant_id: str,

    ):
        logger.info("Starting upload flow")

        
        file_type = self.detector.detect(file)

        
        await self.validator.validate(file, file_type)

        
        file_path, original_name,unique_name = self.storage_service.generate_file_path(
            original_filename=file.filename,
            tenant_id=tenant_id,
            project_id=project.project_id,
        )

        
        await self.storage_service.save_file(file, file_path)
        
        file_size_mb = (file.size / self.settings.TO_BYTES).__round__(2)

        
        normalizer = NormalizerFactory.create_normalizer(file_name=original_name,file_type=file_type, tenant_id=tenant_id, project_id=project.project_id, file_path=file_path)
        
        normalized_file : NormalizedFileModel = await normalizer.normalize()
        
        ## Push to MongoDB
        
        logger.info(
            f"Using project: {project.project_id} (DB ID: {str(project.iid)})"
        )
        
        file_model = FileModel(
            file_tenant_id=tenant_id,
            file_project_iid=project.iid,
            file_name=original_name,
            file_type=file_type,
            file_size_mb=file_size_mb,
            file_path=file_path,
        )
        
        file_iid = await self.file_repo.add_file(file_model)


        logger.info(
            "Upload flow completed",
            extra={
                "file_path": file_path,
                "file_type": file_type,
                "file_size": file_size_mb,
            },
        )
        
        

        return FileResponseSchema(
            file_id=str(file_iid),
            file_name=original_name,
            file_type=file_type,
            file_size=file_size_mb,
            file_path=file_path,
            normalized_file=normalized_file
        )
        
    
    async def execute_batch(
        self,
        files: list[UploadFile],
        tenant_id: str,
        project_id: str,
    ):
        project : ProjectModel= await self.project_repo.get_project_or_create_one(project_id=project_id, tenant_id=tenant_id) 
        
        logger.info("Starting batch upload flow", extra={"files_count": len(files)})

        results: list[FileResponseSchema] = []


        for file in files:
            result = await self._execute(file, tenant_id=tenant_id, project=project)
            results.append(result)
        
        response_date = NormalizedFilesSchema(
            tenant_id=tenant_id,
            project_iid=str(project.iid) if isinstance(project.iid, ObjectId) else project.iid,
            uploaded_files_count=len(results),
            files=results
        )
        return response_date
        
        
 
    async def process_semantic_chunks(self,normalized_files_data: NormalizedFilesSchema):
        try:
            
            chunking_service = SemanticChunkingCore(
                embedding_client=self.embedding_client,  
                vdb_client=self.vdb_client,   
                batch_size=32
            )
            
            success = await chunking_service.process_and_store_semantic_chunks(normalized_files_data)
            
            if success:
                logger.info("Semantic chunks processed and stored successfully")
            else:
                logger.error("Failed to process semantic chunks")
                
            return success
            
        except Exception as e:
            logger.error(f"Semantic chunking process failed: {str(e)}")
            raise
