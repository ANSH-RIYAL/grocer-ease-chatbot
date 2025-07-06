#!/bin/bash

# GrocerEase Chatbot Test Runner
# This script runs all tests with coverage and generates reports

set -e

echo "🧪 Starting GrocerEase Chatbot test suite..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Create test directories if they don't exist
mkdir -p tests/reports
mkdir -p tests/coverage

# Install test dependencies if needed
print_status "Installing test dependencies..."
pip install -r requirements-test.txt

# Run linting first
print_status "Running code linting..."
if command -v black &> /dev/null; then
    black --check src/ tests/ || print_warning "Code formatting issues found. Run 'black src/ tests/' to fix."
else
    print_warning "Black not found. Skipping code formatting check."
fi

if command -v isort &> /dev/null; then
    isort --check-only src/ tests/ || print_warning "Import sorting issues found. Run 'isort src/ tests/' to fix."
else
    print_warning "isort not found. Skipping import sorting check."
fi

# Run type checking
print_status "Running type checking..."
if command -v mypy &> /dev/null; then
    mypy src/ --ignore-missing-imports || print_warning "Type checking issues found."
else
    print_warning "mypy not found. Skipping type checking."
fi

# Run unit tests with coverage
print_status "Running unit tests with coverage..."
pytest tests/unit/ \
    --cov=src \
    --cov-report=html:tests/coverage/html \
    --cov-report=xml:tests/coverage/coverage.xml \
    --cov-report=term-missing \
    --cov-fail-under=80 \
    --verbose \
    --tb=short \
    -n auto

if [ $? -eq 0 ]; then
    print_success "Unit tests passed!"
else
    print_error "Unit tests failed!"
    exit 1
fi

# Run integration tests
print_status "Running integration tests..."
pytest tests/integration/ \
    --verbose \
    --tb=short \
    --junitxml=tests/reports/integration.xml

if [ $? -eq 0 ]; then
    print_success "Integration tests passed!"
else
    print_error "Integration tests failed!"
    exit 1
fi

# Run all tests together for final report
print_status "Running complete test suite..."
pytest tests/ \
    --cov=src \
    --cov-report=html:tests/coverage/html \
    --cov-report=xml:tests/coverage/coverage.xml \
    --cov-report=term-missing \
    --junitxml=tests/reports/junit.xml \
    --verbose \
    --tb=short

# Generate test summary
print_status "Generating test summary..."
echo "=== TEST SUMMARY ===" > tests/reports/summary.txt
echo "Date: $(date)" >> tests/reports/summary.txt
echo "Total tests: $(pytest tests/ --collect-only -q | grep 'test session starts' | awk '{print $6}')" >> tests/reports/summary.txt
echo "Coverage: $(coverage report --format=total)" >> tests/reports/summary.txt

# Display coverage summary
print_status "Coverage Summary:"
coverage report --show-missing

# Check if coverage meets minimum threshold
COVERAGE=$(coverage report --format=total | grep TOTAL | awk '{print $4}' | sed 's/%//')
if (( $(echo "$COVERAGE >= 80" | bc -l) )); then
    print_success "Coverage threshold met: ${COVERAGE}%"
else
    print_warning "Coverage below threshold: ${COVERAGE}% (minimum: 80%)"
fi

# Generate HTML coverage report
print_status "Generating HTML coverage report..."
coverage html -d tests/coverage/html

print_success "All tests completed successfully!"
print_status "Reports generated in tests/reports/"
print_status "Coverage report available in tests/coverage/html/index.html"

# Optional: Open coverage report in browser
if command -v xdg-open &> /dev/null; then
    read -p "Open coverage report in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open tests/coverage/html/index.html
    fi
elif command -v open &> /dev/null; then
    read -p "Open coverage report in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open tests/coverage/html/index.html
    fi
fi

echo "🎉 Test suite completed!" 