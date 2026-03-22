import asyncio
from faster_whisper import WhisperModel
from helpers.ffmpeg_utils import preprocess_audio, cleanup_temp_file
import json
from typing import Dict, Any, List
from .base_normalizer import BaseNormalizer
from core.exceptions import (
    AudioProcessingException, 
    TranscriptionException,
    FFmpegException
)
from helpers.logger import get_logger

logger = get_logger(__name__)

class AudioNormalizer(BaseNormalizer):
    """Normalizer for audio files using Whisper for transcription"""
    
    def __init__(self, file_path: str  ):
        super().__init__(file_path)
        
        
        
    async def normalize(self,) -> Dict[str, Any]:
        """Normalize audio file to standard JSON schema"""
        processed_audio_path = None
        try:
            # Preprocess audio
            
            processed_audio_path = await preprocess_audio(
                self.file_path, 
                "temp_tenant",  # These would come from context
                "temp_project"
            )
            
            # Transcribe using Whisper
            segments = await self._transcribe_audio(processed_audio_path)
            
            # Calculate metadata
            duration = max(segment["end"] for segment in segments) if segments else 0.0
            word_count = sum(len(segment["text"].split()) for segment in segments)
            
            
            result = self._create_base_schema("audio")
            result["segments"] = segments
            result["metadata"]["duration"] = duration
            result["metadata"]["word_count"] = word_count
            
            return result
            
        except AudioProcessingException:
            raise
        except Exception as e:
            logger.error(f"Audio normalization failed: {str(e)}")
            raise AudioProcessingException(
                file_name=self.file_name,
                reason=str(e)
            )
        finally:
            # Cleanup processed audio
            if processed_audio_path:
                try:
                    
                    await cleanup_temp_file(processed_audio_path)
                except Exception as e:
                    logger.warning(f"Cleanup failed: {str(e)}")
    
    async def _transcribe_audio(self, audio_path: str,whisper_model: WhisperModel) -> List[Dict]:
        
        try:
            
            
            
            result = whisper_model.transcribe(
                audio_path, 
                language=self.language,
                verbose=False
            )
            
            
            segments = []
            for i, segment in enumerate(result["segments"]):
                segments.append({
                    "segment_id": f"seg_{i}",
                    "text": segment["text"].strip(),
                    "start": float(segment["start"]),
                    "end": float(segment["end"]),
                    "speaker": None,
                    "page": 1,
                    "source": "audio"
                })
            
            return segments
            
        except ImportError:
            logger.error("Whisper library not installed")
            raise TranscriptionException(
                file_name=self.file_name,
                model_error="Whisper library not installed"
            )
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            raise TranscriptionException(
                file_name=self.file_name,
                model_error=str(e)
            )
