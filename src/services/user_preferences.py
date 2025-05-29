from typing import Dict, Optional
from datetime import datetime, timezone
from pymongo.errors import PyMongoError

from src.core.logging import get_logger
from src.core.config import settings
from src.core.constants import USER_PREFERENCES_COLLECTION
from src.core.database import db

logger = get_logger(__name__)

class UserPreferences:
    def __init__(self):
        # Initialize static preferences with their possible values
        self.static_preferences = {
            "vegetarian": {"type": "boolean", "values": ["yes", "no", "not_set"]},
        }
        
        # Initialize MongoDB collection
        self.collection = db.get_db()[USER_PREFERENCES_COLLECTION]
        logger.info("User preferences service initialized successfully")
    
    def get_preference(self, user_id: str, preference: str) -> str:
        """Get a specific preference for a user from the database."""
        try:
            user_prefs = self.collection.find_one({'user_id': user_id})
            if user_prefs and preference in user_prefs.get('preferences', {}):
                return user_prefs['preferences'][preference]
            return "not_set"
        except PyMongoError as e:
            logger.error(f"Error retrieving preference for user {user_id}: {str(e)}")
            return "not_set"
    
    def set_preference(self, user_id: str, preference: str, value: str) -> bool:
        """Set a preference for a user in the database."""
        if preference not in self.static_preferences:
            logger.error(f"Invalid preference: {preference}")
            return False
            
        if value not in self.static_preferences[preference]["values"]:
            logger.error(f"Invalid value for preference {preference}: {value}")
            return False
            
        try:
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        f'preferences.{preference}': value,
                        'last_updated': datetime.now(timezone.utc)
                    }
                },
                upsert=True
            )
            logger.info(f"Set preference {preference}={value} for user {user_id}")
            return result.modified_count > 0 or result.upserted_id is not None
        except PyMongoError as e:
            logger.error(f"Error setting preference for user {user_id}: {str(e)}")
            return False
    
    def get_all_preferences(self, user_id: str) -> Dict[str, str]:
        """Get all preferences for a user from the database."""
        try:
            user_prefs = self.collection.find_one({'user_id': user_id})
            if user_prefs:
                return user_prefs.get('preferences', {})
            return {}
        except PyMongoError as e:
            logger.error(f"Error retrieving preferences for user {user_id}: {str(e)}")
            return {}
    
    def clear_preferences(self, user_id: str) -> bool:
        """Clear all preferences for a user from the database."""
        try:
            result = self.collection.delete_one({'user_id': user_id})
            logger.info(f"Cleared preferences for user {user_id}")
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Error clearing preferences for user {user_id}: {str(e)}")
            return False

# Create a singleton instance
user_preferences = UserPreferences() 