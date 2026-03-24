from typing import List
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from helpers import get_logger
from .chunking_exceptions import ChunkingAlgorithmException
from schemas.normalized_schemas import Segment
from models.chunk_model import SemanticChunk

logger = get_logger(__name__)


class SemanticChunkingCore:
    def __init__(
        self,
        similarity_threshold: float = 0.7,
        max_tokens_per_chunk: int = 300,
        overlap_tokens: int = 50,
    ):
        self.similarity_threshold = similarity_threshold
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.overlap_tokens = overlap_tokens

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

            i = 0
            while i < len(segments):
                segment = segments[i]
                embedding = embeddings[i]

               
                temp_segments = current_chunk_segments + [segment]
                temp_token_count = sum(len(seg.text.split()) for seg in temp_segments)

                if temp_token_count <= self.max_tokens_per_chunk:
                    current_chunk_segments.append(segment)
                    current_chunk_embeddings.append(embedding)
                    i += 1
                else:
                   
                    if current_chunk_segments:
                        merged_chunk = self._merge_segments(current_chunk_segments, chunk_order)
                        semantic_chunks.append(merged_chunk)
                        chunk_order += 1

                        
                        overlap_size = 0
                        cumulative_overlap_tokens = 0
                        j = len(current_chunk_segments) - 1
                        while j >= 0 and cumulative_overlap_tokens < self.overlap_tokens:
                            seg_tokens = len(current_chunk_segments[j].text.split())
                            if cumulative_overlap_tokens + seg_tokens > self.overlap_tokens:
                                break
                            cumulative_overlap_tokens += seg_tokens
                            overlap_size += 1
                            j -= 1

                        
                        i -= overlap_size
                        current_chunk_segments = []
                        current_chunk_embeddings = []

                    else:
                        
                        logger.warning(f"Skipping large segment at index {i} due to exceeding max tokens.")
                        i += 1

            
            if current_chunk_segments:
                merged_chunk = self._merge_segments(current_chunk_segments, chunk_order)
                semantic_chunks.append(merged_chunk)

            return semantic_chunks
            
        except Exception as e:
            logger.error(f"Semantic chunking failed for file {file_name}: {str(e)}")
            raise ChunkingAlgorithmException(
                file_name=file_name,
                algorithm_error=str(e)
            )

    def _merge_segments(self, segments: List[Segment], chunk_order: int) -> SemanticChunk:
        merged_text = "\n".join(
            seg.text.strip() for seg in segments
        )

        start_times = [seg.start for seg in segments if seg.start is not None]
        end_times = [seg.end for seg in segments if seg.end is not None]

        start = min(start_times) if start_times else segments[0].start
        end = max(end_times) if end_times else segments[-1].end
        duration = (end - start) if start is not None and end is not None else None

        page = segments[0].page
        speakers = list(set(seg.speaker for seg in segments if seg.speaker is not None))

        return SemanticChunk(
            chunk_order=chunk_order,
            text=merged_text,
            start=start,
            end=end,
            duration=duration,
            page=page,
            speakers=speakers
        )
