from typing import Dict, List, Tuple, Literal
import google.generativeai as genai
from src.core.logging import get_logger
from src.core.config import settings
from src.core.constants import (
    CATEGORIES,
    CATEGORY_EXAMPLES,
    ERROR_MESSAGES
)

logger = get_logger(__name__)

class MessageClassifier:
    def __init__(self, classifier_type: Literal["gemini"] = "gemini"):
        self.classifier_type = classifier_type
        
        try:
            if not settings.GEMINI_API_KEY:
                raise ValueError(ERROR_MESSAGES["API_KEY_MISSING"])
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)
            
            logger.info(f"Message classifier initialized successfully with {classifier_type}")
        except Exception as e:
            logger.error(f"Failed to initialize message classifier: {str(e)}")
            raise
    
    def classify_message(self, message: str) -> str:
        """Classify a message into one of the predefined categories."""
        if not message or not isinstance(message, str):
            logger.error(ERROR_MESSAGES["INVALID_MESSAGE"])
            return "Others"
            
        try:
            return self._classify_with_gemini(message)
            
        except Exception as e:
            logger.error(f"Error classifying message: {str(e)}")
            return "Others"
    
    def _classify_with_gemini(self, message: str) -> str:
        """Classify message using Gemini model."""
        prompt = f"""
        You are an AI assistant that categorizes user messages into one of the following types:

        1. Recipe type - User asks for a recipe or cooking instructions.
        2. Item Addition type - User wants to add an item to their shopping list.
        3. Item Information type - User asks for details about an item (including price).
        4. Update Cart type - User wants to modify, remove, or delete items from their shopping list.
        5. Others - Any message that does not fit the above categories.

        Classify the following message and return ONLY the exact category name (including "type" suffix):

        Message: "{message}"

        Category:
        """
        
        try:
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                logger.warning("Empty response from Gemini classifier")
                return "Others"
            
            category = response.text.strip()
            
            # Validate the response
            if category in CATEGORIES:
                logger.info(f"Message classified as '{category}'")
                return category
            else:
                logger.warning(f"Invalid category '{category}' from Gemini, defaulting to Others")
                return "Others"
                
        except Exception as e:
            logger.error(f"Error in Gemini classification: {str(e)}")
            return "Others"
    
    def get_category_examples(self, category: str) -> List[str]:
        """Get example messages for a specific category."""
        return CATEGORY_EXAMPLES.get(category, [])

# Create a singleton instance
message_classifier = MessageClassifier("gemini") 