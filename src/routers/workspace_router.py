from fastapi import APIRouter, UploadFile, File,Depends

from typing import List

from helpers import get_logger
from core import get_tenant_id
from orchestrators import get_upload_orchestrator
from orchestrators import UploadOrchestrator
from schemas import UploadFilesResponse


logger = get_logger(__name__)

workspace_route = APIRouter(
    prefix="/api/v1/workspace/{project_id}",
    tags=["api","v1" , "upload", ],
)



@workspace_route.post("/upload",response_model=UploadFilesResponse,description="Upload files to a specific project ")
async def upload_files(project_id: str,files: List[UploadFile]= File(...),tenant_id: str = Depends(get_tenant_id)
                       ,orchestrator: UploadOrchestrator = Depends(get_upload_orchestrator)):
    return await orchestrator.execute_batch(files=files,tenant_id=tenant_id,project_id=project_id)
    



   