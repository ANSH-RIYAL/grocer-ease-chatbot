import pytest
from typing import Generator
from fastapi.testclient import TestClient
from pymongo import MongoClient
from datetime import datetime
import os

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
    db._client = test_db.client
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restore the original database connection
    db._client = None

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