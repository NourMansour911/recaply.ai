
from fastapi import UploadFile
from helpers.logger import get_logger
from core import get_settings
from core.exceptions import  InvalidFileExtensionException, UnsupportedFileTypeException

logger = get_logger(__name__)


class FileDetector:
    

    def __init__(self, settings= get_settings):

        self.settings = settings
        
        self.supported_types = {
        "audio": ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp3"],
        "srt": ["application/x-subrip"],
        "vtt": ["text/vtt"],
        "txt": ["text/plain"],
        "pdf": ["application/pdf"],}
        
        self.extensions_mapping = {
            ".mp3": "audio",
            ".wav": "audio",
            ".srt": "srt",
            ".vtt": "vtt",
            ".txt": "txt",
            ".pdf": "pdf",}
        
    def detect(self, file: UploadFile) -> str:

        content_type = (file.content_type or "").lower()
        filename = (file.filename or "").lower()

        logger.info(
            f"Detecting file type: filename={filename}, content_type={content_type}"
        )

        
        for file_type, mime_list in self.supported_types.items():
            if content_type in mime_list:
                logger.info(f"Detected file type via MIME: {file_type}")
                return file_type

        
        for ext, file_type in self.extensions_mapping.items():
            if filename.endswith(ext):
                logger.info(f"Detected file type via extension: {file_type}")
                return file_type

        
        if "." in filename:
            extension = filename.split(".")[-1]
            logger.error(f"Invalid file extension: .{extension}")
            raise InvalidFileExtensionException(extension=extension)

        logger.error(f"Unsupported file type with content_type={content_type}")
        raise UnsupportedFileTypeException(content_type=content_type)
    