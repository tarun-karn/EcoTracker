from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from teams.models import Team
from activities.models import ActivitySubmission, CarbonLog
from users.models import UserProfile
from ai_features.models import AIRecommendation, CarbonPrediction, EfficiencyInsight, DynamicChallenge
from ai_features.ai_services import EcoMentorAI, CarbonPredictorAI, EfficiencyAnalyzerAI, ChallengeGeneratorAI, AICalculatorService
from django.views.decorators.http import require_POST
import json
import logging
# import openai # Uncomment for OpenAI integration
# from django.conf import settings # Uncomment for OpenAI integration

logger = logging.getLogger(__name__)

User = get_user_model()

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get or create user profile and update stats
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.update_stats()
        
        # Basic dashboard data
        context['submissions'] = ActivitySubmission.objects.filter(user=user).order_by('-submitted_at')[:10]
        context['total_points'] = profile.total_points
        context['total_carbon_saved'] = profile.total_carbon_saved
        context['profile'] = profile
        
        # AI-Enhanced Features
        self._add_ai_recommendations(context, user)
        self._add_carbon_predictions(context, user)
        self._add_efficiency_insights(context, user)
        self._add_dynamic_challenges(context, user)
        
        return context
    
    def _add_ai_recommendations(self, context, user):
        """Add AI recommendations to context"""
        try:
            eco_mentor = EcoMentorAI(user)
            # Get latest recommendation or generate new one
            latest_rec = AIRecommendation.objects.filter(
                user=user, is_active=True
            ).order_by('-created_at').first()
            
            if not latest_rec or (latest_rec.expires_at and latest_rec.expires_at < timezone.now()):
                recommendation = eco_mentor.generate_personalized_recommendation()
                context['ai_recommendation'] = recommendation
            else:
                context['ai_recommendation'] = {
                    'id': latest_rec.id,
                    'title': latest_rec.title,
                    'content': latest_rec.content,
                    'metadata': latest_rec.metadata,
                    'motivational_message': latest_rec.metadata.get('motivational_message', 'Keep up the great work!')
                }
        except Exception as e:
            # Fallback recommendation
            context['ai_recommendation'] = {
                'title': 'Keep Going! 🌱',
                'content': 'Continue your eco journey with small, consistent actions!',
                'metadata': {},
                'motivational_message': 'Every action counts!'
            }
    
    def _add_carbon_predictions(self, context, user):
        """Add carbon impact predictions"""
        try:
            predictor = CarbonPredictorAI(user)
            predictions = predictor.predict_future_savings(30)
            context['carbon_predictions'] = predictions
        except Exception:
            context['carbon_predictions'] = {
                'daily': 2.0,
                'weekly': 14.0,
                'monthly': 60.0,
                'confidence': 0.5,
                'trend_direction': 'stable'
            }
    
    def _add_efficiency_insights(self, context, user):
        """Add efficiency analysis"""
        try:
            analyzer = EfficiencyAnalyzerAI(user)
            # Get recent insights or generate new ones
            recent_insights = EfficiencyInsight.objects.filter(
                user=user
            ).order_by('-created_at')[:3]
            
            if recent_insights.count() < 2:
                insights = analyzer.calculate_efficiency_insights()
                context['efficiency_insights'] = insights
            else:
                context['efficiency_insights'] = [
                    {
                        'title': insight.title,
                        'description': insight.description,
                        'score': insight.efficiency_score
                    } for insight in recent_insights
                ]
        except Exception:
            context['efficiency_insights'] = []
    
    def _add_dynamic_challenges(self, context, user):
        """Add dynamic challenges"""
        try:
            # Get active challenges
            active_challenges = DynamicChallenge.objects.filter(
                user=user,
                is_completed=False,
                expires_at__gt=timezone.now()
            ).order_by('-created_at')[:3]
            
            context['active_challenges'] = [
                {
                    'id': challenge.id,
                    'title': challenge.title,
                    'description': challenge.description,
                    'progress_percentage': challenge.progress_percentage,
                    'target_value': challenge.target_value,
                    'current_progress': challenge.current_progress,
                    'reward_points': challenge.reward_points,
                    'difficulty': challenge.difficulty,
                    'expires_at': challenge.expires_at
                } for challenge in active_challenges
            ]
            
            # Generate new challenge if none active
            if not active_challenges:
                challenge_gen = ChallengeGeneratorAI(user)
                new_challenge = challenge_gen.generate_weekly_challenge()
                context['active_challenges'] = [new_challenge]
                
        except Exception:
            context['active_challenges'] = []

