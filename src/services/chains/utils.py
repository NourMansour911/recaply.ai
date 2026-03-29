
from typing import List
from models import Segment


def format_segments(segments: List[Segment]) -> str:
    
    return "\n".join([
        f"[{s.id}] {s.text}"
        for s in segments
    ])