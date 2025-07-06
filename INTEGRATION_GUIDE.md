# GrocerEase Integration Guide: Python Backend + React Frontend

## Overview
This guide outlines the integration strategy between the Python FastAPI backend and React frontend for the GrocerEase chatbot application.

## Architecture

```
┌─────────────────┐    HTTP/JSON    ┌─────────────────┐
│   React App     │ ◄─────────────► │  Python FastAPI │
│  (Port 3000)    │                 │   (Port 8000)   │
└─────────────────┘                 └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│   Local State   │                 │   MongoDB       │
│  (Shopping List)│                 │  (Database)     │
└─────────────────┘                 └─────────────────┘
```

## API Endpoints Mapping

### Backend Endpoints (Python FastAPI)
- `GET /health` - Health check
- `POST /api/v1/chat` - Chat functionality
- `GET /api/v1/preferences/{user_id}` - Get user preferences
- `POST /api/v1/preferences` - Set user preference
- `DELETE /api/v1/preferences/{user_id}` - Clear user preferences

### Frontend Service Methods (React)
- `chatService.sendMessage(userId, message)` → `POST /api/v1/chat`
- `chatService.getUserPreferences(userId)` → `GET /api/v1/preferences/{user_id}`
- `chatService.setUserPreference(userId, preference, value)` → `POST /api/v1/preferences`
- `chatService.clearUserPreferences(userId)` → `DELETE /api/v1/preferences/{user_id}`
- `chatService.healthCheck()` → `GET /health`

## Setup Instructions

### 1. Backend Setup (Python)

```bash
# Navigate to project root
cd /path/to/grocer-ease-chatbot

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export MONGO_URI="your_mongodb_connection_string"
export GEMINI_API_KEY="your_gemini_api_key"
export STRUCTURED_PROMPTING_API_KEY="your_structured_prompting_key"

# Start the backend server
python src/main.py
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup (React)

```bash
# Navigate to frontend directory
cd grocer-ease-ui

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env

# Start the frontend development server
npm start
```

The frontend will be available at `http://localhost:3000`

### 3. Environment Configuration

#### Backend Environment Variables
```bash
# .env file in project root
MONGO_URI=mongodb://localhost:27017
DB_NAME=chatbot_db
GEMINI_API_KEY=your_gemini_api_key
STRUCTURED_PROMPTING_API_KEY=your_structured_prompting_key
LOG_LEVEL=INFO
```

#### Frontend Environment Variables
```bash
# .env file in grocer-ease-ui directory
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENV=development
```

## Data Flow

### 1. Chat Flow
```
User Input → React ChatModal → chatService.sendMessage() → 
Python /api/v1/chat → AI Processing → 
Response with bot_response + shopping_list → 
React State Update → UI Update
```

### 2. User Preferences Flow
```
Component Mount → chatService.getUserPreferences() → 
Python /api/v1/preferences/{user_id} → 
MongoDB Query → Response → React State Update
```

### 3. Shopping List Management
```
Backend AI extracts items → Updates shopping_list in response → 
Frontend receives response → Updates local shopping list state → 
UI reflects changes
```

## Key Integration Points

### 1. User ID Management
- Frontend generates unique user IDs for session management
- Backend uses user IDs for preferences and chat history
- User IDs are passed in all API requests

### 2. Request/Response Format
- **Request**: `{user_id: string, user_message: string}`
- **Response**: `{bot_response: string, shopping_list: string[]}`

### 3. Error Handling
- Frontend catches API errors and displays user-friendly messages
- Backend returns appropriate HTTP status codes
- CORS is configured to allow cross-origin requests

## Testing the Integration

### 1. Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 2. Chat Endpoint
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user", "user_message": "Add milk to my list"}'
```

### 3. Frontend Integration
1. Open `http://localhost:3000`
2. Click "Try Smart Shopping Assistant"
3. Send a message like "Add milk to my shopping list"
4. Verify the response and shopping list update

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend CORS_ORIGINS includes `http://localhost:3000`
   - Check that frontend is making requests to correct URL

2. **API Connection Errors**
   - Verify both servers are running
   - Check environment variables are set correctly
   - Ensure MongoDB is accessible

3. **User ID Issues**
   - Verify user IDs are being generated and passed correctly
   - Check that user IDs are consistent across requests

### Debug Steps

1. **Backend Logs**
   ```bash
   # Check backend logs for errors
   tail -f logs/app.log
   ```

2. **Frontend Console**
   - Open browser developer tools
   - Check Network tab for API requests
   - Review Console for JavaScript errors

3. **API Testing**
   ```bash
   # Test API directly
   curl -X GET http://localhost:8000/health
   curl -X POST http://localhost:8000/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test", "user_message": "hello"}'
   ```

## Production Deployment

### Backend Deployment
- Deploy to cloud platform (Render, Heroku, AWS, etc.)
- Set production environment variables
- Configure MongoDB Atlas for database

### Frontend Deployment
- Build production version: `npm run build`
- Deploy to static hosting (Netlify, Vercel, etc.)
- Update `REACT_APP_API_URL` to production backend URL

### Environment Variables for Production
```bash
# Backend
MONGO_URI=mongodb+srv://...
GEMINI_API_KEY=your_production_key
STRUCTURED_PROMPTING_API_KEY=your_production_key

# Frontend
REACT_APP_API_URL=https://your-backend-domain.com/api/v1
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **CORS**: Restrict CORS origins in production
3. **User Authentication**: Implement proper user authentication
4. **Rate Limiting**: Add rate limiting to prevent abuse
5. **Input Validation**: Validate all user inputs

## Future Enhancements

1. **Real-time Updates**: Implement WebSocket for real-time chat
2. **User Authentication**: Add JWT-based authentication
3. **Shopping List Sync**: Sync shopping lists across devices
4. **Offline Support**: Add service worker for offline functionality
5. **Analytics**: Track user interactions and preferences 