class LeaderboardView(LoginRequiredMixin, View):
    def get(self, request):
        # Individual Leaderboard
        individual_leaderboard = User.objects.annotate(
            total_points=Sum('carbonlog__points_earned')
        ).filter(total_points__gt=0).order_by('-total_points')[:10]

        # Team Leaderboard
        team_leaderboard = sorted(Team.objects.all(), key=lambda t: t.total_points, reverse=True)[:10]

        context = {
            'individual_leaderboard': individual_leaderboard,
            'team_leaderboard': team_leaderboard,
        }
        return render(request, 'dashboard/leaderboard.html', context)


class AICalculatorView(LoginRequiredMixin, TemplateView):
    template_name = 'ai_calculator/calculator.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'AI Carbon Calculator'
        return context

@login_required
def carbon_chart_data(request):
    try:
        # Data for the last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Aggregate user's data
        user_data = CarbonLog.objects.filter(
            user=request.user,
            timestamp__gte=thirty_days_ago
        ).annotate(day=TruncDay('timestamp')).values('day').annotate(
            daily_sum=Sum('carbon_saved_kg')
        ).order_by('day')

        # Aggregate campus-wide data
        campus_data = CarbonLog.objects.filter(
            timestamp__gte=thirty_days_ago
        ).annotate(day=TruncDay('timestamp')).values('day').annotate(
            daily_sum=Sum('carbon_saved_kg')
        ).order_by('day')

        labels = [(thirty_days_ago + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]

        user_values = {item['day'].strftime('%Y-%m-%d'): float(item['daily_sum'] or 0) for item in user_data}
        campus_values = {item['day'].strftime('%Y-%m-%d'): float(item['daily_sum'] or 0) for item in campus_data}

        user_chart_data = [user_values.get(label, 0) for label in labels]
        campus_chart_data = [campus_values.get(label, 0) for label in labels]

        return JsonResponse({
            'labels': labels,
            'user_data': user_chart_data,
            'campus_data': campus_chart_data,
        })
    except Exception as e:
        # Return empty data on error
        labels = [(timezone.now() - timedelta(days=30) + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]
        return JsonResponse({
            'labels': labels,
            'user_data': [0] * 31,
            'campus_data': [0] * 31,
            'error': str(e)
        })


@login_required
def carbon_pie_chart_data(request):
    """API endpoint for pie chart data showing carbon savings by activity type"""
    try:
        # Get carbon savings by activity type for the user
        # Since CarbonLog doesn't have activity_type directly, we need to get it from ActivitySubmission
        activity_data = CarbonLog.objects.filter(
            user=request.user,
            submission__isnull=False  # Only include logs with associated submissions
        ).values('submission__activity_type').annotate(
            total_carbon=Sum('carbon_saved_kg')
        ).filter(total_carbon__gt=0).order_by('-total_carbon')
        
        # Activity type mapping for better display names
        activity_names = {
            'TREE': 'Tree Planting 🌳',
            'RECYCLE': 'Recycling ♻️',
            'CLEANUP': 'Clean-up 🧹',
            'AWARENESS': 'Awareness 📢',
            'ENERGY_SAVING': 'Energy Saving ⚡',
            'WATER_CONSERVATION': 'Water Conservation 💧',
            'TRANSPORT': 'Eco Transport 🚲',
            'WASTE_REDUCTION': 'Waste Reduction 🗑️'
        }
        
        # Colors for pie chart segments
        colors = [
            '#10b981',  # Green for trees
            '#3b82f6',  # Blue for recycling
            '#f59e0b',  # Orange for cleanup
            '#8b5cf6',  # Purple for awareness
            '#ef4444',  # Red for energy
            '#06b6d4',  # Cyan for water
            '#84cc16',  # Lime for transport
            '#f97316'   # Orange for waste
        ]
        
        labels = []
        data = []
        background_colors = []
        border_colors = []
        
        for i, item in enumerate(activity_data):
            activity_type = item['submission__activity_type']
            carbon_amount = float(item['total_carbon'])
            
            labels.append(activity_names.get(activity_type, activity_type.title()))
            data.append(carbon_amount)
            background_colors.append(colors[i % len(colors)])
            border_colors.append('#ffffff')
        
        # If no data, return a placeholder
        if not data:
            return JsonResponse({
                'labels': ['No Data'],
                'data': [1],
                'backgroundColor': ['#e5e7eb'],
                'borderColor': ['#ffffff'],
                'total_carbon': 0,
                'message': 'Start logging activities to see your carbon impact!'
            })
        
        total_carbon = sum(data)
        
        return JsonResponse({
            'labels': labels,
            'data': data,
            'backgroundColor': background_colors,
            'borderColor': border_colors,
            'total_carbon': round(total_carbon, 2),
            'activity_count': len(data)
        })
        
    except Exception as e:
        logger.error(f"Pie chart data error: {e}")
        return JsonResponse({
            'labels': ['Error'],
            'data': [1],
            'backgroundColor': ['#ef4444'],
            'borderColor': ['#ffffff'],
            'total_carbon': 0,
            'error': str(e)
        })


@login_required
@require_POST
def chatbot_api(request):
    """AI Eco Chatbot API with OpenRouter AI Integration"""
    try:
        from ai_features.ai_services import OpenRouterAI, EcoMentorAI, CarbonPredictorAI, EfficiencyAnalyzerAI, ChallengeGeneratorAI
        
        data = json.loads(request.body)
        user_query = data.get('query', '').strip().lower()
        
        if not user_query:
            return JsonResponse({'response': 'Please ask me something! 🤔'})
        
        # Initialize AI services
        openrouter = OpenRouterAI()
        eco_mentor = EcoMentorAI(request.user)
        profile = getattr(request.user, 'profile', None)
        
        # Prepare user context for AI
        user_context = {
            'username': request.user.username,
            'total_points': profile.total_points if profile else 0,
            'total_carbon': profile.total_carbon_saved if profile else 0,
            'recent_activities': 'Various eco activities',
            'level': 'Active eco-warrior'
        }
        
        additional_data = {}
        
        # Handle specific query types with AI enhancement
        if any(word in user_query for word in ['recommend', 'should', 'suggest', 'what', 'activity']):
            try:
                recommendation = eco_mentor.generate_personalized_recommendation()
                additional_data['recommendation'] = recommendation
                ai_response = openrouter.generate_eco_chatbot_response(
                    f"The user is asking for recommendations. I have this recommendation: {recommendation['title']} - {recommendation['content']}",
                    user_context
                )
            except Exception as e:
                ai_response = "I'd love to give you a personalized recommendation! Try recycling, energy saving, or tree planting activities. 🌱"
        
        elif any(word in user_query for word in ['points', 'score', 'progress', 'doing']):
            points_info = f"You have {user_context['total_points']} points and saved {user_context['total_carbon']}kg CO₂!"
            ai_response = openrouter.generate_eco_chatbot_response(
                f"User asking about their progress: {points_info}",
                user_context
            )
            
        elif any(word in user_query for word in ['challenge', 'goal', 'mission']):
            try:
                current_challenges = DynamicChallenge.objects.filter(
                    user=request.user,
                    is_completed=False,
                    expires_at__gt=timezone.now()
                ).first()
                
                if current_challenges:
                    challenge_info = f"Current challenge: {current_challenges.title}"
                    additional_data['current_challenge'] = {
                        'title': current_challenges.title,
                        'progress': current_challenges.progress_percentage,
                        'reward': current_challenges.reward_points
                    }
                else:
                    challenge_gen = ChallengeGeneratorAI(request.user)
                    new_challenge = challenge_gen.generate_weekly_challenge()
                    challenge_info = f"New challenge created: {new_challenge['title']}"
                    additional_data['new_challenge'] = new_challenge
                
                ai_response = openrouter.generate_eco_chatbot_response(
                    f"User asking about challenges: {challenge_info}",
                    user_context
                )
            except Exception as e:
                ai_response = "I can help you with exciting eco challenges! Try asking me to generate a new one! 🎮"
        
        elif any(word in user_query for word in ['predict', 'future', 'forecast', 'will']):
            try:
                predictor = CarbonPredictorAI(request.user)
                predictions = predictor.predict_future_savings(30)
                additional_data['predictions'] = predictions
                ai_response = openrouter.generate_eco_chatbot_response(
                    f"User asking about predictions. Forecast: {predictions['monthly']}kg CO₂ this month",
                    user_context
                )
            except Exception as e:
                ai_response = "I can predict your future carbon savings! Based on your activity, you're on track for great impact! 📈"
        
        elif any(word in user_query for word in ['efficient', 'efficiency', 'performance']):
            try:
                analyzer = EfficiencyAnalyzerAI(request.user)
                insights = analyzer.calculate_efficiency_insights()
                additional_data['insights'] = insights
                ai_response = openrouter.generate_eco_chatbot_response(
                    f"User asking about efficiency. Current efficiency: {insights.get('efficiency_score', 0)} pts/kg CO₂",
                    user_context
                )
            except Exception as e:
                ai_response = "Your eco efficiency is improving! Every action counts toward a sustainable future! ⚡"
        
        elif any(word in user_query for word in ['calculator', 'calculate', 'compute', 'impact']):
            ai_response = openrouter.generate_eco_chatbot_response(
                "User wants to use the carbon calculator",
                user_context
            ) + "\n\n📊 Try our AI Calculator: [Visit Calculator](/dashboard/ai-calculator/)"
        
        else:
            # General AI response for any other query
            ai_response = openrouter.generate_eco_chatbot_response(user_query, user_context)
        
        return JsonResponse({
            'response': ai_response,
            'additional_data': additional_data,
            'ai_powered': True,
            'timestamp': timezone.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'response': 'Invalid request format. Please try again! 🤖'})
    except Exception as e:
        logger.error(f"Chatbot AI error: {e}")
        return JsonResponse({
            'response': 'I\'m having some technical difficulties. Please try again! 😅',
            'error': str(e)
        })


# AI-Enhanced API Endpoints

@login_required
def ai_recommendation_api(request):
    """Get personalized AI recommendation"""
    try:
        eco_mentor = EcoMentorAI(request.user)
        recommendation = eco_mentor.generate_personalized_recommendation()
        return JsonResponse({
            'success': True,
            'recommendation': recommendation
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def carbon_prediction_api(request):
    """Get carbon impact predictions"""
    days_ahead = int(request.GET.get('days', 30))
    try:
        predictor = CarbonPredictorAI(request.user)
        predictions = predictor.predict_future_savings(days_ahead)
        return JsonResponse({
            'success': True,
            'predictions': predictions
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def efficiency_insights_api(request):
    """Get efficiency insights"""
    try:
        analyzer = EfficiencyAnalyzerAI(request.user)
        insights = analyzer.calculate_efficiency_insights()
        return JsonResponse({
            'success': True,
            'insights': insights
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def generate_challenge_api(request):
    """Generate new dynamic challenge"""
    try:
        challenge_gen = ChallengeGeneratorAI(request.user)
        # Always force new challenge when user clicks the button
        challenge = challenge_gen.generate_weekly_challenge(force_new=True)
        return JsonResponse({
            'success': True,
            'challenge': challenge,
            'message': 'New challenge generated! 🎮'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def update_challenge_progress_api(request):
    """Update challenge progress"""
    try:
        data = json.loads(request.body)
        challenge_id = data.get('challenge_id')
        progress = data.get('progress', 0)
        
        challenge = DynamicChallenge.objects.get(
            id=challenge_id,
            user=request.user
        )
        
        challenge.current_progress = min(progress, challenge.target_value)
        if challenge.current_progress >= challenge.target_value:
            challenge.is_completed = True
            challenge.completed_at = timezone.now()
            
            # Award points to user profile
            profile = request.user.profile
            profile.total_points += challenge.reward_points
            profile.save()
            
        challenge.save()
        
        return JsonResponse({
            'success': True,
            'progress_percentage': challenge.progress_percentage,
            'is_completed': challenge.is_completed,
            'points_awarded': challenge.reward_points if challenge.is_completed else 0
        })
        
    except DynamicChallenge.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Challenge not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def ai_calculator_api(request):
    """AI-based carbon savings calculator"""
    try:
        calculator = AICalculatorService(request.user)
        
        if request.method == 'POST':
            data = json.loads(request.body)
            activity_type = data.get('activity_type', 'RECYCLE')
            quantity = float(data.get('quantity', 1))
            duration_hours = data.get('duration_hours')
            
            result = calculator.calculate_activity_impact(activity_type, quantity, duration_hours)
            
            return JsonResponse({
                'success': True,
                'calculation': result
            })
        
        else:
            # GET request - return calculator info
            return JsonResponse({
                'success': True,
                'available_activities': [
                    {'type': 'TREE', 'name': 'Tree Planting', 'unit': 'trees'},
                    {'type': 'RECYCLE', 'name': 'Recycling', 'unit': 'kg'},
                    {'type': 'CLEANUP', 'name': 'Cleanup', 'unit': 'kg'},
                    {'type': 'AWARENESS', 'name': 'Awareness Campaign', 'unit': 'hours'},
                    {'type': 'ENERGY_SAVING', 'name': 'Energy Saving', 'unit': 'kWh'}
                ]
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def ai_calculator_compound_api(request):
    """Calculate compound effects for multiple activities"""
    try:
        calculator = AICalculatorService(request.user)
        data = json.loads(request.body)
        activities = data.get('activities', [])
        
        result = calculator.calculate_compound_activities(activities)
        
        return JsonResponse({
            'success': True,
            'compound_result': result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required 
def ai_calculator_predict_api(request):
    """Predict outcomes for planned activities"""
    try:
        calculator = AICalculatorService(request.user)
        activity_type = request.GET.get('activity_type', 'RECYCLE')
        target_quantity = float(request.GET.get('quantity', 5))
        
        result = calculator.predict_activity_outcomes(activity_type, target_quantity)
        
        return JsonResponse({
            'success': True,
            'prediction': result
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
