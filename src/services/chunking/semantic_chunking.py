from typing import List, Optional
from schemas import Segment
from scipy.spatial.distance import cosine
from helpers.logger import get_logger

logger = get_logger(__name__)


class SemanticChunkingService:
    def __init__(self, embedding_client, similarity_threshold: float):
        self.embedding_client = embedding_client
        self.similarity_threshold = similarity_threshold

    async def run(
        self,
        segments: List[Segment],
        max_chunk_size: int,
        overlap: int,
        min_chunk_size: int = 210,
    ) -> List[Segment]:

        final_chunks: List[Segment] = []

        current_segments: List[Segment] = []
        current_word_count = 0
        current_avg_emb: Optional[List[float]] = None

        for seg in segments:
            seg_words = seg.text.split()
            seg_word_count = len(seg_words)
            seg_emb = await self.embedding_client.embed_text(seg.text)

            
            if not current_segments:
                current_segments.append(seg)
                current_word_count = seg_word_count
                current_avg_emb = seg_emb
                continue

            similarity = 1 - cosine(current_avg_emb, seg_emb)

            can_fit_max = current_word_count + seg_word_count <= max_chunk_size
            reached_min = current_word_count >= min_chunk_size

            should_merge = (
                not reached_min  
                or (can_fit_max and similarity >= self.similarity_threshold)
            )

            if should_merge and can_fit_max:
                
                total_words = current_word_count + seg_word_count

                current_avg_emb = [
                    (a * current_word_count + b * seg_word_count) / total_words
                    for a, b in zip(current_avg_emb, seg_emb)
                ]

                current_segments.append(seg)
                current_word_count = total_words

            else:
                
                chunk_text = " ".join([s.text for s in current_segments])

                final_chunks.append(Segment(
                    text=chunk_text,
                    start=current_segments[0].start,
                    end=current_segments[-1].end,
                    speakers=None
                ))

                
                words = chunk_text.split()
                overlap_words = words[-overlap:] if overlap < len(words) else words
                overlap_text = " ".join(overlap_words)

                
                current_segments = []
                current_word_count = 0
                current_avg_emb = None

                if overlap_words:
                    overlap_segment = Segment(
                        text=overlap_text,
                        start=current_segments[-1].start if current_segments else seg.start,
                        end=current_segments[-1].end if current_segments else seg.end,
                        speakers=None
                    )
                    current_segments.append(overlap_segment)
                    current_word_count = len(overlap_words)

                
                current_segments.append(seg)
                current_word_count += seg_word_count
                current_avg_emb = seg_emb

        
        if current_segments:
            chunk_text = " ".join([s.text for s in current_segments])

            final_chunks.append(Segment(
                text=chunk_text,
                start=current_segments[0].start,
                end=current_segments[-1].end,
                speakers=None
            ))

        return final_chunks