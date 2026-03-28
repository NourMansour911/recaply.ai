from core.app_exceptions import AppException
from ..service_exceptions import ServiceException


class FilesServiceException(ServiceException):
    """Base exception for the Files microservice."""
    def __init__(self, message="Files service error", details=None,status_code=500):
        super().__init__(message=message, details=details,status_code=status_code)


class FileTooLargeException(FilesServiceException):
    def __init__(self, file_name: str, size_mb: float, max_size_mb: float):
        details = {
            "file_name": file_name,
            "size_mb": size_mb,
            "max_size_mb": max_size_mb
        }
        super().__init__(message="File exceeds maximum allowed size", details=details,status_code=400)


class EmptyFileException(FilesServiceException):
    def __init__(self, file_name: str):
        details = {"file_name": file_name}
        super().__init__(message="Uploaded file is empty", details=details,status_code=400)


class UploadFailedException(FilesServiceException):
    def __init__(self, file_name: str, message: str):
        details = {"file_name": file_name}
        super().__init__(message=message, details=details)


class InvalidFileExtensionException(FilesServiceException):
    def __init__(self, file_name: str, extension: str):
        details = {"file_name": file_name, "extension": extension}
        super().__init__(message="Invalid file extension", details=details,status_code=400)


class UnsupportedFileTypeException(FilesServiceException):
    def __init__(self, file_name: str, content_type: str):
        details = {"file_name": file_name, "content_type": content_type}
        super().__init__(message="Unsupported file type", details=details,status_code=400)