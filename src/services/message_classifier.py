from typing import Dict, List, Tuple, Literal
from transformers import pipeline
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
    def __init__(self, classifier_type: Literal["bart", "gemini"] = "bart"):
        self.classifier_type = classifier_type
        self.confidence_thresholds = {
            "Recipe type": 0.7,
            "Item Addition type": 0.7,
            "Item Information type": 0.6,
            "Update Cart type": 0.7,
            "Others": 0.3
        }
        
        try:
            if classifier_type == "bart":
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
            if self.classifier_type == "bart":
                return self._classify_with_bart(message)
            else:
                return self._classify_with_gemini(message)
            
        except Exception as e:
            logger.error(f"Error classifying message: {str(e)}")
            return "Others"
    
    def _classify_with_bart(self, message: str) -> str:
        """Classify message using BART model."""
        category_templates = {
            "Recipe type": "This message is asking for cooking instructions or a recipe for {}",
            "Item Addition type": "This message is requesting to add items to a shopping list, mentioning {}",
            "Item Information type": "This message is asking for information about a product or item {}",
            "Update Cart type": "This message is requesting to modify, remove, or delete items from a shopping list, mentioning {}",
            "Others": "This is a general conversation message about {}"
        }
        
        results = []
        for category, template in category_templates.items():
            result = self.classifier(
                message,
                [category],
                hypothesis_template=template
            )
            results.append((category, result['scores'][0]))
        
        category, confidence = max(results, key=lambda x: x[1])
        
        if confidence < self.confidence_thresholds[category]:
            logger.info(f"Confidence {confidence:.2f} below threshold for '{category}', defaulting to Others")
            return "Others"
        
        logger.info(f"Message classified as '{category}' with confidence {confidence:.2f}")
        return category
    
    def _classify_with_gemini(self, message: str) -> str:
        """Classify message using Gemini model."""
        prompt = f"""
        You are an AI assistant that categorizes user messages into one of the following types:

        1. Recipe type - User asks for a recipe.
        2. Item Addition type - User wants to add an item to their shopping list.
        3. Item Information type - User asks for details about an item (including price).
        4. Update Cart type - User wants to modify their cart.
        5. Others - Any message that does not fit the above categories.

        Classify the following message and return ONLY the category name:

        User message: "{message}"
        """
        
        try:
            response = self.model.generate_content(prompt)
            category = response.text.strip()
            
            # Validate the category
            if category not in self.confidence_thresholds:
                logger.warning(f"Invalid category returned by Gemini: {category}")
                return "Others"
                
            logger.info(f"Message classified as '{category}' using Gemini")
            return category
            
        except Exception as e:
            logger.error(f"Error in Gemini classification: {str(e)}")
            return "Others"
    
    def get_category_examples(self, category: str) -> List[str]:
        """Get example messages for a given category."""
        return CATEGORY_EXAMPLES.get(category, [])

# Create a singleton instance with default classifier type
message_classifier = MessageClassifier(settings.CLASSIFIER_TYPE if hasattr(settings, 'CLASSIFIER_TYPE') else "bart") 