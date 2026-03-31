from models import ProjectModel
from helpers.enums import DBEnum
from helpers.logger import get_logger
import logging

logger = get_logger("project_repo", level=logging.DEBUG)


class ProjectRepo:

    def __init__(self, db_client: object):
        self.db_client = db_client
        self.collection = self.db_client[DBEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        if DBEnum.COLLECTION_PROJECT_NAME.value not in await self.db_client.list_collection_names():
            indexes = ProjectModel.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def create_project(self, project: ProjectModel):
        result = await self.collection.insert_one(
            project.model_dump(by_alias=True, exclude_unset=True)
        )
        project.iid = result.inserted_id
        return project

    async def get_project(self, project_id: str, tenant_id: str):
        record = await self.collection.find_one({
            "project_id": project_id,
            "tenant_id": tenant_id
        })
        return ProjectModel(**record) if record else None

    async def get_projects_by_tenant(self, tenant_id: str):
        cursor = self.collection.find({"tenant_id": tenant_id})
        return [ProjectModel(**doc) async for doc in cursor]

    async def project_exists(self, project_id: str, tenant_id: str) -> bool:
        return await self.collection.count_documents({
            "project_id": project_id,
            "tenant_id": tenant_id
        }, limit=1) > 0

    async def delete_project_by_iid(self, project_iid):
        result = await self.collection.delete_one({"_id": project_iid})
        return result.deleted_count > 0

    async def delete_projects_by_tenant(self, tenant_id: str):
        result = await self.collection.delete_many({
            "tenant_id": tenant_id
        })
        return result.deleted_count

    async def get_project_or_create_one(self, tenant_id: str, project_id: str) -> ProjectModel:
        logger.debug(f"Fetching project with ID: {project_id}")

        record = await self.collection.find_one({
            "project_id": project_id,
            "tenant_id": tenant_id
        })

        if record is None:
            logger.info(f"No project found with ID {project_id}, creating new one")
            project = ProjectModel(project_id=project_id, tenant_id=tenant_id)
            project = await self.create_project(project=project)
            return project

        logger.info(f"Project found with ID: {project_id}")
        return ProjectModel(**record)