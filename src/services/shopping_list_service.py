from typing import List, Optional, Dict, Any
from datetime import datetime
from pymongo.errors import PyMongoError
from pydantic import BaseModel, Field

from src.core.database import db
from src.core.logging import get_logger
from src.core.constants import (
    SHOPPING_LIST_COLLECTION,
    ERROR_MESSAGES,
    VALIDATION_MESSAGES,
    SUCCESS_MESSAGES
)
from src.models.shopping_list import (
    ShoppingListItem,
    RemovedItem,
    ActionLog,
    UserPreferences,
    ShoppingListState,
    ConversationContext
)

logger = get_logger(__name__)

def clean_item_name(item_name: str) -> str:
    """Remove quantities and measurements from item names for generic product matching."""
    import re
    
    # More comprehensive patterns to remove quantities and measurements
    patterns = [
        # Fractions with units: "3/4 cup", "1/2 tsp", etc.
        r'^\d+(?:\.\d+)?\s*(?:/\d+)?\s*(?:cups?|tablespoons?|tbsp|teaspoons?|tsp|ounces?|oz|lbs?|pounds?|kg|grams?|g|cloves?|pieces?|slices?)\s+',
        # Fractions without units: "3/4", "1/2", etc.
        r'^\d+(?:\.\d+)?\s*(?:/\d+)?\s+',
        # Numbers with units: "1 cup", "2 tbsp", "1.5 lbs", etc.
        r'^\d+(?:\.\d+)?\s*(?:cups?|tablespoons?|tbsp|teaspoons?|tsp|ounces?|oz|lbs?|pounds?|kg|grams?|g|cloves?|pieces?|slices?)\s+',
        # Just numbers at start: "1", "2", "1.5", etc.
        r'^\d+(?:\.\d+)?\s+',
        # Common suffixes
        r'\s+(?:to taste|optional|for serving|for garnish|plus more for dusting)\s*$',
        # Preparation methods
        r'\s+(?:finely chopped|minced|grated|diced|shredded)\s*$',
        # Parenthetical additions
        r'\s*\([^)]*\)\s*$',
    ]
    
    cleaned_name = item_name
    for pattern in patterns:
        cleaned_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE)
    
    # Clean up extra spaces and normalize
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
    
    return cleaned_name

