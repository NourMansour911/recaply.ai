from models import FileModel
from helpers.enums import DBEnum
from helpers.logger import get_logger
from bson import ObjectId
import logging

logger = get_logger("file_repo")


class FileRepo:

    def __init__(self, db_client: object):
        self.db_client = db_client
        self.collection = self.db_client[DBEnum.COLLECTION_FILE_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        if DBEnum.COLLECTION_FILE_NAME.value not in await self.db_client.list_collection_names():
            indexes = FileModel.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def add_file(self, file: FileModel):
        result = await self.collection.insert_one(
            file.model_dump(by_alias=True, exclude_none=True)
        )
        file.iid = result.inserted_id
        return file.iid

    async def get_file(self, project_iid: str, file_name: str) -> FileModel | None:
        record = await self.collection.find_one({
            "file_project_iid": ObjectId(project_iid) if isinstance(project_iid, str) else project_iid,
            "file_name": file_name,
        })
        return FileModel(**record) if record else None

    async def get_all_project_files(self, project_iid: str) -> list[FileModel]:
        query = {
            "file_project_iid": ObjectId(project_iid) if isinstance(project_iid, str) else project_iid
        }
        result = await self.collection.find(query).to_list(length=None)
        return [FileModel(**record) for record in result]

    async def delete_files_by_project(self, project_iid):
        result = await self.collection.delete_many({
            "file_project_iid": project_iid
        })
        return result.deleted_count

    async def delete_files_by_projects(self, project_iids: list):
        result = await self.collection.delete_many({
            "file_project_iid": {"$in": project_iids}
        })
        return result.deleted_count