from typing import Dict, List, Optional, Literal
from transformers import pipeline
import google.generativeai as genai
from datetime import datetime, timezone
from pymongo.errors import PyMongoError

from src.core.logging import get_logger
from src.core.config import settings
from src.core.constants import ERROR_MESSAGES, USER_PREFERENCES_COLLECTION
from src.core.database import db

logger = get_logger(__name__)

class UserPreferences:
    def __init__(self, model_type: Literal["bart", "gemini"] = "gemini"):
        self.model_type = model_type
        # Initialize static preferences with their possible values
        self.static_preferences = {
            "vegetarian": {"type": "boolean", "values": ["yes", "no", "not_set"]},
        }
        
        # Initialize MongoDB collection
        self.collection = db.get_db()[USER_PREFERENCES_COLLECTION]
        
        try:
            if model_type == "bart":
                # Initialize the zero-shot classifier
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device=-1  # CPU
                )
            else:  # gemini
                if not settings.GEMINI_API_KEY:
                    raise ValueError(ERROR_MESSAGES["API_KEY_MISSING"])
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
            
            logger.info(f"User preferences service initialized successfully with {model_type}")
        except Exception as e:
            logger.error(f"Failed to initialize user preferences service: {str(e)}")
            raise
    
    def get_static_preferences(self, user_id: str) -> Dict[str, str]:
        """Get all static preferences for a user from the database."""
        try:
            user_prefs = self.collection.find_one({'user_id': user_id})
            if user_prefs:
                return user_prefs.get('static_preferences', {})
            return {}
        except PyMongoError as e:
            logger.error(f"Error retrieving preferences for user {user_id}: {str(e)}")
            return {}
    
    def set_static_preference(self, user_id: str, preference: str, value: str) -> bool:
        """Set a static preference for a user in the database."""
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
                        f'static_preferences.{preference}': value,
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
    
    def extract_preferences_from_message(self, user_id: str, message: str) -> Dict[str, str]:
        """Extract preferences from a user message and store them in the database."""
        if self.model_type == "bart":
            preferences = self._extract_with_bart(message)
        else:
            preferences = self._extract_with_gemini(user_id, message)
        
        # Store the extracted preferences
        if preferences:
            try:
                self.collection.update_one(
                    {'user_id': user_id},
                    {
                        '$set': {
                            'extracted_preferences': preferences,
                            'last_extracted': datetime.now(timezone.utc),
                            'message': message
                        }
                    },
                    upsert=True
                )
                logger.info(f"Stored extracted preferences for user {user_id}")
            except PyMongoError as e:
                logger.error(f"Error storing extracted preferences for user {user_id}: {str(e)}")
        
        return preferences
    
    def _extract_with_bart(self, message: str) -> Dict[str, str]:
        """Extract preferences using BART model."""
        preferences = {}
        
        # Create hypothesis templates for each preference type
        for pref, config in self.static_preferences.items():
            if config["type"] == "boolean":
                template = "This message indicates that the user is {}"
                result = self.classifier(
                    message,
                    ["yes", "no"],
                    hypothesis_template=template
                )
                if result["scores"][0] > 0.7:  # Confidence threshold
                    preferences[pref] = "yes"
                elif result["scores"][1] > 0.7:
                    preferences[pref] = "no"
            
            elif config["type"] == "level":
                template = "This message indicates the user's {} preference"
                result = self.classifier(
                    message,
                    config["values"][:-1],  # Exclude "not_set"
                    hypothesis_template=template
                )
                if result["scores"][0] > 0.7:
                    preferences[pref] = result["labels"][0]
            
            elif config["type"] == "multi_select":
                for value in config["values"][:-1]:  # Exclude "not_set"
                    template = "This message indicates the user prefers {}"
                    result = self.classifier(
                        message,
                        ["yes", "no"],
                        hypothesis_template=template
                    )
                    if result["scores"][0] > 0.7:
                        if pref not in preferences:
                            preferences[pref] = []
                        preferences[pref].append(value)
        
        return preferences
    
    def _extract_with_gemini(self, user_id: str, message: str) -> Dict[str, str]:
        """Extract preferences using Gemini model."""
        prompt = f"""
        You are an AI assistant that extracts user preferences from messages.
        Analyze the following message and identify any preferences mentioned.
        Return the preferences in JSON format with the following structure:
        {{
            "preferences": {{
                "preference_name": "value"
            }}
        }}
        
        Available preferences and their possible values:
        {self.static_preferences}
        
        Message: "{message}"
        """
        
        try:
            response = self.model.generate_content(prompt)
            extracted_preferences = eval(response.text.strip())
            
            # Update user's preferences
            for pref, value in extracted_preferences.get("preferences", {}).items():
                if pref in self.static_preferences:
                    self.set_static_preference(user_id, pref, value)
            
            logger.info(f"Extracted preferences from message for user {user_id}")
            return extracted_preferences.get("preferences", {})
            
        except Exception as e:
            logger.error(f"Error extracting preferences: {str(e)}")
            return {}
    
    def get_all_preferences(self, user_id: str) -> Dict[str, Dict[str, str]]:
        """Get all preferences (static and dynamic) for a user from the database."""
        try:
            user_prefs = self.collection.find_one({'user_id': user_id})
            if user_prefs:
                return {
                    'static': user_prefs.get('static_preferences', {}),
                    'dynamic': user_prefs.get('extracted_preferences', {})
                }
            return {'static': {}, 'dynamic': {}}
        except PyMongoError as e:
            logger.error(f"Error retrieving all preferences for user {user_id}: {str(e)}")
            return {'static': {}, 'dynamic': {}}
    
    def get_dynamic_preferences(self, user_id: str) -> Dict[str, str]:
        """Get dynamic preferences for a user from the database."""
        try:
            user_prefs = self.collection.find_one({'user_id': user_id})
            if user_prefs:
                return user_prefs.get('extracted_preferences', {})
            return {}
        except PyMongoError as e:
            logger.error(f"Error retrieving dynamic preferences for user {user_id}: {str(e)}")
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

# Create a singleton instance with default model type
user_preferences = UserPreferences(settings.PREFERENCE_MODEL_TYPE if hasattr(settings, 'PREFERENCE_MODEL_TYPE') else "gemini") 