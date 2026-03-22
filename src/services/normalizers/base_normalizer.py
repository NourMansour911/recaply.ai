from abc import ABC, abstractmethod
from typing import List
from src.schemas.normalized_schemas import NormalizedContent, FileType, Segment

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
