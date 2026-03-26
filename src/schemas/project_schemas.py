from pydantic import BaseModel
from typing import Optional


class DeleteProjectResponse(BaseModel):
    success: bool
    message: str
    project_id: Optional[str] = None


class DeleteTenantResponse(BaseModel):
    success: bool
    message: str
    tenant_id: Optional[str] = None
    deleted_projects_count: Optional[int] = 0