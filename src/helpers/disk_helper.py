
import os
import uuid
import re

from helpers.logger import get_logger  
from core.settings import get_settings

import os


logger = get_logger(__name__)  


base_dir = os.path.dirname(os.path.dirname(__file__))

files_dir = os.path.join(base_dir,get_settings.FILES_PATH)
database_dir = os.path.join(base_dir,get_settings.DATABASES_PATH)


def get_database_path(db_name: str):
        database_path = os.path.join(
            database_dir, db_name
        )

        if not os.path.exists(database_path):
            os.makedirs(database_path)

        return database_path

def get_project_path(tenant_id: str,project_id: str):
        project_dir = os.path.join(files_dir,tenant_id, project_id)
        
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
            logger.info(f"Created project directory: {project_dir}")
        else:
            logger.debug(f"Project directory exists: {project_dir}")
        
        return project_dir   
 


    
