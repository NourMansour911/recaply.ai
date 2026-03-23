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
    max_words: int = 80
    ) -> List[Segment]:

        merged_segments = []
        current_segments = []
        current_word_count = 0

        for seg in segments:
            words = seg.text.split()
            word_count = len(words)

            
            current_segments.append(seg)
            current_word_count += word_count

            
            if current_word_count >= target_words:

                
                if current_word_count <= max_words:
                    merged_segments.append(self._merge_window(current_segments))
                    current_segments = []
                    current_word_count = 0

                
                else:
                    last_seg = current_segments.pop()

                    merged_segments.append(self._merge_window(current_segments))

                    
                    current_segments = [last_seg]
                    current_word_count = len(last_seg.text.split())

        
        if current_segments:
            merged_segments.append(self._merge_window(current_segments))

        return merged_segments
    
    def _merge_window(self, segments: List[Segment]) -> Segment:
        return Segment(
            segment_id=f"chunk_{segments[0].segment_id}_{segments[-1].segment_id}",
            text=" ".join(seg.text for seg in segments).strip(),
            start=segments[0].start,
            end=segments[-1].end,
            speaker=", ".join(filter(None, {seg.speaker for seg in segments})) or None,
            page=segments[0].page
        )