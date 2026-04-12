from fastapi import APIRouter, Depends, File, Path, UploadFile

from typing import List

from helpers import get_logger
from core import get_tenant_id
from orchestrators import (
    ChainsOrchestrator,
    ChatOrchestrator,
    UploadOrchestrator,
    get_chains_orchestrator,
    get_chat_orchestrator,
    get_upload_orchestrator,
)
from schemas import ChainsResponse, ChatRequest, UploadFilesResponse


logger = get_logger(__name__)

workspace_route = APIRouter(
    prefix="/api/v1/workspace/{project_id}",
    tags=["Workspace"],
)



@workspace_route.post(
    "/upload",
    response_model=UploadFilesResponse,
    summary="Upload workspace files",
    description="Uploads one or more files to the selected project and stores them for later processing.",
    response_description="Upload result with project and vector collection details.",
)
async def upload_files(
    project_id: str = Path(..., description="Project identifier to store uploaded files under."),
    files: List[UploadFile] = File(..., description="Files to upload to the project."),
    tenant_id: str = Depends(get_tenant_id),
    orchestrator: UploadOrchestrator = Depends(get_upload_orchestrator),
):
    return await orchestrator.execute_batch(files=files,tenant_id=tenant_id,project_id=project_id)

@workspace_route.get(
    "/chains/{session_id}/{user_id}",
    response_model=ChainsResponse,
    summary="Generate meeting report",
    description="Runs the recap chains pipeline for the selected project and returns the structured meeting report.",
    response_description="Structured recap output and enriched source segments.",
)
async def get_chains(
    session_id: str = Path(..., description="Session identifier used for LangSmith trace metadata."),
    user_id: str = Path(..., description="User identifier used for LangSmith trace metadata."),
    project_id: str = Path(..., description="Project identifier to analyze."),
    tenant_id: str = Depends(get_tenant_id),
    orchestrator: ChainsOrchestrator = Depends(get_chains_orchestrator),
):
    return await orchestrator.execute(
        tenant_id=tenant_id,
        project_id=project_id,
        user_id=user_id,
        session_id=session_id,
    )


@workspace_route.post(
    "/chat/{session_id}/{user_id}",
    summary="Chat with project files",
    description="Starts a retrieval-augmented chat session over the selected project's files.",
    response_description="Chat answer payload.",
)
async def chat(
    chat_request: ChatRequest,
    session_id: str = Path(..., description="Session identifier used for memory and trace metadata."),
    user_id: str = Path(..., description="User identifier used for memory and trace metadata."),
    project_id: str = Path(..., description="Project identifier to chat over."),
    tenant_id: str = Depends(get_tenant_id),
    orchestrator: ChatOrchestrator = Depends(get_chat_orchestrator),
):
    return await orchestrator.execute(user_id=user_id,chat_request=chat_request,tenant_id=tenant_id,project_id=project_id,session_id=session_id)
    



   