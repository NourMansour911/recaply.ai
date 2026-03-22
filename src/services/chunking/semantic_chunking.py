from typing import List, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from helpers import get_logger
from .chunking_exceptions import ChunkingAlgorithmException
from src.schemas.normalized_schemas import Segment
from models.chunk_model import SemanticChunk

logger = get_logger(__name__)


class SemanticChunkingCore:
    def __init__(
        self,
        similarity_threshold: float = 0.7,
        max_tokens_per_chunk: int = 300,
        min_tokens_per_chunk: int = 20
    ):
        self.similarity_threshold = similarity_threshold
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.min_tokens_per_chunk = min_tokens_per_chunk

    def perform_semantic_chunking(
        self, 
        segments: List[Segment], 
        embeddings: List[List[float]], 
        file_name: str
    ) -> List[SemanticChunk]:
        
        try:
            if len(segments) != len(embeddings):
                raise ChunkingAlgorithmException(
                    file_name=file_name,
                    algorithm_error="Mismatch between segments and embeddings count"
                )

            semantic_chunks = []
            current_chunk_segments = []
            current_chunk_embeddings = []
            chunk_order = 0

            for i, (segment, embedding) in enumerate(zip(segments, embeddings)):
                
                if not current_chunk_segments:
                    
                    current_chunk_segments.append(segment)
                    current_chunk_embeddings.append(embedding)
                else:
                   
                    avg_embedding = np.mean(current_chunk_embeddings, axis=0)
                    
                    similarity = cosine_similarity([avg_embedding], [embedding])[0][0]
                    
                    
                    current_token_count = sum(len(seg.text.split()) for seg in current_chunk_segments)
                    would_exceed_limit = (current_token_count + len(segment.text.split())) > self.max_tokens_per_chunk
                    
                    
                    should_merge = (
                        similarity >= self.similarity_threshold and 
                        not would_exceed_limit and
                        self._should_merge_segment(current_chunk_segments, segment)
                    )
                    
                    if should_merge:
                        
                        current_chunk_segments.append(segment)
                        current_chunk_embeddings.append(embedding)
                    else:
                        if current_token_count >= self.min_tokens_per_chunk:
                            merged_chunk = self._merge_segments(current_chunk_segments, chunk_order)
                            semantic_chunks.append(merged_chunk)
                            chunk_order += 1
                        
                        current_chunk_segments = [segment]
                        current_chunk_embeddings = [embedding]

            
            if current_chunk_segments:
                current_token_count = sum(len(seg.text.split()) for seg in current_chunk_segments)
                if current_token_count >= self.min_tokens_per_chunk:
                    merged_chunk = self._merge_segments(current_chunk_segments, chunk_order)
                    semantic_chunks.append(merged_chunk)

            return semantic_chunks
            
        except Exception as e:
            logger.error(f"Semantic chunking failed for file {file_name}: {str(e)}")
            raise ChunkingAlgorithmException(
                file_name=file_name,
                algorithm_error=str(e)
            )

    def _should_merge_segment(self, current_segments: List[Segment], new_segment: Segment) -> bool:
        current_speakers = set(seg.speaker for seg in current_segments if seg.speaker)
        if current_speakers and new_segment.speaker:
            if new_segment.speaker not in current_speakers:
                
                return False
        
        # Check for temporal continuity
        if current_segments and new_segment.start is not None and current_segments[-1].end is not None:
            time_gap = new_segment.start - current_segments[-1].end
            if time_gap > 15.0:  
                return False
                
        return True

    def _merge_segments(self, segments: List[Segment], chunk_order: int) -> SemanticChunk:
        
        if not segments:
            raise ValueError("Cannot merge empty segment list")

        merged_text = " ".join([seg.text.strip() for seg in segments])

        start_times = [seg.start for seg in segments if seg.start is not None]
        end_times = [seg.end for seg in segments if seg.end is not None]
        
        start = min(start_times) if start_times else segments[0].start
        end = max(end_times) if end_times else segments[-1].end
        duration = (end - start) if start is not None and end is not None else None

        
        page = segments[0].page

        speakers = list(set(seg.speaker for seg in segments if seg.speaker))

        return SemanticChunk(
            chunk_order=chunk_order,
            text=merged_text,
            start=start,
            end=end,
            duration=duration,
            page=page,
            speakers=speakers
        )
