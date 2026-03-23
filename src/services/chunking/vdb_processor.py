from typing import List, Dict, Any
import uuid
from integrations.llm import LLMInterface
from datetime import datetime
from helpers import get_logger
from .chunking_exceptions import VectorDBInsertionException
from models.chunk_model import SemanticChunk, VDBChunkPayload, ChunkMetadata
from schemas.normalized_schemas import NormalizedFileData
from integrations.vector_db import VectorDBInterface
from core.settings import Settings

logger = get_logger(__name__)


class VectorDBProcessor:
    def __init__(self, vdb_client: VectorDBInterface, settings:Settings,embedding_client: LLMInterface, batch_size: int = 32):
        self.vdb_client = vdb_client
        self.embedding_client = embedding_client
        self.batch_size = batch_size
        self.settings = settings

    async def prepare_and_store_chunks(
        self,
        semantic_chunks: List[SemanticChunk],
        file: NormalizedFileData,
        project_iid: str,
        collection_name: str,
        tenant_id: str
    ) -> bool:
        
        collection_name = collection_name
        try:
            
            texts = []
            vectors = []
            record_ids = []
            payloads:List[VDBChunkPayload] = []
            
            for i, chunk in enumerate(semantic_chunks):
                try:
                    
                    embedding = await self.generate_chunk_embedding(chunk)
                    if embedding is None:
                        continue
                    
                    
                    payload = VDBChunkPayload(
                                text=chunk.text,
                                metadata=ChunkMetadata(
                                    speakers= chunk.speakers,
                                    word_count=  len(chunk.text.split()),
                                    file_id= file.file_id,
                                    file_name= file.file_name,
                                    file_type=  file.file_type,
                                    language= file.normalized_file.language,
                                    tenant_id= tenant_id,
                                    project_iid=  project_iid,
                                    chunk_order= i,
                                    created_at=  datetime.now().isoformat(),
                                )
                            )
                    
                    
                    texts.append(chunk.text)
                    vectors.append(embedding)
                    record_ids.append(str(uuid.uuid4()))
                    
                    
                    if len(texts) >= self.batch_size:
                        await self._store_batch(
                            collection_name=collection_name,
                            texts=texts,
                            vectors=vectors,
                            record_ids=record_ids,
                            payloads= payloads
                        )
                        
                        
                        texts.clear()
                        vectors.clear()
                        record_ids.clear()
                        payloads.clear()
                        
                except Exception as e:
                    logger.error(f"Failed to process chunk {i}: {str(e)}")
                    continue
            
            
            if texts:
                await self._store_batch(
                    collection_name=collection_name,
                    texts=texts,
                    vectors=vectors,
                    record_ids=record_ids,
                    payloads=payloads
                )
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to prepare and store chunks: {str(e)}")
            raise VectorDBInsertionException(
                file_name=file.file_name,
                insertion_error=str(e),
                batch_size=self.batch_size
            )

    async def generate_chunk_embedding(self, chunk: SemanticChunk) -> List[float]:
       
        try:
            embedding = await self.embedding_client.embed_text(chunk.text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding for chunk: {str(e)}")
            return None


    async def _store_batch(
        self, 
        collection_name: str, 
        texts: List[str], 
        vectors: List[List[float]], 
        record_ids: List[str], 
        payloads: List[VDBChunkPayload]
    ) -> bool:
        
        try:
           
            await self._ensure_collection_exists(collection_name, len(vectors[0]) if vectors else 0)
            
            
            metadata_list = [payload.metadata for payload in payloads]
            
            success = self.vdb_client.insert_many(
                collection_name=collection_name,
                texts=texts,
                vectors=vectors,
                record_ids=record_ids,
                metadata=metadata_list,
                batch_size=self.batch_size
            )
            
            if success:
                logger.info(f"Stored batch of {len(texts)} chunks in vector database")
            else:
                logger.error("Failed to store batch in vector database")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to store batch in vector database: {str(e)}")
            return False

    async def _ensure_collection_exists(self, collection_name: str, embedding_size: int) -> bool:
        
        try:
            if not self.vdb_client.is_collection_existed(collection_name):
                
                if hasattr(self.embedding_client, 'embedding_size'):
                    size = self.embedding_client.embedding_size
                else:
                    size = embedding_size if embedding_size > 0 else self.settings.EMBEDDING_MODEL_SIZE
                    
                self.vdb_client.create_collection(
                    collection_name=collection_name,
                    embedding_size=size
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            return False
