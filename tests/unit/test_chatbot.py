from config import MONGO_URI, DB_NAME
from database import get_db_connection
from chatbot import ChatBot


def main():
    db = get_db_connection(MONGO_URI, DB_NAME)
    chatbot = ChatBot(db)
    
    user_id = "example_user_id"  # Replace with actual user ID logic
    while True:
        user_message = input("You: ")
        if user_message.lower() in ['exit', 'quit']:
            break
        
        bot_response = chatbot.receive_message(user_message,user_id)
        print(f"Bot: {bot_response}")

if __name__ == "__main__":
    main()