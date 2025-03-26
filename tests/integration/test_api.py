import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.api.main import app
from src.models.chat import ChatRequest, ChatResponse
from src.models.shopping_list import ShoppingList

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_chat_endpoint(client, test_user_id, mock_ai_response):
    """Test the chat endpoint with different types of messages."""
    with patch('src.services.ai_service.AIService.categorize_message') as mock_categorize, \
         patch('src.services.ai_service.AIService.generate_response') as mock_generate, \
         patch('src.services.ai_service.AIService.extract_ingredients') as mock_extract, \
         patch('src.services.shopping_list_service.ShoppingListService.add_items') as mock_add_items, \
         patch('src.services.shopping_list_service.ShoppingListService.get_shopping_list') as mock_get_list:
        
        # Setup mocks
        mock_categorize.return_value = "Recipe type"
        mock_generate.return_value = "Here's a recipe..."
        mock_extract.return_value = ["pasta", "tomato"]
        mock_add_items.return_value = True
        mock_get_list.return_value = ["pasta", "tomato", "milk"]
        
        # Test recipe request
        recipe_request = ChatRequest(
            user_id=test_user_id,
            user_message="How do I make pasta?"
        )
        response = client.post("/api/v1/chat", json=recipe_request.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert "bot_response" in data
        assert "shopping_list" in data
        assert isinstance(data["shopping_list"], list)
        
        # Test item addition request
        add_item_request = ChatRequest(
            user_id=test_user_id,
            user_message="Add milk to my list"
        )
        response = client.post("/api/v1/chat", json=add_item_request.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert "milk" in data["shopping_list"]
        
        # Test invalid request
        invalid_request = {"user_id": test_user_id}  # Missing user_message
        response = client.post("/api/v1/chat", json=invalid_request)
        assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_chat_history_persistence(client, test_user_id, mock_ai_response):
    """Test that chat history is properly persisted."""
    with patch('src.services.ai_service.AIService.categorize_message') as mock_categorize, \
         patch('src.services.ai_service.AIService.generate_response') as mock_generate, \
         patch('src.services.ai_service.AIService.extract_ingredients') as mock_extract, \
         patch('src.services.shopping_list_service.ShoppingListService.add_items') as mock_add_items, \
         patch('src.services.shopping_list_service.ShoppingListService.get_shopping_list') as mock_get_list:
        
        # Setup mocks
        mock_categorize.return_value = "Recipe type"
        mock_generate.return_value = "Here's a recipe..."
        mock_extract.return_value = ["pasta", "tomato"]
        mock_add_items.return_value = True
        mock_get_list.return_value = ["pasta", "tomato"]
        
        # Send multiple messages
        messages = [
            "How do I make pasta?",
            "What ingredients do I need?",
            "Add tomato to my list"
        ]
        
        for message in messages:
            response = client.post(
                "/api/v1/chat",
                json=ChatRequest(user_id=test_user_id, user_message=message).model_dump()
            )
            assert response.status_code == 200
        
        # Verify shopping list contains ingredients from all messages
        response = client.post(
            "/api/v1/chat",
            json=ChatRequest(user_id=test_user_id, user_message="Show my shopping list").model_dump()
        )
        assert response.status_code == 200
        data = response.json()
        assert "pasta" in data["shopping_list"]
        assert "tomato" in data["shopping_list"]

def test_error_handling(client):
    """Test API error handling."""
    # Test with invalid user_id
    response = client.post(
        "/api/v1/chat",
        json=ChatRequest(user_id="", user_message="Hello").model_dump()
    )
    assert response.status_code == 422  # Validation error
    
    # Test with invalid request body
    response = client.post("/api/v1/chat", json={})
    assert response.status_code == 422
    
    # Test with non-JSON body
    response = client.post("/api/v1/chat", data="not json")
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_concurrent_requests(client, test_user_id, mock_ai_response):
    """Test handling of concurrent requests."""
    import concurrent.futures
    
    with patch('src.services.ai_service.AIService.categorize_message') as mock_categorize, \
         patch('src.services.ai_service.AIService.generate_response') as mock_generate, \
         patch('src.services.ai_service.AIService.extract_ingredients') as mock_extract, \
         patch('src.services.shopping_list_service.ShoppingListService.add_items') as mock_add_items, \
         patch('src.services.shopping_list_service.ShoppingListService.get_shopping_list') as mock_get_list:
        
        # Setup mocks
        mock_categorize.return_value = "Item Addition type"
        mock_generate.return_value = "Added to your list"
        mock_extract.return_value = ["milk", "bread", "eggs", "cheese", "butter"]
        mock_add_items.return_value = True
        mock_get_list.return_value = ["milk", "bread", "eggs", "cheese", "butter"]
        
        def send_request(message):
            return client.post(
                "/api/v1/chat",
                json=ChatRequest(user_id=test_user_id, user_message=message).model_dump()
            )
        
        messages = [
            "Add milk",
            "Add bread",
            "Add eggs",
            "Add cheese",
            "Add butter"
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            responses = list(executor.map(send_request, messages))
        
        # Verify all requests were successful
        assert all(r.status_code == 200 for r in responses)
        
        # Verify shopping list contains all items
        response = client.post(
            "/api/v1/chat",
            json=ChatRequest(user_id=test_user_id, user_message="Show my list").model_dump()
        )
        assert response.status_code == 200
        data = response.json()
        shopping_list = data["shopping_list"]
        assert all(item in shopping_list for item in ["milk", "bread", "eggs", "cheese", "butter"]) 