class ShoppingListService:
    def __init__(self):
        self.collection = db.get_db()[SHOPPING_LIST_COLLECTION]
    
    def add_items(self, user_id: str, items: List[str]) -> bool:
        """Add items to a user's shopping list."""
        if not user_id or not isinstance(user_id, str):
            logger.error(VALIDATION_MESSAGES["USER_ID_REQUIRED"], user_id=user_id)
            return False
            
        if not items or not isinstance(items, list):
            logger.error(VALIDATION_MESSAGES["INVALID_ITEMS"], items=items)
            return False
            
        try:
            # Convert items to ShoppingListItem objects
            shopping_items = []
            for item in items:
                try:
                    shopping_items.append(ShoppingListItem(
                        name=item,
                        added_at=datetime.utcnow(),
                        source="direct_addition"
                    ))
                except ValueError as e:
                    logger.warning(f"Invalid item format: {item}", error=str(e))
                    continue
            
            if not shopping_items:
                logger.error(VALIDATION_MESSAGES["NO_VALID_ITEMS"])
                return False
                
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$addToSet': {
                        'items': {
                            '$each': [item.model_dump() for item in shopping_items]
                        }
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                },
                upsert=True
            )
            
            # Log action for agentic tracking
            if result.acknowledged:
                self._log_action(user_id, "item_addition", items)
            
            return result.acknowledged
        except PyMongoError as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], user_id=user_id, error=str(e))
            return False
    
    def delete_items(self, user_id: str, items: List[str]) -> bool:
        """Delete items from a user's shopping list."""
        if not user_id or not isinstance(user_id, str):
            logger.error(VALIDATION_MESSAGES["USER_ID_REQUIRED"], user_id=user_id)
            return False
            
        if not items or not isinstance(items, list):
            logger.error(VALIDATION_MESSAGES["INVALID_ITEMS"], items=items)
            return False
            
        try:
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$pull': {
                        'items': {
                            '$in': [{'name': item} for item in items]
                        }
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            # Log action and add to removed items
            if result.acknowledged:
                self._log_action(user_id, "item_removal", items, reason="user_request")
                self._add_to_removed_items(user_id, items)
            
            return result.acknowledged
        except PyMongoError as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], user_id=user_id, error=str(e))
            return False
    
    def clear_shopping_list(self, user_id: str) -> bool:
        """Clear all items from a user's shopping list."""
        if not user_id or not isinstance(user_id, str):
            logger.error(VALIDATION_MESSAGES["USER_ID_REQUIRED"], user_id=user_id)
            return False
            
        try:
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'items': [],
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Log action
            if result.acknowledged:
                self._log_action(user_id, "clear_list", [], reason="user_request")
            
            return result.acknowledged
        except PyMongoError as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], user_id=user_id, error=str(e))
            return False
    
    def get_shopping_list(self, user_id: str) -> List[str]:
        """Get all items from a user's shopping list."""
        if not user_id or not isinstance(user_id, str):
            logger.error(VALIDATION_MESSAGES["USER_ID_REQUIRED"], user_id=user_id)
            return []
            
        try:
            result = self.collection.find_one({'user_id': user_id})
            if not result:
                return []
                
            items = result.get('items', [])
            # Convert ShoppingListItem objects back to strings
            return [item['name'] if isinstance(item, dict) else item for item in items]
        except PyMongoError as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], user_id=user_id, error=str(e))
            return []

    # New agentic methods
    def get_shopping_list_state(self, user_id: str) -> Optional[ShoppingListState]:
        """Get enhanced shopping list state with action tracking."""
        if not user_id or not isinstance(user_id, str):
            logger.error(VALIDATION_MESSAGES["USER_ID_REQUIRED"], user_id=user_id)
            return None
            
        try:
            result = self.collection.find_one({'user_id': user_id})
            if not result:
                return ShoppingListState(
                    user_id=user_id,
                    last_updated=datetime.utcnow()
                )
            
            # Convert to enhanced state
            items = []
            for item_data in result.get('items', []):
                if isinstance(item_data, dict):
                    items.append(ShoppingListItem(**item_data))
                else:
                    items.append(ShoppingListItem(
                        name=item_data,
                        added_at=datetime.utcnow()
                    ))
            
            removed_items = []
            for removed_data in result.get('removed_items', []):
                removed_items.append(RemovedItem(**removed_data))
            
            action_history = []
            for action_data in result.get('action_history', []):
                action_history.append(ActionLog(**action_data))
            
            user_preferences = UserPreferences(**result.get('user_preferences', {}))
            
            return ShoppingListState(
                user_id=user_id,
                items=items,
                removed_items=removed_items,
                action_history=action_history,
                user_preferences=user_preferences,
                last_updated=result.get('updated_at', datetime.utcnow())
            )
        except PyMongoError as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], user_id=user_id, error=str(e))
            return None

    def add_item_with_context(self, user_id: str, item: str, quantity: int = 1, 
                            source: str = "direct_addition") -> bool:
        """Add item with context awareness and action tracking."""
        if not user_id or not isinstance(user_id, str):
            logger.error(VALIDATION_MESSAGES["USER_ID_REQUIRED"], user_id=user_id)
            return False
            
        if not item or not isinstance(item, str):
            logger.error(VALIDATION_MESSAGES["INVALID_ITEMS"], items=[item])
            return False
        
        try:
            # Clean the item name to remove quantities
            cleaned_item_name = clean_item_name(item)
            
            # Check if item was recently removed
            state = self.get_shopping_list_state(user_id)
            if state:
                for removed_item in state.removed_items:
                    if removed_item.name.lower() == cleaned_item_name.lower():
                        logger.info(f"Item {cleaned_item_name} was recently removed, asking for confirmation")
                        # For now, just log it - in future we can ask for confirmation
                        pass
            
            # Add item with enhanced structure (using cleaned name)
            shopping_item = ShoppingListItem(
                name=cleaned_item_name,
                quantity=quantity,
                source=source,
                added_at=datetime.utcnow()
            )
            
            # Check if item already exists (by cleaned name only)
            existing_item = self.collection.find_one(
                {'user_id': user_id, 'items.name': {'$regex': f'^{cleaned_item_name}$', '$options': 'i'}}
            )
            
            if existing_item:
                logger.info(f"Item {item} already exists in shopping list")
                return True
            
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$push': {
                        'items': shopping_item.model_dump()
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                },
                upsert=True
            )
            
            # Log action
            if result.acknowledged:
                self._log_action(user_id, "item_addition", [cleaned_item_name], quantity)
            
            return result.acknowledged
        except PyMongoError as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], user_id=user_id, error=str(e))
            return False

    def sync_shopping_list(self, user_id: str, items: List[str]) -> Dict[str, Any]:
        """Synchronize the user's shopping list with the provided items.
        - Cleans input names
        - Dedupe case-insensitively
        - Computes diff vs current and applies adds/removals
        - Logs actions accordingly
        Returns a dict with added/removed and the updated items list.
        """
        if not user_id or not isinstance(user_id, str):
            logger.error(VALIDATION_MESSAGES["USER_ID_REQUIRED"], user_id=user_id)
            return {"success": False, "error": VALIDATION_MESSAGES["USER_ID_REQUIRED"]}

        if items is None or not isinstance(items, list):
            logger.error(VALIDATION_MESSAGES["INVALID_ITEMS"], items=items)
            return {"success": False, "error": VALIDATION_MESSAGES["INVALID_ITEMS"]}

        try:
            # Clean and dedupe incoming items
            cleaned_incoming = []
            seen = set()
            for raw in items:
                if not isinstance(raw, str) or not raw.strip():
                    continue
                cleaned = clean_item_name(raw.strip())
                key = cleaned.lower()
                if key not in seen:
                    seen.add(key)
                    cleaned_incoming.append(cleaned)

            # Current items (cleaned)
            current_items_raw = self.get_shopping_list(user_id)
            current_items_cleaned = []
            current_seen = set()
            for raw in current_items_raw:
                cleaned = clean_item_name(raw)
                key = cleaned.lower()
                if key not in current_seen:
                    current_seen.add(key)
                    current_items_cleaned.append(cleaned)

            # Compute diffs
            incoming_set = set(i.lower() for i in cleaned_incoming)
            current_set = set(i.lower() for i in current_items_cleaned)

            to_add_keys = incoming_set - current_set
            to_remove_keys = current_set - incoming_set

            # Map keys back to canonical names
            added = []
            removed = []

            # Add missing
            for key in to_add_keys:
                # find the representative from cleaned_incoming matching this key
                name = next((i for i in cleaned_incoming if i.lower() == key), None)
                if name:
                    if self.add_item_with_context(user_id, name, source="frontend_sync"):
                        added.append(name)

            # Remove extras
            for key in to_remove_keys:
                name = next((i for i in current_items_cleaned if i.lower() == key), None)
                if name:
                    if self.remove_item_with_tracking(user_id, name, reason="frontend_sync"):
                        removed.append(name)

            # Return updated state
            updated_state = self.get_shopping_list_state(user_id)
            updated_items = [item.name for item in updated_state.items] if updated_state else []

            return {
                "success": True,
                "added": added,
                "removed": removed,
                "items": updated_items
            }
        except PyMongoError as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], user_id=user_id, error=str(e))
            return {"success": False, "error": str(e)}

    def remove_item_with_tracking(self, user_id: str, item: str, reason: str = "user_request") -> bool:
        """Remove item with tracking and history."""
        if not user_id or not isinstance(user_id, str):
            logger.error(VALIDATION_MESSAGES["USER_ID_REQUIRED"], user_id=user_id)
            return False
            
        if not item or not isinstance(item, str):
            logger.error(VALIDATION_MESSAGES["INVALID_ITEMS"], items=[item])
            return False
        
        try:
            # Clean the item name for consistent matching
            cleaned_item_name = clean_item_name(item)
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$pull': {
                        'items': {
                            '$or': [
                                {'name': cleaned_item_name},
                                {'name': {'$regex': f'^{cleaned_item_name}$', '$options': 'i'}}
                            ]
                        }
                    },
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            # Log action and add to removed items
            if result.acknowledged:
                self._log_action(user_id, "item_removal", [cleaned_item_name], reason=reason)
                self._add_to_removed_items(user_id, [cleaned_item_name], reason)
            
            return result.acknowledged
        except PyMongoError as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], user_id=user_id, error=str(e))
            return False

    def _log_action(self, user_id: str, action_type: str, items: List[str], 
                   quantity: Optional[int] = None, reason: Optional[str] = None):
        """Log action for intelligent decision making."""
        try:
            action_log = ActionLog(
                type=action_type,
                items=items,
                quantity=quantity,
                reason=reason,
                timestamp=datetime.utcnow()
            )
            
            self.collection.update_one(
                {'user_id': user_id},
                {
                    '$push': {
                        'action_history': {
                            '$each': [action_log.model_dump()],
                            '$slice': -50  # Keep last 50 actions
                        }
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to log action: {str(e)}")

    def _add_to_removed_items(self, user_id: str, items: List[str], reason: str = "user_request"):
        """Add items to removed items history."""
        try:
            removed_items = []
            for item in items:
                removed_items.append(RemovedItem(
                    name=item,
                    removed_at=datetime.utcnow(),
                    reason=reason
                ).model_dump())
            
            self.collection.update_one(
                {'user_id': user_id},
                {
                    '$push': {
                        'removed_items': {
                            '$each': removed_items,
                            '$slice': -100  # Keep last 100 removed items
                        }
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to add to removed items: {str(e)}")

    def update_user_preferences(self, user_id: str, preferences: UserPreferences) -> bool:
        """Update user preferences for intelligent suggestions."""
        if not user_id or not isinstance(user_id, str):
            logger.error(VALIDATION_MESSAGES["USER_ID_REQUIRED"], user_id=user_id)
            return False
        
        try:
            result = self.collection.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'user_preferences': preferences.model_dump(),
                        'updated_at': datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            # Log action
            if result.acknowledged:
                self._log_action(user_id, "preference_update", [], reason="user_update")
            
            return result.acknowledged
        except PyMongoError as e:
            logger.error(ERROR_MESSAGES["GENERAL_ERROR"], user_id=user_id, error=str(e))
            return False

# Create a singleton instance
shopping_list_service = ShoppingListService() 