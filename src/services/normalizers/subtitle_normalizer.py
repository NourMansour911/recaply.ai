import re
from typing import List
from .base_normalizer import BaseNormalizer
from  .normalize_exceptions import (
    SubtitleParsingException,
    InvalidTimeFormatException
)
from helpers.logger import get_logger
import webvtt
from pysrt import SubRipFile
from .normalized_schemas import Segment


logger = get_logger(__name__)

class SubtitleNormalizer(BaseNormalizer):
    def __init__(self, file_type: str, tenant_id: str, project_id: str, file_path: str, file_name: str, language: str ):
        self.file_name = file_name
        self.file_path = file_path
        self.file_type = file_type
        self.tenant_id = tenant_id
        self.project_id = project_id
        self.language = language
    
    
        
    
    async def normalize(self):
        
        
        
        try:
            if self.file_type == 'srt':
                segments = self._parse_srt()
            elif self.file_type == 'vtt':
                segments = self._parse_vtt()
            else:
                raise SubtitleParsingException(
                    file_name=self.file_name,
                    format_type=self.file_type,
                    parse_error="Unsupported subtitle format"
                )
            
            
            segment_objects = [
                Segment(
                    segment_id=seg["segment_id"],
                    text=seg["text"],
                    start=seg["start"],
                    end=seg["end"],
                    speaker=seg["speaker"],
                    page=seg["page"]
                ) for seg in segments
            ]
            
            
            result = self._create_normalized_file_model( self.file_name, self.file_type,self.language, segment_objects)
            return result
            
        except SubtitleParsingException:
            raise
        except Exception as e:
            logger.error(f"Subtitle normalization failed: {str(e)}")
            raise SubtitleParsingException(
                file_name=self.file_name,
                format_type=self.file_type,
                parse_error=str(e)
            )
    
    def _parse_srt(self) -> List[Segment]:
        
        try:
            subs = SubRipFile.open(self.file_path, encoding='utf-8')
            segments : list[Segment] = []
            
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
                
                segments.append(
                    Segment(
                        segment_id=f"seg_{i}",
                        text=sub.text.strip().replace('\n', ' '),
                        start=start_time,
                        end=end_time,
                        speaker=None,
                        page=1
                    )
                )

            
            return segments
        except SubtitleParsingException:
            raise
        except Exception as e:
            logger.error(
            "SRT parsing failed",
            extra={
                "file_name": self.file_name,
                "tenant_id": self.tenant_id,
                "project_id": self.project_id,
                "error": str(e)
            }
        )
            raise SubtitleParsingException(
                file_name=self.file_name,
                format_type="srt",
                parse_error=f"SRT parsing failed: {str(e)}"
            )
    
    def _parse_vtt(self) -> List[Segment]:
        
        try:
            vtt = webvtt.read(self.file_path)
            segments : list[Segment] = []
            
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
                
                segments.append(
                Segment(
                    segment_id=f"seg_{i}",
                    text=caption.text.strip().replace('\n', ' '),
                    start=start_time,
                    end=end_time,
                    speaker=None,
                    page=1
                )
            )

            
            return segments
        except SubtitleParsingException:
            raise
        except Exception as e:
            logger.error(
            "VTT parsing failed",
            extra={
                "file_name": self.file_name,
                "tenant_id": self.tenant_id,
                "project_id": self.project_id,
                "error": str(e)
            }
        )
            raise SubtitleParsingException(
                file_name=self.file_name,
                format_type="vtt",
                parse_error=f"VTT parsing failed: {str(e)}"
            )
    
    def _srt_time_to_seconds(self, time_str: str) -> float:
        
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
