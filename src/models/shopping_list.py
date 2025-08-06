from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class ShoppingListItem(BaseModel):
    """Enhanced shopping list item with action tracking."""
    name: str
    quantity: int = 1
    unit: str = ""
    source: str = "direct_addition"  # direct_addition, recipe_suggestion
    added_at: datetime
    removed: bool = False

class RemovedItem(BaseModel):
    """Track removed items to prevent accidental re-addition."""
    name: str
    removed_at: datetime
    reason: str = "user_request"

class ActionLog(BaseModel):
    """Log all actions for intelligent decision making."""
    type: str  # item_addition, item_removal, quantity_update, recipe_request, substitution
    items: List[str]
    quantity: Optional[int] = None
    reason: Optional[str] = None
    timestamp: datetime

class UserPreferences(BaseModel):
    """User preferences for intelligent suggestions."""
    dietary: str = "none"  # vegetarian, vegan, none
    allergies: List[str] = []  # ["nut allergy", "shellfish"]
    preferences: List[str] = []  # ["no_dairy", "gluten_free"]
    restrictions: List[str] = []

class ShoppingListState(BaseModel):
    """Enhanced shopping list with action tracking and user preferences."""
    user_id: str
    items: List[ShoppingListItem] = []
    removed_items: List[RemovedItem] = []
    action_history: List[ActionLog] = []
    user_preferences: UserPreferences = UserPreferences()
    last_updated: datetime

class ConversationContext(BaseModel):
    """Context for intelligent decision making."""
    user_id: str
    current_flow: str = "direct_shopping"  # recipe_shopping, direct_shopping
    active_recipe: Optional[str] = None
    user_preferences: UserPreferences = UserPreferences()
    recent_actions: List[ActionLog] = []

# Legacy models for backward compatibility
class ShoppingList(BaseModel):
    user_id: str
    items: List[str]
    updated_at: datetime

class ShoppingListUpdate(BaseModel):
    items: List[str] 