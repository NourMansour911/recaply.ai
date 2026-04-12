from fastapi import APIRouter, Depends, Path, Query, Request, UploadFile

from core.main_dependencies import get_tenant_id
from typing import List
from schemas import SearchRequest
from helpers import get_logger
from services import get_vdb_service
from services.vdb_service import VDBService
from schemas.vectordb_schema import CollectionChunksResponse, ChunksQuerySchema

logger = get_logger(__name__)

vectordb_route = APIRouter(
    prefix="/api/projects/{project_id}/vdb",
    tags=["Admin", "VectorDB"],
)




@vectordb_route.get(
    "/info",
    summary="Get collection info",
    description="Returns the underlying vector collection information for the project.",
    response_description="Collection metadata and info payload.",
)
async def vdb_get_chunks(
    project_id: str = Path(..., description="Project identifier used to resolve the vector collection."),
    service: VDBService = Depends(get_vdb_service),
    tenant_id: str = Depends(get_tenant_id),
):

    return service.get_collection_info(project_id=project_id,tenant_id=tenant_id) 

@vectordb_route.get(
    "/chunks",
    response_model=CollectionChunksResponse,
    summary="List collection chunks",
    description="Returns paginated chunks from the project vector collection.",
    response_description="Paginated chunk list.",
)
async def vdb_get_chunks(
    project_id: str = Path(..., description="Project identifier used to resolve the vector collection."),
    query: ChunksQuerySchema = Depends(),
    service: VDBService = Depends(get_vdb_service),
    tenant_id: str = Depends(get_tenant_id),
):
    return service.get_chunks(project_id=project_id,tenant_id=tenant_id,page=query.page,limit=query.limit,text_limit=query.text_limit) 


