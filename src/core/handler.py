from fastapi.responses import JSONResponse
from fastapi import Request
from core.exceptions import AppException
from helpers import get_logger

logger = get_logger(__name__)


async def app_exception_handler(request: Request, exc: AppException):
    logger.error(exc.message, exc_info=True,extra={"path":request.url.path,
        "status_code":exc.status_code,"method":request.method,"body":request.json()})
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.message,
                 "path":request.url.path})