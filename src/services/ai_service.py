from typing import List, Dict, Any, Optional
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import json

from src.core.config import settings
from src.core.logging import get_logger
from src.core.constants import (
    INGREDIENT_EXTRACTION_PROMPT,
    ERROR_MESSAGES,
    SUCCESS_MESSAGES
)
from src.services.message_classifier import message_classifier
from src.services.user_preferences import user_preferences

logger = get_logger(__name__)

class AIService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            logger.error(ERROR_MESSAGES["API_KEY_MISSING"])
            raise ValueError(ERROR_MESSAGES["API_KEY_MISSING"])
            
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
            logger.info(SUCCESS_MESSAGES["AI_SERVICE_INIT"])
        except Exception as e:
            logger.error(ERROR_MESSAGES["AI_SERVICE_INIT_FAILED"], error=str(e))
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def generate_response(
        self,
        prompt: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate a response from the AI model."""
        if not prompt or not isinstance(prompt, str):
            logger.error(ERROR_MESSAGES["INVALID_PROMPT"])
            raise ValueError(ERROR_MESSAGES["INVALID_PROMPT"])
            
        try:
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                logger.error(ERROR_MESSAGES["EMPTY_RESPONSE"])
                raise ValueError(ERROR_MESSAGES["EMPTY_RESPONSE"])
            return response.text.strip()
        except Exception as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], error=str(e))
            raise
    
    def categorize_message(self, message: str) -> str:
        """Categorize user message into predefined types."""
        return message_classifier.classify_message(message)
    
    def extract_user_preferences(self, user_id: str, message: str) -> Dict[str, str]:
        """Extract user preferences from the message."""
        try:
            preferences = user_preferences.extract_preferences_from_message(user_id, message)
            logger.info("Extracted user preferences", user_id=user_id, preferences=preferences)
            return preferences
        except Exception as e:
            logger.error("Error extracting user preferences", user_id=user_id, error=str(e))
            return {}
    
    def extract_ingredients(self, chat_history: List[Dict[str, str]]) -> List[str]:
        """Extract ingredients from chat history."""
        if not chat_history or not isinstance(chat_history, list):
            logger.error(ERROR_MESSAGES["INVALID_CHAT_HISTORY"])
            return []
            
        try:
            conversation_text = "\n".join([
                f"{msg['role'].capitalize()}: {msg['message']}"
                for msg in chat_history
                if isinstance(msg, dict) and 'role' in msg and 'message' in msg
            ])
            prompt = INGREDIENT_EXTRACTION_PROMPT + conversation_text

            response = self.generate_response(prompt)
            # Clean up response by removing extra characters
            cleaned_response = response.strip().lstrip("```").rstrip("```").strip()
            
            try:
                # Try to parse as JSON first
                ingredients = json.loads(cleaned_response)
            except json.JSONDecodeError:
                # If JSON parsing fails, try eval as fallback
                ingredients = eval(cleaned_response)
                
            # Validate and clean ingredients
            if not isinstance(ingredients, list):
                logger.error(ERROR_MESSAGES["INVALID_INGREDIENTS"], ingredients=ingredients)
                return []
                
            # Clean and validate each ingredient
            cleaned_ingredients = []
            for ingredient in ingredients:
                if isinstance(ingredient, str) and ingredient.strip():
                    cleaned_ingredients.append(ingredient.strip().lower())
                    
            # Remove duplicates and sort alphabetically
            return sorted(list(set(cleaned_ingredients)))
            
        except Exception as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], error=str(e))
            return []

# Create a singleton instance
ai_service = AIService() 