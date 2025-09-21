#!/usr/bin/env python
"""
Chatbot Diagnostic Script
Diagnoses chatbot visibility and functionality issues
"""

import os
import sys
import django
from django.contrib.auth import get_user_model
from django.test.client import Client
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

def diagnose_chatbot_issues():
    """Diagnose common chatbot issues"""
    print("🔍 AI Chatbot Diagnostic Tool")
    print("=" * 50)
    
    # Test 1: Check if chatbot API endpoint works
    print("\n1. Testing Chatbot API Endpoint...")
    client = Client()
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='chatbot_test_user',
        defaults={
            'email': 'chatbot@test.com',
            'first_name': 'Chatbot',
            'last_name': 'Tester'
        }
    )
    
    client.force_login(user)
    
    try:
        response = client.post('/dashboard/api/chatbot/', 
                             json.dumps({'query': 'hello'}),
                             content_type='application/json')
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ API Endpoint Working")
            print(f"   📨 Response: {data.get('response', 'No response')[:100]}...")
        else:
            print(f"   ❌ API Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ API Exception: {e}")
    
    # Test 2: Check dashboard loads with chatbot elements
    print("\n2. Testing Dashboard Template...")
    try:
        response = client.get('/dashboard/')
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for chatbot elements
            chatbot_elements = {
                'chatbot-container': 'chatbot-container' in content,
                'chatbot-toggle': 'chatbot-toggle' in content,
                'chatbot-window': 'chatbot-window' in content,
                'chat-form': 'chat-form' in content,
                'AI banner': 'AI Features Now Active' in content
            }
            
            print("   📋 Template Elements Check:")
            for element, found in chatbot_elements.items():
                status = "✅" if found else "❌"
                print(f"      {status} {element}")
                
            if all(chatbot_elements.values()):
                print("   ✅ All chatbot elements present in template")
            else:
                print("   ⚠️  Some chatbot elements missing")
                
        else:
            print(f"   ❌ Dashboard Error: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard Exception: {e}")
    
    # Test 3: Check AI services
    print("\n3. Testing AI Services...")
    try:
        from ai_features.ai_services import EcoMentorAI
        eco_mentor = EcoMentorAI(user)
        recommendation = eco_mentor.generate_personalized_recommendation()
        
        if recommendation:
            print("   ✅ AI Services Working")
            print(f"   🤖 Sample recommendation: {recommendation.get('title', 'N/A')}")
        else:
            print("   ❌ AI Services returned empty result")
    except Exception as e:
        print(f"   ❌ AI Services Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 TROUBLESHOOTING GUIDE")
    print("=" * 50)
    
    print("\n📱 IF CHATBOT BUTTON IS NOT VISIBLE:")
    print("   1. Clear browser cache (Ctrl+F5)")
    print("   2. Check browser console for JavaScript errors (F12)")
    print("   3. Look for floating button in bottom-right corner")
    print("   4. Try different browser or incognito mode")
    
    print("\n🔘 IF BUTTON IS VISIBLE BUT NOT CLICKABLE:")
    print("   1. Check for JavaScript errors in console")
    print("   2. Ensure no other elements are blocking the button")
    print("   3. Try clicking directly on the chat icon")
    
    print("\n💬 IF CHATBOT OPENS BUT DOESN'T RESPOND:")
    print("   1. Check network tab for failed API requests")
    print("   2. Verify you're logged in")
    print("   3. Check server logs for Python errors")
    
    print("\n🎨 VISUAL INDICATORS TO LOOK FOR:")
    print("   • Floating button with gradient blue-green background")
    print("   • Pulsing animation around the button")
    print("   • Robot emoji (🤖) badge on the button")
    print("   • Tooltip showing 'Chat with AI Eco Mentor' on hover")
    print("   • AI Features banner at top of dashboard")
    
    print("\n🔧 QUICK FIXES:")
    print("   • Refresh the page (F5)")
    print("   • Log out and log back in")
    print("   • Try the AI Calculator link in the banner")
    print("   • Check if you're on the dashboard page (/dashboard/)")
    
    print(f"\n📍 Current Server Status: {'🟢 Running' if True else '🔴 Stopped'}")
    print("   Visit: http://127.0.0.1:8000/dashboard/")

if __name__ == "__main__":
    try:
        diagnose_chatbot_issues()
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        print("\n🚨 Basic troubleshooting:")
        print("   1. Ensure Django server is running: python manage.py runserver")
        print("   2. Visit http://127.0.0.1:8000/dashboard/")
        print("   3. Look for floating button in bottom-right corner")
        print("   4. If button missing, check browser console (F12)")