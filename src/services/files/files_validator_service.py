from fastapi import UploadFile
from helpers.logger import get_logger
from core import get_settings
from core.exceptions import (
    FileTooLargeException,
    EmptyFileException,
)

logger = get_logger(__name__)


class FileValidator:


    def __init__(self):
        self.settings = get_settings
        self.MB = 1024 * 1024 * 8

    def get_max_size(self, file_type: str) -> int:


        

        if file_type == "audio":
            return self.settings.MAX_AUDIO_SIZE_MB * self.MB

        if file_type == "txt":
            return self.settings.MAX_TEXT_SIZE_MB * self.MB

        if file_type in ["srt", "vtt"]:
            return self.settings.MAX_SUBTITLE_SIZE_MB * self.MB

        if file_type == "pdf":
            return self.settings.MAX_PDF_SIZE_MB * self.MB

        return 50 * self.MB  

    async def validate(self, file: UploadFile, file_type: str) -> None:


        if not file.filename:
            logger.error("File has no name")
            raise EmptyFileException()

        # Check not empty
        chunk = await file.read(1024)
        if not chunk:
            logger.error("Empty file uploaded")
            raise EmptyFileException()

        await file.seek(0)

        # Size validation
        max_size = self.get_max_size(file_type)
        size = 0

        while True:
            chunk = await file.read(self.MB)
            if not chunk:
                break

            size += len(chunk)

            if size > max_size:
                logger.error(f"{file_type} exceeds max size")
                raise FileTooLargeException(
                    max_size_mb=max_size // (self.MB)
                )

        await file.seek(0)
        
        logger.info("File validation passed")
        
        return file.filename ,file_type , size