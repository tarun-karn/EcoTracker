#!/usr/bin/env python
"""
Test the chatbot functionality and challenge generation
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
import json

def test_chatbot_page():
    """Test if chatbot page is accessible"""
    print("🌐 Testing Chatbot Page Access...")
    try:
        response = requests.get('http://127.0.0.1:8000/dashboard/chatbot/', timeout=5)
        if response.status_code == 200:
            print("✅ Chatbot page is accessible")
            print(f"   Status: {response.status_code}")
            print(f"   Content length: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Chatbot page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chatbot page access failed: {e}")
        return False

def test_chatbot_api():
    """Test chatbot API functionality"""
    print("🤖 Testing Chatbot API...")
    try:
        # Get CSRF token first
        session = requests.Session()
        response = session.get('http://127.0.0.1:8000/dashboard/chatbot/')
        
        # Extract CSRF token from the response
        csrf_token = None
        if 'csrftoken' in session.cookies:
            csrf_token = session.cookies['csrftoken']
        else:
            # Try to find it in the HTML
            content = response.text
            start = content.find("name='csrfmiddlewaretoken' value='")
            if start != -1:
                start += len("name='csrfmiddlewaretoken' value='")
                end = content.find("'", start)
                csrf_token = content[start:end]
        
        if not csrf_token:
            print("❌ Could not get CSRF token")
            return False
        
        # Test API with different queries
        test_queries = [
            "Hello",
            "What should I do?",
            "Give me a challenge",
            "How are my points?",
            "Show my predictions"
        ]
        
        for query in test_queries:
            print(f"   Testing query: '{query}'")
            
            response = session.post(
                'http://127.0.0.1:8000/dashboard/api/chatbot/',
                headers={
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token,
                    'Referer': 'http://127.0.0.1:8000/dashboard/chatbot/'
                },
                json={'query': query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ '{query}' -> Response: {data.get('response', 'No response')[:50]}...")
                if data.get('additional_data'):
                    print(f"      💡 Additional data: {list(data['additional_data'].keys())}")
            else:
                print(f"   ❌ '{query}' failed: {response.status_code}")
        
        return True
    
    except Exception as e:
        print(f"❌ Chatbot API test failed: {e}")
        return False

def test_challenge_generation():
    """Test challenge generation API"""
    print("🎮 Testing Challenge Generation...")
    try:
        session = requests.Session()
        
        # Get CSRF token
        response = session.get('http://127.0.0.1:8000/dashboard/')
        csrf_token = None
        if 'csrftoken' in session.cookies:
            csrf_token = session.cookies['csrftoken']
        
        if not csrf_token:
            print("❌ Could not get CSRF token for challenge test")
            return False
        
        # Test challenge generation
        response = session.post(
            'http://127.0.0.1:8000/dashboard/api/generate-challenge/',
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token,
                'Referer': 'http://127.0.0.1:8000/dashboard/'
            },
            json={},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                challenge = data.get('challenge', {})
                print(f"   ✅ Challenge generated: {challenge.get('title', 'No title')}")
                print(f"      Description: {challenge.get('description', 'No description')[:60]}...")
                print(f"      Points: {challenge.get('reward_points', 0)}")
                print(f"      AI Generated: {challenge.get('ai_generated', False)}")
                return True
            else:
                print(f"   ❌ Challenge generation failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   ❌ Challenge API failed: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Challenge generation test failed: {e}")
        return False

def main():
    print("🧪 EcoTracker Chatbot & AI Functionality Test")
    print("=" * 60)
    
    # Test chatbot page access
    page_ok = test_chatbot_page()
    
    # Test chatbot API
    api_ok = test_chatbot_api()
    
    # Test challenge generation
    challenge_ok = test_challenge_generation()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Chatbot Page: {'✅ PASS' if page_ok else '❌ FAIL'}")
    print(f"   Chatbot API:  {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"   Challenges:   {'✅ PASS' if challenge_ok else '❌ FAIL'}")
    
    if page_ok and api_ok and challenge_ok:
        print("\n🎉 All tests PASSED! Chatbot is working correctly!")
        print("💡 Try the chatbot at: http://127.0.0.1:8000/dashboard/chatbot/")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()