import logging
from typing import List
from schemas import Segment

logger = logging.getLogger(__name__)


class MergeChunkingService:

    def __init__(self, target_words: int = 50, max_words: int = 80):
        self.target_words = target_words
        self.max_words = max_words

    async def run(self, segments: List[Segment]) -> List[Segment]:
        merged = []
        current = []
        current_words = 0

        for seg in segments:
            words = len(seg.text.split())

            if current_words < self.target_words:
                current.append(seg)
                current_words += words
                continue

            if current_words + words > self.max_words:
                merged.append(self._build_chunk(current))
                current = [seg]
                current_words = words
            else:
                current.append(seg)
                current_words += words

        if current:
            merged.append(self._build_chunk(current))

        return merged

    def _format_speaker(self, speakers):
        if not speakers:
            return None

        if isinstance(speakers, list):
            speakers = ", ".join(speakers)

        speakers = str(speakers).strip().lower()

        if speakers in ["speaker", "unknown", "none", ""]:
            return None

        return speakers

    def _build_chunk(self, group: List[Segment]) -> Segment:
        lines = []

        for seg in group:
            speaker = self._format_speaker(seg.speakers)

            if speaker:
                lines.append(f"[{speaker}]: {seg.text.strip()}")
            else:
                lines.append(seg.text.strip())

        text = "\n".join(lines)

        start = next((s.start for s in group if s.start is not None), None)
        end = next((s.end for s in reversed(group) if s.end is not None), None)

        return Segment(
            segment_id=f"merged-{group[0].segment_id}",
            text=text,
            start=start,
            end=end,
            speakers=None
        )