import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://grocerEase:pinakisir123@grocerease1.tzatn.mongodb.net/?retryWrites=true&w=majority&appName=GrocerEase1")
DB_NAME = os.getenv("DB_NAME", "chatbot_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "chat_history")

AI_MODEL_API_KEY = os.getenv("AI_MODEL_API_KEY", "AIzaSyAQoT5M5-Q33BNjJLQG4rBZ4TJS_WwO2Uo")
AI_MODEL_ENDPOINT = os.getenv("AI_MODEL_ENDPOINT", "https://api.example.com/generate")