#!/usr/bin/env python
"""
Comprehensive AI Integration Test for EcoTracker
Tests AI usage in chatbot, challenge generation, and efficiency insights
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ai_features.ai_services import OpenRouterAI, EcoMentorAI, ChallengeGeneratorAI, EfficiencyAnalyzerAI
from django.contrib.auth.models import User
from users.models import UserProfile
from activities.models import ActivitySubmission, CarbonLog

def test_grok_ai_basic():
    """Test basic OpenRouter AI functionality"""
    print("🤖 Testing OpenRouter AI Basic Functionality")
    print("=" * 50)
    
    openrouter = OpenRouterAI()
    
    # Test 1: Basic content generation
    print("1. Testing Basic Content Generation...")
    result = openrouter.generate_content("What is sustainability in 20 words?")
    if result['success']:
        print(f"✅ Success: {result['content'][:60]}...")
        print(f"   AI Response Length: {len(result['content'])} characters")
    else:
        print(f"❌ Failed: {result['error']}")
        print("   Falling back to rule-based responses")
    
    return result['success']

def test_chatbot_ai_responses():
    """Test chatbot AI responses"""
    print("\n💬 Testing AI-Powered Chatbot Responses")
    print("=" * 50)
    
    openrouter = OpenRouterAI()
    
    user_context = {
        'total_points': 250,
        'total_carbon': 35.5,
        'recent_activities': ['RECYCLE', 'TREE', 'ENERGY_SAVING'],
        'level': 'Intermediate'
    }
    
    test_queries = [
        ("What should I do to help the environment?", "recommendation"),
        ("How are my points?", "progress"),
        ("Give me a challenge", "challenge"),
        ("What's my environmental impact?", "impact"),
        ("How can I be more efficient?", "efficiency")
    ]
    
    ai_responses = 0
    for query, category in test_queries:
        print(f"Testing: '{query}'")
        response = openrouter.generate_eco_chatbot_response(query, user_context)
        
        if "Sorry, I'm having trouble connecting" not in response:
            print(f"✅ AI Response: {response[:80]}...")
            ai_responses += 1
        else:
            print(f"❌ Fallback Response: {response[:60]}...")
    
    print(f"\n📊 AI Response Rate: {ai_responses}/{len(test_queries)} ({(ai_responses/len(test_queries)*100):.0f}%)")
    return ai_responses > 0

def test_challenge_generation_ai():
    """Test AI-powered challenge generation"""
    print("\n🎮 Testing AI-Powered Challenge Generation")
    print("=" * 50)
    
    # Create test user
    try:
        user = User.objects.get(username='ai_challenge_test')
    except User.DoesNotExist:
        user = User.objects.create_user(username='ai_challenge_test', password='testpass123')
    
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.total_points = 350
    profile.total_carbon_saved = 25.5
    profile.save()
    
    challenge_gen = ChallengeGeneratorAI(user)
    
    # Test multiple challenge generations
    ai_challenges = 0
    for i in range(3):
        print(f"\nTest {i+1}: Generating challenge...")
        try:
            challenge = challenge_gen.generate_weekly_challenge(force_new=True)
            print(f"   Title: {challenge['title']}")
            print(f"   Description: {challenge['description'][:60]}...")
            print(f"   Points: {challenge['reward_points']}")
            print(f"   Difficulty: {challenge['difficulty']}")
            
            if challenge.get('ai_generated', False):
                print("   ✅ AI-Generated Challenge")
                ai_challenges += 1
            else:
                print("   ⚠️  Rule-based Challenge (AI fallback)")
                
        except Exception as e:
            print(f"   ❌ Challenge generation failed: {e}")
    
    print(f"\n📊 AI Challenge Generation Rate: {ai_challenges}/3 ({(ai_challenges/3*100):.0f}%)")
    
    # Cleanup
    user.delete()
    return ai_challenges > 0

def test_efficiency_insights_ai():
    """Test AI-powered efficiency insights"""
    print("\n⚡ Testing AI-Powered Efficiency Insights")
    print("=" * 50)
    
    # Create test user with some activity data
    try:
        user = User.objects.get(username='ai_efficiency_test')
    except User.DoesNotExist:
        user = User.objects.create_user(username='ai_efficiency_test', password='testpass123')
    
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.total_points = 500
    profile.total_carbon_saved = 42.0
    profile.save()
    
    # Create some mock carbon logs
    CarbonLog.objects.filter(user=user).delete()  # Clean up first
    for i in range(5):
        CarbonLog.objects.create(
            user=user,
            carbon_saved_kg=8.0 + i,
            points_earned=120 + (i * 10)
        )
    
    analyzer = EfficiencyAnalyzerAI(user)
    
    try:
        insights = analyzer.calculate_efficiency_insights()
        print(f"✅ Efficiency Analysis Complete")
        print(f"   Efficiency Score: {insights['efficiency_score']:.2f} pts/kg CO₂")
        print(f"   Performance Level: {insights['performance_level']}")
        print(f"   Total Points: {insights['total_points']}")
        print(f"   Total Carbon: {insights['total_carbon']}kg CO₂")
        
        if insights.get('ai_generated', False):
            print("   ✅ AI-Generated Insights")
            print(f"   AI Insights: {insights.get('ai_insights', 'None')[:80]}...")
            ai_insights = True
        else:
            print("   ⚠️  Rule-based Insights (AI fallback)")
            ai_insights = False
            
    except Exception as e:
        print(f"❌ Efficiency insights failed: {e}")
        ai_insights = False
    
    # Cleanup
    CarbonLog.objects.filter(user=user).delete()
    user.delete()
    
    return ai_insights

def test_recommendation_ai():
    """Test AI-powered recommendations"""
    print("\n🎯 Testing AI-Powered Recommendations")
    print("=" * 50)
    
    # Create test user
    try:
        user = User.objects.get(username='ai_recommendation_test')
    except User.DoesNotExist:
        user = User.objects.create_user(username='ai_recommendation_test', password='testpass123')
    
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.total_points = 150
    profile.total_carbon_saved = 18.0
    profile.save()
    
    mentor = EcoMentorAI(user)
    
    try:
        recommendation = mentor.generate_personalized_recommendation()
        print(f"✅ Recommendation Generated")
        print(f"   Title: {recommendation['title']}")
        print(f"   Content: {recommendation['content'][:80]}...")
        print(f"   Expected Points: {recommendation['metadata'].get('expected_points', 'N/A')}")
        
        if recommendation['metadata'].get('ai_generated', False):
            print("   ✅ AI-Generated Recommendation")
            ai_recommendation = True
        else:
            print("   ⚠️  Rule-based Recommendation (AI fallback)")
            ai_recommendation = False
            
    except Exception as e:
        print(f"❌ Recommendation generation failed: {e}")
        ai_recommendation = False
    
    # Cleanup
    user.delete()
    return ai_recommendation

def main():
    print("🚀 Comprehensive AI Integration Test for EcoTracker")
    print("=" * 70)
    print("Testing AI integration in chatbot, challenges, efficiency, and recommendations")
    print()
    
    # Test results
    results = {}
    
    # Test basic AI functionality
    results['basic_ai'] = test_grok_ai_basic()
    
    # Test chatbot AI responses
    results['chatbot_ai'] = test_chatbot_ai_responses()
    
    # Test challenge generation
    results['challenge_ai'] = test_challenge_generation_ai()
    
    # Test efficiency insights
    results['efficiency_ai'] = test_efficiency_insights_ai()
    
    # Test recommendations
    results['recommendation_ai'] = test_recommendation_ai()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 AI Integration Test Results Summary")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall Score: {passed_tests}/{total_tests} ({(passed_tests/total_tests*100):.0f}%)")
    
    if passed_tests == total_tests:
        print("🎉 All AI features working perfectly!")
    elif passed_tests > 0:
        print("⚠️  AI partially working - some features using fallback responses")
        print("💡 This is likely due to the Grok API key issue mentioned earlier")
    else:
        print("❌ AI not working - all features using fallback responses")
        print("🔧 Please verify the Grok API key configuration")
    
    print("\n📝 Notes:")
    print("- AI features have fallback mechanisms for reliability")
    print("- Fallback responses ensure the app continues working")
    print("- Fix the API key to enable full AI functionality")
    print("- Current implementation prioritizes AI but gracefully degrades")

if __name__ == "__main__":
    main()