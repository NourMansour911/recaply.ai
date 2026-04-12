from pydantic import BaseModel
from typing import List


class UploadedFileResponse(BaseModel):
    file_name: str
    file_unique_name: str
    file_order: int

class UploadFilesResponse(BaseModel):
    project_iid: str
    vectorDB_collection: str 
    total_files: int
    total_chunks: int
    files: List[UploadedFileResponse]

    
