from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

class HomePageView(TemplateView):
    template_name = 'core/home.html'

@csrf_exempt
@require_POST
def global_chatbot_api(request):
    """Global AI Eco Chatbot API accessible from all pages with Grok AI integration"""
    try:
        data = json.loads(request.body)
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return JsonResponse({'response': 'Please ask me something! 🤔'})
        
        # Always try to use AI first, then fallback
        try:
            # Import AI services
            from ai_features.ai_services import OpenRouterAI
            
            openrouter = OpenRouterAI()
            
            # Prepare user context for authenticated users
            user_context = {
                'username': 'Guest',
                'total_points': 0,
                'total_carbon': 0,
                'level': 'New user',
                'recent_activities': []
            }
            
            # Enhanced context for authenticated users
            if request.user.is_authenticated:
                profile = getattr(request.user, 'profile', None)
                user_context.update({
                    'username': request.user.username,
                    'total_points': profile.total_points if profile else 0,
                    'total_carbon': profile.total_carbon_saved if profile else 0,
                    'level': 'Active eco-warrior'
                })
            
            # Get AI response using Grok
            ai_response = openrouter.generate_eco_chatbot_response(user_query, user_context)
            
            return JsonResponse({
                'response': ai_response,
                'ai_powered': True,
                'user_authenticated': request.user.is_authenticated,
                'model': 'Grok AI via OpenRouter'
            })
            
        except ImportError as e:
            logger.warning(f"AI services not available: {e}")
        except Exception as e:
            logger.error(f"Global chatbot AI error: {e}")
        
        # Enhanced fallback responses
        fallback_responses = {
            'hello': '👋 Hi there! I\'m EcoBot, your AI sustainability assistant powered by Grok! How can I help you save the planet today?',
            'help': '🌱 I can help you with eco-friendly tips, sustainability advice, carbon footprint tracking, and personalized recommendations! What would you like to know?',
            'tips': '💡 Quick eco-tips: Use reusable bags 🛍️, recycle properly ♻️, save energy 💡, plant trees 🌳, and choose sustainable transport 🚄!',
            'carbon': '🌍 Every action counts! Try cycling instead of driving, use LED bulbs, plant trees, and reduce waste. Small changes make BIG impacts! 💪',
            'recycle': '♻️ Great question! Clean containers before recycling, separate materials properly, and check local guidelines. Recycling 1kg saves 1.5kg CO₂!',
            'energy': '⚡ Smart energy tips: Turn off lights, use LED bulbs (90% less energy!), unplug devices, and use natural light when possible! Every kWh saved = 0.85kg CO₂!',
            'water': '💧 Water conservation rocks! Take shorter showers, fix leaks, collect rainwater, and use water-efficient appliances. Save water = save energy!',
            'trees': '🌳 Trees are climate heroes! One tree absorbs 22kg CO₂/year, provides oxygen for 2 people, and supports biodiversity. Plant one today! 🌱',
            'points': f'🏆 {"".join(["You have ", str(getattr(getattr(request.user, "profile", None), "total_points", 0)), " points!"]) if request.user.is_authenticated else "Sign up to start earning points!"} Complete eco-activities to level up!',
            'challenge': '🎮 Ready for a challenge? Try: Plant 3 trees 🌳, recycle 5kg materials ♻️, or save 20kWh energy ⚡! Which interests you?'
        }
        
        # Enhanced keyword matching
        query_lower = user_query.lower()
        for keyword, response in fallback_responses.items():
            if keyword in query_lower:
                return JsonResponse({
                    'response': response,
                    'ai_powered': False,
                    'user_authenticated': request.user.is_authenticated,
                    'fallback_used': True
                })
        
        # Default smart response
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            points = profile.total_points if profile else 0
            carbon = profile.total_carbon_saved if profile else 0
            default_response = f"🤖 Hi {request.user.username}! You have {points} points and saved {carbon}kg CO₂! I'm here to help with eco-tips, challenges, and sustainability advice. Try asking about 'tips', 'recycling', or 'energy saving'! 🌱"
        else:
            default_response = "🌱 Thanks for your question! I'm EcoBot, powered by Grok AI! I help with eco-tips, sustainability advice, and carbon footprint reduction. Try asking about 'tips', 'recycling', 'energy saving', or 'challenges'! Sign up to track your progress! 🚀"
        
        return JsonResponse({
            'response': default_response,
            'ai_powered': False,
            'user_authenticated': request.user.is_authenticated,
            'suggestion': 'Try asking specific questions about sustainability, recycling, energy saving, or eco-challenges!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'response': 'Invalid request format. Please try again! 🤖'})
    except Exception as e:
        logger.error(f"Global chatbot error: {e}")
        return JsonResponse({
            'response': 'I\'m having some technical difficulties. Please try again! 😅',
            'error': str(e) if logger.isEnabledFor(logging.DEBUG) else 'Technical error'
        })
