from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SemanticChunk(BaseModel):
    chunk_order: int = Field(..., description="Order of the chunk in the document")
    text: str = Field(..., description="Merged text content of the chunk")
    start: Optional[float] = Field(None, description="Start time in seconds")
    end: Optional[float] = Field(None, description="End time in seconds")
    duration: Optional[float] = Field(None, description="Duration in seconds")
    page: int = Field(1, description="Page number")
    speakers: List[str] = Field([], description="List of unique speakers in the chunk")


class ChunkMetadata(BaseModel):
    file_id: str = Field(..., description="File identifier")
    file_name: str = Field(..., description="Original file name")
    file_type: str = Field(..., description="File type (audio, srt, vtt, txt, pdf)")
    file_order: int = Field(..., description="Order of the file in the project")
    language: str = Field(..., description="Language code")
    tenant_id: str = Field(..., description="Tenant identifier")
    project_iid: str = Field(..., description="Project identifier")
    chunk_order: int = Field(..., description="Order of the chunk in the document")
    created_at: str = Field(..., description="Creation timestamp")
    word_count: int = Field(..., description="Word count in chunk")
    speakers: List[str] = Field([], description="List of unique speakers in the chunk")


class VDBChunkPayload(BaseModel):
    text: str = Field(..., description="Chunk text content")
    metadata: ChunkMetadata = Field(..., description="Chunk metadata")
