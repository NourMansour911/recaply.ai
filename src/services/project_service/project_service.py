from repos.file_repo import FileRepo
from repos.project_repo import ProjectRepo
from integrations.vector_db import VectorDBInterface
from schemas.project_schemas import DeleteProjectResponse, DeleteTenantResponse
from helpers import get_project_path, get_tenant_path, get_logger
import shutil
import os

from .project_exceptions import (
    ProjectServiceException,
    ProjectNotFoundError,
    TenantNotFoundError,
    ProjectFolderDeletionError,
    TenantFolderDeletionError,
    CollectionDeletionError
)

logger = get_logger("project_service")

class ProjectService:

    def __init__(self, project_repo: ProjectRepo, file_repo: FileRepo, vdb_client: VectorDBInterface):
        self.project_repo = project_repo
        self.file_repo = file_repo
        self.vdb_client = vdb_client

    async def delete_project(self, project_id: str, tenant_id: str) -> DeleteProjectResponse:
        project = await self.project_repo.get_project(project_id, tenant_id)
        if not project:
            raise ProjectNotFoundError(project_id,tenant_id)

        project_iid = project.iid

        try:
            self._delete_project_folder(tenant_id, project_id)
        except ProjectFolderDeletionError:
            raise

        try:
            await self.file_repo.delete_files_by_project(project_iid)
        except Exception as e:
            details = {"project_iid": project_iid, "error": str(e)}
            raise ProjectServiceException(details=details)

        collection_name = self.vdb_client.create_collection_name(project_id=project_id, tenant_id=tenant_id)
        try:
            await self._delete_collection_strict(collection_name)
        except CollectionDeletionError:
            raise

        try:
            await self.project_repo.delete_project_by_iid(project_iid)
        except Exception as e:
            details = {"project_iid": project_iid, "error": str(e)}
            raise ProjectServiceException(details=details)

        return DeleteProjectResponse(success=True, message="Project deleted successfully", project_id=project_id)

    async def delete_tenant(self, tenant_id: str) -> DeleteTenantResponse:
        projects = await self.project_repo.get_projects_by_tenant(tenant_id)
        tenant_path = get_tenant_path(tenant_id)
        tenant_exists = os.path.exists(tenant_path)

        if not projects and not tenant_exists:
            raise TenantNotFoundError(tenant_id)

        if tenant_exists:
            try:
                self._delete_tenant_folder(tenant_id)
            except TenantFolderDeletionError:
                raise

        deleted_count = 0
        if projects:
            project_iids = [p.iid for p in projects]
            try:
                await self.file_repo.delete_files_by_projects(project_iids)
            except Exception as e:
                details = {"project_iids": project_iids, "error": str(e)}
                raise ProjectServiceException(details=details)

            for project in projects:
                deleted_count += 1
                collection_name = self.vdb_client.create_collection_name(project_id=project.project_id, tenant_id=tenant_id)
                try:
                    await self._delete_collection_strict(collection_name)
                except CollectionDeletionError:
                    raise

            try:
                _ = await self.project_repo.delete_projects_by_tenant(tenant_id)
            except Exception as e:
                details = {"tenant_id": tenant_id, "error": str(e)}
                raise ProjectServiceException(details=details)

        return DeleteTenantResponse(success=True, message="Tenant data deleted successfully", tenant_id=tenant_id, deleted_projects_count=deleted_count)

    def _delete_project_folder(self, tenant_id: str, project_id: str):
        try:
            project_path = get_project_path(tenant_id=tenant_id, project_id=project_id, stage="all")
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
        except Exception as e:
            details = {"tenant_id": tenant_id, "project_id": project_id, "error": str(e)}
            logger.error(f"Failed to delete project folder {project_id}", extra=details)
            raise ProjectFolderDeletionError(project_id, tenant_id, details=details)

    def _delete_tenant_folder(self, tenant_id: str):
        try:
            tenant_path = get_tenant_path(tenant_id)
            if os.path.exists(tenant_path):
                shutil.rmtree(tenant_path)
                logger.info(f"Deleted tenant folder: {tenant_path}")
            else:
                logger.warning(f"Tenant folder not found: {tenant_path}")
        except Exception as e:
            details = {"tenant_id": tenant_id, "error": str(e)}
            logger.error(f"Failed to delete tenant folder {tenant_id}", extra=details)
            raise TenantFolderDeletionError(tenant_id, details=details)

    async def _delete_collection_strict(self, collection_name: str):
        try:
            self.vdb_client.delete_collection(collection_name)
        except Exception as e:
            details = {"collection_name": collection_name, "error": str(e)}
            logger.error(f"Failed to delete collection {collection_name}", extra=details)
            raise CollectionDeletionError(collection_name, details=details)