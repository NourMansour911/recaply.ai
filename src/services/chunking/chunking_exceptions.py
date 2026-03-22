from typing import Optional, Dict, Any
from core.app_exceptions import AppException


class BaseChunkingException(AppException):
    """
    Base exception for all chunking-related errors.
    """

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


class EmbeddingGenerationException(BaseChunkingException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        segment_id: Optional[str] = None,
        embedding_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Failed to generate embedding",
            error_code="EMBEDDING_GENERATION_FAILED",
            file_name=file_name,
            details={"segment_id": segment_id, "embedding_error": embedding_error, **(details or {})},
        )


class ChunkingAlgorithmException(BaseChunkingException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        algorithm_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Semantic chunking algorithm failed",
            error_code="CHUNKING_ALGORITHM_FAILED",
            file_name=file_name,
            details={"algorithm_error": algorithm_error, **(details or {})},
        )


class VectorDBInsertionException(BaseChunkingException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        insertion_error: Optional[str] = None,
        batch_size: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Vector database insertion failed",
            error_code="VECTOR_DB_INSERTION_FAILED",
            file_name=file_name,
            details={"insertion_error": insertion_error, "batch_size": batch_size, **(details or {})},
        )


class InvalidSegmentException(BaseChunkingException):
    def __init__(
        self,
        file_name: Optional[str] = None,
        segment_id: Optional[str] = None,
        validation_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Invalid segment detected",
            error_code="INVALID_SEGMENT",
            file_name=file_name,
            details={"segment_id": segment_id, "validation_error": validation_error, **(details or {})},
        )
