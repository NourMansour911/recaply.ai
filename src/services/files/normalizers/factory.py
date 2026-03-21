from typing import Dict, Type
from .base_normalizer import BaseNormalizer
from .audio_normalizer import AudioNormalizer
from .subtitle_normalizer import SubtitleNormalizer
from .text_normalizer import TextNormalizer

class NormalizerFactory:
    """Factory class to create appropriate normalizer based on file type"""
    
    _normalizers: Dict[str, Type[BaseNormalizer]] = {
        'audio': AudioNormalizer,
        'mp3': AudioNormalizer,
        'wav': AudioNormalizer,
        'flac': AudioNormalizer,
        'm4a': AudioNormalizer,
        'srt': SubtitleNormalizer,
        'vtt': SubtitleNormalizer,
        'webvtt': SubtitleNormalizer,
        'txt': TextNormalizer,
        'pdf': TextNormalizer,
        'doc': TextNormalizer,
        'docx': TextNormalizer
    }
    
    @classmethod
    def create_normalizer(cls, file_path: str, language: str = "en") -> BaseNormalizer:
        """Create appropriate normalizer instance based on file extension"""
        file_extension = file_path.lower().split('.')[-1]
        
        if file_extension in cls._normalizers:
            return cls._normalizers[file_extension](file_path, language)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    @classmethod
    def register_normalizer(cls, extensions: list, normalizer_class: Type[BaseNormalizer]):
        """Register a new normalizer for specific file extensions"""
        for ext in extensions:
            cls._normalizers[ext] = normalizer_class
