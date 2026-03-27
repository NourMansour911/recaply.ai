from core.app_exceptions import AppException


class RepoException(AppException):
    """Base exception for repository layer."""
    def __init__(self, message="Repository error", details=None):
        super().__init__(message=message, status_code=500, error_code="REPO_ERROR", details=details)


#  Project Exceptions 
class ProjectRepoException(RepoException):
    """Base exception for Project repository."""
    def __init__(self, message="Project repository error", details=None):
        super().__init__(message=message, details=details)


class ProjectCreationException(ProjectRepoException):
    def __init__(self, project_id=None):
        details = {"project_id": project_id}
        super().__init__(message="Failed to create project", details=details)


class ProjectFetchException(ProjectRepoException):
    def __init__(self, project_id=None):
        details = {"project_id": project_id}
        super().__init__(message="Failed to fetch project", details=details)


class ProjectInitializationException(ProjectRepoException):
    def __init__(self, collection_name=None):
        details = {"collection_name": collection_name}
        super().__init__(message="Failed to initialize project collection", details=details)


class ProjectDeletionException(ProjectRepoException):
    def __init__(self, project_id=None):
        details = {"project_id": project_id}
        super().__init__(message="Failed to delete project(s)", details=details)


#  File Exceptions 
class FileRepoException(RepoException):
    """Base exception for File repository."""
    def __init__(self, message="File repository error", details=None):
        super().__init__(message=message, details=details)


class DatabaseConnectionException(FileRepoException):
    def __init__(self):
        super().__init__(message="Database connection failed")


class InsertFileException(FileRepoException):
    def __init__(self, file_name=None):
        details = {"file_name": file_name}
        super().__init__(message="Failed to insert file", details=details)


class FetchFileException(FileRepoException):
    def __init__(self, file_name=None):
        details = {"file_name": file_name}
        super().__init__(message="Failed to fetch file", details=details)