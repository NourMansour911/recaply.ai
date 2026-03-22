from typing import List, Dict, Any
from helpers import get_logger
from .chunking_exceptions import ChunkingAlgorithmException
from src.schemas.normalized_schemas import NormalizedFileModel
from .semantic_chunking import SemanticChunkingCore
from .embedding_processor import EmbeddingProcessor
from .vdb_processor import VectorDBProcessor

logger = get_logger(__name__)


class ChunkingService:
    def __init__(
        self,
        embedding_client,
        qdrant_client,
        similarity_threshold: float = 0.7,
        max_tokens_per_chunk: int = 300,
        min_tokens_per_chunk: int = 20,
        batch_size: int = 32
    ):
        self.embedding_processor = EmbeddingProcessor(embedding_client)
        self.chunking_core = SemanticChunkingCore(
            similarity_threshold=similarity_threshold,
            max_tokens_per_chunk=max_tokens_per_chunk,
            min_tokens_per_chunk=min_tokens_per_chunk
        )
        self.qdrant_processor = QdrantProcessor(qdrant_client, batch_size)

    async def process_and_store_semantic_chunks(self, response_data: Dict[str, Any]) -> bool:
        """
        Process semantic chunks from response data and store in Qdrant.
        """
        try:
            files = response_data.get("files", [])
            
            for file_data in files:
                normalized_file_data = file_data.get("normalized_file", {})
                if not normalized_file_data:
                    continue
                    
                # Create NormalizedFileModel instance
                normalized_file = NormalizedFileModel(**normalized_file_data)
                
                # Process semantic chunks
                await self._process_file_chunks(normalized_file, file_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to process semantic chunks: {str(e)}")
            raise ChunkingAlgorithmException(
                file_name="multiple_files",
                algorithm_error=f"Semantic chunking processing failed: {str(e)}"
            )

    async def _process_file_chunks(self, normalized_file: NormalizedFileModel, file_data: Dict[str, Any]):
        """
        Process chunks for a single file and store in batches.
        """
        try:
            # Filter valid segments
            valid_segments = self.embedding_processor.filter_valid_segments(
                normalized_file.segments, 
                normalized_file.file_name
            )
            
            if not valid_segments:
                logger.warning(f"No valid segments found for file {normalized_file.file_name}")
                return
            
            # Generate embeddings for segments
            segment_embeddings = await self.embedding_processor.generate_segment_embeddings(
                valid_segments, 
                normalized_file.file_name
            )
            
            # Create semantic chunks
            semantic_chunks = self.chunking_core.perform_semantic_chunking(
                valid_segments, 
                segment_embeddings, 
                normalized_file.file_name
            )
            
            # Store chunks in Qdrant
            await self.qdrant_processor.prepare_and_store_chunks(
                semantic_chunks, 
                normalized_file, 
                file_data
            )
                
        except Exception as e:
            logger.error(f"Failed to process file chunks for {normalized_file.file_name}: {str(e)}")
            raise ChunkingAlgorithmException(
                file_name=normalized_file.file_name,
                algorithm_error=f"File chunk processing failed: {str(e)}"
            )
