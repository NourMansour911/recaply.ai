import re
from typing import Dict, Any, List
from .base_normalizer import BaseNormalizer
from core.exceptions import (
    SubtitleParsingException,
    InvalidTimeFormatException
)
from helpers.logger import get_logger
import webvtt
from pysrt import SubRipFile

logger = get_logger(__name__)

class SubtitleNormalizer(BaseNormalizer):
    """Normalizer for SRT and VTT subtitle files"""
    
    def __init__(self, file_path: str, language: str = "en"):
        super().__init__(file_path, language)
        self.file_extension = file_path.lower().split('.')[-1]
        
    async def normalize(self) -> Dict[str, Any]:
        """Normalize subtitle file to standard JSON schema"""
        try:
            if self.file_extension == 'srt':
                segments = self._parse_srt()
            elif self.file_extension in ['vtt', 'webvtt']:
                segments = self._parse_vtt()
            else:
                raise SubtitleParsingException(
                    file_name=self.file_name,
                    format_type=self.file_extension,
                    parse_error="Unsupported subtitle format"
                )
                
            # Calculate metadata
            duration = max(segment["end"] for segment in segments) if segments else 0.0
            word_count = sum(len(segment["text"].split()) for segment in segments)
            
            # Build result
            result = self._create_base_schema(self.file_extension)
            result["segments"] = segments
            result["metadata"]["duration"] = duration
            result["metadata"]["word_count"] = word_count
            
            return result
            
        except SubtitleParsingException:
            raise
        except Exception as e:
            logger.error(f"Subtitle normalization failed: {str(e)}")
            raise SubtitleParsingException(
                file_name=self.file_name,
                format_type=self.file_extension,
                parse_error=str(e)
            )
    
    def _parse_srt(self) -> List[Dict]:
        """Parse SRT file format"""
        try:
            subs = SubRipFile.open(self.file_path, encoding='utf-8')
            segments = []
            
            for i, sub in enumerate(subs):
                try:
                    start_time = self._srt_time_to_seconds(str(sub.start))
                    end_time = self._srt_time_to_seconds(str(sub.end))
                except Exception as e:
                    raise InvalidTimeFormatException(
                        file_name=self.file_name,
                        time_string=f"{sub.start} -> {sub.end}",
                        format_type="SRT"
                    )
                
                segments.append({
                    "segment_id": f"seg_{i}",
                    "text": sub.text.strip().replace('\n', ' '),
                    "start": start_time,
                    "end": end_time,
                    "speaker": None,
                    "page": 1,
                    "source": "srt"
                })
            
            return segments
        except SubtitleParsingException:
            raise
        except Exception as e:
            logger.error(f"SRT parsing failed: {str(e)}")
            raise SubtitleParsingException(
                file_name=self.file_name,
                format_type="srt",
                parse_error=f"SRT parsing failed: {str(e)}"
            )
    
    def _parse_vtt(self) -> List[Dict]:
        """Parse VTT file format"""
        try:
            vtt = webvtt.read(self.file_path)
            segments = []
            
            for i, caption in enumerate(vtt):
                try:
                    start_time = self._vtt_time_to_seconds(caption.start)
                    end_time = self._vtt_time_to_seconds(caption.end)
                except Exception as e:
                    raise InvalidTimeFormatException(
                        file_name=self.file_name,
                        time_string=f"{caption.start} -> {caption.end}",
                        format_type="VTT"
                    )
                
                segments.append({
                    "segment_id": f"seg_{i}",
                    "text": caption.text.strip().replace('\n', ' '),
                    "start": start_time,
                    "end": end_time,
                    "speaker": None,
                    "page": 1,
                    "source": "vtt"
                })
            
            return segments
        except SubtitleParsingException:
            raise
        except Exception as e:
            logger.error(f"VTT parsing failed: {str(e)}")
            raise SubtitleParsingException(
                file_name=self.file_name,
                format_type="vtt",
                parse_error=f"VTT parsing failed: {str(e)}"
            )
    
    def _srt_time_to_seconds(self, time_str: str) -> float:
        """Convert SRT time format to seconds"""
        try:
            hours, minutes, seconds, milliseconds = re.split('[:,]', time_str)
            return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
        except Exception as e:
            raise InvalidTimeFormatException(
                file_name=self.file_name,
                time_string=time_str,
                format_type="SRT time conversion"
            )
    
    def _vtt_time_to_seconds(self, time_str: str) -> float:
        """Convert VTT time format to seconds"""
        try:
            if '-->' in time_str:
                time_str = time_str.split('-->')[0].strip()
            
            parts = time_str.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = parts
                if '.' in seconds:
                    secs, millis = seconds.split('.')
                    return int(hours) * 3600 + int(minutes) * 60 + int(secs) + int(millis) / 1000
                else:
                    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            elif len(parts) == 2:
                minutes, seconds = parts
                if '.' in seconds:
                    secs, millis = seconds.split('.')
                    return int(minutes) * 60 + int(secs) + int(millis) / 1000
                else:
                    return int(minutes) * 60 + int(seconds)
            else:
                return 0.0
        except Exception as e:
            raise InvalidTimeFormatException(
                file_name=self.file_name,
                time_string=time_str,
                format_type="VTT time conversion"
            )
