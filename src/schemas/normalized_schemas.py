from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class FileType(str, Enum):
    AUDIO = "audio"
    SRT = "srt"
    VTT = "vtt"
    TXT = "txt"
    PDF = "pdf"

class Segment(BaseModel):
    text: str = Field(..., description="Content of the segment")
    start: Optional[float] = Field(None,  description="Start time in seconds", )
    end: Optional[float] = Field(None,  description="End time in seconds", )
    speakers: Optional[List[str]] = Field(None, description="Speaker identifier if available")
    
    
    
class NormalizedContent(BaseModel):
    language: str = Field(..., description="Language code (e.g., 'en', 'ar')")
    segments: List[Segment] = Field(..., description="List of content segments")
    duration: float = Field(..., description="Total duration in seconds", ge=0)
    
    
    
class NormalizedFileData(BaseModel):
    
    file_id: str
    file_name: str
    file_type: str
    file_order: int
    file_size: float
    file_path: str
    normalized_file: NormalizedContent
