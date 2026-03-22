from models import FileModel
from helpers.enums import DBEnum
from helpers.logger import get_logger
from .repo_exceptions import DatabaseConnectionException, InsertFileException, FetchFileException
from bson import ObjectId
import logging

logger = get_logger("file_repo", level=logging.DEBUG)


class FileRepo:


    def __init__(self, db_client: object):
        self.db_client = db_client
        self.collection = self.db_client[DBEnum.COLLECTION_FILE_NAME.value]
        logger.info(f"FileRepo initialized with collection: {DBEnum.COLLECTION_FILE_NAME.value}")

    @classmethod
    async def create_instance(cls, db_client: object):
        try:
            instance = cls(db_client)
            await instance.init_collection()
            logger.info("FileRepo instance created successfully")
            return instance
        except Exception as e:
            logger.error(f"Error creating FileRepo instance: {e}", exc_info=True)
            raise DatabaseConnectionException() from e

    async def init_collection(self):
        try:
            all_collections = await self.db_client.list_collection_names()
            if DBEnum.COLLECTION_FILE_NAME.value not in all_collections:
                indexes = FileModel.get_indexes()
                for index in indexes:
                    await self.collection.create_index(
                        index["key"],
                        name=index["name"],
                        unique=index["unique"]
                    )
                logger.info(f"Collection {DBEnum.COLLECTION_FILE_NAME.value} initialized with indexes")
            else:
                logger.debug(f"Collection {DBEnum.COLLECTION_FILE_NAME.value} already exists")
        except Exception as e:
            logger.error(f"Error initializing collection {DBEnum.COLLECTION_FILE_NAME.value}: {e}", exc_info=True)
            raise DatabaseConnectionException() from e

    async def add_file(self, file: FileModel):
        try:
            result = await self.collection.insert_one(file.model_dump(by_alias=True, exclude_none=True))
            file.iid = result.inserted_id
            logger.info(f"File added successfully with ID: {file.iid}", extra={"file_name": file.file_name})
            return file.iid
        except Exception as e:
            logger.error(f"Error adding file: {e}", exc_info=True, extra={"file_name": file.file_name})
            raise InsertFileException(file_name=file.file_name) from e

    async def get_file(self, project_iid: str, file_name: str) -> FileModel | None:
        try:
            record = await self.collection.find_one({
                "file_project_iid": ObjectId(project_iid) if isinstance(project_iid, str) else project_iid,
                "file_name": file_name,
            })

            if record:
                return FileModel(**record)
            return None

        except Exception as e:
            logger.error(f"Error fetching file {file_name} for project {project_iid}: {e}", exc_info=True)
            raise FetchFileException(file_name=file_name) from e

    async def get_all_project_files(self, project_iid: str,tenant_id: str) -> list[FileModel]:
        try:
            query = {
                "file_project_iid": ObjectId(project_iid) if isinstance(project_iid, str) else project_iid,
                "file_tenant_id": tenant_id
            }
            result = await self.collection.find(query).to_list(length=None)
            logger.info(f"Fetched {len(result)} files for project ID: {project_iid}")
            return [FileModel(**record) for record in result]

        except Exception as e:
            logger.error(f"Error fetching project files for ID {project_iid}: {e}", exc_info=True)
            raise FetchFileException() from e