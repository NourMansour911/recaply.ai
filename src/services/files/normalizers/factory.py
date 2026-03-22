from typing import Dict, Type
from .base_normalizer import BaseNormalizer
from .audio_normalizer import AudioNormalizer
from .subtitle_normalizer import SubtitleNormalizer
from .text_normalizer import TextNormalizer

class NormalizerFactory:
    
    
    _normalizers: Dict[str, Type[BaseNormalizer]] = {
        'audio': AudioNormalizer,
        'srt': SubtitleNormalizer,
        'vtt': SubtitleNormalizer,
        'txt': TextNormalizer,
        'pdf': TextNormalizer,
    }
    
    @classmethod
    def create_normalizer(cls,file_type: str ,tenant_id,project_id,file_path: str, language: str = "en") -> BaseNormalizer:
        
        if file_type in cls._normalizers:
            return cls._normalizers[file_type]()
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
