# PROJECT STRUCTURE

## Directory Layout
```
grocer-ease-chatbot/
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI application with routes
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── constants.py         # Application constants
│   │   ├── database.py          # MongoDB connection
│   │   ├── logging.py           # Structured logging setup
│   │   ├── message_contexts.py  # AI prompt contexts
│   │   └── prompt_safety.py     # Input validation and safety
│   ├── models/
│   │   ├── chat.py              # Chat-related Pydantic models
│   │   └── shopping_list.py     # Shopping list models
│   ├── services/
│   │   ├── ai_service.py        # Google Gemini AI integration
│   │   ├── chat_service.py      # Main message processing pipeline
│   │   ├── message_classifier.py # BART/Gemini intent classification
│   │   ├── shopping_list_service.py # Shopping list CRUD operations
│   │   └── user_preferences.py  # User preference management
│   └── main.py                  # Application entry point
├── tests/
│   ├── conftest.py              # Test configuration and fixtures
│   ├── integration/             # Integration tests
│   │   ├── test_api.py         # API endpoint tests
│   │   ├── test_api_endpoints.py # Comprehensive API tests
│   │   └── test_routes.py      # Route-specific tests
│   └── unit/                    # Unit tests
│       ├── test_ai_service.py  # AI service tests
│       ├── test_chat_service.py # Chat service tests
│       ├── test_message_classifier.py # Classification tests
│       └── test_shopping_list_service.py # Shopping list tests
├── requirements.txt             # Python dependencies
├── pytest.ini                  # Pytest configuration
└── .gitignore                  # Git ignore rules
```

## Layer Responsibilities
- **/src/api:** Define API routes only, no business logic
- **/src/services:** Business logic and agentic processing
- **/src/models:** Data schemas and Pydantic models
- **/src/core:** Infrastructure (config, database, logging, safety)
- **/tests:** Unit and integration tests

## API Integration Rules
- Use only JSON endpoints
- Follow naming conventions (`/api/v1/chat`, `/api/v1/preferences/{user_id}`)
- Responses must include `bot_response`, `shopping_list`, `preferences` fields
- Error responses include `error`, `detail`, `status_code` fields
- All endpoints return JSON responses

## Agentic Logic Flow
- ChatService orchestrates the processing pipeline
- MessageClassifier determines intent (recipe, add item, item info, etc.)
- AIService generates intelligent responses using Gemini
- ShoppingListService manages list updates
- UserPreferencesService handles dietary preferences
- Context management across conversation history

## Current API Endpoints
- `POST /api/v1/chat` - Chat processing with JSON request/response
- `GET /api/v1/preferences/{user_id}` - Get user preferences
- `POST /api/v1/preferences` - Set user preferences
- `DELETE /api/v1/preferences/{user_id}` - Clear user preferences
- `GET /health` - Health check endpoint

## Current Data Models
```json
// Chat Message
{
  "user_id": "string",
  "user_message": "string",
  "bot_response": "string",
  "timestamp": "datetime"
}

// Shopping List Item
{
  "name": "string",
  "quantity": "integer",
  "unit": "string"
}

// User Preferences
{
  "user_id": "string",
  "preferences": {
    "vegetarian": "yes/no/not_set",
    "gluten_free": "yes/no/not_set",
    "dairy_free": "yes/no/not_set"
  }
}
```

## Current Error Handling
- **400 Bad Request**: Invalid input validation
- **500 Internal Server Error**: Server-side processing errors
- **Graceful Degradation**: Fallback responses for service failures
- **Structured Logging**: Error tracking and monitoring

## Current Testing Framework
- **Unit Tests**: Individual service and function testing
- **Integration Tests**: API endpoint testing
- **Mock Testing**: External dependencies
- **Database Testing**: Test fixtures and cleanup
- **Coverage**: Target > 80% code coverage

## Current Performance Features
- **Response Time**: < 2 seconds for chat requests
- **Retry Mechanisms**: Exponential backoff for AI calls
- **Connection Pooling**: Database optimization
- **Structured Logging**: Performance monitoring

## Current Security Measures
- **Input Validation**: Pydantic models with validation
- **CORS Configuration**: Cross-origin request handling
- **Prompt Safety**: Input sanitization and validation
- **Environment Variables**: Secure configuration management

## Current Limitations (To Be Addressed)
- No rate limiting implementation
- Limited caching mechanisms
- No authentication/authorization
- No monitoring or analytics
- Limited error recovery strategies
- No performance optimization

## Environment Variables Required
```bash
MONGO_URI=mongodb+srv://...
DB_NAME=chatbot_db
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=gemini-2.0-flash
CLASSIFIER_TYPE=bart
PREFERENCE_MODEL_TYPE=bart
STRUCTURED_PROMPTING_API_KEY=your_structured_prompting_key
LOG_LEVEL=INFO
CORS_ORIGINS=["*"]
```

## Dependencies
- **FastAPI**: Web framework
- **Pymongo**: MongoDB driver
- **Google Generative AI**: Gemini API integration
- **Transformers**: BART model for classification
- **Pydantic**: Data validation
- **Structlog**: Structured logging
- **Tenacity**: Retry mechanisms
- **Pytest**: Testing framework

## Project Structure Constraints
- Fixed src/ structure with api/, services/, core/, models/
- No folder name changes once initialized
- Pure API service - no frontend components
- Maintain existing service structure and patterns

## Quality Assurance Requirements
- **Code Quality**: PEP 8 with Black formatting
- **Type Hints**: All functions must have type hints
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit and integration tests
- **Error Handling**: Comprehensive error scenarios
- **Performance**: < 2 second response times
- **Security**: Input validation and sanitization

## External Service Integration
- **Google Gemini AI:** Primary AI service for response generation
- **BART Model:** Message classification (transformers library)
- **MongoDB Atlas:** Database for chat history, shopping lists, preferences
- **Retry Mechanisms:** Exponential backoff for AI service failures
- **Fallback Strategies:** Graceful degradation when services fail

## Project Setup Tips
- `.env` required for API keys and database connection
- `uvicorn src.api.main:app --reload` for development
- MongoDB Atlas for database hosting
- Environment variables for all external services 