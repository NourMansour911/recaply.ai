
from fastapi import UploadFile
from helpers.logger import get_logger
from core.settings import Settings
from .files_exceptions import  InvalidFileExtensionException, UnsupportedFileTypeException

logger = get_logger(__name__)


class FileDetectorService:
    

    def __init__(self, settings: Settings):

        self.settings = settings
                
        self.supported_types = {
            "audio": ["audio/mpeg", "audio/wav", "audio/x-wav", "audio/mp3"],
            "srt": ["application/x-subrip"],
            "vtt": ["text/vtt", "text/vtt; charset=utf-8"], 
            "txt": ["text/plain"],
            "pdf": ["application/pdf"],
        }
        
        self.extensions_mapping = {
        ".mp3": "audio",
        ".wav": "audio",
        ".srt": "srt",
        ".vtt": "vtt",
        ".webvtt": "vtt",  
        ".txt": "txt",
        ".pdf": "pdf",}
        
    def detect(self, file: UploadFile) -> str:

        content_type = (file.content_type or "").lower()
        file_name = (file.filename or "").lower()

        logger.info(
            f"Detecting file type: filename={file.filename}, content_type={content_type}"
        )

        
        for file_type, mime_list in self.supported_types.items():
            if content_type in mime_list:
                logger.info(f"Detected file type via MIME: {file_type}")
                return file_type

        
        for ext, file_type in self.extensions_mapping.items():
            if file_name.endswith(ext):
                logger.info(f"Detected file type via extension: {file_type}")
                return file_type

        
        if "." in file_name:
            extension = file_name.split(".")[-1]
            logger.error(f"Invalid file extension: .{extension}")
            raise InvalidFileExtensionException( file_name=file.filename,extension=extension)

        logger.error(f"Unsupported file type with content_type={content_type}")
        raise UnsupportedFileTypeException( file_name=file.filename,content_type=content_type)
    