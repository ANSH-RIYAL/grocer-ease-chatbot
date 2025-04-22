from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GrocerEase Chatbot"
    
    # MongoDB Settings
    MONGO_URI: str
    DB_NAME: str = "chatbot_db"
    
    # AI Model Settings
    GEMINI_API_KEY: str
    GEMINI_MODEL_NAME: str = "gemini-1.5-pro"
    CLASSIFIER_TYPE: str = "bart"  # Options: "bart" or "gemini"
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"
    
    # Security Settings
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 