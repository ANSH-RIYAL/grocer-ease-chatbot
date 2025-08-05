# PROJECT SCOPE

## One-line Summary
A conversational AI-powered API service that helps users manage grocery shopping lists through natural language interaction with intelligent response generation.

## What We're Building
- **Functionality Overview:** FastAPI-based chatbot service with intelligent message processing, shopping list management, recipe assistance, and user preference integration
- **Input Behavior:** JSON POST requests with user_id and user_message for chat processing
- **Output Behavior:** JSON responses with bot_response, shopping_list, and user preferences
- **Core Logic Description:** 
  1. Receive user message via API endpoint
  2. Classify message intent using BART/Gemini classifier
  3. Generate intelligent response using Google Gemini AI with context
  4. Update shopping list based on extracted items
  5. Return response with updated list and preferences
- **Intelligent Processing:** Context-aware responses, conversation history tracking, user preference integration, and intelligent item extraction

## What We're NOT Building
- Frontend UI components or user interfaces
- User authentication and session management
- Rate limiting and API protection mechanisms
- Caching layer or Redis integration
- Payment processing or e-commerce features
- Real-time WebSocket connections
- Mobile applications or native apps
- Complex monitoring and analytics systems

## Build Philosophy
- **Simplicity First**: Use standard libraries, avoid complex abstractions, focus on core functionality
- **Reliability Focus**: Robust error handling, graceful degradation, comprehensive fallback strategies
- **Agentic Intelligence**: Smart processing with clear logic flow, context-aware responses
- **Quality Code**: Self-documenting, maintainable, easy to understand and modify
- **Performance**: Efficient resource usage, optimized database queries, fast response times

## Development Rules & Constraints
- **Project Structure:** Fixed src/ structure with api/, services/, core/, models/ - no folder name changes
- **Stack Limitations:** FastAPI backend only, MongoDB database, Google Gemini AI, no frontend components
- **Code Organization:** Clear separation between API routes, business logic, and infrastructure
- **Integration Patterns:** JSON-only API communication, structured error responses
- **AI Service Integration:** Centralized management with retry logic and fallback strategies
- **Context Management:** State preservation across requests, conversation history tracking

## External Dependencies
- **Primary Services:** Google Gemini AI for response generation, MongoDB Atlas for data persistence
- **Secondary Services:** BART model for message classification, structured prompting API
- **Rate Limits & Costs:** Gemini API usage limits, MongoDB Atlas connection limits
- **Fallback Strategies:** Manual item extraction when AI fails, graceful degradation responses

## Performance Requirements
- **Response Time:** < 2 seconds for chat requests, < 5 seconds for complex operations
- **Concurrency:** Support for multiple simultaneous users
- **Resource Usage:** Efficient memory usage, optimized database queries
- **Scalability:** Handle increased load through connection pooling and async processing

## Development Phases

### Phase 1: Core Logic + Data Structures ✅
- **Backend Checklist:** 
  - [x] ChatService message processing pipeline
  - [x] AIService Gemini integration with retry logic
  - [x] MessageClassifier BART/Gemini classification
  - [x] ShoppingListService CRUD operations
  - [x] UserPreferencesService management
- **Agentic Logic Checklist:**
  - [x] Context-aware response generation
  - [x] Conversation history tracking
  - [x] User preference integration
  - [x] Intent classification accuracy
  - [x] Item extraction from messages

### Phase 2: Enhanced Shopping List Agentic Logic
- **Backend Checklist:**
  - [ ] Enhanced item recognition with AI
  - [ ] Smart item removal with fuzzy matching
  - [ ] Quantity management ("2 apples", "3 bags")
  - [ ] Context-aware shopping list updates
  - [ ] Improved prompt engineering for shopping
- **Agentic Logic Checklist:**
  - [ ] Recipe → Shopping list integration
  - [ ] Smart item addition/removal
  - [ ] Quantity detection and management
  - [ ] Context-aware list modifications
  - [ ] Preference-aware substitutions

### Phase 3: Quality & Optimization
- **Backend Checklist:**
  - [ ] Complete unit and integration testing
  - [ ] Performance benchmarking
  - [ ] Production deployment preparation
  - [ ] Comprehensive API documentation
  - [ ] Security hardening
- **Agentic Logic Checklist:**
  - [ ] Test all agentic processing scenarios
  - [ ] Validate intelligent response quality
  - [ ] Optimize response generation speed
  - [ ] Ensure reliable error recovery
  - [ ] Monitor AI service performance

## Real Data Requirements
- **Example Data Structures:** 
  - Chat messages: {user_id, user_message, bot_response, timestamp}
  - Shopping lists: {user_id, items[], last_updated}
  - User preferences: {user_id, preferences{vegetarian, gluten_free, dairy_free}}
- **Expected Data Sources:** User input via API, AI-generated responses, database persistence
- **Data Relationships:** User-centric data model with conversation history and preferences
- **Data Validation:** Pydantic models for request/response validation, input sanitization 