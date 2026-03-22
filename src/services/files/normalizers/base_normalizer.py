from abc import ABC, abstractmethod
from typing import List, Optional
import uuid
from datetime import datetime
from core.exceptions import NormalizationException
from .normalized_schemas import NormalizedFileModel, FileType, Segment, Metadata

class BaseNormalizer(ABC):

    
    @abstractmethod
    async def normalize(self, file_type: str, tenant_id: str, project_id: str, file_path: str, file_name: str, language: str = "en") -> NormalizedFileModel:
        pass
    
    
    def _create_normalized_file_model(self, file_name: str, file_type: str,language: str ,segments: List[Segment]) -> NormalizedFileModel:
        
        try:

            
            return NormalizedFileModel(
                file_name=file_name,
                file_type=FileType(file_type),
                language=language,
                segments=segments,
                duration=segments[-1].end 
            )
            
        except Exception as e:
            raise NormalizationException(
                file_name=file_name,
                file_type=file_type,
                normalization_error=f"Failed to create normalized file model: {str(e)}"
            )
