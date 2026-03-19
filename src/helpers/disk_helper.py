import os
import uuid
import re

from helpers.logger import get_logger  
from core.settings import get_settings

logger = get_logger(__name__)  

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def get_database_path(db_name: str):
    DATABASE_DIR = os.path.join(BASE_DIR, get_settings.DATABASES_PATH)
    database_path = os.path.join(DATABASE_DIR, db_name)
    os.makedirs(database_path, exist_ok=True)
    return database_path


def get_project_path(tenant_id: str, project_id: str, stage: str = "raw") -> str:
    if stage not in ["raw", "normalized", "temp"]:
        raise ValueError(f"Unknown stage: {stage}")

    project_path = os.path.join(BASE_DIR, get_settings.FILES_PATH, tenant_id, project_id, stage)
    os.makedirs(project_path, exist_ok=True)
    logger.debug(f"Project {stage} path: {project_path}")
    return project_path