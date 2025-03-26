from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    user_id: str
    user_message: str
    bot_response: str
    timestamp: datetime

class ChatHistory(BaseModel):
    messages: List[Dict[str, str]]

class ChatRequest(BaseModel):
    user_id: str
    user_message: str

class ChatResponse(BaseModel):
    bot_response: str
    shopping_list: List[str] 