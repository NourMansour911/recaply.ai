from typing import List
from helpers import get_logger
from .chunking_exceptions import EmbeddingGenerationException
from schemas.normalized_schemas import Segment
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
                
                embedding =  await self.embedding_client.embed_text(segment.text.strip())
                
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

