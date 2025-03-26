import pytest
from unittest.mock import Mock, patch
from src.services.ai_service import AIService

@pytest.fixture
def ai_service():
    return AIService()

def test_categorize_message(ai_service):
    """Test message categorization."""
    with patch.object(ai_service, 'generate_response') as mock_generate:
        # Test recipe type
        mock_generate.return_value = "Recipe type"
        assert ai_service.categorize_message("How do I make pasta?") == "Recipe type"
        
        # Test item addition type
        mock_generate.return_value = "Item Addition type"
        assert ai_service.categorize_message("Add milk to my list") == "Item Addition type"
        
        # Test invalid category
        mock_generate.return_value = "Invalid Category"
        assert ai_service.categorize_message("Some message") == "Others"

def test_extract_ingredients(ai_service):
    """Test ingredient extraction from chat history."""
    chat_history = [
        {"role": "user", "message": "I want to make pasta with tomatoes"},
        {"role": "assistant", "message": "You'll need pasta, tomatoes, and garlic"}
    ]
    
    with patch.object(ai_service, 'generate_response') as mock_generate:
        mock_generate.return_value = '["pasta", "tomatoes", "garlic"]'
        ingredients = ai_service.extract_ingredients(chat_history)
        assert set(ingredients) == {"pasta", "tomatoes", "garlic"}
        
        # Test error handling
        mock_generate.side_effect = Exception("API Error")
        ingredients = ai_service.extract_ingredients(chat_history)
        assert ingredients == []

def test_generate_response(ai_service):
    """Test response generation."""
    with patch.object(ai_service.model, 'generate_content') as mock_generate:
        mock_generate.return_value = Mock(text="Test response")
        response = ai_service.generate_response("Test prompt")
        assert response == "Test response"
        
        # Test error handling
        mock_generate.side_effect = Exception("API Error")
        with pytest.raises(Exception):
            ai_service.generate_response("Test prompt") 