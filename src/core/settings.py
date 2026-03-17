from pydantic_settings import BaseSettings

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


    # Tokens
    OPENAI_API_KEY : str
    LANGSMITH_API_KEY : str
    
    
    class Config:
        env_file = ".env"
        
        
settings  = Settings()