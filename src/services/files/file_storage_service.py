import os
import aiofiles
from helpers.logger import get_logger
from helpers import get_project_path
import uuid
import re
from fastapi import UploadFile
from .files_exceptions import UploadFailedException

logger = get_logger(__name__)


class FileStorageService:

    def generate_file_path(self, original_filename: str,tenant_id: str,project_id: str,file_order: int):
        project_path = get_project_path(tenant_id=tenant_id,project_id=project_id)
        file_name = re.sub(r"[^\w.]", "_", original_filename).lower()
        unique_name = f"{uuid.uuid4()}_{file_name}"
        file_path = os.path.join(project_path,file_order ,unique_name)
        return file_path, original_filename, unique_name

    async def save_file(self, file: UploadFile, file_path: str):
        try:
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)
            logger.info("File saved successfully", extra={"file_path": file_path})
        except Exception as e:
            logger.error("Error saving file", exc_info=True, extra={"file_path": file_path})
            raise UploadFailedException(file_name=file.filename, message=f"Error saving file: {e}")
        finally:
            await file.seek(0)