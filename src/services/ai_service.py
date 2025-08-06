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
from src.models.shopping_list import ShoppingListState, ActionLog, UserPreferences

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
        message_type: str = "Others",
        user_preferences: Optional[Dict[str, str]] = None,
        shopping_list_state: Optional[ShoppingListState] = None
    ) -> str:
        """Generate a response from the AI model with context awareness."""
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
            
            # Generate action summary if shopping list state is available
            action_summary = ""
            if shopping_list_state:
                action_summary = self._generate_action_summary(shopping_list_state)
            
            # Format user preferences if available
            preferences_text = ""
            if user_preferences:
                preferences_text = "\nUser Preferences:\n" + "\n".join(
                    f"- {pref}: {value}" for pref, value in user_preferences.items()
                    if value != "not_set"
                )
            
            # Format the context into the prompt with safety guidelines
            enhanced_prompt = f"""
            {context['persona']}
            
            Task: {context['task']}
            Context: {context['context']}
            
            References to consider:
            {chr(10).join(f"- {ref}" for ref in context['references'])}
            
            {preferences_text}
            
            {action_summary}
            
            Chat History:
            {self._format_chat_history(chat_history) if chat_history else 'No previous conversation.'}
            
            User Message: {sanitized_prompt}
            
            {PromptSafety.add_safety_context("")}
            
            Please provide a helpful response considering the above context, references, and user preferences.
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

    def _generate_action_summary(self, shopping_list_state: ShoppingListState) -> str:
        """Generate concise action summary for AI context."""
        try:
            current_items = [item.name for item in shopping_list_state.items if not item.removed]
            recent_actions = shopping_list_state.action_history[-3:]  # Last 3 actions
            
            # Format user preferences
            prefs = shopping_list_state.user_preferences
            allergies_text = f"allergies: {', '.join(prefs.allergies)}" if prefs.allergies else ""
            dietary_text = f"dietary: {prefs.dietary}" if prefs.dietary != "none" else ""
            
            preferences_summary = ""
            if allergies_text or dietary_text:
                preferences_summary = f"User has {allergies_text} {dietary_text}".strip()
            
            # Format recent actions
            action_summary = ""
            if recent_actions:
                action_descriptions = []
                for action in recent_actions:
                    if action.type == "item_addition":
                        action_descriptions.append(f"added {', '.join(action.items)}")
                    elif action.type == "item_removal":
                        action_descriptions.append(f"removed {', '.join(action.items)}")
                    elif action.type == "recipe_request":
                        action_descriptions.append(f"requested recipe")
                    elif action.type == "clear_list":
                        action_descriptions.append("cleared list")
                
                action_summary = f"Recent actions: {', '.join(action_descriptions)}"
            
            # Combine into final summary
            summary_parts = []
            if preferences_summary:
                summary_parts.append(preferences_summary)
            if current_items:
                summary_parts.append(f"Current list: {', '.join(current_items)}")
            if action_summary:
                summary_parts.append(action_summary)
            
            if summary_parts:
                return f"Context Summary:\n{chr(10).join(summary_parts)}\n"
            
            return ""
            
        except Exception as e:
            logger.error(f"Failed to generate action summary: {str(e)}")
            return ""

    def extract_items_with_context(
        self, 
        user_message: str, 
        current_list: List[str], 
        shopping_list_state: Optional[ShoppingListState] = None
    ) -> Dict[str, Any]:
        """Extract items with context awareness and user preferences."""
        try:
            # Build context-aware prompt
            context_parts = []
            
            if shopping_list_state:
                # Add user preferences
                prefs = shopping_list_state.user_preferences
                if prefs.allergies:
                    context_parts.append(f"User has allergies: {', '.join(prefs.allergies)}")
                if prefs.dietary != "none":
                    context_parts.append(f"User is {prefs.dietary}")
                
                # Add removal history
                removed_items = [item.name for item in shopping_list_state.removed_items]
                if removed_items:
                    context_parts.append(f"Recently removed: {', '.join(removed_items)}")
            
            context_text = "\n".join(context_parts) if context_parts else "No special context"
            
            prompt = f"""
            Extract shopping list items from the user message with context awareness.
            
            Context:
            {context_text}
            
            Current shopping list: {', '.join(current_list)}
            
            User message: "{user_message}"
            
            Instructions:
            - Extract items mentioned for shopping
            - Handle quantities (e.g., "2 apples" → {{"apples": 2}})
            - Identify removals (e.g., "I don't want X" → remove X)
            - Consider user preferences (e.g., nut allergy alternatives)
            - Return JSON format with items_to_add, items_to_remove, quantities
            
            Return JSON format:
            {{
                "items_to_add": ["item1", "item2"],
                "items_to_remove": ["item3"],
                "quantities": {{"item1": 2, "item2": 1}},
                "context": "recipe_shopping|direct_shopping|modification"
            }}
            """
            
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                return {"items_to_add": [], "items_to_remove": [], "quantities": {}, "context": "direct_shopping"}
            
            # Parse JSON response
            try:
                result = json.loads(response.text.strip())
                return {
                    "items_to_add": result.get("items_to_add", []),
                    "items_to_remove": result.get("items_to_remove", []),
                    "quantities": result.get("quantities", {}),
                    "context": result.get("context", "direct_shopping")
                }
            except json.JSONDecodeError:
                logger.error("Failed to parse AI response as JSON")
                return {"items_to_add": [], "items_to_remove": [], "quantities": {}, "context": "direct_shopping"}
                
        except Exception as e:
            logger.error(f"Failed to extract items with context: {str(e)}")
            return {"items_to_add": [], "items_to_remove": [], "quantities": {}, "context": "direct_shopping"}

    def extract_removal_items(self, user_message: str, current_list: List[str]) -> List[str]:
        """Extract items to remove from user message."""
        try:
            prompt = f"""
            Extract items that the user wants to remove from their shopping list.
            
            Current shopping list: {', '.join(current_list)}
            User message: "{user_message}"
            
            Instructions:
            - Identify items the user wants to remove
            - Look for phrases like "remove", "don't want", "delete", "take off"
            - Return only the item names as a JSON array
            
            Return JSON format:
            ["item1", "item2"]
            """
            
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                return []
            
            try:
                result = json.loads(response.text.strip())
                return result if isinstance(result, list) else []
            except json.JSONDecodeError:
                logger.error("Failed to parse removal response as JSON")
                return []
                
        except Exception as e:
            logger.error(f"Failed to extract removal items: {str(e)}")
            return []

    def _format_chat_history(self, chat_history: List[Dict[str, str]]) -> str:
        """Format chat history for AI context."""
        if not chat_history:
            return "No previous conversation."
        
        formatted_history = []
        for i, message in enumerate(chat_history[-5:], 1):  # Last 5 messages
            user_msg = message.get('user_message', '')
            bot_msg = message.get('bot_response', '')
            formatted_history.append(f"User {i}: {user_msg}")
            if bot_msg:
                formatted_history.append(f"Bot {i}: {bot_msg}")
        
        return "\n".join(formatted_history)

    def categorize_message(self, message: str) -> str:
        """Categorize user message using the message classifier."""
        return message_classifier.classify_message(message)

    def extract_ingredients(self, chat_history: List[Dict[str, str]]) -> List[str]:
        """Extract ingredients from chat history using AI."""
        if not chat_history:
            return []
        
        try:
            # Combine recent messages for context
            recent_messages = []
            for message in chat_history[-3:]:  # Last 3 messages
                user_msg = message.get('user_message', '')
                bot_msg = message.get('bot_response', '')
                if user_msg:
                    recent_messages.append(f"User: {user_msg}")
                if bot_msg:
                    recent_messages.append(f"Bot: {bot_msg}")
            
            conversation_text = "\n".join(recent_messages)
            
            prompt = f"""
            {INGREDIENT_EXTRACTION_PROMPT}
            
            Conversation:
            {conversation_text}
            
            Extract only the food items and ingredients mentioned in this conversation.
            Return them as a JSON array of strings.
            """
            
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                return self._manual_ingredient_extraction(conversation_text)
            
            try:
                ingredients = json.loads(response.text.strip())
                if isinstance(ingredients, list):
                    return [ingredient.lower().strip() for ingredient in ingredients if ingredient]
                else:
                    return self._manual_ingredient_extraction(conversation_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI response as JSON, using manual extraction")
                return self._manual_ingredient_extraction(conversation_text)
                
        except Exception as e:
            logger.error(f"Error extracting ingredients with AI: {str(e)}")
            return self._manual_ingredient_extraction(" ".join([msg.get('user_message', '') for msg in chat_history]))

    def _manual_ingredient_extraction(self, text: str) -> List[str]:
        """Manual ingredient extraction as fallback."""
        # Common food items for manual extraction
        common_foods = [
            "milk", "bread", "eggs", "cheese", "butter", "chicken", "beef", "pork",
            "fish", "shrimp", "salmon", "tuna", "rice", "pasta", "noodles",
            "tomatoes", "onions", "garlic", "potatoes", "carrots", "lettuce",
            "spinach", "kale", "broccoli", "cauliflower", "peppers", "cucumber",
            "apples", "bananas", "oranges", "grapes", "strawberries", "blueberries",
            "flour", "sugar", "salt", "pepper", "oil", "vinegar", "soy sauce",
            "ketchup", "mustard", "mayonnaise", "yogurt", "cream", "sour cream",
            "bacon", "ham", "sausage", "turkey", "lamb", "duck", "goose",
            "shrimp", "crab", "lobster", "mussels", "clams", "oysters",
            "beans", "lentils", "chickpeas", "quinoa", "couscous", "bulgur",
            "nuts", "almonds", "walnuts", "pecans", "cashews", "peanuts",
            "seeds", "sunflower seeds", "pumpkin seeds", "chia seeds", "flax seeds"
        ]
        
        text_lower = text.lower()
        found_ingredients = []
        
        for food in common_foods:
            if food in text_lower:
                found_ingredients.append(food)
        
        return found_ingredients

# Create a singleton instance
ai_service = AIService() 