import google.generativeai as genai
import json
import logging
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ChatBot:
    def __init__(self, db, api_key):
        self.db = db
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")  # Initialize model only once

    def categorize_message(self, user_message):
        """Classify user messages into predefined categories."""
        categorization_prompt = """
        You are an AI assistant that categorizes user messages into one of the following types:

        1. **Recipe type** - User asks for a recipe.
        2. **Item Addition type** - User wants to add an item to their shopping list.
        3. **Item Information type** - User asks for details about an item (including price).
        4. **Update Cart type** - User wants to modify their cart.
        5. **Others** - Any message that does not fit the above categories.

        Classify the following message and return **only** the category name:

        User message: "{}"
        """

        try:
            response = self.model.generate_content(categorization_prompt.format(user_message))
            category = response.text.strip()
            return category if category in ["Recipe type", "Item Addition type", "Item Information type", "Update Cart type", "Others"] else "Others"
        except Exception as e:
            logging.error(f"Error categorizing message: {e}")
            return "Others"

    def receive_message(self, user_message, user_id, message_type):
        """Process user message, generate AI response based on type, store chat, and return response."""
        chat_history = self.retrieve_chat_history(user_id)
        print(user_id, user_message, message_type, chat_history, end = '\n\n\n\n')
        response = self.generate_response(user_message, chat_history, message_type)
        self.store_chat(user_message, response, user_id)
        return response

    def generate_response(self, user_message, chat_history, message_type):
        """Generate response based on categorized message type."""
        templates = {
            "Recipe type": """You are an AI assistant that provides recipes in a structured format. When the user asks for a recipe, respond in the following format:
            Dish: "<name of the dish>"
            Ingredients:
            1. "<ingredient 1>"
            2. "<ingredient 2>"
            3. "<ingredient 3>"
            ...

            Instructions:
            1. "<instruction 1>"
            2. "<instruction 2>"
            3. "<instruction 3>"
            ...

            Example Interaction:
            User: I want to make a sandwich.  
            Response:
            Dish: "Sandwich"
            Ingredients:
            1. "2 slices of bread"
            2. "2 slices of cheese"
            3. "1 tablespoon of butter"
            4. "Lettuce"
            5. "Tomato slices"

            Instructions: 
            1. "Spread butter on one side of each slice of bread."
            2. "Place cheese, lettuce, and tomato slices between the bread slices."
            3. "Press the sandwich lightly and serve."

            Now, respond to the following user request in the same format.

            User Request:
            "{}"
            """,
            "Item Addition type": "User wants to add an item. Respond with a confirmation message: '{}'",
            "Item Information type": "Provide detailed information and price for the requested item: '{}'",
            "Update Cart type": "User wants to update their cart. Confirm and provide update: '{}'",
            "Others": "Normal conversation response: '{}'"
        }
        # print(templates["Recipe type"],'\n\n\n\n')
        print("Recipe type" == message_type, message_type, end = '\n\n\n\n')
        # print(templates[str(message_type).strip()],'\n\n\n\n')

        print(templates[message_type],'\n\n\n\n')

        formatted_prompt = templates[message_type].format(user_message)
        print('THIS IS THE FORMATTED PROMPT\n', formatted_prompt, end = '\n\n\n\n')

        try:
            response = self.model.generate_content(formatted_prompt)
            print(response.text, end = '\n\n\n\n')
            return self.parse_response(response.text)
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return "An error occurred while generating a response. Please try again."

    def parse_response(self, response_text):
        """Parse the model's response and handle any potential issues."""
        # Strip unwanted characters like backticks and extra spaces.
        cleaned_response = response_text.strip().lstrip("```").rstrip("```").strip()

        print(cleaned_response, end = '\n\n\n\n')
        # Attempt to parse the response as JSON
        try:
            # Directly parse the cleaned response as a JSON list
            response_data = json.loads(cleaned_response)
            return response_data
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON response: {response_text}")
            # If JSON parsing fails, return the raw response as a fallback
            return response_text


    def retrieve_chat_history(self, user_id):
        """Retrieve chat history for a given user_id from the database."""
        try:
            chat_collection = self.db["chat_history"]
            chat_history = list(chat_collection.find({"user_id": user_id}).sort("timestamp"))
            return [{"role": "user", "message": entry["user_message"]} for entry in chat_history] + \
                   [{"role": "assistant", "message": entry["bot_response"]} for entry in chat_history]
        except Exception as e:
            logging.error(f"Error retrieving chat history: {e}")
            return []

    def store_chat(self, user_message, bot_response, user_id):
        """Store chat message in the database."""
        try:
            chat_collection = self.db["chat_history"]
            chat_collection.insert_one({"user_message": user_message, "bot_response": bot_response, "user_id": user_id, "timestamp": datetime.now(timezone.utc)})
        except Exception as e:
            logging.error(f"Database insertion error: {e}")

    def extract_ingredients(self, user_id):
        """Extract ingredient names from the chat history for a given user_id."""
        chat_history = self.retrieve_chat_history(user_id)
        prompt = ("""
        You are an AI assistant skilled in analyzing conversations and extracting useful information.  
        Your task is to extract all ingredient names mentioned throughout the conversation history.  

        Instructions:  
        - Identify all ingredients in the conversation, including synonyms or variations.  
        - Ignore quantities and focus only on the ingredient names.  
        - List each ingredient separately without duplicates.  
        - Return the output as a **JSON list**, like this:  

        ["item_1", "item_2", "item_3"]

        Example 1:  
        Input:  
        User: I'm making pasta. I have tomatoes and garlic, but I need parmesan and olive oil.  
        Assistant: That sounds great! You might also want some salt and pepper.  

        Output:  
        ["tomatoes", "garlic", "parmesan", "olive oil", "salt", "pepper"]

        Example 2 (No ingredients mentioned):  
        Input:  
        User: What’s your favorite dish?  
        Assistant: I love Italian food!  

        Output:  
        []

        Now, analyze the following conversation history and return the extracted ingredients in the required format.  

        Conversation History:  
        """)
        
        conversation_text = self.format_chat_history(chat_history)
        prompt += conversation_text

        try:
            response = self.model.generate_content(prompt)
            # Clean up response by removing extra characters (backticks or markdown)
            cleaned_response = response.text.strip().lstrip("```").rstrip("```").strip()

            # Attempt to parse the cleaned response as JSON
            ingredients = json.loads(cleaned_response)
            
            # Ensure ingredients are returned in a list format
            if isinstance(ingredients, list):
                return ingredients
            else:
                logging.error("Extracted ingredients are not in list format.")
                return []
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON response: {response.text}")
            return []
        except Exception as e:
            logging.error(f"Error extracting ingredients: {e}")
            return []


    def format_chat_history(self, chat_history):
        """Format the chat history for the model prompt."""
        formatted_history = "\n".join([f"{msg['role'].capitalize()}: {msg['message']}" for msg in chat_history])
        formatted_history += "\n\nGive response in 200 words or less.\n\n"
        return formatted_history
