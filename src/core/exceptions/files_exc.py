from typing import Optional, Dict, Any
from .app_exc import AppException


class UnsupportedFileTypeException(AppException):
    """
    Raised when file MIME type is not supported.
    """

    def __init__(self, content_type: Optional[str] = None):
        super().__init__(
            message="Unsupported file type",
            status_code=400,
            error_code="UNSUPPORTED_FILE_TYPE",
            details={"content_type": content_type} if content_type else None,
        )


class InvalidFileExtensionException(AppException):
    """
    Raised when file extension is not recognized or invalid.
    """

    def __init__(self, extension: Optional[str] = None):
        super().__init__(
            message="Invalid file extension",
            status_code=400,
            error_code="INVALID_FILE_EXTENSION",
            details={"extension": extension} if extension else None,
        )


class FileTooLargeException(AppException):
    """
    Raised when uploaded file exceeds allowed size.
    """

    def __init__(self, max_size_mb: int):
        super().__init__(
            message="File too large",
            status_code=400,
            error_code="FILE_TOO_LARGE",
            details={"max_size_mb": max_size_mb},
        )


class EmptyFileException(AppException):
    """
    Raised when uploaded file is empty.
    """

    def __init__(self):
        super().__init__(
            message="File is empty",
            status_code=400,
            error_code="EMPTY_FILE",
            details=None,
        )


class UploadFailedException(AppException):
    """
    Raised when file upload fails due to system/internal error.
    """

    def __init__(
        self,
        message: str = "File upload failed",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code="UPLOAD_FAILED",
            details=details,
        )