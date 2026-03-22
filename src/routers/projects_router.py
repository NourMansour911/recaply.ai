from fastapi import APIRouter, UploadFile, Request,File,Depends

from typing import List

from helpers import get_logger
from core.main_dependencies import get_tenant_id

logger = get_logger(__name__)

projects_route = APIRouter(
    prefix="/api/projects",
    tags=["api_v1", "projects", "admin"],
)





@projects_route.get("",description="List all projects for the tenant")
async def list_projects(tenant_id: str = Depends(get_tenant_id)):
    pass


@projects_route.get("/{project_id}",description="Retrieve details of specific project (tenant-scoped)") 
async def get_project_info(tenant_id: str = Depends(get_tenant_id)):
    pass

@projects_route.delete("/{project_id}",description="Delete a project along with all files, chunks, chains and summaries (tenant-scoped)")
async def delete_project(tenant_id: str = Depends(get_tenant_id)):
    pass




   