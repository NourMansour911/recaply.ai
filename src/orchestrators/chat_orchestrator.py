from typing import List, Dict
from helpers.logger import get_logger
from schemas import  ChatRequest
from repos import FileRepo, ProjectRepo
from models import  FileModel
from services.chat import ChatService
from services.project_service import ProjectServiceException

logger = get_logger(__name__)


class ChatOrchestrator:

    def __init__(
        self,
        file_repo: FileRepo,
        project_repo: ProjectRepo,
        chat_service: ChatService,
    ):
        self.file_repo = file_repo
        self.project_repo = project_repo
        self.chat_service = chat_service

    async def execute(
        self,
        chat_request: ChatRequest,
        project_id: str,
        tenant_id: str,
        session_id: str,
        user_id: str
    ) :


        try:
            project = await self.project_repo.get_project(
                project_id=project_id,
                tenant_id=tenant_id,
            )
        except Exception as e:
            logger.error("ProjectRepo failed", exc_info=True)
            raise ProjectServiceException(details={"project_id": project_id, "error": str(e)}) from e

        if not project:
            raise ProjectServiceException(details={"project_id": project_id, "error": "Project not found"})


        try:
            files: List[FileModel] = await self.file_repo.get_all_project_files(
                project_iid=project.iid
            )
        except Exception as e:
            logger.error("FileRepo failed", exc_info=True)
            raise ProjectServiceException(details={"project_iid": str(project.iid), "error": str(e)}) from e

        if not files:
            raise ProjectServiceException(details={"project_id": project_id, "error": "No files found"})
        
        logger.info(f"Starting chat flow{chat_request.message}")
        

        response = await self.chat_service.run(user_id=user_id,project_id=project_id,tenant_id=tenant_id,session_id=session_id,message=chat_request.message,vdb_collection_name=project.vdb_collection_name)

        return response
