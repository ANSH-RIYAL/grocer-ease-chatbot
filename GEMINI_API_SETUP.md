# Gemini API Setup Guide

## Current Status
✅ **API Key Configured**: Your Gemini API key is already set in `.env`  
⚠️ **Rate Limit Issue**: You're hitting the Gemini API quota limits (429 errors)

## 🔑 Where Your API Key is Configured

### 1. Environment File
Your API key is configured in the `.env` file in the project root:
```bash
GEMINI_API_KEY=AIzaSyD4PRV5vHdCy8kWr9WiQUbZ4I-p0r4sTCc
```

### 2. Configuration Loading
The API key is loaded in `src/core/config.py`:
```python
GEMINI_API_KEY: str = "dummy_key"  # Default for testing
```

### 3. Usage Locations
The API key is used in these services:
- `src/services/ai_service.py` - Main AI response generation
- `src/services/message_classifier.py` - Message classification (if using Gemini)

## 🚨 Current Issue: Rate Limits

From your logs, you're getting 429 errors:
```
429 You exceeded your current quota, please check your plan and billing details.
```

This means:
- ✅ Your API key is working
- ❌ You've hit the rate limits/quota
- ⏱️ You need to wait or upgrade your plan

## 🔧 Solutions

### Option 1: Wait for Rate Limit Reset
The error shows retry delays:
- First error: 29 seconds
- Second error: 25 seconds  
- Third error: 21 seconds
- Fourth error: 17 seconds

**Action**: Wait about 30-60 seconds between requests.

### Option 2: Switch to BART Classifier (Recommended)
Currently, you're using Gemini for message classification. Switch to BART to reduce API calls:

Update your `.env` file:
```bash
# Change this line in .env
CLASSIFIER_TYPE=bart
PREFERENCE_MODEL_TYPE=bart
```

### Option 3: Get a New API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Update your `.env` file:
```bash
GEMINI_API_KEY=your_new_api_key_here
```

### Option 4: Upgrade Your Plan
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Check your current quota
3. Upgrade if needed

## 🛠️ Quick Fix: Switch to BART

Let's switch to BART classifier to reduce API calls: