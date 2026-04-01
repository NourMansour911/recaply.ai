from fastapi import APIRouter, UploadFile, File,Depends

from typing import List

from helpers import get_logger
from core import get_tenant_id
from orchestrators import get_upload_orchestrator,get_chains_orchestrator,get_chat_orchestrator,UploadOrchestrator,ChainsOrchestrator,ChatOrchestrator
from schemas import UploadFilesResponse,ChainsResponse,ChatRequest


logger = get_logger(__name__)

workspace_route = APIRouter(
    prefix="/api/v1/workspace/{project_id}",
    tags=["api","v1" , "upload", ],
)



@workspace_route.post("/upload",response_model=UploadFilesResponse,description="Upload files to a specific project ")
async def upload_files(project_id: str,files: List[UploadFile]= File(...),tenant_id: str = Depends(get_tenant_id)
                       ,orchestrator: UploadOrchestrator = Depends(get_upload_orchestrator)):
    return await orchestrator.execute_batch(files=files,tenant_id=tenant_id,project_id=project_id)

@workspace_route.get("/chains",response_model=ChainsResponse,description="get comprehensive meeting report")
async def get_chains(project_id: str,tenant_id: str = Depends(get_tenant_id)
                       ,orchestrator: ChainsOrchestrator = Depends(get_chains_orchestrator)):
    return await orchestrator.execute(tenant_id=tenant_id,project_id=project_id)


@workspace_route.post("/chat",description="Chat with a specific project files")
async def chat(chat_request: ChatRequest,project_id: str,tenant_id: str = Depends(get_tenant_id)
                       ,orchestrator: ChatOrchestrator = Depends(get_chat_orchestrator)):
    return await orchestrator.execute(chat_request=chat_request,tenant_id=tenant_id,project_id=project_id)
    



   