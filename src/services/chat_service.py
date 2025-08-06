from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from pymongo.errors import PyMongoError

from src.core.database import db
from src.core.logging import get_logger
from src.services.ai_service import ai_service
from src.services.shopping_list_service import shopping_list_service
from src.models.shopping_list import ShoppingListState, UserPreferences

logger = get_logger(__name__)

class ChatService:
    def __init__(self):
        self.collection = db.get_db()['chat_history']
    
    def store_message(self, user_id: str, user_message: str, bot_response: str) -> bool:
        """Store a chat message in the database."""
        try:
            self.collection.insert_one({
                'user_id': user_id,
                'user_message': user_message,
                'bot_response': bot_response,
                'timestamp': datetime.now(timezone.utc)
            })
            return True
        except Exception as e:
            logger.error("Error storing chat message", user_id=user_id, error=str(e))
            return False
    
    def get_chat_history(self, user_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieve chat history for a user."""
        try:
            chat_history = list(self.collection.find(
                {'user_id': user_id}
            ).sort('timestamp', 1).limit(limit))  # Sort by timestamp ascending
            
            messages = []
            for entry in chat_history:
                messages.append({
                    'user_message': entry['user_message'],
                    'bot_response': entry['bot_response']
                })
            
            return messages
        except Exception as e:
            logger.error("Error retrieving chat history", user_id=user_id, error=str(e))
            return []
    
    def process_message(self, user_id: str, user_message: str, user_preferences: Dict[str, str]) -> Dict[str, Any]:
        """Process a user message with agentic features and return bot response with updated shopping list."""
        try:
            # Get enhanced shopping list state for context
            shopping_list_state = shopping_list_service.get_shopping_list_state(user_id)
            
            # Categorize message
            message_type = ai_service.categorize_message(user_message)
            logger.info("Message categorized", user_id=user_id, message_type=message_type)
            
            # Get chat history
            chat_history = self.get_chat_history(user_id)
            
            # Generate response with context awareness
            bot_response = ai_service.generate_response(
                user_message, 
                chat_history,
                message_type,
                user_preferences=user_preferences,
                shopping_list_state=shopping_list_state
            )
            
            # Store the message
            self.store_message(user_id, user_message, bot_response)
            
            # Process shopping list updates with context awareness
            self._process_shopping_list_updates(user_id, user_message, message_type, shopping_list_state)
            
            # Get updated shopping list
            shopping_list = shopping_list_service.get_shopping_list(user_id)
            logger.info("Retrieved shopping list", user_id=user_id, items_count=len(shopping_list))
            
            return {
                'bot_response': bot_response,
                'shopping_list': shopping_list,
                'preferences': user_preferences
            }
            
        except Exception as e:
            logger.error("Error processing message", user_id=user_id, error=str(e))
            return {
                'bot_response': "I apologize, but I encountered an error processing your message. Please try again.",
                'shopping_list': [],
                'preferences': user_preferences
            }

    def _process_shopping_list_updates(self, user_id: str, user_message: str, message_type: str, 
                                     shopping_list_state: Optional[ShoppingListState]) -> None:
        """Process shopping list updates with context awareness."""
        try:
            current_list = shopping_list_service.get_shopping_list(user_id)
            
            # Extract items with context awareness
            extraction_result = ai_service.extract_items_with_context(
                user_message, 
                current_list, 
                shopping_list_state
            )
            
            # Process additions
            items_to_add = extraction_result.get("items_to_add", [])
            quantities = extraction_result.get("quantities", {})
            
            for item in items_to_add:
                quantity = quantities.get(item, 1)
                success = shopping_list_service.add_item_with_context(
                    user_id, item, quantity, "ai_extraction"
                )
                if success:
                    logger.info(f"Added item with context", user_id=user_id, item=item, quantity=quantity)
            
            # Process removals
            items_to_remove = extraction_result.get("items_to_remove", [])
            
            for item in items_to_remove:
                success = shopping_list_service.remove_item_with_tracking(
                    user_id, item, "user_request"
                )
                if success:
                    logger.info(f"Removed item with tracking", user_id=user_id, item=item)
            
            # Handle special message types
            if message_type == "Item Addition type" and not items_to_add:
                # Fallback to direct extraction for addition messages
                ingredients = self._extract_items_from_message(user_message)
                if ingredients:
                    for item in ingredients:
                        shopping_list_service.add_item_with_context(user_id, item, 1, "direct_addition")
            
            elif message_type == "Update Cart type" and not items_to_remove:
                # Fallback to AI removal extraction
                removal_items = ai_service.extract_removal_items(user_message, current_list)
                for item in removal_items:
                    shopping_list_service.remove_item_with_tracking(user_id, item, "user_request")
            
        except Exception as e:
            logger.error("Error processing shopping list updates", user_id=user_id, error=str(e))

    def _extract_items_from_message(self, message: str) -> List[str]:
        """Extract items from message using simple patterns."""
        import re
        
        # Common food items for pattern matching
        common_foods = [
            "milk", "bread", "eggs", "cheese", "butter", "chicken", "beef", "pork",
            "fish", "shrimp", "salmon", "tuna", "rice", "pasta", "noodles",
            "tomatoes", "onions", "garlic", "potatoes", "carrots", "lettuce",
            "spinach", "kale", "broccoli", "cauliflower", "peppers", "cucumber",
            "apples", "bananas", "oranges", "grapes", "strawberries", "blueberries",
            "flour", "sugar", "salt", "pepper", "oil", "vinegar", "soy sauce",
            "ketchup", "mustard", "mayonnaise", "yogurt", "cream", "sour cream"
        ]
        
        message_lower = message.lower()
        found_items = []
        
        # Look for common food items
        for food in common_foods:
            if food in message_lower:
                found_items.append(food)
        
        # Look for patterns like "add X" or "buy X"
        add_patterns = re.findall(r'add\s+(\w+)', message_lower)
        buy_patterns = re.findall(r'buy\s+(\w+)', message_lower)
        need_patterns = re.findall(r'need\s+(\w+)', message_lower)
        
        found_items.extend(add_patterns)
        found_items.extend(buy_patterns)
        found_items.extend(need_patterns)
        
        return list(set(found_items))

# Create a singleton instance
chat_service = ChatService() 