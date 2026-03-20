from pydantic import BaseModel
from typing import List

class FileResponseSchema(BaseModel):
    project_iid: str
    file_id: str
    file_name: str
    file_type: str
    file_size: float
    file_path: str

class UploadResponseSchema(BaseModel):
    tenant_id: str
    project_id: str
    uploaded_files_count: int
    files: List[FileResponseSchema]
    
