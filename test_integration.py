#!/usr/bin/env python3
"""
Integration test script for GrocerEase chatbot
Tests the connection between frontend and backend
"""

import requests
import json
import time

def test_backend_health():
    """Test backend health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend health check passed")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check error: {e}")
        return False

def test_backend_chat():
    """Test backend chat endpoint"""
    try:
        data = {
            "user_id": "test_user_123",
            "user_message": "Hello, can you help me with shopping?"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Backend chat endpoint working")
            print(f"   Response: {result}")
            return True
        else:
            print(f"❌ Backend chat endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Backend chat endpoint error: {e}")
        return False

def test_backend_preferences():
    """Test backend preferences endpoint"""
    try:
        # Test get preferences
        response = requests.get("http://localhost:8000/api/v1/preferences/test_user_123")
        if response.status_code == 200:
            print("✅ Backend preferences GET endpoint working")
        else:
            print(f"❌ Backend preferences GET failed: {response.status_code}")
            return False
        
        # Test set preference
        data = {
            "user_id": "test_user_123",
            "preference": "vegetarian",
            "value": "yes"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/preferences",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Backend preferences POST endpoint working")
            return True
        else:
            print(f"❌ Backend preferences POST failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend preferences endpoint error: {e}")
        return False

def test_frontend():
    """Test frontend accessibility"""
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend accessibility failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend accessibility error: {e}")
        return False

def test_frontend_api_connection():
    """Test if frontend can connect to backend API"""
    try:
        # This simulates what the frontend would do
        data = {
            "user_id": "frontend_test_user",
            "user_message": "Test message from frontend"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/chat",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Frontend can connect to backend API")
            return True
        else:
            print(f"❌ Frontend API connection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend API connection error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting GrocerEase Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Backend Chat", test_backend_chat),
        ("Backend Preferences", test_backend_preferences),
        ("Frontend Accessibility", test_frontend),
        ("Frontend-Backend API Connection", test_frontend_api_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
        print("\n🌐 Access your application:")
        print("   Frontend: http://localhost:3000")
        print("   Backend API: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
    
    return passed == total

if __name__ == "__main__":
    main() 