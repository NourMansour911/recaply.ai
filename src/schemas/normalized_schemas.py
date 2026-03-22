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
    segment_id: str = Field(..., description="Unique identifier for the segment")
    text: str = Field(..., description="Content of the segment")
    start: Optional[float] = Field(None,  description="Start time in seconds", )
    end: Optional[float] = Field(None,  description="End time in seconds", )
    speaker: Optional[str] = Field(None, description="Speaker identifier if available")
    page: int = Field(1, description="Page number (for documents)", ge=1)
    
    
class NormalizedFileModel(BaseModel):
    language: str = Field(..., description="Language code (e.g., 'en', 'ar')")
    segments: List[Segment] = Field(..., description="List of content segments")
    duration: float = Field(..., description="Total duration in seconds", ge=0)
    
    
    
class FileResponseSchema(BaseModel):
    
    file_id: str
    file_name: str
    file_type: str
    file_size: float
    file_path: str
    normalized_file: NormalizedFileModel

class NormalizedFilesSchema(BaseModel):
    tenant_id: str
    project_iid: str
    uploaded_files_count: int
    files: List[FileResponseSchema]
