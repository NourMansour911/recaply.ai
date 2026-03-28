from pydantic import BaseModel, Field
from typing import Optional,List
from bson.objectid import ObjectId
from datetime import datetime

class Segment(BaseModel):
    text: str = Field(..., description="Content of the segment")
    start: Optional[float] = Field(None,  description="Start time in seconds", )
    end: Optional[float] = Field(None,  description="End time in seconds", )
    speakers: Optional[List[str]] = Field(None, description="Speaker identifier if available")

class FileModel(BaseModel):
    iid: Optional[ObjectId] = Field(None, alias="_id")
    file_tenant_id: str
    file_project_iid: ObjectId
    file_project_id: str
    file_name: str = Field(..., min_length=1)
    file_unique_name: str
    file_type: str = Field(default="file", min_length=1)
    file_order: int
    file_size_mb: float = Field(ge=0, default=None)
    file_path: str = Field(..., min_length=1)
    file_content: List[Segment]
    file_pushed_at: datetime = Field(default=datetime.now())
    file_language: Optional[str] = Field(default="en", description="Language code (e.g., 'en', 'ar')")
    file_duration: Optional[float] = Field(None, description="Total duration in seconds", ge=0)
    file_config: Optional[dict] = None

    model_config = {  
        "arbitrary_types_allowed": True, 
        "populate_by_name": True,
        "json_encoders": {ObjectId: str}   
    }
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("file_project_iid", 1),
                    ("file_name", 1)
                ],
                "name": "file_name_index_1",
                "unique": False
            },
        ]