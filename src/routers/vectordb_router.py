from fastapi import APIRouter, UploadFile, Request,File,Depends

from core.main_dependencies import get_tenant_id
from typing import List
from schemas import SearchRequest
from helpers.logger import get_logger
from services import get_vdb_service
from services.vdb_service import VDBService
from schemas.vectordb_schema import CollectionChunksResponse,ChunksQuerySchema

logger = get_logger(__name__)

vectordb_route = APIRouter(
    prefix="/api/projects/{project_id}/vdb",
    tags=["api_v1", "vdb"],
)




@vectordb_route.get("/info")
async def vdb_info(project_id: str,service: VDBService = Depends(get_vdb_service),tenant_id: str = Depends(get_tenant_id)):

    return service.get_collection_info(project_id=project_id,tenant_id=tenant_id) 

@vectordb_route.get("/chunks",response_model=CollectionChunksResponse)
async def vdb_info(project_id: str,query: ChunksQuerySchema=Depends(),service: VDBService = Depends(get_vdb_service),tenant_id: str = Depends(get_tenant_id)):
    return service.get_chunks(project_id=project_id,tenant_id=tenant_id,page=query.page,limit=query.limit,text_limit=query.text_limit) 




@vectordb_route.post("/search")
async def vdb_push(project_id: str,request_schema: SearchRequest ,service: VDBService = Depends(get_vdb_service)):

    return await service.vdb_search(project_id=project_id,request_schema=request_schema) 