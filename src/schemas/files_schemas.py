from pydantic import BaseModel
from typing import List
from models import FileModel

class UploadFilesResponse(BaseModel):
    project_iid: str
    vectorDB_collection: str 
    total_files: int
    total_chunks: int
    files: List[FileModel]

    
