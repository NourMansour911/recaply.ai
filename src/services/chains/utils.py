
from typing import List
from models import Segment


def format_segments(segments: List[Segment]) -> str:
    
    return "\n\n\n".join([
        f"[{s.id}]\n {s.text}"
        for s in segments
    ])
    
def get_config(name: str, user_id: str):
    return {
        "run_name": name,
        "tags": ["api"],
        "metadata": {"user_id": user_id}
    }