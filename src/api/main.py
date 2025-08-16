from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from src.core.config import settings
from src.core.logging import get_logger
from src.services.chat_service import chat_service
from src.services.user_preferences import user_preferences
from src.services.context_manager import context_manager
from src.services.shopping_list_service import shopping_list_service
from src.services.recipe_service import recipe_service
from src.models.shopping_list import UserPreferences

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

class EnhancedUserPreferencesRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")
    dietary: str = Field(default="none", description="Dietary preference")
    allergies: List[str] = Field(default=[], description="List of allergies")
    preferences: List[str] = Field(default=[], description="Additional preferences")
    restrictions: List[str] = Field(default=[], description="Dietary restrictions")

class ContextSummaryResponse(BaseModel):
    user_id: str
    context_summary: str
    suggestions: List[str]

class RecipeRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")
    recipe_query: str = Field(..., min_length=1, description="Recipe request or query")

class SubstitutionRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")
    item: str = Field(..., min_length=1, description="Item to find substitutions for")

class ShoppingListSyncRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")
    items: List[str] = Field(default_factory=list, description="Updated shopping list items (strings)")

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

@app.post(f"{settings.API_V1_STR}/recipe/suggest")
async def suggest_recipe(request: RecipeRequest) -> Dict[str, Any]:
    """Suggest a recipe based on user preferences and current shopping list."""
    try:
        # Get user preferences
        user_prefs = user_preferences.get_all_preferences(request.user_id)
        
        # Convert to UserPreferences object
        prefs = UserPreferences()
        if user_prefs.get("dietary"):
            prefs.dietary = user_prefs["dietary"]
        if user_prefs.get("allergies"):
            prefs.allergies = user_prefs["allergies"].split(",") if isinstance(user_prefs["allergies"], str) else user_prefs["allergies"]
        
        # Get current shopping list
        current_list = shopping_list_service.get_shopping_list(request.user_id)
        
        # Get recipe suggestion
        recipe_result = recipe_service.suggest_recipe(prefs, current_list)
        
        return {
            "user_id": request.user_id,
            "recipe_suggestion": recipe_result.get("suggestion"),
            "missing_ingredients": recipe_result.get("missing_ingredients", []),
            "reason": recipe_result.get("reason", ""),
            "alternatives": recipe_result.get("alternatives", [])
        }
        
    except Exception as e:
        logger.error(f"Error suggesting recipe for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.post(f"{settings.API_V1_STR}/recipe/generate")
async def generate_recipe(request: RecipeRequest) -> Dict[str, Any]:
    """Generate a custom recipe using AI."""
    try:
        # Get user preferences
        user_prefs = user_preferences.get_all_preferences(request.user_id)
        
        # Convert to UserPreferences object
        prefs = UserPreferences()
        if user_prefs.get("dietary"):
            prefs.dietary = user_prefs["dietary"]
        if user_prefs.get("allergies"):
            prefs.allergies = user_prefs["allergies"].split(",") if isinstance(user_prefs["allergies"], str) else user_prefs["allergies"]
        
        # Generate recipe with AI
        recipe_result = recipe_service.generate_recipe_with_ai(request.recipe_query, prefs)
        
        return {
            "user_id": request.user_id,
            "recipe": recipe_result.get("suggestion"),
            "missing_ingredients": recipe_result.get("missing_ingredients", []),
            "reason": recipe_result.get("reason", ""),
            "error": recipe_result.get("error")
        }
        
    except Exception as e:
        logger.error(f"Error generating recipe for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.post(f"{settings.API_V1_STR}/substitutions")
async def get_substitutions(request: SubstitutionRequest) -> Dict[str, Any]:
    """Get substitution suggestions for an item based on user preferences."""
    try:
        # Get user preferences
        user_prefs = user_preferences.get_all_preferences(request.user_id)
        
        # Convert to UserPreferences object
        prefs = UserPreferences()
        if user_prefs.get("dietary"):
            prefs.dietary = user_prefs["dietary"]
        if user_prefs.get("allergies"):
            prefs.allergies = user_prefs["allergies"].split(",") if isinstance(user_prefs["allergies"], str) else user_prefs["allergies"]
        
        # Get substitutions
        substitutions = recipe_service.suggest_substitutions(request.item, prefs)
        
        return {
            "user_id": request.user_id,
            "original_item": request.item,
            "substitutions": substitutions,
            "reason": f"Based on {prefs.dietary} diet and allergies: {', '.join(prefs.allergies) if prefs.allergies else 'none'}"
        }
        
    except Exception as e:
        logger.error(f"Error getting substitutions for user {request.user_id}: {str(e)}")
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

@app.post(f"{settings.API_V1_STR}/preferences/enhanced")
async def set_enhanced_user_preferences(request: EnhancedUserPreferencesRequest) -> Dict[str, bool]:
    """Set enhanced user preferences with allergies and dietary restrictions."""
    try:
        # Create UserPreferences object
        user_prefs = UserPreferences(
            dietary=request.dietary,
            allergies=request.allergies,
            preferences=request.preferences,
            restrictions=request.restrictions
        )
        
        # Update via context manager
        success = context_manager.update_user_preferences(request.user_id, user_prefs)
        
        return {"success": success}
    except Exception as e:
        logger.error(f"Error setting enhanced preferences for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get(f"{settings.API_V1_STR}/context/{{user_id}}")
async def get_context_summary(user_id: str) -> ContextSummaryResponse:
    """Get context summary and intelligent suggestions for a user."""
    try:
        context_summary = context_manager.get_context_summary(user_id)
        
        # Get intelligent suggestions based on current context
        shopping_list_state = shopping_list_service.get_shopping_list_state(user_id)
        current_items = [item.name for item in shopping_list_state.items if not item.removed] if shopping_list_state else []
        
        # Generate suggestions based on current state
        suggestions = []
        if not current_items:
            suggestions.append("Your shopping list is empty. Try adding some items!")
        else:
            suggestions.append(f"You have {len(current_items)} items in your list.")
        
        # Add context-specific suggestions
        context_suggestions = context_manager.get_intelligent_suggestions(user_id, "")
        suggestions.extend(context_suggestions)
        
        return ContextSummaryResponse(
            user_id=user_id,
            context_summary=context_summary,
            suggestions=suggestions
        )
    except Exception as e:
        logger.error(f"Error getting context summary for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get(f"{settings.API_V1_STR}/shopping-list/state/{{user_id}}")
async def get_shopping_list_state(user_id: str) -> Dict[str, Any]:
    """Get enhanced shopping list state with action tracking."""
    try:
        state = shopping_list_service.get_shopping_list_state(user_id)
        if not state:
            return {
                "user_id": user_id,
                "items": [],
                "removed_items": [],
                "action_history": [],
                "user_preferences": {},
                "last_updated": None
            }
        
        return {
            "user_id": state.user_id,
            "items": [item.model_dump() for item in state.items],
            "removed_items": [item.model_dump() for item in state.removed_items],
            "action_history": [action.model_dump() for action in state.action_history],
            "user_preferences": state.user_preferences.model_dump(),
            "last_updated": state.last_updated.isoformat() if state.last_updated else None
        }
    except Exception as e:
        logger.error(f"Error getting shopping list state for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get(f"{settings.API_V1_STR}/shopping-list/items/{{user_id}}")
async def get_shopping_list_items(user_id: str) -> Dict[str, Any]:
    """Get items-only shopping list for a user (strings only)."""
    try:
        items = shopping_list_service.get_shopping_list(user_id)
        return {"user_id": user_id, "items": items}
    except Exception as e:
        logger.error(f"Error getting shopping list items for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.put(f"{settings.API_V1_STR}/shopping-list/sync")
async def sync_shopping_list(request: ShoppingListSyncRequest) -> Dict[str, Any]:
    """Synchronize the user's shopping list with the provided items (frontend edit)."""
    try:
        result = shopping_list_service.sync_shopping_list(request.user_id, request.items)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Sync failed"))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing shopping list for user {request.user_id}: {str(e)}")
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
    return {"status": "healthy", "service": settings.PROJECT_NAME} 