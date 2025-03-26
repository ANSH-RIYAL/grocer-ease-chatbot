import google.generativeai as genai
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure Gemini API
API_KEY = "AIzaSyAQoT5M5-Q33BNjJLQG4rBZ4TJS_WwO2Uo"
genai.configure(api_key=API_KEY)

# Chat history storage
chat_history = []

# Load prompts from JSON file
with open("prompts.json", "r") as file:
    prompts = json.load(file)

def initialize_model():
    """Initialize and return the Gemini model."""
    return genai.GenerativeModel("gemini-1.5-pro")

def get_gemini_response(user_message):
    """Generate a response from Gemini based on user input."""
    global chat_history
    
    # Append user message to chat history
    chat_history.append({"role": "user", "message": user_message})
    
    try:
        model = initialize_model()
        response = model.generate_content(user_message)
        ai_message = response.text.strip() if response.text else "I'm not sure how to respond."
        
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        ai_message = "An error occurred while generating a response. Please try again."
    
    # Append AI response to chat history
    chat_history.append({"role": "assistant", "message": ai_message})
    
    return ai_message

def extract_ingredients():
    """Extract ingredient names from the chat history."""
    prompt = prompts["extract_ingredients"]

    
    # Convert chat history to formatted string
    conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['message']}" for msg in chat_history])
    prompt += conversation_text
    
    try:
        model = initialize_model()
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error extracting ingredients: {e}")
        return "An error occurred while extracting ingredients."

def interactive_chat():
    """Start an interactive chat loop with the user."""
    print("Gemini AI Chatbot - Type 'exit' to end the chat.")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() == "exit":
            print("Extracting ingredients from chat history...\n")
            extracted_ingredients = extract_ingredients()
            print("Extracted Ingredients:")
            print(json.dumps(extracted_ingredients, indent=2))
            break
        
        response = get_gemini_response(user_input)
        print(f"Gemini: {response}")

if __name__ == "__main__":
    interactive_chat()
