# IMPLEMENTATION GUIDE

## ChatGPT Prompt Templates
- "Help me define the phases for a chatbot API service that processes grocery shopping requests"
- "Convert this user story into a SCOPE_DOC Phase plan for agentic logic development"
- "Generate realistic JSON payload for a chat message requesting to add items to shopping list"
- "Review and improve the agentic logic flow in our ChatService pipeline"
- "Design integration patterns for Google Gemini AI service with fallback strategies"
- "Create testing strategies for AI service failure scenarios"

## Cursor Prompts

### Backend Development
- "Add a new route in `/src/api/main.py` for processing chat messages"
- "Implement logic in `/src/services/chat_service.py` to process user messages with agentic intelligence"
- "Update the AIService to generate better contextual responses using Gemini"
- "Enhance the MessageClassifier to improve intent recognition accuracy"
- "Add comprehensive error handling to the ShoppingListService"
- "Implement input validation for the chat endpoint using Pydantic models"

### Core Logic Implementation
- "Create a ChatService that handles message processing with context awareness"
- "Implement AIService with proper retry logic and fallback mechanisms"
- "Build MessageClassifier with confidence scoring and threshold management"
- "Add ShoppingListService with CRUD operations and data validation"
- "Create UserPreferencesService with preference management and integration"

### API Development
- "Create REST API endpoints for chat processing and user preferences"
- "Implement request/response validation for chat endpoint"
- "Add error handling and status codes for all API endpoints"
- "Create documentation for API endpoints with examples"
- "Implement health checks and monitoring endpoints"

## Integration Prompts

### Backend-Service Integration
- "Wire up the ChatService to properly integrate with AIService and ShoppingListService"
- "Ensure error messages from API are properly formatted and include appropriate status codes"
- "Test the complete agentic processing pipeline from API request to response"
- "Connect user preferences to AI response generation"

### Data Flow Integration
- "Connect ChatService to MessageClassifier with proper error handling"
- "Integrate AIService with Gemini API using retry mechanisms"
- "Link ShoppingListService to database with connection pooling"
- "Create data validation between all service components"

### Error Handling Integration
- "Implement comprehensive error handling across all endpoints"
- "Add validation for user input and API requests"
- "Create fallback mechanisms for AI service failures"
- "Ensure graceful degradation when external services fail"

## Override Flags
- `#COMMERCIAL_FEATURE` → allow use of advanced AI libraries or complex frameworks
- `#ALLOW_AUTH` → enable user authentication and session management
- `#IGNORE_STRUCTURE_CONSTRAINTS` → allow folder creation (use sparingly)
- `#COMPLEX_INTEGRATION` → allow advanced external service integration
- `#REAL_TIME_FEATURES` → enable WebSocket or complex real-time updates
- `#ENTERPRISE_FEATURES` → enable advanced features and compliance
- `#AGENTIC_FOCUS` → prioritize intelligent processing over simple responses

## Specific Implementation Prompts

### For Backend Services
```
"Implement [service name] that:
1. Handles [specific functionality]
2. Integrates with [external service]
3. Provides proper error handling
4. Includes logging and monitoring
5. Follows the established patterns in /services/
Use the existing structure and maintain consistency."
```

### For Agentic Logic
```
"Enhance the [service name] to:
1. Improve context awareness and conversation history
2. Generate more intelligent responses using Gemini
3. Handle user preferences in response generation
4. Provide better fallback mechanisms
5. Optimize performance and response times
Maintain the existing API structure and error handling."
```

### For API Integration
```
"Connect [component A] to [component B] by:
1. Establishing proper data flow
2. Implementing error handling
3. Adding validation where needed
4. Ensuring good user experience
5. Following established patterns
Maintain simplicity and avoid over-engineering."
```

## AI Service Specific Prompts
- "Optimize prompt engineering for better Gemini responses"
- "Implement retry logic with exponential backoff for AI service calls"
- "Add fallback responses when AI service is unavailable"
- "Enhance context management for multi-turn conversations"
- "Improve intent classification accuracy with BART model"

## Shopping List Specific Prompts
- "Enhance item extraction prompts for better shopping list recognition"
- "Implement smart item removal with fuzzy matching"
- "Add quantity detection for shopping list items"
- "Create context-aware shopping list updates"
- "Improve recipe integration with shopping list management"
- "Add preference-aware substitutions for dietary restrictions"

## Sample Data Payloads

### Request Example
```json
{
  "user_id": "user123",
  "user_message": "Add milk and bread to my shopping list"
}
```

### Response Example
```json
{
  "bot_response": "I've added milk and bread to your shopping list. Is there anything else you need?",
  "shopping_list": ["milk", "bread", "eggs", "butter"],
  "preferences": {
    "vegetarian": "not_set",
    "gluten_free": "not_set",
    "dairy_free": "not_set"
  }
}
```

### Error Response Example
```json
{
  "error": "validation_error",
  "detail": "User ID and message are required",
  "status_code": 400
}
```

### API Inputs
- POST requests to `/api/v1/chat` with JSON payload containing user_id and user_message
- GET requests to `/api/v1/preferences/{user_id}` for retrieving user preferences
- POST requests to `/api/v1/preferences` for setting user preferences
- DELETE requests to `/api/v1/preferences/{user_id}` for clearing preferences

## Critical User Flows
- **User sends message → AI classifies intent → Updates shopping list → Returns response**
- **User asks for recipe → AI generates recipe with ingredients → Adds ingredients to list**
- **User provides invalid input → Backend returns clear error message**
- **User sets preferences → AI considers preferences in future responses**
- **AI service fails → System provides graceful fallback response**

## Edge Cases
- **Input Validation:** Empty user_message, missing user_id, very long messages (>1000 characters)
- **Service Failures:** Gemini API rate limit exceeded, AI service timeout (>30 seconds), malformed AI responses
- **Performance Limits:** Concurrent user requests, large conversation history, complex recipe generation
- **Data Corruption:** Invalid JSON payload, corrupted database entries, missing user preferences
- **Network Issues:** MongoDB connection failures, AI service unavailable, timeout scenarios

## Performance Test Scenarios
- **Concurrent Users:** 10+ simultaneous chat requests
- **Large Data Sets:** Users with 50+ conversation history entries
- **Complex Operations:** Recipe generation with 20+ ingredients
- **Memory Usage:** Efficient handling of large context windows
- **Response Times:** < 2 seconds for chat requests, < 5 seconds for complex operations

## Expected Behavior on Failure
- **Backend:**
  - HTTP status codes: 400 for validation errors, 500 for server errors, 503 for AI service errors
  - Error message format: `{"error": "error_type", "detail": "description", "status_code": 400}`
  - Logging and monitoring: Structured logging with error tracking
- **API Client:**
  - Receive clear error message in response
  - Get appropriate HTTP status code
  - Fallback response when AI service is unavailable: "I'm having trouble processing that right now. Could you try rephrasing?"

## Quality Assurance Requirements
- **Testing Strategy:** Unit tests for all services, integration tests for API endpoints, performance tests for AI calls
- **Error Handling:** Comprehensive error scenarios including AI service failures, database errors, validation errors
- **Performance Monitoring:** Track response times, AI service latency, database query performance
- **User Experience:** Ensure helpful error messages, graceful degradation, consistent response format
- **Security:** Input sanitization, prompt safety validation, secure API key handling 