from fastapi import UploadFile,HTTPException
from helpers.logger import get_logger
from core.settings import Settings
from services.files import FileDetectorService, FileStorageService, FileValidatorService
from repos import ProjectRepo,FileRepo
from models import FileModel,ProjectModel
from services.normalizers import NormalizerFactory
from schemas.normalized_schemas import NormalizedContent
from services.chunking import ChunkingService
from integrations.vector_db import VectorDBFactory
from integrations.llm import LLMFactory
from bson import ObjectId
from schemas import UploadFilesSchema,NormalizedFileData

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
        embedding_client: LLMFactory,
        chunking_service: ChunkingService
        
    ):
        self.storage_service = storage_service
        self.detector = detector
        self.validator = validator
        self.settings = settings
        self.file_repo = file_repo
        self.project_repo = project_repo
        self.vdb_client = vdb_client
        self.embedding_client = embedding_client
        self.chunking_service = chunking_service



    async def _execute(
        self,
        file: UploadFile,
        file_order: int,
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
            file_order=file_order
        )

        
        await self.storage_service.save_file(file, file_path)
        
        file_size_mb = (file.size / self.settings.TO_BYTES).__round__(2)

        
        normalizer = NormalizerFactory.create_normalizer(file_name=original_name,file_type=file_type, tenant_id=tenant_id, project_id=project.project_id, file_path=file_path)
        
        normalized_file : NormalizedContent = await normalizer.normalize()
        
        
        
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
            file_order=file_order
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
        
        

        return NormalizedFileData(
            file_id=str(file_iid),
            file_name=original_name,
            file_type=file_type,
            file_size=file_size_mb,
            file_path=file_path,
            file_order=file_order,
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
        
        
        vectorDB_collections = []
        total_chunks = 0
        total_files = 0
        for i,file in enumerate(files):
            file_data = await self._execute(file, tenant_id=tenant_id, project=project,file_order=i+1)
            
            vdb_collection_name , no_of_chunks = await self.chunking_service.process_and_store_chunks(file_data=file_data, project_iid=str(project.iid), tenant_id=tenant_id,project_id=project_id)
            total_chunks += no_of_chunks
            total_files += 1
            vectorDB_collections.append(vdb_collection_name)

        return UploadFilesSchema( total_files=total_files,
                                 vectorDB_collections=vectorDB_collections,
                                 project_iid=str(project.iid),
                                 total_chunks=total_chunks)
        
        
 