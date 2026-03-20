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
        
        

class ProjectRepoException(AppException):
    def __init__(
        self,
        message: str = "Project repository error",
        error_code: str = "PROJECT_REPO_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=500, error_code=error_code, details=details)


class ProjectCreationException(ProjectRepoException):
    def __init__(self, project_id: Optional[str] = None):
        details = {"project_id": project_id} if project_id else None
        super().__init__(
            message="Failed to create project",
            error_code="PROJECT_CREATE_ERROR",
            details=details,
        )


class ProjectFetchException(ProjectRepoException):
    def __init__(self, project_id: Optional[str] = None):
        details = {"project_id": project_id} if project_id else None
        super().__init__(
            message="Failed to fetch project",
            error_code="PROJECT_FETCH_ERROR",
            details=details,
        )


class ProjectInitializationException(ProjectRepoException):
    def __init__(self, collection_name: Optional[str] = None):
        details = {"collection_name": collection_name} if collection_name else None
        super().__init__(
            message="Failed to initialize project collection",
            error_code="PROJECT_INIT_ERROR",
            details=details,
        )


class ProjectDeletionException(ProjectRepoException):
    def __init__(self, project_id: Optional[str] = None):
        details = {"project_id": project_id} if project_id else None
        super().__init__(
            message="Failed to delete project",
            error_code="PROJECT_DELETE_ERROR",
            details=details,
        )