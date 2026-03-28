from ..service_exceptions import ServiceException


class ProjectServiceException(ServiceException):
    def __init__(self, message="Project service error", details=None):
        super().__init__(message=message, details=details)


class ProjectNotFoundError(ProjectServiceException):
    def __init__(self, project_id: str, tenant_id: str,details=None):
        message = f"Project not found: {project_id}"
        context = {"project_id": project_id,
                  "tenant_id": tenant_id}
        if details:
            context.update(details)
        super().__init__(message=message, details=context)


class TenantNotFoundError(ProjectServiceException):
    def __init__(self, tenant_id: str, details=None):
        message = f"Tenant not found: {tenant_id}"
        context = {"tenant_id": tenant_id}
        if details:
            context.update(details)
        super().__init__(message=message, details=context)


class ProjectFolderDeletionError(ProjectServiceException):
    def __init__(self, project_id: str, tenant_id: str, details=None):
        message = f"Failed to delete project folder: {project_id}"
        context = {"project_id": project_id, "tenant_id": tenant_id}
        if details:
            context.update(details)
        super().__init__(message=message, details=context)


class TenantFolderDeletionError(ProjectServiceException):
    def __init__(self, tenant_id: str, details=None):
        message = f"Failed to delete tenant folder: {tenant_id}"
        context = {"tenant_id": tenant_id}
        if details:
            context.update(details)
        super().__init__(message=message, details=context)


class CollectionDeletionError(ProjectServiceException):
    def __init__(self, collection_name: str, details=None):
        message = f"Failed to delete collection: {collection_name}"
        context = {"collection_name": collection_name}
        if details:
            context.update(details)
        super().__init__(message=message, details=context)