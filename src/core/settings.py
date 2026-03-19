from pydantic_settings import BaseSettings
from typing import List

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
   
    # AUDIO FILES
    ALLOWED_AUDIO_MIME_TYPES: list
    ALLOWED_AUDIO_EXTENSIONS: list
    MAX_AUDIO_FILE_SIZE_BITS: int

    # TRANSCRIPT FILES
    ALLOWED_TEXT_MIME_TYPES: list
    ALLOWED_TEXT_EXTENSIONS: list
    MAX_TEXT_FILE_SIZE_BITS: int

    BITS_IN_MB: int
    
    class Config:
        env_file = ".env"

    # Tokens
    OPENAI_API_KEY : str
    LANGSMITH_API_KEY : str
    
    
    class Config:
        env_file = ".env"
        
        
get_settings  = Settings()