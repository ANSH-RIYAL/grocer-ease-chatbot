import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from datetime import datetime
import os
from pymongo import MongoClient

from src.api.main import app
from src.core.config import settings
from src.core.database import db

# Test database configuration
TEST_DB_NAME = f"{settings.DB_NAME}_test"

@pytest.fixture(scope="session")
def test_db() -> Generator:
    """Create a test database and clean it up after tests."""
    # Create a test database
    test_client = MongoClient(settings.MONGO_URI)
    test_db = test_client[TEST_DB_NAME]
    
    yield test_db
    
    # Clean up after tests
    test_client.drop_database(TEST_DB_NAME)
    test_client.close()

@pytest.fixture(scope="session")
def client(test_db) -> Generator:
    """Create a test client with the test database."""
    # Override the database connection
    def mock_get_db():
        return test_db
    
    app.dependency_overrides[db.get_db] = mock_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restore the original database connection
    app.dependency_overrides.clear()

@pytest.fixture
def test_user_id() -> str:
    """Generate a test user ID."""
    return f"test_user_{datetime.now().timestamp()}"

@pytest.fixture
def sample_chat_message(test_user_id) -> dict:
    """Create a sample chat message."""
    return {
        "user_id": test_user_id,
        "user_message": "I want to make pasta",
        "bot_response": "Here's a recipe for pasta...",
        "timestamp": datetime.utcnow()
    }

@pytest.fixture
def sample_shopping_list(test_user_id) -> dict:
    """Create a sample shopping list."""
    return {
        "user_id": test_user_id,
        "items": ["pasta", "tomato sauce", "cheese"],
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_ai_response():
    """Create a mock AI response."""
    return {
        "recipe": {
            "name": "Simple Pasta",
            "ingredients": ["pasta", "tomato sauce", "cheese"],
            "instructions": ["Boil pasta", "Add sauce", "Top with cheese"]
        }
    }

@pytest.fixture
def mock_chat_history(test_user_id) -> list:
    """Create a mock chat history."""
    return [
        {
            "user_id": test_user_id,
            "user_message": "How do I make pasta?",
            "bot_response": "Here's a recipe for pasta...",
            "timestamp": datetime.utcnow()
        },
        {
            "user_id": test_user_id,
            "user_message": "What ingredients do I need?",
            "bot_response": "You'll need pasta, tomato sauce, and cheese.",
            "timestamp": datetime.utcnow()
        }
    ]

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["TESTING"] = "true"
    yield
    os.environ.pop("TESTING", None)

@pytest.fixture(scope="function")
def test_user_preferences() -> Dict[str, str]:
    """Provide test user preferences."""
    return {
        "vegetarian": "yes",
        "gluten_free": "no",
        "dairy_free": "not_set"
    }

@pytest.fixture(scope="function")
def setup_test_data(test_db, test_user_id, test_user_preferences):
    """Set up test data in the database."""
    # Clear existing data
    test_db.preferences.delete_many({})
    test_db.chat_history.delete_many({})
    test_db.shopping_lists.delete_many({})
    
    # Insert test preferences
    test_db.preferences.insert_one({
        "user_id": test_user_id,
        "preferences": test_user_preferences
    })
    
    yield
    
    # Cleanup after test
    test_db.preferences.delete_many({})
    test_db.chat_history.delete_many({})
    test_db.shopping_lists.delete_many({})

@pytest.fixture(scope="function")
def mock_ai_service(monkeypatch):
    """Mock AI service responses."""
    def mock_generate_response(*args, **kwargs):
        return "This is a mock response"
    
    def mock_categorize_message(*args, **kwargs):
        return "general"
    
    def mock_extract_ingredients(*args, **kwargs):
        return ["milk", "eggs"]
    
    monkeypatch.setattr("src.services.ai_service.AIService.generate_response", mock_generate_response)
    monkeypatch.setattr("src.services.ai_service.AIService.categorize_message", mock_categorize_message)
    monkeypatch.setattr("src.services.ai_service.AIService.extract_ingredients", mock_extract_ingredients)

@pytest.fixture(scope="function")
def mock_database_connection(monkeypatch, test_db):
    """Mock database connection."""
    def mock_get_db():
        return test_db
    
    monkeypatch.setattr("src.core.database.get_database", mock_get_db) 