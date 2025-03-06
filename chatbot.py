import google.generativeai as genai
import json
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatBot:
    def __init__(self, db, api_key):
        self.db = db
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")  # Initialize model only once
    
    def receive_message(self, user_message, user_id):
        """Process user message, generate AI response, store chat, and return response."""
        chat_history = self.retrieve_chat_history(user_id)
        response = self.generate_response(user_message, chat_history)
        self.store_chat(user_message, response, user_id)
        return response
    
    def generate_response(self, user_message, chat_history):
        """Generate a response from Gemini based on user input and chat history."""
        chat_history.append({"role": "user", "message": user_message})
        
        try:
            response = self.model.generate_content(self.format_chat_history(chat_history))
            ai_message = response.text.strip() if response.text else "I'm not sure how to respond."
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            ai_message = "An error occurred while generating a response. Please try again."
        
        chat_history.append({"role": "assistant", "message": ai_message})
        return ai_message
    
    def retrieve_chat_history(self, user_id):
        """Retrieve chat history for a given user_id from the database."""
        try:
            chat_collection = self.db['chat_history']
            user_chat_history = chat_collection.find({"user_id": user_id})
            chat_history = list(user_chat_history)
            chat_history = sorted(chat_history, key=lambda x: x['timestamp'])  # Sort by timestamp if necessary
            return [{"role": entry['role'], "message": entry['message']} for entry in chat_history]
        except Exception as e:
            logging.error(f"Error retrieving chat history: {e}")
            return []
    
    def store_chat(self, user_message, bot_response, user_id):
        """Store chat message in the database."""
        chat_entry = {
            "user_message": user_message,
            "bot_response": bot_response,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc)
        }
        success = self.insert_chat(chat_entry)
        if success:
            logging.info("Chat entry successfully inserted.")
        else:
            logging.error("Failed to insert chat entry.")
    
    def insert_chat(self, chat_entry):
        """Insert a chat entry into the database."""
        try:
            chat_collection = self.db['chat_history']
            result = chat_collection.insert_one(chat_entry)
            return result.acknowledged
        except Exception as e:
            logging.error(f"Database insertion error: {e}")
            return False
    
    def format_chat_history(self, chat_history):
        """Format the chat history for the model prompt."""
        formatted_history = "\n".join([f"{msg['role'].capitalize()}: {msg['message']}" for msg in chat_history])
        formatted_history += "\n\nGive response in 50 words or less.\n\n"
        return formatted_history
    
    def extract_ingredients(self, user_id):
        """Extract ingredient names from the chat history for a given user_id."""
        chat_history = self.retrieve_chat_history(user_id)
        prompt = (
            "You are an AI assistant skilled in analyzing conversations and extracting useful information. "
            "Given a conversation history, identify all the ingredients mentioned throughout the dialogue. "
            "Extract only the ingredient names, ensuring you include synonyms or variations if present. "
            "List each ingredient separately without duplicates. If quantities are mentioned, ignore them and focus only on the ingredient names. "
            "Return the output in the following format: {item_1, item_2, ...}\n\n"
            "**Example Input:**\n"
            "User: I'm making pasta. I have tomatoes and garlic, but I need parmesan and olive oil.\n"
            "Assistant: That sounds great! You might also want some salt and pepper.\n\n"
            "**Example Output:**\n"
            "{tomatoes, garlic, parmesan, olive oil, salt, pepper}\n\n"
            "If there is no conversation history or items to return, return an empty {\}"
            "**Conversation History:**\n"
        )
        
        conversation_text = self.format_chat_history(chat_history)
        prompt += conversation_text
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error extracting ingredients: {e}")
            return "An error occurred while extracting ingredients."
