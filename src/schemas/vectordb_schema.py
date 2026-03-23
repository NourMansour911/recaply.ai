from pydantic import BaseModel,Field
from typing import List,Optional
from models.chunk_model import ChunkMetadata

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 5

class ChunkResponse(BaseModel):
    id: str = Field(..., description="Chunk ID")
    text: str = Field(..., description="Chunk text (full or truncated)")
    metadata: ChunkMetadata


class CollectionChunksResponse(BaseModel):
    collection_name: str
    total_chunks: int
    returned_chunks: int
    chunks: List[ChunkResponse]