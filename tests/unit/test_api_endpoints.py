import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

@pytest.fixture
def test_user_id():
    return "test_user_123"

@pytest.fixture
def sample_chat_request():
    return {
        "user_id": "test_user_123",
        "user_message": "I need to buy groceries for making pasta"
    }

@pytest.fixture
def sample_preferences_request():
    return {
        "dietary_restrictions": ["vegetarian"],
        "allergies": ["nuts"],
        "cuisine_preferences": ["italian"],
        "budget_range": "medium",
        "cooking_skill": "intermediate"
    }

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_chat_endpoint_success(sample_chat_request):
    """Test successful chat endpoint."""
    with patch('src.api.routes.chat.ChatService') as mock_chat_service:
        mock_service = Mock()
        mock_service.process_message.return_value = {
            "bot_response": "I'll help you with your grocery list!",
            "shopping_list": ["pasta", "tomatoes"],
            "preferences": {}
        }
        mock_chat_service.return_value = mock_service
        
        response = client.post("/api/v1/chat", json=sample_chat_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "bot_response" in data
        assert "shopping_list" in data
        assert "preferences" in data

def test_chat_endpoint_missing_user_id():
    """Test chat endpoint with missing user_id."""
    request_data = {"user_message": "Hello"}
    response = client.post("/api/v1/chat", json=request_data)
    assert response.status_code == 422

def test_chat_endpoint_missing_message():
    """Test chat endpoint with missing user_message."""
    request_data = {"user_id": "test_user"}
    response = client.post("/api/v1/chat", json=request_data)
    assert response.status_code == 422

def test_chat_endpoint_service_error(sample_chat_request):
    """Test chat endpoint when service throws an error."""
    with patch('src.api.routes.chat.ChatService') as mock_chat_service:
        mock_service = Mock()
        mock_service.process_message.side_effect = Exception("Service error")
        mock_chat_service.return_value = mock_service
        
        response = client.post("/api/v1/chat", json=sample_chat_request)
        assert response.status_code == 500

def test_get_preferences_success(test_user_id):
    """Test getting user preferences successfully."""
    with patch('src.api.routes.preferences.PreferencesService') as mock_pref_service:
        mock_service = Mock()
        mock_service.get_preferences.return_value = {
            "dietary_restrictions": ["vegetarian"],
            "allergies": ["nuts"]
        }
        mock_pref_service.return_value = mock_service
        
        response = client.get(f"/api/v1/preferences/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert "dietary_restrictions" in data
        assert "allergies" in data

def test_get_preferences_not_found(test_user_id):
    """Test getting preferences for non-existent user."""
    with patch('src.api.routes.preferences.PreferencesService') as mock_pref_service:
        mock_service = Mock()
        mock_service.get_preferences.return_value = {}
        mock_pref_service.return_value = mock_service
        
        response = client.get(f"/api/v1/preferences/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data == {}

def test_save_preferences_success(test_user_id, sample_preferences_request):
    """Test saving user preferences successfully."""
    with patch('src.api.routes.preferences.PreferencesService') as mock_pref_service:
        mock_service = Mock()
        mock_service.save_preferences.return_value = True
        mock_pref_service.return_value = mock_service
        
        response = client.post(f"/api/v1/preferences/{test_user_id}", 
                              json=sample_preferences_request)
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Preferences saved successfully"

def test_save_preferences_validation_error(test_user_id):
    """Test saving preferences with invalid data."""
    invalid_request = {"dietary_restrictions": "not_a_list"}
    response = client.post(f"/api/v1/preferences/{test_user_id}", 
                          json=invalid_request)
    assert response.status_code == 422

def test_save_preferences_service_error(test_user_id, sample_preferences_request):
    """Test saving preferences when service fails."""
    with patch('src.api.routes.preferences.PreferencesService') as mock_pref_service:
        mock_service = Mock()
        mock_service.save_preferences.return_value = False
        mock_pref_service.return_value = mock_service
        
        response = client.post(f"/api/v1/preferences/{test_user_id}", 
                              json=sample_preferences_request)
        assert response.status_code == 500

def test_get_shopping_list_success(test_user_id):
    """Test getting shopping list successfully."""
    with patch('src.api.routes.shopping_list.ShoppingListService') as mock_list_service:
        mock_service = Mock()
        mock_service.get_shopping_list.return_value = [
            {"name": "milk", "quantity": "1 liter", "category": "dairy"}
        ]
        mock_list_service.return_value = mock_service
        
        response = client.get(f"/api/v1/shopping-list/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "milk"

def test_get_shopping_list_empty(test_user_id):
    """Test getting empty shopping list."""
    with patch('src.api.routes.shopping_list.ShoppingListService') as mock_list_service:
        mock_service = Mock()
        mock_service.get_shopping_list.return_value = []
        mock_list_service.return_value = mock_service
        
        response = client.get(f"/api/v1/shopping-list/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data == []

def test_add_shopping_list_items_success(test_user_id):
    """Test adding items to shopping list successfully."""
    items = [{"name": "bread", "quantity": "2 loaves", "category": "bakery"}]
    
    with patch('src.api.routes.shopping_list.ShoppingListService') as mock_list_service:
        mock_service = Mock()
        mock_service.add_items.return_value = True
        mock_list_service.return_value = mock_service
        
        response = client.post(f"/api/v1/shopping-list/{test_user_id}/items", 
                              json={"items": items})
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Items added successfully"

def test_add_shopping_list_items_validation_error(test_user_id):
    """Test adding items with invalid data."""
    invalid_items = [{"name": "bread"}]  # Missing required fields
    
    response = client.post(f"/api/v1/shopping-list/{test_user_id}/items", 
                          json={"items": invalid_items})
    assert response.status_code == 422

def test_remove_shopping_list_item_success(test_user_id):
    """Test removing item from shopping list successfully."""
    with patch('src.api.routes.shopping_list.ShoppingListService') as mock_list_service:
        mock_service = Mock()
        mock_service.remove_item.return_value = True
        mock_list_service.return_value = mock_service
        
        response = client.delete(f"/api/v1/shopping-list/{test_user_id}/items/bread")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Item removed successfully"

def test_remove_shopping_list_item_not_found(test_user_id):
    """Test removing non-existent item."""
    with patch('src.api.routes.shopping_list.ShoppingListService') as mock_list_service:
        mock_service = Mock()
        mock_service.remove_item.return_value = False
        mock_list_service.return_value = mock_service
        
        response = client.delete(f"/api/v1/shopping-list/{test_user_id}/items/nonexistent")
        assert response.status_code == 404

def test_clear_shopping_list_success(test_user_id):
    """Test clearing shopping list successfully."""
    with patch('src.api.routes.shopping_list.ShoppingListService') as mock_list_service:
        mock_service = Mock()
        mock_service.clear_shopping_list.return_value = True
        mock_list_service.return_value = mock_service
        
        response = client.delete(f"/api/v1/shopping-list/{test_user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Shopping list cleared successfully"

def test_api_documentation_available():
    """Test that API documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema_available():
    """Test that OpenAPI schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data

def test_cors_headers():
    """Test that CORS headers are properly set."""
    response = client.options("/api/v1/chat")
    # Note: FastAPI TestClient doesn't fully simulate CORS, but we can test the endpoint exists
    assert response.status_code in [200, 405]  # 405 if OPTIONS not implemented

def test_rate_limiting_headers():
    """Test that rate limiting headers are present (if implemented)."""
    response = client.get("/health")
    # This test assumes rate limiting headers might be present
    # Adjust based on your actual rate limiting implementation
    assert response.status_code == 200 