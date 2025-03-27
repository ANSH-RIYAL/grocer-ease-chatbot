from typing import Dict, List, Tuple
from transformers import pipeline
from src.core.logging import get_logger
from src.core.constants import (
    CATEGORIES,
    CATEGORY_EXAMPLES,
    ERROR_MESSAGES
)

logger = get_logger(__name__)

class MessageClassifier:
    def __init__(self):
        try:
            # Initialize the zero-shot classifier
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=-1  # CPU
            )
            # Define confidence thresholds for each category
            self.confidence_thresholds = {
                "Recipe type": 0.7,
                "Item Addition type": 0.7,
                "Item Information type": 0.6,
                "Update Cart type": 0.7,
                "Others": 0.3
            }
            logger.info("Message classifier initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize message classifier: {str(e)}")
            raise
    
    def classify_message(self, message: str) -> str:
        """Classify a message into one of the predefined categories."""
        if not message or not isinstance(message, str):
            logger.error(ERROR_MESSAGES["INVALID_MESSAGE"])
            return "Others"
            
        try:
            # Define specific hypothesis templates for each category
            category_templates = {
                "Recipe type": "This message is asking for cooking instructions or a recipe for {}",
                "Item Addition type": "This message is requesting to add items to a shopping list, mentioning {}",
                "Item Information type": "This message is asking for information about a product or item {}",
                "Update Cart type": "This message is requesting to modify, remove, or delete items from a shopping list, mentioning {}",
                "Others": "This is a general conversation message about {}"
            }
            
            # Run classification for each category with its specific template
            results = []
            for category, template in category_templates.items():
                result = self.classifier(
                    message,
                    [category],
                    hypothesis_template=template
                )
                results.append((category, result['scores'][0]))
            
            # Get the category with highest confidence
            category, confidence = max(results, key=lambda x: x[1])
            
            # Check if confidence meets the threshold
            if confidence < self.confidence_thresholds[category]:
                logger.info(f"Confidence {confidence:.2f} below threshold for '{category}', defaulting to Others")
                return "Others"
            
            logger.info(f"Message classified as '{category}' with confidence {confidence:.2f}")
            return category
            
        except Exception as e:
            logger.error(f"Error classifying message: {str(e)}")
            return "Others"
    
    def get_category_examples(self, category: str) -> List[str]:
        """Get example messages for a given category."""
        return CATEGORY_EXAMPLES.get(category, [])

# Create a singleton instance
message_classifier = MessageClassifier() 