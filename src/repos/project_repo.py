from models import ProjectModel
from helpers.enums import DBEnum
from helpers.logger import get_logger  
import logging
from core.exceptions.repo_exceptions import (
    ProjectCreationException,
    ProjectFetchException,
    ProjectInitializationException,
    ProjectDeletionException
)

logger = get_logger("project_repo", level=logging.DEBUG)  # Logger for this layer

class ProjectRepo():

    def __init__(self, db_client: object):
        self.db_client = db_client
        self.collection = self.db_client[DBEnum.COLLECTION_PROJECT_NAME.value]
        logger.info(f"ProjectRepo initialized with collection: {DBEnum.COLLECTION_PROJECT_NAME.value}")
    
    @classmethod
    async def create_instance(cls, db_client: object):
        logger.debug("Creating ProjectRepo instance")
        try:
            instance = cls(db_client)
            await instance.init_collection()
            logger.info("ProjectRepo instance created successfully")
            return instance
        except Exception as e:
            logger.error(f"Error creating ProjectRepo instance: {e}", exc_info=True)
            raise ProjectInitializationException(collection_name=DBEnum.COLLECTION_PROJECT_NAME.value) from e

    async def init_collection(self):
        try:
            all_collections = await self.db_client.list_collection_names()
            if DBEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
                self.collection = self.db_client[DBEnum.COLLECTION_PROJECT_NAME.value]
                indexes = ProjectModel.get_indexes()
                for index in indexes:
                    await self.collection.create_index(
                        index["key"],
                        name=index["name"],
                        unique=index["unique"]
                    )
                logger.info(f"Collection {DBEnum.COLLECTION_PROJECT_NAME.value} initialized with indexes")
            else:
                logger.debug(f"Collection {DBEnum.COLLECTION_PROJECT_NAME.value} already exists")
        except Exception as e:
            logger.error(f"Error initializing collection {DBEnum.COLLECTION_PROJECT_NAME.value}: {e}", exc_info=True)
            raise ProjectInitializationException(collection_name=DBEnum.COLLECTION_PROJECT_NAME.value) from e

    async def create_project(self, project: ProjectModel):
        try:
            logger.debug(f"Inserting project: {project.model_dump()}")
            result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
            project.iid = result.inserted_id
            logger.info(f"Project created successfully with ID: {project.iid}")
            return project
        except Exception as e:
            logger.error(f"Error creating project: {e}", exc_info=True)
            raise ProjectCreationException(project_id=getattr(project, "project_id", None)) from e

    async def get_project_or_create_one(self,tenant_id: str,project_id: str) -> ProjectModel:
        try:
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
        except Exception as e:
            logger.error(f"Error fetching or creating project with ID {project_id}: {e}", exc_info=True)
            raise ProjectFetchException(project_id=project_id) from e

    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        try:
            total_documents = await self.collection.count_documents({})
            total_pages = total_documents // page_size + (1 if total_documents % page_size > 0 else 0)
            logger.debug(f"Total documents: {total_documents}, Total pages: {total_pages}")

            cursor = self.collection.find().skip((page-1) * page_size).limit(page_size)
            projects = []
            async for document in cursor:
                projects.append(ProjectModel(**document))

            logger.info(f"Fetched {len(projects)} projects for page {page}")
            return projects, total_pages
        except Exception as e:
            logger.error(f"Error fetching all projects for page {page}: {e}", exc_info=True)
            raise ProjectFetchException() from e

    async def project_exists(self, project_id: str) -> bool:
        try:
            logger.debug(f"Checking existence of project: {project_id}")
            record = await self.collection.find_one({"project_id": project_id})
            exists = record is not None
            logger.info(f"Project {project_id} exists: {exists}")
            return exists
        except Exception as e:
            logger.error(f"Error checking existence of project {project_id}: {e}", exc_info=True)
            return False

    async def delete_project(self, project_id: str) -> bool:
        try:
            logger.debug(f"Attempting to delete project: {project_id}")
            result = await self.collection.delete_one({"project_id": project_id})
            deleted = result.deleted_count > 0
            if deleted:
                logger.info(f"Project {project_id} deleted successfully")
            else:
                logger.info(f"Project {project_id} not found, nothing deleted")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}", exc_info=True)
            raise ProjectDeletionException(project_id=project_id) from e