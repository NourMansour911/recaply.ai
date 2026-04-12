from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Configs
    APP_NAME: str
    APP_VERSION: str

    STORAGE_PATH: str

    # Database
    MONGODB_URI: str
    MONGODB_DATABASE: str
    QDRANT_URL: str
    REDIS_URL: str

    # Max file sizes
    MAX_AUDIO_SIZE_MB: int
    MAX_TEXT_SIZE_MB: int
    MAX_SUBTITLE_SIZE_MB: int
    MAX_PDF_SIZE_MB: int

    TO_BYTES: int

    # Chunking
    CHUNK_OVERLAP: int
    CHUNK_MIN_SIZE: int
    CHUNK_MAX_SIZE: int
    CHUNKS_SIMILARITY_THRESHOLD: float

    # APIs
    COHERE_API_KEY: str
    LANGSMITH_API_KEY: str
    OPENAI_API_URL: str
    OPENAI_API_KEY: str

    # Models
    GENERATION_BACKEND: str
    GENERATION_MODEL_ID: str

    EMBEDDING_BACKEND: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int

    TOP_K_DOCS: int

    VECTOR_DB_BACKEND: str
    VECTOR_DB_DISTANCE_METHOD: str

    class Config:
        env_file = ".env"



def get_settings() -> Settings:
    return Settings()