# GrocerEase Chatbot API Documentation

## Overview
The GrocerEase Chatbot API provides a conversational interface for recipe queries, shopping list management, and grocery item information. The API uses FastAPI and follows RESTful principles.

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