from typing import List
from models import Segment
from helpers.logger import get_logger
from .chunking_exceptions import ChunkProcessingError

logger = get_logger(__name__)


class MergeChunkingService:

    async def run(self, segments: List[Segment], max_chunk_size: int) -> List[Segment]:
        try:
            merged_chunks = []
            current_chunk = []
            current_words = 0

            for seg in segments:
                seg_words = len(seg.text.split())
                seg_chars = len(seg.text)

                if current_words + seg_words > max_chunk_size:
                    if current_chunk:
                        merged_text = "\n".join([s.text for s in current_chunk])
                        merged_chunks.append(
                            Segment(
                                text=merged_text,
                                start=current_chunk[0].start,
                                end=current_chunk[-1].end,
                                speakers=list({s for seg in current_chunk if seg.speakers for s in seg.speakers})
                            )
                        )
                    current_chunk = [seg]
                    current_words = seg_words
                    current_chars = seg_chars
                else:
                    current_chunk.append(seg)
                    current_words += seg_words
                    current_chars += seg_chars

            if current_chunk:
                merged_text = "\n".join([s.text for s in current_chunk])
                merged_chunks.append(
                    Segment(
                        text=merged_text,
                        start=current_chunk[0].start,
                        end=current_chunk[-1].end,
                        speakers=list({s for seg in current_chunk if seg.speakers for s in seg.speakers})
                    )
                )

            return merged_chunks
        except Exception as e:
            logger.error("Failed during merge chunking", exc_info=True)
            raise ChunkProcessingError(segment_index=0, message=str(e))