from fastapi import APIRouter, UploadFile, Request,File,Depends

from typing import List

from helpers import get_logger
from core.dependencies import get_tenant_id

logger = get_logger(__name__)

project_router = APIRouter(
    prefix="/api/projects",
    tags=["api_v1", "projects", "admin"],
)





@project_router.get("",description="Retrieve all projects for the tenant")
async def get_projects(tenant_id: str = Depends(get_tenant_id)):
    pass


@project_router.get("/{project_id}",description="Retrieve details of specofoc project") 
async def get_project_info(tenant_id: str = Depends(get_tenant_id)):
    pass

@project_router.delete("/{project_id}",description="Delete a project along with all files, chunks, chains and summaries (tenant-scoped)")
async def delete_project(tenant_id: str = Depends(get_tenant_id)):
    pass




   