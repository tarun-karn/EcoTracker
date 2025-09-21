#!/usr/bin/env python
"""
AI Features Test Script
Tests all AI functionality including chatbot, predictions, insights, and challenges
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

from ai_features.ai_services import EcoMentorAI, CarbonPredictorAI, EfficiencyAnalyzerAI, ChallengeGeneratorAI
from ai_features.models import AIRecommendation, DynamicChallenge
from users.models import UserProfile

User = get_user_model()

def test_ai_services():
    """Test all AI service classes"""
    print("🤖 Testing AI Services...")
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='ai_test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'AI',
            'last_name': 'Tester'
        }
    )
    
    # Create user profile if needed
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    print(f"✅ Test user: {user.username}")
    
    # Test EcoMentorAI
    print("\n📝 Testing EcoMentorAI...")
    try:
        eco_mentor = EcoMentorAI(user)
        recommendation = eco_mentor.generate_personalized_recommendation()
        print(f"✅ Recommendation generated: {recommendation.get('title', 'N/A')}")
    except Exception as e:
        print(f"❌ EcoMentorAI failed: {e}")
    
    # Test CarbonPredictorAI
    print("\n📊 Testing CarbonPredictorAI...")
    try:
        predictor = CarbonPredictorAI(user)
        predictions = predictor.predict_future_savings(30)
        print(f"✅ Predictions generated: {len(predictions.get('predictions', []))} days")
    except Exception as e:
        print(f"❌ CarbonPredictorAI failed: {e}")
    
    # Test EfficiencyAnalyzerAI
    print("\n⚡ Testing EfficiencyAnalyzerAI...")
    try:
        analyzer = EfficiencyAnalyzerAI(user)
        insights = analyzer.calculate_efficiency_insights()
        print(f"✅ Efficiency insights: {insights.get('efficiency_score', 0):.2f} pts/kg")
    except Exception as e:
        print(f"❌ EfficiencyAnalyzerAI failed: {e}")
    
    # Test ChallengeGeneratorAI
    print("\n🎮 Testing ChallengeGeneratorAI...")
    try:
        challenge_gen = ChallengeGeneratorAI(user)
        challenge = challenge_gen.generate_weekly_challenge()
        print(f"✅ Challenge generated: {challenge.get('challenge_text', 'N/A')}")
    except Exception as e:
        print(f"❌ ChallengeGeneratorAI failed: {e}")

def test_chatbot_api():
    """Test chatbot API endpoint"""
    print("\n🤖 Testing Chatbot API...")
    
    client = Client()
    
    # Get test user
    user = User.objects.get(username='ai_test_user')
    client.force_login(user)
    
    # Test different queries
    test_queries = [
        "hello",
        "how are my points?",
        "give me a recommendation",
        "what should I do?",
        "show me a challenge",
        "what's my prediction?",
        "how efficient am I?"
    ]
    
    for query in test_queries:
        try:
            response = client.post('/dashboard/api/chatbot/', 
                                 json.dumps({'query': query}),
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Query: '{query}' -> Response: {len(data.get('response', ''))} chars")
            else:
                print(f"❌ Query: '{query}' -> Status: {response.status_code}")
        except Exception as e:
            print(f"❌ Query: '{query}' -> Error: {e}")

def test_ai_models():
    """Test AI model creation and queries"""
    print("\n📊 Testing AI Models...")
    
    # Test model counts
    models_data = [
        (AIRecommendation, "AI Recommendations"),
        (DynamicChallenge, "Dynamic Challenges"),
    ]
    
    for model, name in models_data:
        try:
            count = model.objects.count()
            print(f"✅ {name}: {count} records")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

def test_dashboard_integration():
    """Test dashboard integration with AI features"""
    print("\n🏠 Testing Dashboard Integration...")
    
    client = Client()
    user = User.objects.get(username='ai_test_user')
    client.force_login(user)
    
    try:
        response = client.get('/dashboard/')
        if response.status_code == 200:
            content = response.content.decode()
            
            # Check for AI feature elements
            ai_elements = [
                'chatbot-toggle',
                'ai_recommendation',
                'carbon_predictions',
                'active_challenges',
                'efficiency_insights'
            ]
            
            for element in ai_elements:
                if element in content:
                    print(f"✅ Found: {element}")
                else:
                    print(f"⚠️  Missing: {element}")
        else:
            print(f"❌ Dashboard failed: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard integration failed: {e}")

if __name__ == "__main__":
    print("🧪 AI Features Test Suite")
    print("=" * 50)
    
    try:
        test_ai_services()
        test_ai_models() 
        test_chatbot_api()
        test_dashboard_integration()
        
        print("\n" + "=" * 50)
        print("✅ AI Features Test Complete!")
        print("\n💡 To interact with AI features:")
        print("1. Visit the dashboard at http://127.0.0.1:8000/dashboard/")
        print("2. Look for the floating chat button (bottom-right)")
        print("3. Try asking: 'What should I do?', 'How are my points?'")
        print("4. Check the AI recommendation panels on the dashboard")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)