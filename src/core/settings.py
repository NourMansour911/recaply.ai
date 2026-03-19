from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    
    # Configs
    APP_NAME : str
    APP_VERSION : str

    # Paths
    FILES_PATH :str
    DATABASES_PATH :str
    VDB_PATH:str
    
    # Database
    MONGODB_URL: str
    MONGODB_DATABASE: str
    
    # Max file sizes
    MAX_AUDIO_SIZE_MB: int
    MAX_TEXT_SIZE_MB: int 
    MAX_SUBTITLE_SIZE_MB: int
    MAX_PDF_SIZE_MB: int
    
    TO_BYTES: int

    
    class Config:
        env_file = ".env"

    # Tokens
    OPENAI_API_KEY : str
    LANGSMITH_API_KEY : str
    
    
    class Config:
        env_file = ".env"



def get_settings() -> Settings:
    return Settings()