from abc import ABC, abstractmethod
from typing import Dict, Any
import uuid
from datetime import datetime
from core.exceptions import (
    NormalizationException
)

class BaseNormalizer(ABC):
    """Base class for all normalizers"""
    
    def __init__(self, file_path: str, language: str = "en"):
        self.file_path = file_path
        self.language = language
        self.file_id = str(uuid.uuid4())
        self.file_name = file_path.split('/')[-1]
        
    @abstractmethod
    async def normalize(self) -> Dict[str, Any]:
        """Normalize file to standard JSON schema"""
        pass
    
    def _create_base_schema(self, file_type: str) -> Dict[str, Any]:
        """Create base JSON schema structure"""
        try:
            return {
                "file_id": self.file_id,
                "file_type": file_type,
                "language": self.language,
                "segments": [],
                "metadata": {
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "duration": 0.0,
                    "word_count": 0
                }
            }
        except Exception as e:
            raise NormalizationException(
                file_name=self.file_name,
                file_type=file_type,
                normalization_error=f"Failed to create base schema: {str(e)}"
            )
