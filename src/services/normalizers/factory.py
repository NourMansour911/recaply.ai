from typing import Dict, Type
from .base_normalizer import BaseNormalizer
from .audio_normalizer import AudioNormalizer
from .subtitle_normalizer import SubtitleNormalizer
from .text_normalizer import TextNormalizer
from .normalizers_exceptions import NormalizerException

class NormalizerFactory:

    _normalizers: Dict[str, Type[BaseNormalizer]] = {
        'audio': AudioNormalizer,
        'srt': SubtitleNormalizer,
        'vtt': SubtitleNormalizer,
        'txt': TextNormalizer,
        'pdf': TextNormalizer,
    }

    @classmethod
    def create_normalizer(cls, file_type: str, file_name: str, tenant_id, project_id, file_path: str, language: str = "en") -> BaseNormalizer:
        if file_type in cls._normalizers:
            return cls._normalizers[file_type](
                file_path=file_path,
                file_name=file_name,
                file_type=file_type,
                tenant_id=tenant_id,
                project_id=project_id,
            )
        else:
            raise NormalizerException(message=f"Unsupported file type: {file_type}", details={"file_name": file_name})