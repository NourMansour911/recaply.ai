from typing import Dict, Any, List 

from .base_normalizer import BaseNormalizer
from .normalize_exceptions import (
    AudioProcessingException,
    TranscriptionException,
)
from helpers.logger import get_logger
from helpers.ffmpeg_utils import preprocess_audio, cleanup_temp_file
from src.schemas.normalized_schemas import Segment  
from integrations.whisper_provider import get_whisper_provider

logger = get_logger(__name__)


class AudioNormalizer(BaseNormalizer):


    def __init__(
        self,
        file_path: str,
        file_name: str,
        tenant_id: str,
        project_id: str,
        language: str ,
        file_type: str
    ):
        self.file_path = file_path
        self.file_name = file_name
        self.tenant_id = tenant_id
        self.project_id = project_id
        self.language = language
        self.whisper_provider = get_whisper_provider()

    async def normalize(self) -> Dict[str, Any]:

        processed_audio_path = None
        try:
            processed_audio_path = await preprocess_audio(
                self.file_path,
                self.tenant_id,
                self.project_id
            )

            raw_segments = await self._transcribe_audio(processed_audio_path)
            segment_objects = [
                Segment(
                    segment_id=seg["segment_id"],
                    text=seg["text"],
                    start=seg["start"],
                    end=seg["end"],
                    speaker=seg["speaker"],
                    page=seg["page"]
                )
                for seg in raw_segments
            ]

            # Build normalized result
            result = self._create_normalized_file_model(
                language=self.language,
                segments=segment_objects
            )

            return result

        except AudioProcessingException:
            raise
        except Exception as e:
            logger.error(
                "Audio normalization failed",
                extra={
                    "file_name": self.file_name,
                    "tenant_id": self.tenant_id,
                    "project_id": self.project_id,
                    "error": str(e),
                },
            )
            raise AudioProcessingException(file_name=self.file_name, reason=str(e))
        finally:
            if processed_audio_path:
                try:
                    await cleanup_temp_file(processed_audio_path)
                except Exception as e:
                    logger.warning(f"Cleanup failed: {str(e)}")

    async def _transcribe_audio(self, audio_path: str) -> List[Dict]:

        try:
            whisper_model = self.whisper_provider.get_model()
            result, _ = whisper_model.transcribe(
                audio_path,
                language=self.language,
            )

            segments = []
            for segment in result:
                segments.append({
                    "segment_id": f"seg_{segment.id}",
                    "text": segment.text.strip(),
                    "start": float(segment.start),
                    "end": float(segment.end),
                    "speaker": None,
                    "page": 1,
                })

            return segments

        except ImportError:
            logger.error("Whisper library not installed")
            raise TranscriptionException(
                file_name=self.file_name,
                model_error="Whisper library not installed"
            )
        except Exception as e:
            logger.error(
                "Transcription failed",
                extra={
                    "file_name": self.file_name,
                    "tenant_id": self.tenant_id,
                    "project_id": self.project_id,
                    "error": str(e),
                },
            )
            raise TranscriptionException(file_name=self.file_name, model_error=str(e))

