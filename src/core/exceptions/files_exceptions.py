from core.exceptions import AppException


class UnsupportedFileTypeException(AppException):
    def __init__(self, content_type: str):
        super().__init__(
            message="Unsupported file type",
            status_code=400,
            details={"content_type": content_type},
        )


class FileTooLargeException(AppException):
    def __init__(self, max_size: int):
        super().__init__(
            message="File too large",
            status_code=400,
            details={"max_size_in_mb": max_size},
        )


class InvalidFileExtensionException(AppException):
    def __init__(self, extension: str):
        super().__init__(
            message="Invalid file extension",
            status_code=400,
            details={"extension": extension},
        )
        
class UploadFailedException(AppException):
    def __init__(self, message: str = "File upload failed", status_code: int = 400,details=None):
        self.message = message
        self.status_code = status_code
        self.details = details