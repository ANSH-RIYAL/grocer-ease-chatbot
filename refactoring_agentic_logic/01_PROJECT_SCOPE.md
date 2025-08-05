# PROJECT SCOPE

## One-line Summary
A conversational AI-powered API service that helps users manage grocery shopping lists through natural language interaction with intelligent response generation and agentic state management.

## What We're Building
- **Functionality Overview:** FastAPI-based chatbot service with intelligent message processing, agentic shopping list management, action tracking, and user preference integration
- **Input Behavior:** JSON POST requests with user_id and user_message for chat processing
- **Output Behavior:** JSON responses with bot_response, shopping_list, and user preferences
- **Core Logic Description:** 
  1. Receive user message via API endpoint
  2. Classify message intent using Gemini API
  3. Extract items and actions with context awareness
  4. Update shopping list state with action tracking
  5. Generate intelligent response using Google Gemini AI with context
  6. Return response with updated list and preferences
- **Agentic Processing:** Context-aware responses, action history tracking, user preference integration, intelligent item extraction, and state management

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
- **Primary Services:** Google Gemini AI for response generation and message classification, MongoDB Atlas for data persistence
- **Secondary Services:** Structured prompting API for enhanced AI interactions
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
  - [x] MessageClassifier Gemini-based classification
  - [x] ShoppingListService CRUD operations
  - [x] UserPreferencesService management
- **Agentic Logic Checklist:**
  - [x] Context-aware response generation
  - [x] Conversation history tracking
  - [x] User preference integration
  - [x] Intent classification accuracy
  - [x] Item extraction from messages

### Phase 2: Agentic Shopping List Management
- **Backend Checklist:**
  - [ ] Enhanced shopping list data structure with action tracking
  - [ ] Action logging system for add/remove/recipe operations
  - [ ] User preferences integration (allergies, dietary restrictions)
  - [ ] Context-aware item management with removal history
  - [ ] Action summaries for AI context management
- **Agentic Logic Checklist:**
  - [ ] Intelligent item addition with quantity support
  - [ ] Smart item removal with fuzzy matching and history tracking
  - [ ] Recipe context management and ingredient tracking
  - [ ] Context-aware decision making based on action history
  - [ ] Preference-aware substitutions and suggestions

### Phase 3: Quality & Optimization
- **Backend Checklist:**
  - [ ] Performance benchmarking
  - [ ] Production deployment preparation
  - [ ] Comprehensive API documentation
  - [ ] Security hardening
- **Agentic Logic Checklist:**
  - [ ] Validate intelligent response quality
  - [ ] Optimize response generation speed
  - [ ] Ensure reliable error recovery
  - [ ] Monitor AI service performance

## Real Data Requirements
- **Example Data Structures:** 
  - Chat messages: {user_id, user_message, bot_response, timestamp}
  - Shopping lists: {user_id, items[], action_history[], last_updated}
  - User preferences: {user_id, preferences{vegetarian, gluten_free, dairy_free, allergies}}
  - Action tracking: {action_type, items, quantity, reason, timestamp}
- **Expected Data Sources:** User input via API, AI-generated responses, database persistence
- **Data Relationships:** User-centric data model with conversation history, action tracking, and preferences
- **Data Validation:** Pydantic models for request/response validation, input sanitization 