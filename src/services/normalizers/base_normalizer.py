from abc import ABC, abstractmethod
from typing import List
from schemas.normalized_schemas import NormalizedContent, Segment
from .normalizers_exceptions import NormalizerException

class BaseNormalizer(ABC):

    @abstractmethod
    async def normalize(self) -> NormalizedContent:
        pass

    def _create_normalized_file_model(self, language: str, segments: List[Segment]) -> NormalizedContent:
        return NormalizedContent(
            language=language,
            segments=segments,
            duration=segments[-1].end if segments else 0.0
        )

    def merge_small_segments(self, segments: List[Segment], target_words: int = 50, max_words: int = 80) -> List[Segment]:
        merged_segments = []
        for seg in segments:
            words = seg.text.split()
            word_count = len(words)
            if word_count > max_words:
                start_idx = 0
                while start_idx < word_count:
                    end_idx = min(start_idx + max_words, word_count)
                    chunk_text = " ".join(words[start_idx:end_idx])
                    merged_segments.append(Segment(
                        text=chunk_text,
                        start=seg.start,
                        end=seg.end,
                        speakers=seg.speakers,
                    ))
                    start_idx = end_idx
            else:
                merged_segments.append(seg)

        final_segments = []
        current_segments = []
        current_word_count = 0

        for seg in merged_segments:
            words = seg.text.split()
            word_count = len(words)
            if current_word_count + word_count > max_words:
                if current_segments:
                    final_segments.append(self._merge_window(current_segments))
                if word_count <= max_words:
                    current_segments = [seg]
                    current_word_count = word_count
                else:
                    final_segments.append(seg)
                    current_segments = []
                    current_word_count = 0
            else:
                current_segments.append(seg)
                current_word_count += word_count
                if current_word_count >= target_words:
                    final_segments.append(self._merge_window(current_segments))
                    current_segments = []
                    current_word_count = 0

        if current_segments:
            final_segments.append(self._merge_window(current_segments))

        return final_segments

    def _merge_window(self, segments: List[Segment]) -> Segment:
        if not segments:
            raise NormalizerException(message="Segments list cannot be empty")

        merged_parts = []
        for i, seg in enumerate(segments):
            text = seg.text.strip()
            if not text:
                continue
            if i > 0:
                merged_parts.append("----")
            if seg.speakers:
                speakers_str = ", ".join(seg.speakers)
                merged_parts.append(f"[{speakers_str}]: {text}")
            else:
                merged_parts.append(text)

        merged_text = "\n".join(merged_parts)
        seen = set()
        speakers = []
        for seg in segments:
            if not seg.speakers:
                continue
            for speaker in seg.speakers:
                if speaker not in seen:
                    seen.add(speaker)
                    speakers.append(speaker)

        return Segment(
            text=merged_text,
            start=segments[0].start,
            end=segments[-1].end,
            speakers=speakers if speakers else None,
        )