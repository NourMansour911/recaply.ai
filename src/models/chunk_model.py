from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    file_id: str = Field(..., description="File identifier")
    chunk_order: int = Field(..., description="Order of the chunk in the document")
    created_at: str = Field(..., description="Creation timestamp")
    word_count: int = Field(..., description="Word count in chunk")
    start: Optional[int] = Field(None, description="Start time in seconds")
    end: Optional[int] = Field(None, description="End time in seconds")
    speakers: Optional[List[str]] = Field([], description="List of unique speakers in the chunk")


class VDBChunkPayload(BaseModel):
    text: str = Field(..., description="Chunk text content")
    metadata: ChunkMetadata = Field(..., description="Chunk metadata")
