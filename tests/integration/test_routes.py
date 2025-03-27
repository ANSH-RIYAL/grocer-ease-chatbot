import requests
import json
from datetime import datetime

def test_chat_endpoint(user_id, message):
    # Test new implementation
    new_response = requests.post(
        "http://localhost:8000/api/v1/chat",
        json={"user_id": user_id, "user_message": message}
    )
    new_data = new_response.json()
    
    # Test old implementation
    old_response = requests.post(
        "http://localhost:8001/chat",
        json={"user_id": user_id, "user_message": message}
    )
    old_data = old_response.json()
    
    # Compare responses
    print(f"\nTesting message: {message}")
    print("\nNew Implementation Response:")
    print(json.dumps(new_data, indent=2))
    print("\nOld Implementation Response:")
    print(json.dumps(old_data, indent=2))
    
    # Check if responses are equivalent
    assert new_response.status_code == old_response.status_code, "Status codes don't match"
    assert "bot_response" in new_data, "New response missing bot_response"
    assert "bot_response" in old_data, "Old response missing bot_response"
    assert "shopping_list" in new_data, "New response missing shopping_list"
    assert "shopping_list" in old_data, "Old response missing shopping_list"
    
    print("\n✅ Responses match in structure")
    return new_data, old_data

def main():
    # Test cases
    test_cases = [
        ("test_user_1", "How do I make pasta?"),
        ("test_user_1", "Add milk to my shopping list"),
        ("test_user_1", "What's the price of tomatoes?"),
        ("test_user_1", "Remove milk from my shopping list"),
        ("test_user_2", "How do I make a sandwich?"),
        ("test_user_2", "Add bread to my shopping list"),
    ]
    
    print("Starting route comparison tests...")
    print("=" * 50)
    
    for user_id, message in test_cases:
        try:
            new_data, old_data = test_chat_endpoint(user_id, message)
            print("=" * 50)
        except AssertionError as e:
            print(f"\n❌ Test failed: {str(e)}")
            print("=" * 50)
        except Exception as e:
            print(f"\n❌ Error occurred: {str(e)}")
            print("=" * 50)

if __name__ == "__main__":
    main() 