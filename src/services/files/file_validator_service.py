from fastapi import UploadFile
from helpers.logger import get_logger
from core.settings import Settings
from .files_exceptions import (
    FileTooLargeException,
    EmptyFileException,
)

logger = get_logger(__name__)


class FileValidatorService:


    def __init__(self,settings:Settings):
        self.settings = settings
        

    def get_max_size_mb(self, file_type: str) -> int:

        if file_type == "audio":
            return self.settings.MAX_AUDIO_SIZE_MB  


        if file_type == "txt":
            return self.settings.MAX_TEXT_SIZE_MB 

        if file_type in ["srt", "vtt"]:
            return self.settings.MAX_SUBTITLE_SIZE_MB 

        if file_type == "pdf":
            return self.settings.MAX_PDF_SIZE_MB 
        

        return 50   

    async def validate(self, file: UploadFile, file_type: str) -> None:


        if not file.filename:
            logger.error("File has no name")
            raise EmptyFileException(file_name=file.filename, )

        
        chunk = await file.read(1024)
        if not chunk:
            logger.error("Empty file uploaded")
            raise EmptyFileException(file_name=file.filename, )

        await file.seek(0)

        # Size validation
        max_size = self.get_max_size_mb(file_type) 
        
        logger.info(max_size * self.settings.TO_BYTES)
        logger.info(file.size)
        
        if file.size > (max_size * self.settings.TO_BYTES):
            logger.error(f"{file_type} exceeds max size")
            raise FileTooLargeException(file_name=file.filename, 
                size_mb=(file.size / self.settings.TO_BYTES).__round__(2),
                max_size_mb=max_size 
            )

        await file.seek(0)
        
        logger.info("File validation passed")
        
        return 