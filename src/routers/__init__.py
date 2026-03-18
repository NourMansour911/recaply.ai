from .files_router import files_route
from .projects_router import projects_route


__all__ = ["files_route", "projects_route"]

routers = [files_route, projects_route]