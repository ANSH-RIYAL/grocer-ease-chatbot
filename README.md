# GrocerEase Chatbot

A smart chatbot service that helps users with recipes, shopping lists, and grocery-related queries.

## Features

- Natural language processing using Google's Gemini AI
- Recipe recommendations with ingredients and instructions
- Automatic shopping list management
- Chat history tracking
- RESTful API interface

## Prerequisites

- Python 3.8+
- MongoDB Atlas account
- Google Gemini API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/grocer-ease-chatbot.git
cd grocer-ease-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with the following variables:
```
MONGO_URI=your_mongodb_uri
DB_NAME=chatbot_db
GEMINI_API_KEY=your_gemini_api_key
LOG_LEVEL=INFO
```

## Usage

1. Start the application:
```bash
python src/main.py
```

2. The API will be available at `http://localhost:8000`

3. API Documentation will be available at:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Chat Endpoint
- **POST** `/api/v1/chat`
- Request body:
```json
{
    "user_id": "string",
    "user_message": "string"
}
```
- Response:
```json
{
    "bot_response": "string",
    "shopping_list": ["string"]
}
```

### Health Check
- **GET** `/health`
- Response:
```json
{
    "status": "healthy"
}
```

## Project Structure

```
grocer-ease-chatbot/
├── src/
│   ├── api/
│   │   └── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── logging.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── chat_service.py
│   │   └── shopping_list_service.py
│   └── main.py
├── tests/
├── .env
├── requirements.txt
└── README.md
```

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black .
isort .
```

### Type Checking
```bash
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 