from datetime import datetime, timezone

class ChatBot:
    def __init__(self, db):
        self.db = db

    def receive_message(self, user_message,user_id):
        response = self.generate_response(user_message)
        self.store_chat(user_message, response,user_id)
        return response

    def generate_response(self, user_message):
        # Placeholder for generative AI model response generation
        return "This is a placeholder Gemini response to: " + user_message

    def store_chat(self, user_message, bot_response,user_id):
        chat_entry = {
            "user_message": user_message,
            "bot_response": bot_response,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc)

        }
        success = self.insert_chat(chat_entry)
        if success:
            print("Chat entry successfully inserted.")
        else:
            print("Failed to insert chat entry.")

    def insert_chat(self, chat_entry):
        chat_collection = self.db['chat_history']
        result = chat_collection.insert_one(chat_entry)
        return result.acknowledged