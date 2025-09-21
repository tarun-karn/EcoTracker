#!/usr/bin/env python
"""
Quick test to verify the OpenRouter AI chatbot is working
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ai_features.ai_services import OpenRouterAI

def test_openrouter_ai():
    print("🤖 Testing OpenRouter AI Integration...")
    print("=" * 50)
    
    try:
        # Initialize OpenRouter AI
        openrouter = OpenRouterAI()
        
        # Test basic generation
        print("1. Testing basic content generation...")
        result = openrouter.generate_content("What is sustainability in one sentence?")
        
        if result['success']:
            print(f"✅ Success: {result['content'][:80]}...")
            print(f"   Response length: {len(result['content'])} characters")
        else:
            print(f"❌ Failed: {result['error']}")
        
        # Test eco chatbot response
        print("\n2. Testing eco chatbot response...")
        user_context = {
            'total_points': 150,
            'total_carbon': 25.5,
            'recent_activities': ['RECYCLE', 'TREE'],
            'level': 'Intermediate'
        }
        
        chatbot_response = openrouter.generate_eco_chatbot_response(
            "What should I do to help the environment?", 
            user_context
        )
        
        if "Sorry, I'm having trouble connecting" not in chatbot_response:
            print(f"✅ Chatbot Response: {chatbot_response[:80]}...")
        else:
            print(f"❌ Fallback Response: {chatbot_response[:60]}...")
        
        print(f"\n🎉 OpenRouter AI Test Complete!")
        print(f"{'✅ AI is working properly!' if result['success'] else '⚠️ Using fallback responses'}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_openrouter_ai()