from abc import ABC, abstractmethod
from typing import List
from schemas.normalized_schemas import NormalizedContent, FileType, Segment

class BaseNormalizer(ABC):

    
    @abstractmethod
    async def normalize(self) -> NormalizedContent:
        pass
    
    
    def _create_normalized_file_model(self,language: str ,segments: List[Segment]) -> NormalizedContent:
            return NormalizedContent(
                language=language,
                segments=segments,
                duration=segments[-1].end if segments else 0.0 
            )
    def merge_small_segments(
        self,
        segments: List[Segment],
        target_words: int = 50,
        max_words: int = 80,
        
    ) -> List[Segment]:

        merged_segments = []

        for seg in segments:
            words = seg.text.split()
            word_count = len(words)

            
            if word_count > max_words:
                start_idx = 0
                chunk_order = 0
                while start_idx < word_count:
                    end_idx = min(start_idx + max_words, word_count)
                    chunk_text = " ".join(words[start_idx:end_idx])
                    merged_segments.append(Segment(
                        segment_id=f"{seg.segment_id}_part{chunk_order}",
                        text=chunk_text,
                        start=seg.start,
                        end=seg.end,
                        speaker=seg.speaker,
                        page=seg.page
                    ))
                    start_idx = end_idx
                    chunk_order += 1
            else:
                merged_segments.append(seg)

        
        final_segments = []
        current_segments = []
        current_word_count = 0

        for seg in merged_segments:
            words = seg.text.split()
            word_count = len(words)
            current_segments.append(seg)
            current_word_count += word_count

            if current_word_count >= target_words:
                if current_word_count <= max_words:
                    final_segments.append(self._merge_window(current_segments))
                    current_segments = []
                    current_word_count = 0
                else:
                    last_seg = current_segments.pop()
                    final_segments.append(self._merge_window(current_segments))
                    current_segments = [last_seg]
                    current_word_count = len(last_seg.text.split())

        if current_segments:
            final_segments.append(self._merge_window(current_segments))

        return final_segments    
    def _merge_window(self, segments: List[Segment]) -> Segment:
        merged_parts = []

        for seg in segments:
            speaker = seg.speaker if seg.speaker else "unknown"
            text = seg.text.strip()

            merged_parts.append(f"[{speaker}]: {text}")

        merged_text = "\n".join(merged_parts)

        return Segment(
            segment_id=f"chunk_{segments[0].segment_id}_{segments[-1].segment_id}",
            text=merged_text,
            start=segments[0].start,
            end=segments[-1].end,
            speaker=", ".join(filter(None, {seg.speaker for seg in segments})) or None,
            page=segments[0].page
        )