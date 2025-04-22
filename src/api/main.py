from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from src.core.config import settings
from src.core.logging import get_logger
from src.services.chat_service import chat_service
from src.services.user_preferences import user_preferences

logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")
    user_message: str = Field(..., min_length=1, description="User message")

class PreferenceRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")
    preference: str = Field(..., min_length=1, description="Preference name")
    value: str = Field(..., min_length=1, description="Preference value")

@app.post(f"{settings.API_V1_STR}/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """Handle chat requests and return bot response with shopping list."""
    try:
        logger.info(
            "Received chat request",
            user_id=request.user_id,
            message_length=len(request.user_message)
        )
        
        # Get user preferences
        user_prefs = user_preferences.get_all_preferences(request.user_id)
        
        response = chat_service.process_message(
            request.user_id,
            request.user_message,
            user_preferences=user_prefs
        )
        
        return response
        
    except ValueError as e:
        logger.error(
            "Validation error in chat request",
            user_id=request.user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(
            "Error processing chat request",
            user_id=request.user_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get(f"{settings.API_V1_STR}/preferences/{{user_id}}")
async def get_user_preferences(user_id: str) -> Dict[str, str]:
    """Get all preferences for a user."""
    try:
        preferences = user_preferences.get_all_preferences(user_id)
        return preferences
    except Exception as e:
        logger.error(f"Error getting preferences for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.post(f"{settings.API_V1_STR}/preferences")
async def set_user_preference(request: PreferenceRequest) -> Dict[str, bool]:
    """Set a preference for a user."""
    try:
        success = user_preferences.set_preference(
            request.user_id,
            request.preference,
            request.value
        )
        return {"success": success}
    except Exception as e:
        logger.error(f"Error setting preference for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.delete(f"{settings.API_V1_STR}/preferences/{{user_id}}")
async def clear_user_preferences(user_id: str) -> Dict[str, bool]:
    """Clear all preferences for a user."""
    try:
        success = user_preferences.clear_preferences(user_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Error clearing preferences for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"} 