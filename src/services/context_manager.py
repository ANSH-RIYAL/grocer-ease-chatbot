from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from src.core.logging import get_logger
from src.models.shopping_list import ShoppingListState, ConversationContext, ActionLog, UserPreferences
from src.services.shopping_list_service import shopping_list_service

logger = get_logger(__name__)

class ContextManager:
    """Manages conversation context and intelligent decision making."""
    
    def __init__(self):
        self.conversation_contexts: Dict[str, ConversationContext] = {}
    
    def get_conversation_context(self, user_id: str) -> ConversationContext:
        """Get or create conversation context for a user."""
        if user_id not in self.conversation_contexts:
            # Get user preferences from shopping list state
            shopping_list_state = shopping_list_service.get_shopping_list_state(user_id)
            user_preferences = shopping_list_state.user_preferences if shopping_list_state else UserPreferences()
            
            self.conversation_contexts[user_id] = ConversationContext(
                user_id=user_id,
                user_preferences=user_preferences
            )
        
        return self.conversation_contexts[user_id]
    
    def update_conversation_context(self, user_id: str, **kwargs) -> None:
        """Update conversation context with new information."""
        context = self.get_conversation_context(user_id)
        
        for key, value in kwargs.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        logger.info(f"Updated conversation context for user {user_id}", updates=kwargs)
    
    def should_add_item(self, user_id: str, item: str) -> Dict[str, Any]:
        """Intelligent decision on whether to add an item based on context."""
        context = self.get_conversation_context(user_id)
        shopping_list_state = shopping_list_service.get_shopping_list_state(user_id)
        
        if not shopping_list_state:
            return {"should_add": True, "reason": "new_user", "quantity": 1}
        
        # Check if item was recently removed
        for removed_item in shopping_list_state.removed_items:
            if removed_item.name.lower() == item.lower():
                # Check if removal was recent (within last 10 minutes)
                if datetime.utcnow() - removed_item.removed_at < timedelta(minutes=10):
                    return {
                        "should_add": False, 
                        "reason": "recently_removed",
                        "removed_at": removed_item.removed_at,
                        "removal_reason": removed_item.reason
                    }
        
        # Check if item already exists
        for existing_item in shopping_list_state.items:
            if existing_item.name.lower() == item.lower() and not existing_item.removed:
                return {
                    "should_add": False,
                    "reason": "already_exists",
                    "current_quantity": existing_item.quantity
                }
        
        # Check user preferences for allergies
        if context.user_preferences.allergies:
            for allergy in context.user_preferences.allergies:
                if allergy.lower() in item.lower():
                    return {
                        "should_add": False,
                        "reason": "allergy_concern",
                        "allergy": allergy
                    }
        
        # Check dietary restrictions
        if context.user_preferences.dietary != "none":
            if context.user_preferences.dietary == "vegetarian" and any(meat in item.lower() for meat in ["beef", "pork", "chicken", "meat"]):
                return {
                    "should_add": False,
                    "reason": "dietary_restriction",
                    "restriction": "vegetarian"
                }
        
        return {"should_add": True, "reason": "safe_to_add", "quantity": 1}
    
    def should_remove_item(self, user_id: str, item: str) -> Dict[str, Any]:
        """Intelligent decision on whether to remove an item based on context."""
        shopping_list_state = shopping_list_service.get_shopping_list_state(user_id)
        
        if not shopping_list_state:
            return {"should_remove": False, "reason": "no_items"}
        
        # Check if item exists in list
        for existing_item in shopping_list_state.items:
            if existing_item.name.lower() == item.lower() and not existing_item.removed:
                return {
                    "should_remove": True,
                    "reason": "user_request",
                    "item": existing_item.name,
                    "quantity": existing_item.quantity
                }
        
        return {"should_remove": False, "reason": "item_not_found"}
    
    def get_context_summary(self, user_id: str) -> str:
        """Generate a concise context summary for AI processing."""
        context = self.get_conversation_context(user_id)
        shopping_list_state = shopping_list_service.get_shopping_list_state(user_id)
        
        if not shopping_list_state:
            return "New user, no shopping list yet."
        
        # Get current items
        current_items = [item.name for item in shopping_list_state.items if not item.removed]
        
        # Get recent actions (last 3)
        recent_actions = shopping_list_state.action_history[-3:] if shopping_list_state.action_history else []
        
        # Format user preferences
        prefs = context.user_preferences
        preferences_text = ""
        if prefs.allergies:
            preferences_text += f"Allergies: {', '.join(prefs.allergies)}. "
        if prefs.dietary != "none":
            preferences_text += f"Dietary: {prefs.dietary}. "
        
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
                    action_descriptions.append("requested recipe")
                elif action.type == "clear_list":
                    action_descriptions.append("cleared list")
            
            action_summary = f"Recent: {', '.join(action_descriptions)}. "
        
        # Combine into summary
        summary_parts = []
        if preferences_text:
            summary_parts.append(preferences_text.strip())
        if current_items:
            summary_parts.append(f"Current list: {', '.join(current_items)}")
        if action_summary:
            summary_parts.append(action_summary.strip())
        
        return " ".join(summary_parts) if summary_parts else "No context available."
    
    def update_user_preferences(self, user_id: str, preferences: UserPreferences) -> bool:
        """Update user preferences and sync with conversation context."""
        try:
            # Update in shopping list service
            success = shopping_list_service.update_user_preferences(user_id, preferences)
            
            if success:
                # Update conversation context
                context = self.get_conversation_context(user_id)
                context.user_preferences = preferences
                logger.info(f"Updated user preferences for {user_id}")
            
            return success
        except Exception as e:
            logger.error(f"Failed to update user preferences: {str(e)}")
            return False
    
    def get_intelligent_suggestions(self, user_id: str, current_message: str) -> List[str]:
        """Generate intelligent suggestions based on context."""
        context = self.get_conversation_context(user_id)
        shopping_list_state = shopping_list_service.get_shopping_list_state(user_id)
        
        suggestions = []
        
        # Check for recipe context
        if "recipe" in current_message.lower() or "cook" in current_message.lower():
            context.current_flow = "recipe_shopping"
            suggestions.append("I can help you with recipe suggestions and ingredient lists.")
        
        # Check for dietary restrictions
        if context.user_preferences.dietary != "none":
            if context.user_preferences.dietary == "vegetarian":
                suggestions.append("I'll make sure to suggest vegetarian alternatives.")
            elif context.user_preferences.dietary == "vegan":
                suggestions.append("I'll suggest vegan-friendly options.")
        
        # Check for allergies
        if context.user_preferences.allergies:
            suggestions.append(f"I'll avoid items with {', '.join(context.user_preferences.allergies)}.")
        
        # Check for recently removed items
        if shopping_list_state and shopping_list_state.removed_items:
            recent_removals = [item.name for item in shopping_list_state.removed_items[-3:]]
            if recent_removals:
                suggestions.append(f"Recently removed: {', '.join(recent_removals)}")
        
        return suggestions
    
    def clear_context(self, user_id: str) -> None:
        """Clear conversation context for a user."""
        if user_id in self.conversation_contexts:
            del self.conversation_contexts[user_id]
            logger.info(f"Cleared conversation context for user {user_id}")

# Create a singleton instance
context_manager = ContextManager() 