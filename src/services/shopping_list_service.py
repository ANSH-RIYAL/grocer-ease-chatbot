from typing import List, Optional
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

logger = get_logger(__name__)

class ShoppingListItem(BaseModel):
    """Model for shopping list items."""
    name: str = Field(..., min_length=1, max_length=100)
    quantity: Optional[int] = Field(default=1, ge=1)
    unit: Optional[str] = Field(default=None, max_length=20)

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
                    shopping_items.append(ShoppingListItem(name=item))
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

# Create a singleton instance
shopping_list_service = ShoppingListService() 