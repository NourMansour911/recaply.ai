from fastapi import APIRouter, Depends
from helpers import get_logger
from services import get_project_service
from core.main_dependencies import get_tenant_id
from services.project_service import ProjectService
from schemas import (
    DeleteProjectResponse,
    DeleteTenantResponse
)

logger = get_logger(__name__)

projects_route = APIRouter(
    prefix="/api/v1/projects",
    tags=["Projects", "Admin"],
)


@projects_route.delete(
    "/{project_id}",
    response_model=DeleteProjectResponse,
    summary="Delete project",
    description="Deletes a project and all related files, vectors, and stored artifacts.",
    response_description="Project deletion result."
)
async def delete_project(
    project_id: str,
    tenant_id: str = Depends(get_tenant_id),
    service: ProjectService = Depends(get_project_service)
):
    return await service.delete_project(
        project_id=project_id,
        tenant_id=tenant_id
    )


@projects_route.delete(
    "/all/tenant",
    response_model=DeleteTenantResponse,
    summary="Delete tenant data",
    description="Deletes all data for the tenant, including projects, files, and vector entries.",
    response_description="Tenant deletion result."
)
async def delete_tenant(
    tenant_id: str = Depends(get_tenant_id),
    service: ProjectService = Depends(get_project_service)
):
    return await service.delete_tenant(tenant_id=tenant_id)