from .app_exceptions import AppException
from typing import Optional, Dict, Any


class RepoException(AppException):
    def __init__(
        self,
        message: str = "Repository error",
        error_code: str = "REPO_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=500, error_code=error_code, details=details)


class DatabaseConnectionException(RepoException):
    def __init__(self, file_name: Optional[str] = None):
        details = {"file_name": file_name} if file_name else None
        super().__init__(
            message="Database connection failed",
            error_code="DB_CONNECTION_ERROR",
            details=details,
        )


class InsertFileException(RepoException):
    def __init__(self, file_name: Optional[str] = None):
        details = {"file_name": file_name} if file_name else None
        super().__init__(
            message="Failed to insert file",
            error_code="FILE_INSERT_ERROR",
            details=details,
        )


class FetchFileException(RepoException):
    def __init__(self, file_name: Optional[str] = None):
        details = {"file_name": file_name} if file_name else None
        super().__init__(
            message="Failed to fetch file",
            error_code="FILE_FETCH_ERROR",
            details=details,
        )