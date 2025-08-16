from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from pymongo.errors import PyMongoError

from src.core.database import db
from src.core.logging import get_logger
from src.services.ai_service import ai_service
from src.services.shopping_list_service import shopping_list_service
from src.services.context_manager import context_manager
from src.services.recipe_service import recipe_service
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
            
            # Get conversation context
            conversation_context = context_manager.get_conversation_context(user_id)
            
            # Categorize message
            message_type = ai_service.categorize_message(user_message)
            logger.info("Message categorized", user_id=user_id, message_type=message_type)
            
            # Handle recipe requests specially
            if message_type == "Recipe type":
                return self._handle_recipe_request(user_id, user_message, user_preferences, shopping_list_state)
            
            # Get chat history
            chat_history = self.get_chat_history(user_id)
            
            # Process shopping list updates with intelligent decision making FIRST
            updated_items = self._process_shopping_list_updates_with_context(user_id, user_message, message_type, shopping_list_state)
            
            # Generate response with context awareness AFTER updates
            bot_response = ai_service.generate_response(
                user_message, 
                chat_history,
                message_type,
                user_preferences=user_preferences,
                shopping_list_state=shopping_list_state
            )
            
            # Enhance response with actual items added/removed
            if updated_items:
                if updated_items.get("added"):
                    added_text = ", ".join(updated_items["added"])
                    bot_response += f"\n\nAdded to your list: {added_text}"
                if updated_items.get("removed"):
                    removed_text = ", ".join(updated_items["removed"])
                    bot_response += f"\n\nRemoved from your list: {removed_text}"
            
            # Store the message
            self.store_message(user_id, user_message, bot_response)
            
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

    def _handle_recipe_request(self, user_id: str, user_message: str, user_preferences: Dict[str, str], 
                              shopping_list_state: Optional[ShoppingListState]) -> Dict[str, Any]:
        """Handle recipe requests with intelligent ingredient management."""
        try:
            # Convert user preferences to UserPreferences object
            prefs = UserPreferences()
            if user_preferences.get("dietary"):
                prefs.dietary = user_preferences["dietary"]
            if user_preferences.get("allergies"):
                prefs.allergies = user_preferences["allergies"].split(",") if isinstance(user_preferences["allergies"], str) else user_preferences["allergies"]
            
            # Get current shopping list
            current_list = shopping_list_service.get_shopping_list(user_id)
            
            # STEP 1: Generate recipe with LLM FIRST
            recipe_result = recipe_service.generate_recipe_with_ai(user_message, prefs)
            
            if recipe_result.get("suggestion"):
                recipe = recipe_result["suggestion"]
                
                # STEP 2: Extract ingredients FROM the generated recipe
                recipe_ingredients = recipe.get("ingredients", [])
                
                # STEP 3: Add ingredients to shopping list (only if not already present)
                added_ingredients = []
                for ingredient in recipe_ingredients:
                    # Check if ingredient is already in shopping list
                    if ingredient.lower() not in [item.lower() for item in current_list]:
                        decision = context_manager.should_add_item(user_id, ingredient)
                        if decision["should_add"]:
                            success = shopping_list_service.add_item_with_context(
                                user_id, ingredient, 1, "recipe_generation"
                            )
                            if success:
                                added_ingredients.append(ingredient)
                
                # STEP 4: Generate response with recipe details and added ingredients
                if added_ingredients:
                    ingredients_text = ", ".join(added_ingredients)
                    bot_response = f"Here's a recipe for {recipe['recipe_name']}: {', '.join(recipe_ingredients)}. I've added these ingredients to your shopping list: {ingredients_text}."
                else:
                    bot_response = f"Here's a recipe for {recipe['recipe_name']}: {', '.join(recipe_ingredients)}. All ingredients are already in your shopping list!"
                
                # Log recipe request action
                shopping_list_service._log_action(user_id, "recipe_request", [recipe['recipe_name']], reason="ai_generated")
                
            else:
                # Fallback to hardcoded suggestions if AI generation fails
                recipe_result = recipe_service.suggest_recipe(prefs, current_list)
                
                if recipe_result["suggestion"]:
                    recipe = recipe_result["suggestion"]
                    missing_ingredients = recipe_result["missing_ingredients"]
                    
                    # Add missing ingredients to shopping list
                    added_ingredients = []
                    for ingredient in missing_ingredients:
                        decision = context_manager.should_add_item(user_id, ingredient)
                        if decision["should_add"]:
                            success = shopping_list_service.add_item_with_context(
                                user_id, ingredient, 1, "recipe_suggestion"
                            )
                            if success:
                                added_ingredients.append(ingredient)
                    
                    # Generate response with actual ingredients
                    ingredients_text = ", ".join(added_ingredients)
                    bot_response = f"I suggest making {recipe['name']}! It's {recipe['difficulty']} difficulty and takes {recipe['cook_time']}. I've added these ingredients to your shopping list: {ingredients_text}."
                    
                    # Log recipe request action
                    shopping_list_service._log_action(user_id, "recipe_request", [recipe['name']], reason="fallback_suggestion")
                    
                else:
                    bot_response = "I couldn't generate a recipe for that. Try asking for something specific like 'butter chicken' or 'pasta recipe'!"
                    recipe_result = {"suggestion": None}
            
            # Store the message
            self.store_message(user_id, user_message, bot_response)
            
            # Get updated shopping list
            shopping_list = shopping_list_service.get_shopping_list(user_id)
            
            return {
                'bot_response': bot_response,
                'shopping_list': shopping_list,
                'preferences': user_preferences,
                'recipe_suggestion': recipe_result.get("suggestion")
            }
            
        except Exception as e:
            logger.error("Error handling recipe request", user_id=user_id, error=str(e))
            return {
                'bot_response': "I apologize, but I encountered an error processing your recipe request. Please try again.",
                'shopping_list': [],
                'preferences': user_preferences
            }

    def _process_shopping_list_updates_with_context(self, user_id: str, user_message: str, message_type: str, 
                                                  shopping_list_state: Optional[ShoppingListState]) -> Dict[str, List[str]]:
        """Process shopping list updates with intelligent decision making."""
        try:
            current_list = shopping_list_service.get_shopping_list(user_id)
            added_items = []
            removed_items = []
            
            # Extract items with context awareness
            extraction_result = ai_service.extract_items_with_context(
                user_message, 
                current_list, 
                shopping_list_state
            )
            
            # Process additions with intelligent decision making
            items_to_add = extraction_result.get("items_to_add", [])
            quantities = extraction_result.get("quantities", {})
            
            for item in items_to_add:
                # Check if we should add this item
                decision = context_manager.should_add_item(user_id, item)
                
                if decision["should_add"]:
                    quantity = quantities.get(item, decision.get("quantity", 1))
                    success = shopping_list_service.add_item_with_context(
                        user_id, item, quantity, "ai_extraction"
                    )
                    if success:
                        logger.info(f"Added item with context", user_id=user_id, item=item, quantity=quantity)
                        added_items.append(item)
                else:
                    logger.info(f"Intelligent decision: not adding {item}", user_id=user_id, reason=decision["reason"])
                    # Could add this to bot response for user feedback
            
            # Process removals with intelligent decision making
            items_to_remove = extraction_result.get("items_to_remove", [])
            
            for item in items_to_remove:
                # Check if we should remove this item
                decision = context_manager.should_remove_item(user_id, item)
                
                if decision["should_remove"]:
                    success = shopping_list_service.remove_item_with_tracking(
                        user_id, item, "user_request"
                    )
                    if success:
                        logger.info(f"Removed item with tracking", user_id=user_id, item=item)
                        removed_items.append(item)
                else:
                    logger.info(f"Intelligent decision: not removing {item}", user_id=user_id, reason=decision["reason"])
            
            # Handle special message types with fallback
            if message_type == "Item Addition type" and not items_to_add:
                # Fallback to direct extraction for addition messages
                ingredients = self._extract_items_from_message(user_message)
                if ingredients:
                    for item in ingredients:
                        decision = context_manager.should_add_item(user_id, item)
                        if decision["should_add"]:
                            success = shopping_list_service.add_item_with_context(user_id, item, 1, "direct_addition")
                            if success:
                                added_items.append(item)
            
            elif message_type == "Update Cart type" and not items_to_remove:
                # Fallback to AI removal extraction
                removal_items = ai_service.extract_removal_items(user_message, current_list)
                for item in removal_items:
                    decision = context_manager.should_remove_item(user_id, item)
                    if decision["should_remove"]:
                        success = shopping_list_service.remove_item_with_tracking(user_id, item, "user_request")
                        if success:
                            removed_items.append(item)
            
        except Exception as e:
            logger.error("Error processing shopping list updates", user_id=user_id, error=str(e))
        
        return {
            "added": added_items,
            "removed": removed_items
        }

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