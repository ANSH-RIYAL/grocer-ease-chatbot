# GrocerEase Chatbot API Documentation

## Overview
The GrocerEase Chatbot API provides a conversational interface for recipe queries, shopping list management, and grocery item information. The API uses FastAPI and follows RESTful principles.

## Docker Setup

### Prerequisites
- Docker Desktop installed
- MongoDB Atlas connection string
- Gemini API key
- Structured Prompting API key

### Running with Docker
1. **Start the Application**
   ```bash
   # Start in foreground mode (with logs)
   docker compose up

   # Start in detached mode (background)
   docker compose up -d
   ```

2. **Access the API**
   - Base URL: `http://localhost:8000`
   - API Version: v1
   - Full base URL: `http://localhost:8000/api/v1`

3. **Useful Docker Commands**
   ```bash
   # View logs
   docker compose logs
   docker compose logs -f  # Follow logs

   # Stop the application
   docker compose down

   # Rebuild and restart
   docker compose up --build

   # Restart service
   docker compose restart app
   ```

## Base URL
`http://localhost:8000/api/v1`

## Authentication
Currently, the API uses a simple user_id system for identification. Future versions may implement more robust authentication.

## Endpoints

### 1. Health Check
**Endpoint**: `/health`  
**Method**: GET  
**Description**: Check if the API is running and healthy  
**Response Format**:
```json
{
    "status": "healthy"
}
```

### 2. Chat
**Endpoint**: `/chat`  
**Method**: POST  
**Description**: Send a message to the chatbot and receive a response with updated shopping list  
**Request Format**:
```json
{
    "user_id": "string",      // Required, minimum length: 1
    "user_message": "string"  // Required, minimum length: 1
}
```
**Response Format**:
```json
{
    "bot_response": "string",    // The chatbot's response
    "shopping_list": ["string"]  // Current shopping list items
}
```
**Error Responses**:
- 400 Bad Request: Invalid request format or validation error
- 500 Internal Server Error: Server-side processing error

## Message Types and Processing

The chatbot processes different types of messages:

### 1. Recipe Queries
- **Example**: "How do I make pasta?"
- **Processing**: Generates detailed recipe instructions
- **Confidence Threshold**: 0.7

### 2. Shopping List Management
- **Add Items**: "Add milk to my shopping list"
- **Remove Items**: "Remove milk from my list"
- **Processing**: Updates user's shopping list
- **Confidence Threshold**: 0.7

### 3. Item Information
- **Example**: "What's the price of tomatoes?"
- **Processing**: Provides price information and availability details
- **Confidence Threshold**: 0.6

### 4. General Conversation
- **Example**: "Hello, how are you?"
- **Processing**: Handles general queries and greetings
- **Confidence Threshold**: 0.3

## Features

### 1. Chat History
- Messages are stored with timestamps
- Recent chat history is used for context
- Default history limit: 10 messages

### 2. Shopping List Management
- Automatic ingredient extraction from recipes
- Persistent storage per user
- Real-time updates

### 3. Message Classification
- Zero-shot classification using BART model
- Category-specific confidence thresholds
- Fallback to general conversation for low confidence

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/      # Unit tests
pytest tests/integration/  # Integration tests
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=src tests/
```

## Error Handling

The API implements comprehensive error handling:

1. **Validation Errors** (400)
   - Invalid request format
   - Missing required fields
   - Invalid field values

2. **Server Errors** (500)
   - Database connection issues
   - AI service failures
   - Unexpected processing errors

3. **Graceful Degradation**
   - Fallback responses for service failures
   - Empty shopping list on errors
   - Error logging for debugging

## Rate Limiting and Performance

- No rate limiting implemented
- Response time typically < 2 seconds
- MongoDB for persistent storage
- In-memory caching for frequent queries

## Development Setup

1. **Environment Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Unix
   .\venv\Scripts\activate   # Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Configuration**
   - Copy `.env.example` to `.env`
   - Update environment variables as needed

3. **Running the Server**
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

## Future Improvements

1. **Authentication & Authorization**
   - JWT-based authentication
   - Role-based access control
   - API key management

2. **Enhanced Features**
   - Multi-language support
   - Image recognition for recipes
   - Price comparison across stores
   - Shopping list sharing

3. **Performance Optimizations**
   - Redis caching
   - Rate limiting
   - Response compression

4. **Monitoring & Analytics**
   - Request/response metrics
   - Error tracking
   - Usage analytics

## Environment Variables

The following environment variables are required:

| Variable | Description | Default |
|----------|-------------|---------|
| MONGO_URI | MongoDB connection string | mongodb+srv://... |
| DB_NAME | Database name | chatbot_db |
| GEMINI_API_KEY | Gemini API key | - |
| GEMINI_MODEL_NAME | Gemini model name | gemini-1.5-pro |
| CLASSIFIER_TYPE | Message classifier type | bart |
| PREFERENCE_MODEL_TYPE | Preference model type | bart |
| STRUCTURED_PROMPTING_API_KEY | Structured prompting API key | - |

## Testing the API

### Using curl
```bash
# Health check
curl http://localhost:8000/health

# Chat endpoint
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "user_message": "I need to buy groceries for making pasta"
  }'

# Get user preferences
curl http://localhost:8000/api/v1/preferences/test_user
```

### Using Postman
1. Import the following collection:
   ```json
   {
     "info": {
       "name": "GrocerEase API",
       "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
     },
     "item": [
       {
         "name": "Health Check",
         "request": {
           "method": "GET",
           "url": "http://localhost:8000/health"
         }
       },
       {
         "name": "Chat",
         "request": {
           "method": "POST",
           "url": "http://localhost:8000/api/v1/chat",
           "header": [
             {
               "key": "Content-Type",
               "value": "application/json"
             }
           ],
           "body": {
             "mode": "raw",
             "raw": "{\n    \"user_id\": \"test_user\",\n    \"user_message\": \"I need to buy groceries for making pasta\"\n}"
           }
         }
       }
     ]
   }
   ```

## Troubleshooting

### Common Issues
1. **Container won't start**
   - Check Docker logs: `docker compose logs app`
   - Verify environment variables
   - Check MongoDB connection

2. **API not responding**
   - Verify container is running: `docker ps`
   - Check application logs: `docker compose logs app`
   - Ensure correct port mapping (8000:8000)

3. **Database connection issues**
   - Verify MongoDB URI
   - Check network connectivity
   - Ensure MongoDB Atlas IP whitelist includes your IP

### Debugging Commands
```bash
# View container status
docker ps

# View detailed logs
docker compose logs app

# Access container shell
docker compose exec app bash

# Restart services
docker compose restart app
``` 