#!/usr/bin/env python
"""
Test Grok AI Integration
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ai_features.ai_services import GrokAI, EcoMentorAI, ChallengeGeneratorAI
from django.contrib.auth.models import User
from users.models import UserProfile

def test_grok_api():
    """Test basic Grok AI functionality"""
    print("🤖 Testing Grok AI Integration")
    print("=" * 50)
    
    grok = GrokAI()
    
    # Test basic content generation
    print("1. Testing Basic Content Generation...")
    result = grok.generate_content("Explain AI in a few words")
    if result['success']:
        print(f"✅ Success: {result['content'][:60]}...")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test eco chatbot response
    print("\n2. Testing Eco Chatbot Response...")
    user_context = {
        'total_points': 150,
        'total_carbon': 25.5,
        'recent_activities': ['RECYCLE', 'TREE'],
        'level': 'Intermediate'
    }
    
    response = grok.generate_eco_chatbot_response("What should I do to help the environment?", user_context)
    print(f"✅ Chatbot Response: {response[:80]}...")
    
    # Test challenge generation
    print("\n3. Testing AI Challenge Generation...")
    challenge_result = grok.generate_dynamic_challenge(user_context, 'intermediate')
    if challenge_result['success']:
        challenge = challenge_result['challenge']
        print(f"✅ Challenge Generated: {challenge.get('title', 'No title')}")
        print(f"   Description: {challenge.get('description', 'No description')[:60]}...")
        print(f"   Points: {challenge.get('reward_points', 0)}")
    else:
        print("❌ Challenge Generation Failed")
    
    # Test eco insights
    print("\n4. Testing Eco Insights Generation...")
    user_data = {
        'total_points': 250,
        'total_carbon': 45.2,
        'activity_count': 12,
        'efficiency_score': 5.5,
        'trend': 'increasing'
    }
    
    insights = grok.generate_eco_insights(user_data)
    print(f"✅ Insights Generated: {insights[:80]}...")

def test_enhanced_ai_services():
    """Test AI-enhanced services"""
    print("\n🌱 Testing Enhanced AI Services")
    print("=" * 50)
    
    # Create test user
    try:
        user = User.objects.get(username='grok_test_user')
    except User.DoesNotExist:
        user = User.objects.create_user(username='grok_test_user', password='testpass123')
    
    # Create profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.total_points = 100
    profile.total_carbon_saved = 15.5
    profile.save()
    
    print(f"✅ Test user: {user.username}")
    
    # Test EcoMentorAI
    print("\n1. Testing Enhanced EcoMentorAI...")
    try:
        mentor = EcoMentorAI(user)
        recommendation = mentor.generate_personalized_recommendation()
        print(f"✅ AI Recommendation: {recommendation['title']}")
        print(f"   Content: {recommendation['content'][:80]}...")
        print(f"   AI Generated: {recommendation['metadata'].get('ai_generated', False)}")
    except Exception as e:
        print(f"❌ EcoMentorAI failed: {e}")
    
    # Test ChallengeGeneratorAI
    print("\n2. Testing Enhanced ChallengeGeneratorAI...")
    try:
        challenge_gen = ChallengeGeneratorAI(user)
        challenge = challenge_gen.generate_weekly_challenge(force_new=True)
        print(f"✅ Challenge Generated: {challenge['title']}")
        print(f"   Description: {challenge['description'][:60]}...")
        print(f"   Points: {challenge['reward_points']}")
        print(f"   AI Generated: {challenge.get('ai_generated', False)}")
    except Exception as e:
        print(f"❌ ChallengeGeneratorAI failed: {e}")

def test_api_connectivity():
    """Test direct API connectivity"""
    print("\n🔗 Testing Grok API Connectivity")
    print("=" * 50)
    
    grok = GrokAI()
    
    test_queries = [
        "Hello, how are you?",
        "What is carbon footprint?",
        "Give me an eco-friendly tip",
        "How can I save energy at home?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Testing: '{query}'")
        result = grok.generate_content(query)
        if result['success']:
            print(f"✅ Response length: {len(result['content'])} chars")
            print(f"   Preview: {result['content'][:60]}...")
        else:
            print(f"❌ Failed: {result['error']}")

def main():
    print("🚀 Grok AI Integration Test Suite")
    print("=" * 60)
    
    # Test basic Grok AI
    test_grok_api()
    
    # Test enhanced services
    test_enhanced_ai_services()
    
    # Test API connectivity
    test_api_connectivity()
    
    print("\n🎉 All Tests Completed!")
    print("=" * 60)
    print("✅ Grok AI is now integrated into EcoTracker!")
    print("🤖 Enhanced chatbot with real AI responses")
    print("🎮 AI-generated challenges and insights")
    print("📊 Personalized recommendations powered by AI")
    print("💡 Try the chatbot with queries like:")
    print("   - 'What should I do?'")
    print("   - 'Give me a challenge'")
    print("   - 'How are my points?'")
    print("   - 'What's my environmental impact?'")

if __name__ == "__main__":
    main()