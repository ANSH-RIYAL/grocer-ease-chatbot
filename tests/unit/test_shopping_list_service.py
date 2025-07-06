import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from src.services.shopping_list_service import ShoppingListService

@pytest.fixture
def shopping_list_service(test_db):
    service = ShoppingListService()
    service.collection = test_db['shopping_lists']
    return service

@pytest.fixture
def sample_items():
    return [
        {"name": "milk", "quantity": "1 liter", "category": "dairy"},
        {"name": "bread", "quantity": "2 loaves", "category": "bakery"},
        {"name": "tomatoes", "quantity": "500g", "category": "vegetables"}
    ]

def test_add_items(shopping_list_service, test_user_id, sample_items):
    """Test adding items to shopping list."""
    # Add items
    result = shopping_list_service.add_items(test_user_id, sample_items)
    assert result is True
    
    # Verify items were added
    items = shopping_list_service.get_shopping_list(test_user_id)
    assert len(items) == 3
    assert any(item['name'] == 'milk' for item in items)
    assert any(item['name'] == 'bread' for item in items)
    assert any(item['name'] == 'tomatoes' for item in items)

def test_add_duplicate_items(shopping_list_service, test_user_id):
    """Test adding duplicate items."""
    items = [{"name": "milk", "quantity": "1 liter", "category": "dairy"}]
    
    # Add same item twice
    shopping_list_service.add_items(test_user_id, items)
    shopping_list_service.add_items(test_user_id, items)
    
    # Should only have one instance
    result_items = shopping_list_service.get_shopping_list(test_user_id)
    assert len(result_items) == 1
    assert result_items[0]['name'] == 'milk'

def test_remove_item(shopping_list_service, test_user_id, sample_items):
    """Test removing items from shopping list."""
    # Add items first
    shopping_list_service.add_items(test_user_id, sample_items)
    
    # Remove one item
    result = shopping_list_service.remove_item(test_user_id, "milk")
    assert result is True
    
    # Verify item was removed
    items = shopping_list_service.get_shopping_list(test_user_id)
    assert len(items) == 2
    assert not any(item['name'] == 'milk' for item in items)

def test_remove_nonexistent_item(shopping_list_service, test_user_id):
    """Test removing an item that doesn't exist."""
    result = shopping_list_service.remove_item(test_user_id, "nonexistent")
    assert result is False

def test_get_shopping_list_empty(shopping_list_service, test_user_id):
    """Test getting empty shopping list."""
    items = shopping_list_service.get_shopping_list(test_user_id)
    assert items == []

def test_get_shopping_list_with_items(shopping_list_service, test_user_id, sample_items):
    """Test getting shopping list with items."""
    shopping_list_service.add_items(test_user_id, sample_items)
    items = shopping_list_service.get_shopping_list(test_user_id)
    
    assert len(items) == 3
    for item in items:
        assert 'name' in item
        assert 'quantity' in item
        assert 'category' in item
        assert 'added_at' in item

def test_clear_shopping_list(shopping_list_service, test_user_id, sample_items):
    """Test clearing entire shopping list."""
    # Add items first
    shopping_list_service.add_items(test_user_id, sample_items)
    
    # Clear list
    result = shopping_list_service.clear_shopping_list(test_user_id)
    assert result is True
    
    # Verify list is empty
    items = shopping_list_service.get_shopping_list(test_user_id)
    assert items == []

def test_update_item_quantity(shopping_list_service, test_user_id):
    """Test updating item quantity."""
    items = [{"name": "milk", "quantity": "1 liter", "category": "dairy"}]
    shopping_list_service.add_items(test_user_id, items)
    
    # Update quantity
    result = shopping_list_service.update_item_quantity(test_user_id, "milk", "2 liters")
    assert result is True
    
    # Verify quantity was updated
    items = shopping_list_service.get_shopping_list(test_user_id)
    assert items[0]['quantity'] == "2 liters"

def test_update_nonexistent_item_quantity(shopping_list_service, test_user_id):
    """Test updating quantity of nonexistent item."""
    result = shopping_list_service.update_item_quantity(test_user_id, "nonexistent", "1 liter")
    assert result is False

def test_mark_item_completed(shopping_list_service, test_user_id):
    """Test marking item as completed."""
    items = [{"name": "milk", "quantity": "1 liter", "category": "dairy"}]
    shopping_list_service.add_items(test_user_id, items)
    
    # Mark as completed
    result = shopping_list_service.mark_item_completed(test_user_id, "milk")
    assert result is True
    
    # Verify item is marked as completed
    items = shopping_list_service.get_shopping_list(test_user_id)
    assert items[0]['completed'] is True
    assert 'completed_at' in items[0]

def test_error_handling_add_items(shopping_list_service, test_user_id):
    """Test error handling when adding items."""
    with patch.object(shopping_list_service.collection, 'update_one') as mock_update:
        mock_update.side_effect = Exception("Database error")
        result = shopping_list_service.add_items(test_user_id, [{"name": "test"}])
        assert result is False

def test_error_handling_get_shopping_list(shopping_list_service, test_user_id):
    """Test error handling when getting shopping list."""
    with patch.object(shopping_list_service.collection, 'find') as mock_find:
        mock_find.side_effect = Exception("Database error")
        items = shopping_list_service.get_shopping_list(test_user_id)
        assert items == []

def test_error_handling_remove_item(shopping_list_service, test_user_id):
    """Test error handling when removing item."""
    with patch.object(shopping_list_service.collection, 'update_one') as mock_update:
        mock_update.side_effect = Exception("Database error")
        result = shopping_list_service.remove_item(test_user_id, "test")
        assert result is False

def test_item_validation(shopping_list_service, test_user_id):
    """Test item validation."""
    # Test with invalid item (missing required fields)
    invalid_items = [{"name": "test"}]  # Missing quantity and category
    result = shopping_list_service.add_items(test_user_id, invalid_items)
    assert result is False
    
    # Test with valid item
    valid_items = [{"name": "test", "quantity": "1", "category": "test"}]
    result = shopping_list_service.add_items(test_user_id, valid_items)
    assert result is True 