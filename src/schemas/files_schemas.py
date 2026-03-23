from pydantic import BaseModel
from typing import List


class UploadFilesSchema(BaseModel):
    project_iid: str
    vectorDB_collections: List[str] 
    total_files: int
    total_chunks: int

    
