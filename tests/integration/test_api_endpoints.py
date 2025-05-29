import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any
import json
from src.api.main import app
from src.core.config import settings

client = TestClient(app)

# Test Data
TEST_USER_ID = "test_user_123"
TEST_MESSAGE = "How do I make pasta?"
TEST_PREFERENCE = "vegetarian"
TEST_VALUE = "yes"

@pytest.fixture
def test_user_preferences() -> Dict[str, str]:
    """Fixture to provide test user preferences."""
    return {
        "vegetarian": "yes",
        "gluten_free": "no",
        "dairy_free": "not_set"
    }

@pytest.fixture
def test_chat_request() -> Dict[str, str]:
    """Fixture to provide test chat request data."""
    return {
        "user_id": TEST_USER_ID,
        "user_message": TEST_MESSAGE
    }

@pytest.fixture
def test_preference_request() -> Dict[str, str]:
    """Fixture to provide test preference request data."""
    return {
        "user_id": TEST_USER_ID,
        "preference": TEST_PREFERENCE,
        "value": TEST_VALUE
    }

class TestHealthCheck:
    def test_health_check_success(self):
        """Test health check endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

class TestChatAPI:
    def test_chat_success(self, test_chat_request, test_user_preferences):
        """Test successful chat request processing."""
        response = client.post(
            f"{settings.API_V1_STR}/chat",
            json=test_chat_request
        )
        assert response.status_code == 200
        data = response.json()
        assert "bot_response" in data
        assert "shopping_list" in data
        assert isinstance(data["shopping_list"], list)
        assert "preferences" in data

    def test_chat_invalid_user_id(self):
        """Test chat request with invalid user ID."""
        response = client.post(
            f"{settings.API_V1_STR}/chat",
            json={"user_id": "", "user_message": TEST_MESSAGE}
        )
        assert response.status_code == 400

    def test_chat_invalid_message(self):
        """Test chat request with invalid message."""
        response = client.post(
            f"{settings.API_V1_STR}/chat",
            json={"user_id": TEST_USER_ID, "user_message": ""}
        )
        assert response.status_code == 400

    def test_chat_missing_fields(self):
        """Test chat request with missing required fields."""
        response = client.post(
            f"{settings.API_V1_STR}/chat",
            json={"user_id": TEST_USER_ID}
        )
        assert response.status_code == 400

class TestUserPreferencesAPI:
    def test_get_preferences_success(self, test_user_preferences):
        """Test successful retrieval of user preferences."""
        response = client.get(f"{settings.API_V1_STR}/preferences/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert all(isinstance(v, str) for v in data.values())

    def test_get_preferences_invalid_user(self):
        """Test getting preferences for invalid user ID."""
        response = client.get(f"{settings.API_V1_STR}/preferences/")
        assert response.status_code == 404

    def test_set_preference_success(self, test_preference_request):
        """Test successful setting of user preference."""
        response = client.post(
            f"{settings.API_V1_STR}/preferences",
            json=test_preference_request
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_set_preference_invalid_data(self):
        """Test setting preference with invalid data."""
        response = client.post(
            f"{settings.API_V1_STR}/preferences",
            json={"user_id": TEST_USER_ID}
        )
        assert response.status_code == 400

    def test_clear_preferences_success(self):
        """Test successful clearing of user preferences."""
        response = client.delete(f"{settings.API_V1_STR}/preferences/{TEST_USER_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_clear_preferences_invalid_user(self):
        """Test clearing preferences for invalid user ID."""
        response = client.delete(f"{settings.API_V1_STR}/preferences/")
        assert response.status_code == 404

class TestChatMessageTypes:
    @pytest.mark.parametrize("message,expected_type", [
        ("How do I make pasta?", "recipe"),
        ("Add milk to my shopping list", "shopping"),
        ("What's the price of tomatoes?", "item_info"),
        ("Hello, how are you?", "general")
    ])
    def test_different_message_types(self, message, expected_type):
        """Test different types of chat messages."""
        response = client.post(
            f"{settings.API_V1_STR}/chat",
            json={"user_id": TEST_USER_ID, "user_message": message}
        )
        assert response.status_code == 200
        data = response.json()
        assert "bot_response" in data
        # Note: Actual type checking would require analyzing the response content

class TestErrorHandling:
    def test_database_error(self, monkeypatch):
        """Test handling of database errors."""
        def mock_db_error(*args, **kwargs):
            raise Exception("Database error")
        
        monkeypatch.setattr("src.services.user_preferences.user_preferences.get_all_preferences", mock_db_error)
        
        response = client.get(f"{settings.API_V1_STR}/preferences/{TEST_USER_ID}")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

    def test_ai_service_error(self, monkeypatch):
        """Test handling of AI service errors."""
        def mock_ai_error(*args, **kwargs):
            raise Exception("AI service error")
        
        monkeypatch.setattr("src.services.chat_service.chat_service.process_message", mock_ai_error)
        
        response = client.post(
            f"{settings.API_V1_STR}/chat",
            json={"user_id": TEST_USER_ID, "user_message": TEST_MESSAGE}
        )
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]

class TestShoppingListIntegration:
    def test_shopping_list_updates(self):
        """Test shopping list updates through chat."""
        # First message to add items
        response1 = client.post(
            f"{settings.API_V1_STR}/chat",
            json={"user_id": TEST_USER_ID, "user_message": "Add milk and eggs to my shopping list"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        assert "milk" in [item.lower() for item in data1["shopping_list"]]
        assert "eggs" in [item.lower() for item in data1["shopping_list"]]

        # Second message to remove items
        response2 = client.post(
            f"{settings.API_V1_STR}/chat",
            json={"user_id": TEST_USER_ID, "user_message": "Remove milk from my shopping list"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert "milk" not in [item.lower() for item in data2["shopping_list"]]
        assert "eggs" in [item.lower() for item in data2["shopping_list"]]

class TestUserPreferencesIntegration:
    def test_preferences_affect_responses(self):
        """Test that user preferences affect chat responses."""
        # Set vegetarian preference
        client.post(
            f"{settings.API_V1_STR}/preferences",
            json={"user_id": TEST_USER_ID, "preference": "vegetarian", "value": "yes"}
        )

        # Ask for a recipe
        response = client.post(
            f"{settings.API_V1_STR}/chat",
            json={"user_id": TEST_USER_ID, "user_message": "Give me a recipe for dinner"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "vegetarian" in data["bot_response"].lower() or "meat" not in data["bot_response"].lower()

class TestPerformance:
    def test_response_time(self):
        """Test API response time."""
        import time
        start_time = time.time()
        
        response = client.post(
            f"{settings.API_V1_STR}/chat",
            json={"user_id": TEST_USER_ID, "user_message": TEST_MESSAGE}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Response should be under 2 seconds 