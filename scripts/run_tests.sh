#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Running tests..."

# Run unit tests
echo -e "\n${GREEN}Running unit tests...${NC}"
pytest tests/unit -v --cov=src --cov-report=term-missing

# Run integration tests
echo -e "\n${GREEN}Running integration tests...${NC}"
pytest tests/integration -v --cov=src --cov-report=term-missing

# Generate coverage report
echo -e "\n${GREEN}Generating coverage report...${NC}"
coverage html

echo -e "\n${GREEN}Tests completed successfully!${NC}"
echo "Coverage report available at htmlcov/index.html" 