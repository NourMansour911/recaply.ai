from fastapi import APIRouter, Depends, File, Path, UploadFile

from typing import List

from helpers import get_logger
from core import get_tenant_id
from orchestrators import UploadOrchestrator, get_upload_orchestrator
from schemas import UploadFilesResponse


logger = get_logger(__name__)

files_route = APIRouter(
    prefix="/api/projects/{project_id}/files",
    tags=["Files","Admin"],
)



@files_route.post("",response_model=UploadFilesResponse,description="Upload files to a specific project ")
async def upload_files(
    project_id: str = Path(..., description="Project identifier used to group uploaded files."),
    files: List[UploadFile] = File(..., description="One or more files to upload."),
    tenant_id: str = Depends(get_tenant_id),
    orchestrator: UploadOrchestrator = Depends(get_upload_orchestrator),
):
    return await orchestrator.execute_batch(files=files,tenant_id=tenant_id,project_id=project_id)
    

@files_route.get(
    "",
    summary="List project files",
    description="Returns all files uploaded for the given project.",
    response_description="Project files list.",
    responses={501: {"description": "Not implemented yet."}},
)
async def list_project_files(
    project_id: str = Path(..., description="Project identifier to fetch files for."),
    tenant_id: str = Depends(get_tenant_id),
):
    pass

@files_route.delete(
    "/{file_name}",
    summary="Delete project file",
    description="Deletes a file and its associated chunks from the project scope.",
    response_description="Deletion result.",
    responses={501: {"description": "Not implemented yet."}},
)
async def delete_file(
    project_id: str = Path(..., description="Project identifier that owns the file."),
    file_name: str = Path(..., description="Original or stored file name to delete."),
    tenant_id: str = Depends(get_tenant_id),
):
    pass



   