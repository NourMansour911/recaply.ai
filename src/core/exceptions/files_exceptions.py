from typing import Optional, Dict, Any
from core.exceptions.app_exceptions import AppException


class BaseFileException(AppException):
    """
    Base exception for all file-related errors.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        file_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400,
    ):
        base_details = details or {}

        if file_name:
            base_details["file_name"] = file_name

        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=base_details if base_details else None,
        )


class UnsupportedFileTypeException(BaseFileException):
    def __init__(self, file_name: Optional[str] = None, content_type: Optional[str] = None):
        super().__init__(
            message="Unsupported file type",
            error_code="UNSUPPORTED_FILE_TYPE",
            file_name=file_name,
            details={"content_type": content_type} if content_type else None,
        )


class InvalidFileExtensionException(BaseFileException):
    def __init__(self, file_name: Optional[str] = None, extension: Optional[str] = None):
        super().__init__(
            message="Invalid file extension",
            error_code="INVALID_FILE_EXTENSION",
            file_name=file_name,
            details={"extension": extension} if extension else None,
        )


class FileTooLargeException(BaseFileException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        size_mb: Optional[int] = None,
        max_size_mb: Optional[int] = None,
    ):
        super().__init__(
            message="File too large",
            error_code="FILE_TOO_LARGE",
            file_name=file_name,
            details={
                "size_mb": size_mb,
                "max_size_mb": max_size_mb,
            },
        )


class EmptyFileException(BaseFileException):
    def __init__(self, file_name: Optional[str] = None):
        super().__init__(
            message="File is empty",
            error_code="EMPTY_FILE",
            file_name=file_name,
        )


class UploadFailedException(BaseFileException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        message: str = "File upload failed",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        super().__init__(
            message=message,
            error_code="UPLOAD_FAILED",
            file_name=file_name,
            details=details,
            status_code=status_code,
        )