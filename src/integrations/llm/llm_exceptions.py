from typing import Optional, Dict, Any
from core import AppException


class BaseLLMException(AppException):


    def __init__(
        self,
        message: str,
        error_code: str,
        model_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        base_details = details or {}

        if model_id:
            base_details["model_id"] = model_id

        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=base_details if base_details else None,
        )


class LLMInitializationException(BaseLLMException):
    def __init__(
        self,
        model_id: Optional[str] = None,
        provider: Optional[str] = None,
        init_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="LLM provider initialization failed",
            error_code="LLM_INITIALIZATION_FAILED",
            model_id=model_id,
            details={"provider": provider, "init_error": init_error, **(details or {})},
        )


class LLMGenerationException(BaseLLMException):
    def __init__(
        self,
        model_id: Optional[str] = None,
        prompt: Optional[str] = None,
        generation_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Text generation failed",
            error_code="LLM_GENERATION_FAILED",
            model_id=model_id,
            details={"prompt": prompt[:100] + "..." if prompt and len(prompt) > 100 else prompt, 
                    "generation_error": generation_error, **(details or {})},
        )


class LLMEmbeddingException(BaseLLMException):
    def __init__(
        self,
        model_id: Optional[str] = None,
        text_sample: Optional[str] = None,
        embedding_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Text embedding failed",
            error_code="LLM_EMBEDDING_FAILED",
            model_id=model_id,
            details={"text_sample": text_sample[:50] + "..." if text_sample and len(text_sample) > 50 else text_sample,
                    "embedding_error": embedding_error, **(details or {})},
        )


class LLMModelNotSetException(BaseLLMException):
    def __init__(
        self,
        operation: str,
        model_type: str,
        provider: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=f"Model not set for {operation}",
            error_code="LLM_MODEL_NOT_SET",
            details={"operation": operation, "model_type": model_type, "provider": provider, **(details or {})},
        )


class LLMAPINotAvailableException(BaseLLMException):
    def __init__(
        self,
        provider: str,
        api_endpoint: Optional[str] = None,
        network_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="LLM API not available",
            error_code="LLM_API_NOT_AVAILABLE",
            details={"provider": provider, "api_endpoint": api_endpoint, "network_error": network_error, **(details or {})},
            status_code=503,
        )


class LLMRateLimitException(BaseLLMException):
    def __init__(
        self,
        model_id: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="LLM rate limit exceeded",
            error_code="LLM_RATE_LIMIT_EXCEEDED",
            model_id=model_id,
            details={"retry_after": retry_after, **(details or {})},
            status_code=429,
        )


class LLMInvalidResponseException(BaseLLMException):
    def __init__(
        self,
        model_id: Optional[str] = None,
        response_data: Optional[str] = None,
        validation_error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message="Invalid LLM response received",
            error_code="LLM_INVALID_RESPONSE",
            model_id=model_id,
            details={"response_data": response_data, "validation_error": validation_error, **(details or {})},
        )
