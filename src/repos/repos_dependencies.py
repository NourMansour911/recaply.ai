from fastapi import Depends
from repos.file_repo import FileRepo
from repos.project_repo import ProjectRepo
from core.main_dependencies import get_db_client


async def get_project_repo(db_client: object = Depends(get_db_client)):
    return await ProjectRepo.create_instance(db_client=db_client)

async def get_file_repo(db_client: object = Depends(get_db_client)):
    return await FileRepo.create_instance(db_client=db_client)

