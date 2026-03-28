from fastapi import UploadFile,HTTPException
from helpers.logger import get_logger
from core.settings import Settings
from services.files import FileDetectorService, FileStorageService, FileValidatorService
from repos import ProjectRepo,FileRepo
from models import FileModel,ProjectModel
from services.normalizers import NormalizerFactory
from services.chunking import ChunkingService
from services.project_service import ProjectService
from integrations.vector_db import VectorDBInterface
from integrations.llm import LLMInterface
from models.file_model import Segment
from schemas import UploadFilesSchema
from typing import List

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
        vdb_client: VectorDBInterface, 
        embedding_client: LLMInterface ,
        chunking_service: ChunkingService,
        project_service: ProjectService
        
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
        self.project_service = project_service


    async def _upload_normalize(
        self,
        file: UploadFile,
        file_order: int,
        project: ProjectModel,

    ):
        logger.info("Starting upload flow")

        
        file_type = self.detector.detect(file)

        
        await self.validator.validate(file, file_type)

        
        file_path, original_name,unique_name = self.storage_service.generate_file_path(
            original_filename=file.filename,
            tenant_id=project.tenant_id,
            project_id=project.project_id,
            file_order=file_order
        )

        
        await self.storage_service.save_file(file, file_path)
        
        file_size_mb = (file.size / self.settings.TO_BYTES).__ceil__()

        
        normalizer = NormalizerFactory.create_normalizer(file_name=original_name,file_type=file_type, tenant_id=project.tenant_id, project_id=project.project_id, file_path=file_path)
        
        normalized_segments : List[Segment] = await normalizer.normalize()
        file_duration = normalized_segments[-1].end
        
        
        logger.info(
            f"Using project: {project.project_id} (DB ID: {str(project.iid)})"
        )
        
        file_model = FileModel(
            file_tenant_id=project.tenant_id,
            file_project_iid=project.iid,
            file_name=original_name,
            file_type=file_type,
            file_content=normalized_segments,
            file_unique_name=unique_name,
            file_size_mb=file_size_mb,
            file_path=file_path,
            file_order=file_order,
            file_duration=file_duration,
            file_project_id=project.project_id,
        )
        
        file_iid = await self.file_repo.add_file(file_model)
        file_model.iid = file_iid
        
        logger.info(
            "Upload flow completed",
            extra={
                "file_path": file_path,
                "file_type": file_type,
                "file_size": file_size_mb,
            },
        )
        
        

        return file_model
        
    
    async def execute_batch(
        self,
        files: list[UploadFile],
        tenant_id: str,
        project_id: str,
    ):
        
        if await self.project_repo.project_exists(project_id=project_id,tenant_id=tenant_id):
           await self.project_service.delete_project(project_id=project_id,tenant_id=tenant_id)
        
        project : ProjectModel= await self.project_repo.get_project_or_create_one(project_id=project_id, tenant_id=tenant_id) 
        logger.info("Starting batch upload flow", extra={"files_count": len(files)})
        
        
        
        normalized_files : List[FileModel] = []
        total_chunks = 0
        total_files = 0
        project_vectors = []
        project_texts = []
        
        project_metadatas = []
        
        for i,file in enumerate(files):
            file_model = await self._upload_normalize(file, project=project,file_order=i+1)
            normalized_files.append(file_model)
            texts, vectors, _ ,metadatas = await self.chunking_service.process_file_chunks(file_model=file_model,idx=total_chunks )
            project_texts.extend(texts)
            project_vectors.extend(vectors)
            project_metadatas.extend(metadatas)
            total_chunks += len(texts)
            total_files += 1
        
        vectorDB_collection = self.vdb_client.create_collection_name(project_id=project_id,tenant_id=tenant_id)
        project_record_ids = list(range(total_chunks))
        logger.info(f"{len(project_texts)},{len(project_vectors)},{len(project_record_ids)},{len(project_metadatas)}")
        chunks_stored = await self.vdb_client.store_batch(collection_name=vectorDB_collection,batch_size=250,texts=project_texts, vectors=project_vectors,record_ids=project_record_ids,metadatas=project_metadatas)
        
        if chunks_stored:
            logger.info("Chunks stored successfully")
            return UploadFilesSchema(total_files=total_files,
                                    vectorDB_collection=vectorDB_collection,
                                    project_iid=str(project.iid),
                                    total_chunks=total_chunks,
                                    files=normalized_files
                                    )

        
        
 