#!/bin/bash

# GrocerEase Integration Startup Script
# This script starts both the Python backend and React frontend

echo "🚀 Starting GrocerEase Integration..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Check if ports are available
echo -e "${BLUE}🔍 Checking port availability...${NC}"

if port_in_use 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use. Backend may already be running.${NC}"
fi

if port_in_use 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use. Frontend may already be running.${NC}"
fi

# Create environment file for frontend if it doesn't exist
if [ ! -f "grocer-ease-ui/.env" ]; then
    echo -e "${BLUE}📝 Creating frontend environment file...${NC}"
    echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > grocer-ease-ui/.env
    echo -e "${GREEN}✅ Frontend environment file created${NC}"
fi

# Function to start backend
start_backend() {
    echo -e "${BLUE}🐍 Starting Python backend...${NC}"
    cd "$(dirname "$0")"
    
    # Check if virtual environment exists
    if [ -d "myenv" ]; then
        echo -e "${BLUE}🔧 Activating virtual environment...${NC}"
        source myenv/bin/activate
    fi
    
    # Set Python path to include current directory
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    echo -e "${BLUE}🔧 Set PYTHONPATH to include current directory${NC}"
    
    # Install Python dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
        pip install -r requirements.txt
    fi
    
    # Check and fix .env file if needed
    if [ -f ".env" ]; then
        echo -e "${BLUE}🔍 Checking .env file format...${NC}"
        if grep -q "LOG_LEVEL=INFO CLASSIFIER_TYPE" .env; then
            echo -e "${YELLOW}⚠️  Fixing corrupted .env file...${NC}"
            cp .env .env.backup
            sed 's/LOG_LEVEL=INFO CLASSIFIER_TYPE/LOG_LEVEL=INFO\nCLASSIFIER_TYPE/' .env.backup > .env
            echo -e "${GREEN}✅ .env file fixed${NC}"
        fi
    fi
    
    # Start the backend
    echo -e "${BLUE}🚀 Starting backend server on port 8000...${NC}"
    python -m src.main &
    BACKEND_PID=$!
    echo -e "${GREEN}✅ Backend started with PID: $BACKEND_PID${NC}"
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}⚛️  Starting React frontend...${NC}"
    cd grocer-ease-ui
    
    # Install npm dependencies
    echo -e "${BLUE}📦 Installing npm dependencies...${NC}"
    npm install
    
    # Start the frontend
    echo -e "${BLUE}🚀 Starting frontend server on port 3000...${NC}"
    npm start &
    FRONTEND_PID=$!
    echo -e "${GREEN}✅ Frontend started with PID: $FRONTEND_PID${NC}"
}

# Function to wait for services to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}⏳ Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}⏳ Attempt $attempt/$max_attempts - $service_name not ready yet...${NC}"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start within expected time${NC}"
    return 1
}

# Function to cleanup on exit
cleanup() {
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        echo -e "${BLUE}🛑 Stopping backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        echo -e "${BLUE}🛑 Stopping frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    echo -e "${GREEN}✅ Services stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start services
start_backend
start_frontend

# Wait for services to be ready
if wait_for_service "http://localhost:8000/health" "Backend"; then
    if wait_for_service "http://localhost:3000" "Frontend"; then
        echo -e "${GREEN}🎉 Integration is ready!${NC}"
        echo -e "${BLUE}📱 Frontend: http://localhost:3000${NC}"
        echo -e "${BLUE}🔧 Backend API: http://localhost:8000${NC}"
        echo -e "${BLUE}📚 API Docs: http://localhost:8000/docs${NC}"
        echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
        
        # Keep script running
        while true; do
            sleep 1
        done
    else
        echo -e "${RED}❌ Frontend failed to start${NC}"
        cleanup
    fi
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    cleanup
fi 