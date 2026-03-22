from pydantic import BaseModel
from typing import List


class UploadFilesSchema(BaseModel):
    project_iid: str
    vectorDB_collections: List[str] 
    no_of_files: int
    total_chunks: int

    
