#!/bin/bash

# GrocerEase Chatbot Deployment Script
# This script helps deploy the application to Railway

set -e

echo "🚀 Starting GrocerEase Chatbot deployment..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway..."
    railway login
fi

# Create new project if it doesn't exist
echo "📦 Creating Railway project..."
railway init

# Set environment variables
echo "🔧 Setting environment variables..."
railway variables set MONGO_URI="$MONGO_URI"
railway variables set DB_NAME="chatbot_db"
railway variables set GEMINI_API_KEY="$GEMINI_API_KEY"
railway variables set GEMINI_MODEL_NAME="gemini-1.5-pro"
railway variables set CLASSIFIER_TYPE="bart"
railway variables set PREFERENCE_MODEL_TYPE="bart"
railway variables set STRUCTURED_PROMPTING_API_KEY="$STRUCTURED_PROMPTING_API_KEY"

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

# Get the deployment URL
echo "🌐 Getting deployment URL..."
DEPLOY_URL=$(railway status --json | jq -r '.url')
echo "✅ Deployment successful!"
echo "🌐 Your application is available at: $DEPLOY_URL"
echo "📚 API Documentation: $DEPLOY_URL/docs"
echo "❤️  Health Check: $DEPLOY_URL/health"

echo "🎉 Deployment completed successfully!" 