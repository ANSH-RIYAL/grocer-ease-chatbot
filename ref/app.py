from fastapi import FastAPI, HTTPException
from pymongo import MongoClient, errors as mongo_errors
from pydantic import BaseModel
import json
import logging
from config import MONGO_URI, DB_NAME
from database import get_db_connection

# Import ChatBot and ShoppingListManager classes
from chatbot import ChatBot
from shopping_list import ShoppingListManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Print to console
        logging.FileHandler("app.log"),  # Log to a file
    ],
)

# Initialize FastAPI app
app = FastAPI()

# Try to connect to the database
try:
    db = get_db_connection(MONGO_URI, DB_NAME)
    logging.info("Successfully connected to the database.")
except mongo_errors.ConnectionError as e:
    logging.error(f"Error connecting to the database: {e}")
    db = None  # Assume no connection is established

# Initialize ChatBot and ShoppingListManager instances
chatbot = ChatBot(db, api_key="AIzaSyAQoT5M5-Q33BNjJLQG4rBZ4TJS_WwO2Uo")
shopping_list_manager = ShoppingListManager(db)

# Request model
class ChatRequest(BaseModel):
    user_id: str
    user_message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    user_id = request.user_id
    user_message = request.user_message

    if not user_id or not user_message:
        logging.warning("Missing user_id or user_message.")
        raise HTTPException(status_code=400, detail="Missing user_id or user_message")

    logging.info(f"Received message from user {user_id}: {user_message}")

    # Categorize user message
    try:
        message_type = chatbot.categorize_message(user_message)
        logging.info(f"Categorized message as: {message_type}")
    except Exception as e:
        logging.error(f"Error categorizing message: {e}")
        message_type = "Others"

    # Get chatbot response based on categorized type
    try:
        bot_response = chatbot.receive_message(user_message, user_id, message_type)
        # bot_response = chatbot.receive_message(user_message, user_id, "Recipe type")
        logging.info(f"Bot response: {bot_response}")
    except Exception as e:
        logging.error(f"Error generating chatbot response: {e}")
        bot_response = "Sorry, I couldn't understand your message."

    # Extract updated shopping list (ingredients from chat history)
    try:
        updated_shopping_list = chatbot.extract_ingredients(user_id)
        logging.info(f"Updated shopping list: {updated_shopping_list}")
    except Exception as e:
        logging.error(f"Error extracting ingredients: {e}")
        updated_shopping_list = []

    # Add items to the shopping list in the database
    try:
        shopping_list_manager.add_items(user_id, updated_shopping_list)
        logging.info(f"Shopping list for user {user_id} updated successfully in the database.")
    except Exception as e:
        logging.error(f"Error adding items to shopping list for user {user_id}: {e}")

    # Retrieve the updated shopping list from the database
    try:
        shopping_list = shopping_list_manager.get_shopping_list(user_id)
        logging.info(f"Shopping list for user {user_id} fetched successfully: {shopping_list}")
    except Exception as e:
        logging.error(f"Error fetching shopping list for user {user_id}: {e}")
        shopping_list = []

    return {"bot_response": bot_response, "shopping_list": shopping_list}
