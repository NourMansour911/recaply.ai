from pydantic import BaseModel
from typing import List, Optional
from .chains_output_schemas import GenerateOutput
class EnrichedSegment(BaseModel):
    id: str
    file_unique_name: str
    start: Optional[float]
    end: Optional[float]
    text: str
    file_type: str
    file_order: int
    
class ChainsResponse(BaseModel):
    output: GenerateOutput
    segments: List[EnrichedSegment]