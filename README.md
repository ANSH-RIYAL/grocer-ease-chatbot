# GrocerEase Chatbot

A conversational AI-powered chatbot that helps users manage their grocery shopping lists, find recipes, and get information about grocery items.

## Features

- 🤖 Conversational interface for grocery shopping
- 📝 Automatic shopping list management
- 🍳 Recipe suggestions and instructions
- 💰 Price and availability information
- 🔄 Real-time updates and synchronization
- 🎯 Personalized recommendations

## Quick Start with Docker

### Prerequisites
- Docker Desktop installed
- MongoDB Atlas connection string
- Gemini API key
- Structured Prompting API key

### Running with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/grocer-ease-chatbot.git
   cd grocer-ease-chatbot
   ```

2. **Start the application**
   ```bash
   # Start in foreground mode (with logs)
   docker compose up

   # Or start in detached mode (background)
   docker compose up -d
   ```

3. **Access the API**
   - Base URL: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

## Development Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory with the following variables:
```env
MONGO_URI=mongodb+srv://your_mongodb_uri
DB_NAME=chatbot_db
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_NAME=gemini-1.5-pro
CLASSIFIER_TYPE=bart
PREFERENCE_MODEL_TYPE=bart
STRUCTURED_PROMPTING_API_KEY=your_structured_prompting_api_key
```

### 3. Running the Application
```bash
# Development mode
uvicorn src.api.main:app --reload --port 8000

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## API Usage

### Example Requests

1. **Health Check**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Chat Endpoint**
   ```bash
   curl -X POST http://localhost:8000/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user",
       "user_message": "I need to buy groceries for making pasta"
     }'
   ```

3. **Get User Preferences**
   ```bash
   curl http://localhost:8000/api/v1/preferences/test_user
   ```

For detailed API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## Docker Commands

### Basic Commands
```bash
# Start services
docker compose up

# Start in detached mode
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs
docker compose logs -f  # Follow logs

# Rebuild and restart
docker compose up --build
```

### Troubleshooting
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

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test categories
pytest tests/unit/      # Unit tests
pytest tests/integration/  # Integration tests
```

## Project Structure

```
grocer-ease-chatbot/
├── src/
│   ├── api/           # API endpoints
│   ├── core/          # Core functionality
│   ├── services/      # Business logic
│   └── models/        # Data models
├── tests/             # Test files
├── scripts/           # Utility scripts
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker services
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- FastAPI for the web framework
- MongoDB for the database
- Google's Gemini for AI capabilities
- All contributors and users of the project 