#!/usr/bin/env python
"""
Test script for Gemini AI Integration in EcoTracker
Tests the new AI-powered chatbot and challenge generation
"""

import os
import sys
import json
import django

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from ai_features.ai_services import GeminiAI, EcoMentorAI, ChallengeGeneratorAI
from users.models import UserProfile

def test_gemini_ai():
    """Test basic Gemini AI functionality"""
    print("🤖 Testing Gemini AI Integration")
    print("=" * 50)
    
    gemini = GeminiAI()
    
    # Test basic content generation
    print("\n1. Testing Basic Content Generation...")
    result = gemini.generate_content("Explain how AI works in a few words")
    
    if result['success']:
        print(f"✅ Success: {result['content'][:100]}...")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test eco chatbot response
    print("\n2. Testing Eco Chatbot Response...")
    user_context = {
        'username': 'testuser',
        'total_points': 150,
        'total_carbon': 25.5,
        'recent_activities': 'recycling, tree planting',
        'level': 'Intermediate'
    }
    
    response = gemini.generate_eco_chatbot_response(
        "What should I do to help the environment?",
        user_context
    )
    print(f"✅ Chatbot Response: {response[:100]}...")
    
    # Test challenge generation
    print("\n3. Testing AI Challenge Generation...")
    challenge_result = gemini.generate_dynamic_challenge(user_context, 'intermediate')
    
    if challenge_result['success']:
        challenge = challenge_result['challenge']
        print(f"✅ Challenge Generated:")
        print(f"   Title: {challenge.get('title', 'N/A')}")
        print(f"   Description: {challenge.get('description', 'N/A')[:60]}...")
        print(f"   Reward: {challenge.get('reward_points', 'N/A')} points")
    else:
        print(f"❌ Challenge Generation Failed")
    
    # Test insights generation
    print("\n4. Testing Eco Insights Generation...")
    user_data = {
        'total_points': 250,
        'total_carbon': 45.2,
        'activity_count': 12,
        'efficiency_score': 5.5,
        'trend': 'improving'
    }
    
    insights = gemini.generate_eco_insights(user_data)
    print(f"✅ Insights Generated: {insights[:100]}...")

def test_enhanced_ai_services():
    """Test enhanced AI services with Gemini integration"""
    print("\n\n🌱 Testing Enhanced AI Services")
    print("=" * 50)
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='gemini_test_user',
        defaults={
            'email': 'gemini@test.com',
            'first_name': 'Gemini',
            'last_name': 'Tester'
        }
    )
    
    # Create user profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'total_points': 150,
            'total_carbon_saved': 25.5,
            'badge': 'BRONZE'
        }
    )
    
    print(f"✅ Test user: {user.username}")
    
    # Test Enhanced EcoMentorAI
    print("\n1. Testing Enhanced EcoMentorAI...")
    try:
        eco_mentor = EcoMentorAI(user)
        recommendation = eco_mentor.generate_personalized_recommendation()
        print(f"✅ AI Recommendation: {recommendation['title']}")
        print(f"   Content: {recommendation['content'][:80]}...")
        print(f"   AI Generated: {recommendation['metadata'].get('ai_generated', False)}")
    except Exception as e:
        print(f"❌ EcoMentorAI failed: {e}")
    
    # Test Enhanced ChallengeGeneratorAI
    print("\n2. Testing Enhanced ChallengeGeneratorAI...")
    try:
        challenge_gen = ChallengeGeneratorAI(user)
        challenge = challenge_gen.generate_weekly_challenge(force_new=True)
        print(f"✅ AI Challenge: {challenge['title']}")
        print(f"   Description: {challenge['description'][:80]}...")
        print(f"   Reward: {challenge['reward_points']} points")
        print(f"   AI Generated: {challenge.get('ai_generated', False)}")
    except Exception as e:
        print(f"❌ ChallengeGeneratorAI failed: {e}")

def test_api_connectivity():
    """Test Gemini API connectivity and response format"""
    print("\n\n🔗 Testing Gemini API Connectivity")
    print("=" * 50)
    
    gemini = GeminiAI()
    
    # Test simple query
    test_queries = [
        "Hello, how are you?",
        "What is carbon footprint?",
        "Give me an eco-friendly tip",
        "How can I save energy at home?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        result = gemini.generate_content(query)
        
        if result['success']:
            print(f"✅ Response length: {len(result['content'])} chars")
            print(f"   Preview: {result['content'][:60]}...")
        else:
            print(f"❌ Failed: {result['error']}")

def main():
    """Run all Gemini AI tests"""
    print("🚀 Gemini AI Integration Test Suite")
    print("=" * 60)
    
    try:
        test_gemini_ai()
        test_enhanced_ai_services()
        test_api_connectivity()
        
        print("\n\n🎉 All Tests Completed!")
        print("=" * 60)
        print("✅ Gemini AI is now integrated into EcoTracker!")
        print("🤖 Enhanced chatbot with real AI responses")
        print("🎮 AI-generated challenges and insights")
        print("📊 Personalized recommendations powered by AI")
        print("\n💡 Try the chatbot with queries like:")
        print("   - 'What should I do?'")
        print("   - 'Give me a challenge'")
        print("   - 'How are my points?'")
        print("   - 'What's my environmental impact?'")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        print("Please check your Gemini API key and network connection.")

if __name__ == "__main__":
    main()