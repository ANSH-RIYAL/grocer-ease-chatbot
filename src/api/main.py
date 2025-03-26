from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any

from src.core.config import settings
from src.core.logging import get_logger
from src.services.chat_service import chat_service

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

@app.post(f"{settings.API_V1_STR}/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """Handle chat requests and return bot response with shopping list."""
    try:
        logger.info(
            "Received chat request",
            user_id=request.user_id,
            message_length=len(request.user_message)
        )
        
        response = chat_service.process_message(
            request.user_id,
            request.user_message
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

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"} 