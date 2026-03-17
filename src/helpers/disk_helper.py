
import os
import uuid
import re

from helpers.logger import get_logger  
from core.settings import settings

import os


logger = get_logger(__name__)  


base_dir = os.path.dirname(os.path.dirname(__file__))

files_dir = os.path.join(base_dir,settings.FILES_PATH)
database_dir = os.path.join(base_dir,settings.DATABASES_PATH)


def get_database_path(db_name: str):
        database_path = os.path.join(
            database_dir, db_name
        )

        if not os.path.exists(database_path):
            os.makedirs(database_path)

        return database_path

def get_project_path(project_id: str):
        project_dir = os.path.join(files_dir, project_id)
        
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
            logger.info(f"Created project directory: {project_dir}")
        else:
            logger.debug(f"Project directory exists: {project_dir}")
        
        return project_dir   
 

def get_clean_filename(original_filename: str) -> str:
    cln_name = re.sub(r'[^\w.]', '', original_filename).lower()
    logger.debug(f"Cleaned filename: {original_filename} -> {cln_name}")
    return cln_name

def generate_file_path(original_filename: str, project_id: str):
    try:
        project_path = get_project_path(project_id=project_id)
        file_name = get_clean_filename(original_filename=original_filename)
        random_name = str(uuid.uuid4()) + "_" + file_name
        file_path = os.path.join(project_path, random_name)
        logger.debug(f"Generated file path: {file_path}")
    except Exception as e:
        logger.error(f"Error generating file path for {original_filename}: {e}", exc_info=True)
        return e.__str__()
    return file_path, random_name


    
