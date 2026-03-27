from ..service_exceptions import ServiceException


class NormalizerException(ServiceException):
    def __init__(self, message="Normalizer service error", details=None):
        super().__init__(message=message, details=details)


class SubtitleParsingException(NormalizerException):
    def __init__(self, file_name: str, format_type: str, parse_error: str, details=None):
        message = f"Failed to parse subtitle file: {file_name}"
        context = {"file_name": file_name, "format_type": format_type, "parse_error": parse_error}
        if details:
            context.update(details)
        super().__init__(message=message, details=context)


class InvalidTimeFormatException(NormalizerException):
    def __init__(self, file_name: str, time_string: str, format_type: str, details=None):
        message = f"Invalid time format in file: {file_name}"
        context = {"file_name": file_name, "time_string": time_string, "format_type": format_type}
        if details:
            context.update(details)
        super().__init__(message=message, details=context)


class TextExtractionException(NormalizerException):
    def __init__(self, file_name: str, file_type: str, extraction_error: str, details=None):
        message = f"Text extraction failed for file: {file_name}"
        context = {"file_name": file_name, "file_type": file_type, "extraction_error": extraction_error}
        if details:
            context.update(details)
        super().__init__(message=message, details=context)


class AudioProcessingException(NormalizerException):
    def __init__(self, file_name: str, reason: str, details=None):
        message = f"Audio processing failed for file: {file_name}"
        context = {"file_name": file_name, "reason": reason}
        if details:
            context.update(details)
        super().__init__(message=message, details=context)


class TranscriptionException(NormalizerException):
    def __init__(self, file_name: str, model_error: str, details=None):
        message = f"Audio transcription failed for file: {file_name}"
        context = {"file_name": file_name, "model_error": model_error}
        if details:
            context.update(details)
        super().__init__(message=message, details=context)