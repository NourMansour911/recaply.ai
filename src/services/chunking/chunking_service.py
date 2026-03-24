from helpers import get_logger
from schemas import NormalizedFileData, Segment
import uuid
from datetime import datetime
from typing import List
from integrations.llm import LLMInterface
from models.chunk_model import ChunkMetadata


logger = get_logger(__name__)


class ChunkingService:
    def __init__(
        self,
        embedding_client : LLMInterface,
    ):
        self.embedding_client = embedding_client
    
    
    
    
    async def process_file_chunks(self, file_data: NormalizedFileData, project_iid: str, tenant_id: str,idx: int):
        

        segments = file_data.normalized_file.segments
        
        texts, vectors, record_ids, metadatas = await self._embed_and_prepare_chunks(
            idx=idx,
            chunks= segments, 
            file= file_data, 
            project_iid= str(project_iid),
            tenant_id= tenant_id,
        )
        
        return texts, vectors, record_ids, metadatas



    async def _embed_and_prepare_chunks(
        self,
        idx: int,
        chunks: List[Segment],
        file: NormalizedFileData,
        project_iid: str,
        tenant_id: str
    ):

        idx += len(chunks)

    
        texts = []
        vectors = []
        record_ids = list(range(idx, idx + len(chunks)))
        metadatas: List[ChunkMetadata] = []

        for i, chunk in enumerate(chunks):
                if not chunk.text or not chunk.text.strip():
                    logger.warning(f"Skipping empty chunk {i}")
                    continue

                embedding =  await self.embedding_client.embed_text(chunk.text.strip())

                if not embedding:
                    logger.warning(f"Skipping chunk {i} due to empty embedding")
                    continue

                
                metadata=ChunkMetadata(
                    speakers=chunk.speakers,
                    word_count=len(chunk.text.split()),
                    file_id=file.file_id,
                    file_name=file.file_name,
                    file_type=file.file_type,
                    file_order=file.file_order,
                    language=file.normalized_file.language,
                    tenant_id=tenant_id,
                    project_iid=str(project_iid),  
                    chunk_order=i,
                    created_at=datetime.now().isoformat(),
                )
                

                
                metadatas.append(metadata)

                texts.append(chunk.text)
                vectors.append(embedding)
                record_ids.append(str(uuid.uuid4()))


        
      
        return texts, vectors, record_ids, metadatas
            
 