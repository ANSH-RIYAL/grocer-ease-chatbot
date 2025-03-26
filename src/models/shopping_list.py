from pydantic import BaseModel
from typing import List
from datetime import datetime

class ShoppingList(BaseModel):
    user_id: str
    items: List[str]
    updated_at: datetime

class ShoppingListUpdate(BaseModel):
    items: List[str] 