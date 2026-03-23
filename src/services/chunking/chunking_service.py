from typing import List, Dict, Any
from helpers import get_logger
from .chunking_exceptions import ChunkingAlgorithmException
from schemas.normalized_schemas import NormalizedContent
from .semantic_chunking import SemanticChunkingCore
from .embedding_processor import EmbeddingProcessor
from .vdb_processor import VectorDBProcessor
from schemas import NormalizedFileData
from core.settings import Settings
logger = get_logger(__name__)


class ChunkingService:
    def __init__(
        self,
        embedding_client,
        vdb_client,
        settings: Settings,
        similarity_threshold: float = 0.7,
        max_tokens_per_chunk: int = 300,
        min_tokens_per_chunk: int = 20,
        batch_size: int = 32,
    ):
        self.settings = settings
        self.embedding_processor = EmbeddingProcessor(embedding_client,settings=self.settings)
        self.chunking_core = SemanticChunkingCore(
            similarity_threshold=similarity_threshold,
            max_tokens_per_chunk=max_tokens_per_chunk,
            min_tokens_per_chunk=min_tokens_per_chunk
        )
        self.vdb_processor = VectorDBProcessor(batch_size=batch_size, vdb_client=vdb_client, settings=self.settings,embedding_client=embedding_client)

    async def process_and_store_semantic_chunks(self, file_data: NormalizedFileData, project_iid: str, tenant_id: str,project_id: str) -> bool:
        
        try:
            
                    
                
            vdb_collection_name , no_of_chunks = await self._process_file_chunks( normalized_file=file_data.normalized_file, file_data=file_data, project_iid=project_iid, tenant_id=tenant_id,project_id=project_id)
            
            return vdb_collection_name , no_of_chunks
            
        except Exception as e:
            logger.error(f"Failed to process semantic chunks: {str(e)}")
            raise ChunkingAlgorithmException(
                file_name="multiple_files",
                algorithm_error=f"Semantic chunking processing failed: {str(e)}"
            )

    async def _process_file_chunks(self, normalized_file: NormalizedContent, file_data: NormalizedFileData, project_iid: str, tenant_id: str,project_id: str) :
        
        try:
            valid_segments = self.embedding_processor.filter_valid_segments(
                normalized_file.segments, 
            )
            
            if not valid_segments:
                logger.warning(f"No valid segments found for file {file_data.file_name}")
                return
            
            
            segment_embeddings = await self.embedding_processor.generate_segment_embeddings(
                valid_segments, 
                file_data.file_name
            )
            
            
            semantic_chunks = self.chunking_core.perform_semantic_chunking(
                valid_segments, 
                segment_embeddings, 
                file_data.file_name
            )
            
            vdb_collection_name = f"vdb_{tenant_id}_{project_id}"
            
            await self.vdb_processor.prepare_and_store_chunks(
                semantic_chunks= semantic_chunks, 
                file= file_data, 
                project_iid= str(project_iid),
                tenant_id= tenant_id,
                collection_name=vdb_collection_name
            )
            
            return vdb_collection_name, len(semantic_chunks)
                
        except Exception as e:
            logger.error(f"Failed to process file chunks for {file_data.file_name}: {str(e)}")
            raise ChunkingAlgorithmException(
                file_name=file_data.file_name,
                algorithm_error=f"File chunk processing failed: {str(e)}"
            )
