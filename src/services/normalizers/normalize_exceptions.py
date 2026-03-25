from typing import Optional, Dict, Any
from core.app_exceptions import AppException


class BaseNormalizeException(AppException):


    def __init__(
        self,
        message: str,
        error_code: str,
        file_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        base_details = details or {}

        if file_name:
            base_details["file_name"] = file_name

        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=base_details if base_details else None,
        )


class AudioProcessingException(BaseNormalizeException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Audio processing failed",
            error_code="AUDIO_PROCESSING_FAILED",
            file_name=file_name,
            details={"reason": reason, **(details or {})},
        )


class TranscriptionException(BaseNormalizeException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        model_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Audio transcription failed",
            error_code="TRANSCRIPTION_FAILED",
            file_name=file_name,
            details={"model_error": model_error, **(details or {})},
        )


class SubtitleParsingException(BaseNormalizeException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        format_type: Optional[str] = None,
        parse_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Subtitle parsing failed",
            error_code="SUBTITLE_PARSING_FAILED",
            file_name=file_name,
            details={"format_type": format_type, "parse_error": parse_error, **(details or {})},
        )


class TextExtractionException(BaseNormalizeException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        file_type: Optional[str] = None,
        extraction_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Text extraction failed",
            error_code="TEXT_EXTRACTION_FAILED",
            file_name=file_name,
            details={"file_type": file_type, "extraction_error": extraction_error, **(details or {})},
        )


class NormalizationException(BaseNormalizeException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        file_type: Optional[str] = None,
        normalization_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="File normalization failed",
            error_code="NORMALIZATION_FAILED",
            file_name=file_name,
            details={"file_type": file_type, "normalization_error": normalization_error, **(details or {})},
        )


class FFmpegException(BaseNormalizeException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        ffmpeg_error: Optional[str] = None,
        command: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="FFmpeg processing failed",
            error_code="FFMPEG_FAILED",
            file_name=file_name,
            details={"ffmpeg_error": ffmpeg_error, "command": command, **(details or {})},
            status_code=500,
        )


class InvalidTimeFormatException(BaseNormalizeException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        time_string: Optional[str] = None,
        format_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Invalid time format in file",
            error_code="INVALID_TIME_FORMAT",
            file_name=file_name,
            details={"time_string": time_string, "format_type": format_type, **(details or {})},
        )


class SegmentProcessingException(BaseNormalizeException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        processing_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Segment processing failed",
            error_code="SEGMENT_PROCESSING_FAILED",
            file_name=file_name,
            details={"processing_error": processing_error, **(details or {})},
        )
