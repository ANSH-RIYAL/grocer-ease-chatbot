import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from src.services.user_preferences import UserPreferences

@pytest.fixture
def preferences_service(test_db):
    service = UserPreferences()
    service.collection = test_db['user_preferences']
    return service

@pytest.fixture
def sample_preferences():
    return {
        "vegetarian": "yes"
    }

def test_set_preference(preferences_service, test_user_id):
    """Test setting a user preference."""
    result = preferences_service.set_preference(test_user_id, "vegetarian", "yes")
    assert result is True
    
    # Verify preference was set
    value = preferences_service.get_preference(test_user_id, "vegetarian")
    assert value == "yes"

def test_get_preference_nonexistent(preferences_service, test_user_id):
    """Test getting preference for user that doesn't exist."""
    value = preferences_service.get_preference(test_user_id, "vegetarian")
    assert value == "not_set"

def test_get_all_preferences(preferences_service, test_user_id, sample_preferences):
    """Test getting all preferences for a user."""
    # Set a preference first
    preferences_service.set_preference(test_user_id, "vegetarian", "yes")
    
    # Get all preferences
    prefs = preferences_service.get_all_preferences(test_user_id)
    assert prefs["vegetarian"] == "yes"

def test_get_all_preferences_empty(preferences_service, test_user_id):
    """Test getting preferences for user with no preferences."""
    prefs = preferences_service.get_all_preferences(test_user_id)
    assert prefs == {}

def test_clear_preferences(preferences_service, test_user_id):
    """Test clearing user preferences."""
    # Set a preference first
    preferences_service.set_preference(test_user_id, "vegetarian", "yes")
    
    # Clear preferences
    result = preferences_service.clear_preferences(test_user_id)
    assert result is True
    
    # Verify preferences were cleared
    prefs = preferences_service.get_all_preferences(test_user_id)
    assert prefs == {}

def test_clear_nonexistent_preferences(preferences_service, test_user_id):
    """Test clearing preferences for user that doesn't exist."""
    result = preferences_service.clear_preferences(test_user_id)
    assert result is False

def test_invalid_preference(preferences_service, test_user_id):
    """Test setting an invalid preference."""
    result = preferences_service.set_preference(test_user_id, "invalid_pref", "yes")
    assert result is False

def test_invalid_value(preferences_service, test_user_id):
    """Test setting an invalid value for a preference."""
    result = preferences_service.set_preference(test_user_id, "vegetarian", "invalid_value")
    assert result is False

def test_error_handling_set_preference(preferences_service, test_user_id):
    """Test error handling when setting preference."""
    with patch.object(preferences_service.collection, 'update_one') as mock_update:
        mock_update.side_effect = Exception("Database error")
        result = preferences_service.set_preference(test_user_id, "vegetarian", "yes")
        assert result is False

def test_error_handling_get_preference(preferences_service, test_user_id):
    """Test error handling when getting preference."""
    with patch.object(preferences_service.collection, 'find_one') as mock_find:
        mock_find.side_effect = Exception("Database error")
        value = preferences_service.get_preference(test_user_id, "vegetarian")
        assert value == "not_set"

def test_error_handling_get_all_preferences(preferences_service, test_user_id):
    """Test error handling when getting all preferences."""
    with patch.object(preferences_service.collection, 'find_one') as mock_find:
        mock_find.side_effect = Exception("Database error")
        prefs = preferences_service.get_all_preferences(test_user_id)
        assert prefs == {}

def test_error_handling_clear_preferences(preferences_service, test_user_id):
    """Test error handling when clearing preferences."""
    with patch.object(preferences_service.collection, 'delete_one') as mock_delete:
        mock_delete.side_effect = Exception("Database error")
        result = preferences_service.clear_preferences(test_user_id)
        assert result is False 