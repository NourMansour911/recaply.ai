from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from helpers import get_logger
from core import get_settings,Settings

logger = get_logger(__name__)

home_route = APIRouter(
    prefix="",
    tags=["system", "health","welcome"],
)

@home_route.get(
    "/",
    description="Home endpoint for service health and basic info"
)
async def home(settings:Settings = Depends(get_settings)):
    logger.info("Home endpoint called")

    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }