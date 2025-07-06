import pytest
from src.core.config import settings
from src.services.chat_service import ChatService
from src.services.ai_service import AIService

def test_chatbot_initialization():
    """Test that the chatbot can be initialized."""
    # Test that settings can be loaded
    assert settings.PROJECT_NAME == "GrocerEase Chatbot"
    assert settings.API_V1_STR == "/api/v1"
    
    # Test that services can be initialized
    chat_service = ChatService()
    ai_service = AIService()
    
    assert chat_service is not None
    assert ai_service is not None

def test_config_settings():
    """Test that configuration settings are properly loaded."""
    assert hasattr(settings, 'DB_NAME')
    assert hasattr(settings, 'MONGO_URI')
    assert hasattr(settings, 'GEMINI_API_KEY')
    assert hasattr(settings, 'GEMINI_MODEL_NAME')