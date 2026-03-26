from models import ProjectModel
from helpers.enums import DBEnum
from helpers.logger import get_logger  
import logging
from .repo_exceptions import (
    ProjectCreationException,
    ProjectFetchException,
    ProjectInitializationException,
    ProjectDeletionException
)

logger = get_logger("project_repo", level=logging.DEBUG)  


class ProjectRepo:

    def __init__(self, db_client: object):
        self.db_client = db_client
        self.collection = self.db_client[DBEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        try:
            instance = cls(db_client)
            await instance.init_collection()
            return instance
        except Exception as e:
            raise ProjectInitializationException(
                collection_name=DBEnum.COLLECTION_PROJECT_NAME.value
            ) from e

    async def init_collection(self):
        try:
            if DBEnum.COLLECTION_PROJECT_NAME.value not in await self.db_client.list_collection_names():
                indexes = ProjectModel.get_indexes()
                for index in indexes:
                    await self.collection.create_index(
                        index["key"],
                        name=index["name"],
                        unique=index["unique"]
                    )
        except Exception as e:
            raise ProjectInitializationException(
                collection_name=DBEnum.COLLECTION_PROJECT_NAME.value
            ) from e


    async def create_project(self, project: ProjectModel):
        try:
            result = await self.collection.insert_one(
                project.model_dump(by_alias=True, exclude_unset=True)
            )
            project.iid = result.inserted_id
            return project
        except Exception as e:
            raise ProjectCreationException(
                project_id=getattr(project, "project_id", None)
            ) from e


    async def get_project(self, project_id: str, tenant_id: str):
        try:
            record = await self.collection.find_one({
                "project_id": project_id,
                "tenant_id": tenant_id
            })
            return ProjectModel(**record) if record else None
        except Exception as e:
            raise ProjectFetchException(project_id=project_id) from e

    async def get_projects_by_tenant(self, tenant_id: str):
        try:
            cursor = self.collection.find({"tenant_id": tenant_id})
            return [ProjectModel(**doc) async for doc in cursor]
        except Exception as e:
            raise ProjectFetchException() from e

    async def project_exists(self, project_id: str, tenant_id: str) -> bool:
        try:
            return await self.collection.count_documents({
                "project_id": project_id,
                "tenant_id": tenant_id
            }, limit=1) > 0
        except Exception:
            return False


    async def delete_project_by_iid(self, project_iid):
        try:
            result = await self.collection.delete_one({"_id": project_iid})
            return result.deleted_count > 0
        except Exception as e:
            raise ProjectDeletionException(project_id=str(project_iid)) from e

    async def delete_projects_by_tenant(self, tenant_id: str):
        try:
            result = await self.collection.delete_many({
                "tenant_id": tenant_id
            })
            return result.deleted_count
        except Exception as e:
            raise ProjectDeletionException(project_id=tenant_id) from e