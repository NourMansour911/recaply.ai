from fastapi import Header, Request, HTTPException, status
from core.whisper_provider import WhisperProvider

def get_tenant_id(x_tenant_id: str = Header(...)) -> str:
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Tenant-ID header is required"
        )
    return x_tenant_id

def get_project_id(x_project_id: str = Header(...)) -> str:
    if not x_project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Project-ID header is required"
        )
    return x_project_id

def get_db_client(request: Request):
    return request.app.state.db_client


def get_whisper_provider():
    return WhisperProvider()