import pytest
from src.core.config import settings
from src.services.shopping_list_service import ShoppingListService

def test_shopping_list_service_initialization():
    """Test that the shopping list service can be initialized."""
    service = ShoppingListService()
    assert service is not None

def test_config_loading():
    """Test that configuration can be loaded."""
    assert settings.DB_NAME == "chatbot_db"
    assert settings.MONGO_URI is not None

def test_service_attributes():
    """Test that the service has the expected attributes."""
    service = ShoppingListService()
    assert hasattr(service, 'collection')
    assert hasattr(service, 'add_items')
    assert hasattr(service, 'get_shopping_list')