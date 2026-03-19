from fastapi import APIRouter, UploadFile, Request,File,Depends

from typing import List

from helpers import get_logger
from core import get_tenant_id,Settings,get_settings
from services import get_upload_orchestrator
from services.orchestrators import UploadOrchestrator
from schemas import UploadResponseSchema


logger = get_logger(__name__)

files_route = APIRouter(
    prefix="/api/projects/{project_id}/files",
    tags=["api_v1", "files", "admin"],
)



@files_route.post("",response_model=UploadResponseSchema,description="Upload files to a specific project ")
async def upload_files(project_id: str,files: List[UploadFile]= File(...),tenant_id: str = Depends(get_tenant_id)
                       ,orchestrator: UploadOrchestrator = Depends(get_upload_orchestrator)):
    return await orchestrator.execute_batch(files=files,tenant_id=tenant_id,project_id=project_id)
    

@files_route.get("",description="List all files for a project ")
async def list_project_files(project_id: str,files: List[UploadFile]= File(...),tenant_id: str = Depends(get_tenant_id)):
    pass

@files_route.delete("/{file_id}",description="Delete a file and all associated chunks (project-scoped)")
async def delete_file(tenant_id: str = Depends(get_tenant_id)):
    pass



   