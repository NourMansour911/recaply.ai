from repos.file_repo import FileRepo
from repos.project_repo import ProjectRepo
from integrations.vector_db import VectorDBInterface
from schemas import (
    DeleteProjectResponse,
    DeleteTenantResponse
)
import asyncio


class ProjectService:

    def __init__(self, project_repo: ProjectRepo, file_repo: FileRepo, vdb_client: VectorDBInterface):
        self.project_repo = project_repo
        self.file_repo = file_repo
        self.vdb_client = vdb_client


    async def delete_project(self, project_id: str, tenant_id: str) -> DeleteProjectResponse:

        project = await self.project_repo.get_project(project_id, tenant_id)

        if not project:
            return DeleteProjectResponse(
                success=False,
                message="Project not found",
                project_id=project_id
            )

        project_iid = project.iid

        
        await self.file_repo.delete_files_by_project(project_iid)

        collection_name = self.vdb_client.create_collection_name(
            project_id=project_id,
            tenant_id=tenant_id
        )

        await self._safe_delete_collection(collection_name)

        await self.project_repo.delete_project_by_iid(project_iid)

        return DeleteProjectResponse(
            success=True,
            message="Project deleted successfully",
            project_id=project_id
        )


    async def delete_tenant(self, tenant_id: str) -> DeleteTenantResponse:

        projects = await self.project_repo.get_projects_by_tenant(tenant_id)

        if not projects:
            return DeleteTenantResponse(
                success=False,
                message="No data found for tenant",
                tenant_id=tenant_id,
                deleted_projects_count=0
            )

        project_iids = [p.iid for p in projects]

        
        await self.file_repo.delete_files_by_projects(project_iids)

        
        tasks = []
        for project in projects:
            collection_name = self.vdb_client.create_collection_name(
                project_id=project.project_id,
                tenant_id=tenant_id
            )
            tasks.append(self._safe_delete_collection(collection_name))

        await asyncio.gather(*tasks)

       
        deleted_count = await self.project_repo.delete_projects_by_tenant(tenant_id)

        return DeleteTenantResponse(
            success=True,
            message="All tenant data deleted successfully",
            tenant_id=tenant_id,
            deleted_projects_count=deleted_count
        )


    async def _safe_delete_collection(self, collection_name: str):
        try:
            await self.vdb_client.delete_collection(collection_name)
        except Exception:
            pass