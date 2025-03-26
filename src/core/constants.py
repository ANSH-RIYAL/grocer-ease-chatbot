"""Constants and prompts used throughout the application."""

# API Endpoints
API_V1_STR = "/api/v1"
CHAT_ENDPOINT = f"{API_V1_STR}/chat"
HEALTH_CHECK_ENDPOINT = f"{API_V1_STR}/health"

# Database Collections
CHAT_COLLECTION = "chat_history"
SHOPPING_LIST_COLLECTION = "shopping_list"

# AI Service Prompts
CATEGORIZATION_PROMPT = """
You are an AI assistant that categorizes user messages into one of the following types:

1. **Recipe type** - User asks for a recipe.
2. **Item Addition type** - User wants to add an item to their shopping list.
3. **Item Information type** - User asks for details about an item (including price).
4. **Update Cart type** - User wants to modify their cart.
5. **Others** - Any message that does not fit the above categories.

Classify the following message and return **only** the category name:

User message: "{}"
"""

INGREDIENT_EXTRACTION_PROMPT = """
You are an AI assistant skilled in analyzing conversations and extracting useful information.  
Your task is to extract all ingredient names mentioned throughout the conversation history.  

Instructions:  
- Identify all ingredients in the conversation, including synonyms or variations.  
- Ignore quantities and focus only on the ingredient names.  
- List each ingredient separately without duplicates.  
- Return the output as a **JSON list**, like this:  

["item_1", "item_2", "item_3"]

Conversation History:  
"""

# Message Categories
VALID_CATEGORIES = [
    "Recipe type",
    "Item Addition type",
    "Item Information type",
    "Update Cart type",
    "Others"
]

# Error Messages
ERROR_MESSAGES = {
    "API_KEY_MISSING": "Gemini API key not found in environment variables",
    "API_KEY_INVALID": "Invalid Gemini API key provided",
    "AI_SERVICE_INIT_FAILED": "Failed to initialize AI service",
    "INVALID_PROMPT": "Invalid prompt provided",
    "EMPTY_RESPONSE": "Empty response from AI model",
    "INVALID_MESSAGE": "Invalid message provided",
    "INVALID_CHAT_HISTORY": "Invalid chat history provided",
    "INVALID_INGREDIENTS": "Invalid ingredients format",
    "GENERAL_ERROR": "An error occurred while generating a response. Please try again."
}

# Validation Messages
VALIDATION_MESSAGES = {
    "USER_ID_REQUIRED": "User ID is required",
    "MESSAGE_REQUIRED": "Message is required",
    "INVALID_ITEMS": "Invalid items provided",
    "NO_VALID_ITEMS": "No valid items to add"
}

# Success Messages
SUCCESS_MESSAGES = {
    "AI_SERVICE_INIT": "AI service initialized successfully",
    "SHOPPING_LIST_UPDATE": "Shopping list for user {} updated successfully in the database",
    "SHOPPING_LIST_FETCH": "Shopping list for user {} fetched successfully: {}"
} 