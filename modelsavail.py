import requests

API_KEY = "AIzaSyBmLT_KCJt6U59ODOVAhUNtHbMCsh2HUGE"  # Replace with your actual API key
URL = f"https://generativelanguage.googleapis.com/v1/models?key={API_KEY}"

try:
    response = requests.get(URL)
    data = response.json()

    if response.status_code == 200:
        print("Available Models:")
        for model in data.get("models", []):
            print(f"- {model['name']}")
    else:
        print(f"Error {response.status_code}: {data}")

except Exception as e:
    print(f"Request failed: {e}")
