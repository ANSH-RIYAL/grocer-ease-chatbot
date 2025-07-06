from typing import List, Dict, Optional
from datetime import datetime, timezone
from pymongo.errors import PyMongoError

from src.core.database import db
from src.core.logging import get_logger
from src.services.ai_service import ai_service
from src.services.shopping_list_service import shopping_list_service

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
                    'role': 'user',
                    'message': entry['user_message']
                })
                messages.append({
                    'role': 'assistant',
                    'message': entry['bot_response']
                })
            
            return messages
        except Exception as e:
            logger.error("Error retrieving chat history", user_id=user_id, error=str(e))
            return []
    
    def process_message(self, user_id: str, user_message: str, user_preferences: Dict[str, str]) -> Dict[str, any]:
        """Process a user message and return bot response with updated shopping list."""
        try:
            # Categorize message
            message_type = ai_service.categorize_message(user_message)
            logger.info("Message categorized", user_id=user_id, message_type=message_type)
            
            # Get chat history
            chat_history = self.get_chat_history(user_id)
            
            # Generate response with user preferences
            bot_response = ai_service.generate_response(
                user_message, 
                chat_history,
                message_type,
                user_preferences=user_preferences
            )
            
            # Store the message
            self.store_message(user_id, user_message, bot_response)
            
            # Handle shopping list updates based on message type
            if message_type == "Item Addition type":
                # Direct extraction for addition messages
                ingredients = self._extract_items_from_message(user_message)
                logger.info("Direct extraction for addition", user_id=user_id, ingredients=ingredients)
                
                if ingredients:
                    success = shopping_list_service.add_items(user_id, ingredients)
                    logger.info("Added items to shopping list", user_id=user_id, success=success)
            else:
                # Use AI extraction for other message types
                ingredients = ai_service.extract_ingredients(chat_history)
                logger.info("AI extracted ingredients", user_id=user_id, ingredients=ingredients)
                
                if ingredients:
                    success = shopping_list_service.add_items(user_id, ingredients)
                    logger.info("Added items to shopping list", user_id=user_id, success=success)
            
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
                'preferences': {}
            }
    
    def _extract_items_from_message(self, message: str) -> List[str]:
        """Extract items directly from user message for addition requests."""
        import re
        
        # Common food items to look for
        common_foods = [
            'milk', 'bread', 'eggs', 'cheese', 'butter', 'yogurt', 'cream',
            'flour', 'sugar', 'salt', 'pepper', 'oil', 'vinegar', 'sauce',
            'tomatoes', 'onions', 'garlic', 'potatoes', 'carrots', 'lettuce',
            'spinach', 'kale', 'cucumber', 'bell peppers', 'mushrooms',
            'chicken', 'beef', 'pork', 'fish', 'shrimp', 'salmon', 'tuna',
            'rice', 'pasta', 'noodles', 'beans', 'lentils', 'chickpeas',
            'apples', 'bananas', 'oranges', 'grapes', 'strawberries',
            'cereal', 'oatmeal', 'granola', 'nuts', 'seeds', 'honey',
            'juice', 'soda', 'water', 'coffee', 'tea', 'wine', 'beer'
        ]
        
        message_lower = message.lower()
        found_items = []
        
        # Look for common food items
        for food in common_foods:
            if food in message_lower:
                found_items.append(food)
        
        # Also look for patterns like "add X" or "buy X"
        add_patterns = re.findall(r'add\s+(\w+)', message_lower)
        buy_patterns = re.findall(r'buy\s+(\w+)', message_lower)
        need_patterns = re.findall(r'need\s+(\w+)', message_lower)
        
        found_items.extend(add_patterns)
        found_items.extend(buy_patterns)
        found_items.extend(need_patterns)
        
        return list(set(found_items))

# Create a singleton instance
chat_service = ChatService() 