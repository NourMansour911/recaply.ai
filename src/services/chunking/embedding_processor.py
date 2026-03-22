from typing import List
from helpers import get_logger
from .chunking_exceptions import EmbeddingGenerationException
from src.schemas.normalized_schemas import Segment
from integrations.llm import LLMInterface
from core.settings import Settings
logger = get_logger(__name__)


class EmbeddingProcessor:
    def __init__(self, embedding_client: LLMInterface,settings:Settings):
        self.embedding_client = embedding_client
        self.settings = settings

    async def generate_segment_embeddings(self, segments: List[Segment], file_name: str) -> List[List[float]]:
        
        embeddings = []
        for segment in segments:
            try:
                
                embedding = await self.embedding_client.embed_text(segment.text.strip())
                
                if embedding is None:
                    logger.warning(f"Failed to generate embedding for segment {segment.segment_id}, using fallback")
                    
                    embedding = [0.0] * self.settings.EMBEDDING_MODEL_SIZE
                
                embeddings.append(embedding)
                
            except Exception as e:
                logger.error(f"Embedding generation failed for segment {segment.segment_id}: {str(e)}")
                raise EmbeddingGenerationException(
                    file_name=file_name,
                    segment_id=segment.segment_id,
                    embedding_error=str(e)
                )
        
        return embeddings

    def filter_valid_segments(self, segments: List[Segment]) -> List[Segment]:
        
        valid_segments = []
        for segment in segments:
            try:
                
                if not segment.text or not segment.text.strip():
                    logger.debug(f"Skipping empty segment {segment.segment_id}")
                    continue
                
                token_count = len(segment.text.split())
                if token_count < 3: 
                    logger.debug(f"Skipping segment {segment.segment_id} with insufficient tokens: {token_count}")
                    continue
                
                valid_segments.append(segment)
                
            except Exception as e:
                logger.warning(f"Error validating segment {segment.segment_id}: {str(e)}")
                
        
        if len(valid_segments) != len(segments):
            logger.info(f"Filtered out {len(segments) - len(valid_segments)} invalid segments")
            
        return valid_segments
