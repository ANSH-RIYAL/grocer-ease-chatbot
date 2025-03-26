import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from src.services.chat_service import ChatService
from src.services.ai_service import AIService
from src.services.shopping_list_service import ShoppingListService

@pytest.fixture
def chat_service(test_db):
    service = ChatService()
    service.collection = test_db['chat_history']
    return service

def test_store_message(chat_service, test_user_id):
    """Test storing chat messages."""
    user_message = "Hello"
    bot_response = "Hi there!"
    
    assert chat_service.store_message(test_user_id, user_message, bot_response)
    
    # Verify message was stored
    messages = chat_service.get_chat_history(test_user_id)
    assert len(messages) == 2  # One user message, one bot response
    assert messages[0]['message'] == user_message
    assert messages[1]['message'] == bot_response

def test_get_chat_history(chat_service, test_user_id):
    """Test retrieving chat history."""
    # Store multiple messages
    messages = [
        ("Hello", "Hi there!"),
        ("How are you?", "I'm good, thanks!"),
        ("What's the weather?", "It's sunny!")
    ]
    
    for user_msg, bot_msg in messages:
        chat_service.store_message(test_user_id, user_msg, bot_msg)
    
    # Get history
    history = chat_service.get_chat_history(test_user_id)
    assert len(history) == len(messages) * 2  # Each message has user and bot response
    
    # Verify order (most recent first)
    assert history[-2]['message'] == messages[-1][0]  # Last user message
    assert history[-1]['message'] == messages[-1][1]  # Last bot response

def test_process_message(chat_service, test_user_id):
    """Test processing a new message."""
    with patch.object(AIService, 'categorize_message') as mock_categorize, \
         patch.object(AIService, 'generate_response') as mock_generate, \
         patch.object(AIService, 'extract_ingredients') as mock_extract, \
         patch.object(ShoppingListService, 'add_items') as mock_add_items, \
         patch.object(ShoppingListService, 'get_shopping_list') as mock_get_list:
        
        # Setup mocks
        mock_categorize.return_value = "Recipe type"
        mock_generate.return_value = "Here's a recipe..."
        mock_extract.return_value = ["pasta", "tomato"]
        mock_add_items.return_value = True
        mock_get_list.return_value = ["pasta", "tomato"]
        
        # Process message
        response = chat_service.process_message(test_user_id, "How do I make pasta?")
        
        # Verify response
        assert response['bot_response'] == "Here's a recipe..."
        assert response['shopping_list'] == ["pasta", "tomato"]
        
        # Verify message was stored
        history = chat_service.get_chat_history(test_user_id)
        assert len(history) == 2  # One user message, one bot response

def test_error_handling(chat_service, test_user_id):
    """Test error handling in chat operations."""
    # Test database error in store_message
    with patch.object(chat_service.collection, 'insert_one') as mock_insert:
        mock_insert.side_effect = Exception("Database error")
        assert not chat_service.store_message(test_user_id, "Hello", "Hi")
    
    # Test database error in get_chat_history
    with patch.object(chat_service.collection, 'find') as mock_find:
        mock_find.side_effect = Exception("Database error")
        assert chat_service.get_chat_history(test_user_id) == []
    
    # Test AI service error in process_message
    with patch.object(AIService, 'categorize_message') as mock_categorize:
        mock_categorize.side_effect = Exception("AI service error")
        response = chat_service.process_message(test_user_id, "Hello")
        assert "error" in response['bot_response'].lower()
        assert response['shopping_list'] == [] 