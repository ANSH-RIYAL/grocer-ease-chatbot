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
from src.core.message_contexts import MESSAGE_CONTEXTS
from src.core.prompt_safety import PromptSafety
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
        chat_history: Optional[List[Dict[str, str]]] = None,
        message_type: str = "Others"
    ) -> str:
        """Generate a response from the AI model."""
        if not prompt or not isinstance(prompt, str):
            logger.error(ERROR_MESSAGES["INVALID_PROMPT"])
            raise ValueError(ERROR_MESSAGES["INVALID_PROMPT"])
            
        try:
            # Validate and sanitize the prompt
            validation_results = PromptSafety.validate_prompt(prompt, message_type)
            if not validation_results['is_safe']:
                logger.warning(f"Prompt validation failed: {validation_results['violations']}")
                return PromptSafety.get_safe_response('prohibited_content')
            
            # Sanitize the prompt
            sanitized_prompt = PromptSafety.sanitize_prompt(prompt)
            
            # Get the context for the message type
            context = MESSAGE_CONTEXTS.get(message_type, MESSAGE_CONTEXTS["Others"])
            
            # Format the context into the prompt with safety guidelines
            enhanced_prompt = f"""
            {context['persona']}
            
            Task: {context['task']}
            Context: {context['context']}
            
            References to consider:
            {chr(10).join(f"- {ref}" for ref in context['references'])}
            
            Chat History:
            {self._format_chat_history(chat_history) if chat_history else 'No previous conversation.'}
            
            User Message: {sanitized_prompt}
            
            {PromptSafety.add_safety_context("")}
            
            Please provide a helpful response considering the above context and references.
            """
            
            response = self.model.generate_content(enhanced_prompt)
            if not response or not response.text:
                logger.error(ERROR_MESSAGES["EMPTY_RESPONSE"])
                raise ValueError(ERROR_MESSAGES["EMPTY_RESPONSE"])
                
            # Validate the response
            response_validation = PromptSafety.validate_prompt(response.text, message_type)
            if not response_validation['is_safe']:
                logger.warning(f"Response validation failed: {response_validation['violations']}")
                return PromptSafety.get_safe_response('prohibited_content')
                
            return response.text.strip()
        except Exception as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], error=str(e))
            raise
    
    def _format_chat_history(self, chat_history: List[Dict[str, str]]) -> str:
        """Format chat history into a readable string."""
        formatted_history = []
        for msg in chat_history:
            role = msg.get('role', 'unknown')
            message = msg.get('message', '')
            formatted_history.append(f"{role.capitalize()}: {message}")
        return "\n".join(formatted_history)
    
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