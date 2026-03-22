from abc import ABC, abstractmethod
from typing import List
from .normalize_exceptions import NormalizationException
from .normalized_schemas import NormalizedFileModel, FileType, Segment

class BaseNormalizer(ABC):

    
    @abstractmethod
    async def normalize(self) -> NormalizedFileModel:
        pass
    
    
    def _create_normalized_file_model(self, file_name: str, file_type: str,language: str ,segments: List[Segment]) -> NormalizedFileModel:
        
        try:

            
            return NormalizedFileModel(
                file_name=file_name,
                file_type=FileType(file_type),
                language=language,
                segments=segments,
                duration=segments[-1].end if segments else 0.0 
            )
            
        except Exception as e:
            raise NormalizationException(
                file_name=file_name,
                file_type=file_type,
                normalization_error=f"Failed to create normalized file model: {str(e)}"
            )
