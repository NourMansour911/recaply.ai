from fastapi import APIRouter, UploadFile, Request,File,Depends

from typing import List

from helpers import get_logger
from core.dependencies import get_tenant_id

logger = get_logger(__name__)

files_router = APIRouter(
    prefix="/projects",
    tags=["api_v1", "files"],
)



@files_router.post("/{project_id}/files")
async def upload_files(project_id: str,files: List[UploadFile]= File(...),tenant_id: str = Depends(get_tenant_id)):
    pass

@files_router.get("/{project_id}/files")
async def get_project_files(project_id: str,files: List[UploadFile]= File(...),tenant_id: str = Depends(get_tenant_id)):
    pass




   