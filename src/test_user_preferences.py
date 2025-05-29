import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import settings
from src.services.user_preferences import UserPreferences


def test_user_preferences():
    print("Initializing UserPreferences...")
    prefs = UserPreferences()
    
    # Test user ID
    user_id = "test_user_1"
    
    print("\n1. Testing preference setting...")
    # Test setting valid preference
    print("Setting vegetarian preference to 'yes'...")
    result = prefs.set_preference(user_id, "vegetarian", "yes")
    print(f"Result: {'Success' if result else 'Failed'}")
    
    # Get the preference
    user_prefs = prefs.get_all_preferences(user_id)
    print(f"Current preferences: {user_prefs}")
    
    print("\n2. Testing invalid preference...")
    # Test setting invalid preference
    print("Setting invalid preference 'invalid_pref'...")
    result = prefs.set_preference(user_id, "invalid_pref", "yes")
    print(f"Result: {'Success' if result else 'Failed'}")
    
    print("\n3. Testing invalid value...")
    # Test setting invalid value
    print("Setting vegetarian preference to 'invalid_value'...")
    result = prefs.set_preference(user_id, "vegetarian", "invalid_value")
    print(f"Result: {'Success' if result else 'Failed'}")
    
    print("\n4. Testing get specific preference...")
    # Test getting specific preference
    pref_value = prefs.get_preference(user_id, "vegetarian")
    print(f"Vegetarian preference value: {pref_value}")
    
    print("\n5. Testing get non-existent preference...")
    # Test getting non-existent preference
    pref_value = prefs.get_preference(user_id, "non_existent")
    print(f"Non-existent preference value: {pref_value}")
    
    print("\n6. Testing clear preferences...")
    result = prefs.clear_preferences(user_id)
    print(f"Clear preferences result: {'Success' if result else 'Failed'}")
    
    # Verify preferences are cleared
    all_prefs = prefs.get_all_preferences(user_id)
    print(f"Preferences after clearing: {all_prefs}")

if __name__ == "__main__":
    try:
        test_user_preferences()
    except Exception as e:
        print(f"An error occurred: {str(e)}") 