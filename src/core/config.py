from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "GrocerEase Chatbot"
    
    # MongoDB Settings
    MONGO_URI: str = "mongodb://localhost:27017"  # Default for testing
    DB_NAME: str = "chatbot_db"
    
    # AI Model Settings
    GEMINI_API_KEY: str = "AIzaSyDat8ktS_PQSuNi8G0KCBMNRufD1Uy8Jqg"  # Default for testing
    GEMINI_MODEL_NAME: str = "gemini-1.5-pro"  # Upgraded for better reasoning
    CLASSIFIER_TYPE: str = "gemini"  # Options: "bart" or "gemini"
    
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