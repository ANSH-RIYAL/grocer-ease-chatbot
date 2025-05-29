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
    
    def process_message(self, user_id: str, user_message: str) -> Dict[str, any]:
        """Process a user message and return bot response with updated shopping list."""
        try:
            # Categorize message
            message_type = ai_service.categorize_message(user_message)
            logger.info("Message categorized", user_id=user_id, message_type=message_type)
            
            # Extract user preferences
            preferences = ai_service.extract_user_preferences(user_id, user_message)
            logger.info("User preferences extracted", user_id=user_id, preferences=preferences)
            
            # Get chat history
            chat_history = self.get_chat_history(user_id)
            
            # Generate response
            bot_response = ai_service.generate_response(user_message, chat_history,message_type)
            
            # Store the message
            self.store_message(user_id, user_message, bot_response)
            
            # Extract and update ingredients
            ingredients = ai_service.extract_ingredients(chat_history)
            if ingredients:
                shopping_list_service.add_items(user_id, ingredients)
            
            # Get updated shopping list
            shopping_list = shopping_list_service.get_shopping_list(user_id)
            
            return {
                'bot_response': bot_response,
                'shopping_list': shopping_list,
                'preferences': preferences
            }
            
        except Exception as e:
            logger.error("Error processing message", user_id=user_id, error=str(e))
            return {
                'bot_response': "I apologize, but I encountered an error processing your message. Please try again.",
                'shopping_list': [],
                'preferences': {}
            }

# Create a singleton instance
chat_service = ChatService() 