import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the settings module
import unittest.mock
mock_settings = unittest.mock.MagicMock()
mock_settings.MONGO_URI = "mongodb://localhost:27017"
mock_settings.GEMINI_API_KEY = "dummy_key"
mock_settings.PREFERENCE_MODEL_TYPE = "bart"
mock_settings.GEMINI_MODEL_NAME = "gemini-1.5-pro"
mock_settings.LOG_LEVEL = "INFO"
mock_settings.LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Patch the settings before importing UserPreferences
with unittest.mock.patch('src.core.config.settings', mock_settings):
    with unittest.mock.patch('src.core.logging.settings', mock_settings):
        from src.services.user_preferences import UserPreferences
        import time

        def test_user_preferences():
            print("Initializing UserPreferences with BART model...")
            prefs = UserPreferences(model_type="bart")
            
            # Test user ID
            user_id = "test_user_1"
            
            print("\n1. Testing static preference setting...")
            # Test setting valid preference
            print("Setting vegetarian preference to 'yes'...")
            result = prefs.set_static_preference(user_id, "vegetarian", "yes")
            print(f"Result: {'Success' if result else 'Failed'}")
            
            # Get the preference
            user_prefs = prefs.get_static_preferences(user_id)
            print(f"Current preferences: {user_prefs}")
            
            print("\n2. Testing preference extraction from messages...")
            test_messages = [
                "I am a vegetarian and I don't eat meat",
                "I eat everything including meat",
                "I prefer vegetarian food but sometimes eat fish",
            ]
            
            for message in test_messages:
                print(f"\nAnalyzing message: '{message}'")
                extracted_prefs = prefs.extract_preferences_from_message(user_id, message)
                print(f"Extracted preferences: {extracted_prefs}")
                time.sleep(1)  # Small delay to avoid overwhelming the model
            
            print("\n3. Testing get all preferences...")
            all_prefs = prefs.get_all_preferences(user_id)
            print(f"All preferences: {all_prefs}")
            
            print("\n4. Testing clear preferences...")
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