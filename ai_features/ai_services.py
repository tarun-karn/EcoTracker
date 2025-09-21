"""
AI Services for Eco-Friendly Campus Tracker
Provides intelligent recommendations, predictions, and insights
"""

import random
import statistics
import time
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from django.contrib.auth.models import User
from django.conf import settings

from activities.models import ActivitySubmission, CarbonLog
from users.models import UserProfile
from .models import AIRecommendation, CarbonPrediction, EfficiencyInsight, DynamicChallenge


class EcoMentorAI:
    """Personalized AI Eco Mentor Service with OpenRouter AI Integration"""
    
    def __init__(self, user: User):
        self.user = user
        self.profile = getattr(user, 'profile', None)
        self.openrouter = OpenRouterAI()
        
    def generate_personalized_recommendation(self) -> Dict:
        
        # Get user's activity history
        user_activities = ActivitySubmission.objects.filter(
            user=self.user, status='APPROVED'
        ).values('activity_type').annotate(
            count=Count('id'),
            total_carbon=Sum('carbon_saved_kg'),
            total_points=Sum('points_awarded')
        )
        
        patterns = {item['activity_type']: item for item in user_activities}
        
        # Use AI for smarter recommendations
        user_context = {
            'total_points': self.profile.total_points if self.profile else 0,
            'total_carbon': self.profile.total_carbon_saved if self.profile else 0,
            'recent_activities': list(patterns.keys())[-5:],  # Last 5 activity types
            'level': self._assess_user_level()
        }
        
        # Get AI-generated recommendation
        ai_prompt = f"""Generate a personalized eco-friendly activity recommendation for a campus sustainability tracker user.
        
User Profile:
        - Points: {user_context['total_points']}
        - Carbon Saved: {user_context['total_carbon']}kg
        - Recent Activities: {', '.join(user_context['recent_activities']) if user_context['recent_activities'] else 'None'}
        - Level: {user_context['level']}
        
        Provide a specific, actionable recommendation with:
        1. Activity suggestion
        2. Target quantity
        3. Expected points (50-200)
        4. Expected CO2 savings (1-50kg)
        5. Motivational message
        
        Keep it encouraging and under 80 words!"""
        
        ai_result = self.openrouter.generate_content(ai_prompt)
        
        if ai_result['success']:
            recommendation = self._parse_ai_recommendation(ai_result['content'], user_context)
        else:
            # Fallback to rule-based recommendation
            recommendation = self._create_smart_recommendation(patterns)
        
        # Store recommendation
        ai_rec = AIRecommendation.objects.create(
            user=self.user,
            recommendation_type=recommendation['type'],
            title=recommendation['title'],
            content=recommendation['content'],
            metadata=recommendation['metadata'],
            expires_at=timezone.now() + timedelta(days=7)
        )
        
        return {
            'id': ai_rec.id,
            'title': recommendation['title'],
            'content': recommendation['content'],
            'metadata': recommendation['metadata'],
            'motivational_message': recommendation['motivational_message']
        }
    
    def _parse_ai_recommendation(self, ai_content: str, user_context: Dict) -> Dict:
        """Parse AI-generated recommendation into structured format"""
        return {
            'type': 'ACTIVITY',
            'title': 'AI-Powered Eco Recommendation 🤖',
            'content': ai_content,
            'metadata': {
                'suggested_activity': 'GENERAL',
                'target_quantity': 5,
                'expected_points': 100,
                'expected_carbon': 10.0,
                'ai_generated': True
            },
            'motivational_message': "Your personalized AI recommendation is ready! 🌱"
        }
    
    def _assess_user_level(self) -> str:
        """Assess user experience level"""
        if not self.profile:
            return 'BEGINNER'
        
        total_points = self.profile.total_points
        activity_count = ActivitySubmission.objects.filter(user=self.user, status='APPROVED').count()
        
        if total_points >= 1000 and activity_count >= 20:
            return 'EXPERT'
        elif total_points >= 500 and activity_count >= 10:
            return 'INTERMEDIATE'
        elif total_points >= 100 and activity_count >= 3:
            return 'NOVICE'
        else:
            return 'BEGINNER'
    
    def _create_smart_recommendation(self, patterns: Dict) -> Dict:
        """Create intelligent recommendation based on user patterns"""
        
        total_points = self.profile.total_points if self.profile else 0
        total_carbon = self.profile.total_carbon_saved if self.profile else 0
        
        if not patterns:
            # New user recommendation
            return {
                'type': 'ACTIVITY',
                'title': 'Start Your Eco Journey! 🌱',
                'content': 'Welcome! Try recycling 2kg of materials to earn 30 points and save 3kg of CO₂.',
                'metadata': {
                    'suggested_activity': 'RECYCLE',
                    'target_quantity': 2,
                    'expected_points': 30,
                    'expected_carbon': 3.0
                },
                'motivational_message': "Every small action counts! Let's make a difference! 🌍"
            }
        
        # Find least performed activity
        activity_counts = {k: v['count'] for k, v in patterns.items()}
        least_performed = min(activity_counts.items(), key=lambda x: x[1])[0]
        
        suggestions = {
            'TREE': ('Plant Trees for Maximum Impact! 🌳', 3, 150, 66.0),
            'RECYCLE': ('Boost Your Recycling Game! ♻️', 5, 75, 7.5),
            'CLEANUP': ('Join a Clean-up Drive! 🧹', 10, 50, 5.0),
            'AWARENESS': ('Spread Environmental Awareness! 📢', 2, 100, 10.0),
            'ENERGY_SAVING': ('Save Energy, Save the Planet! ⚡', 20, 85, 17.0)
        }
        
        title, qty, points, carbon = suggestions[least_performed]
        
        # Motivational message
        if total_points < 100:
            motivation = f"Getting started! 🚀 You have {total_points} points - keep building!"
        elif total_points < 500:
            motivation = f"Great progress! 🎯 {total_points} points and {total_carbon:.1f}kg CO₂ saved!"
        else:
            motivation = f"Eco Champion! 🏆 {total_points} points and {total_carbon:.1f}kg CO₂ saved!"
        
        return {
            'type': 'ACTIVITY',
            'title': title,
            'content': f'{title.split("!")[0]}! Target: {qty} units to earn {points} points and save {carbon}kg CO₂.',
            'metadata': {
                'suggested_activity': least_performed,
                'target_quantity': qty,
                'expected_points': points,
                'expected_carbon': carbon
            },
            'motivational_message': motivation
        }


class CarbonPredictorAI:
    """Carbon Impact Prediction Service"""
    
    def __init__(self, user: User):
        self.user = user
        
    def predict_future_savings(self, days_ahead: int = 30) -> Dict:
        """Predict future carbon savings based on historical trends"""
        
        # Get historical data
        sixty_days_ago = timezone.now() - timedelta(days=60)
        historical_data = CarbonLog.objects.filter(
            user=self.user, timestamp__gte=sixty_days_ago
        ).values_list('carbon_saved_kg', 'timestamp')
        
        if len(historical_data) < 3:
            return self._generate_default_prediction(days_ahead)
        
        # Calculate trends
        daily_savings = self._calculate_daily_averages(historical_data)
        trend = self._calculate_trend(daily_savings)
        predictions = self._generate_predictions(trend, days_ahead)
        
        # Store prediction
        prediction_date = timezone.now().date() + timedelta(days=days_ahead)
        CarbonPrediction.objects.update_or_create(
            user=self.user, prediction_date=prediction_date,
            defaults={
                'predicted_daily_savings': predictions['daily'],
                'predicted_weekly_savings': predictions['weekly'],
                'predicted_monthly_savings': predictions['monthly'],
                'confidence_score': predictions['confidence']
            }
        )
        
        return predictions
    
    def _calculate_daily_averages(self, historical_data: List) -> List[float]:
        """Calculate daily averages from historical data"""
        daily_totals = {}
        for carbon_saved, timestamp in historical_data:
            date_key = timestamp.date()
            daily_totals[date_key] = daily_totals.get(date_key, 0) + carbon_saved
        return list(daily_totals.values())
    
    def _calculate_trend(self, daily_savings: List[float]) -> Dict:
        """Calculate trend from daily savings data"""
        if len(daily_savings) < 2:
            return {'slope': 0, 'average': statistics.mean(daily_savings) if daily_savings else 0}
        
        # Simple linear regression
        n = len(daily_savings)
        x_values = list(range(n))
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(daily_savings)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, daily_savings))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        slope = numerator / denominator if denominator != 0 else 0
        
        return {
            'slope': slope,
            'average': y_mean,
            'variance': statistics.variance(daily_savings) if len(daily_savings) > 1 else 0
        }
    
    def _generate_predictions(self, trend: Dict, days_ahead: int) -> Dict:
        """Generate predictions based on trend analysis"""
        base_daily = max(0, trend['average'] + (trend['slope'] * days_ahead))
        daily_prediction = max(0, base_daily * random.uniform(0.8, 1.2))
        
        confidence = max(0.1, min(0.95, 1.0 - (trend['variance'] / max(1, trend['average']))))
        
        return {
            'daily': round(daily_prediction, 2),
            'weekly': round(daily_prediction * 7, 2),
            'monthly': round(daily_prediction * 30, 2),
            'confidence': round(confidence, 2),
            'trend_direction': 'increasing' if trend['slope'] > 0 else 'stable' if trend['slope'] == 0 else 'decreasing'
        }
    
    def _generate_default_prediction(self, days_ahead: int) -> Dict:
        """Generate default prediction for new users"""
        daily_default = 2.0
        return {
            'daily': daily_default,
            'weekly': daily_default * 7,
            'monthly': daily_default * 30,
            'confidence': 0.3,
            'trend_direction': 'stable'
        }


class EfficiencyAnalyzerAI:
    """Efficiency Analysis Service with AI Enhancement"""
    
    def __init__(self, user: User):
        self.user = user
        self.openrouter = OpenRouterAI()
        
    def calculate_efficiency_insights(self) -> Dict:
        """Calculate efficiency insights with AI enhancement"""
        
        # Overall efficiency calculation
        carbon_logs = CarbonLog.objects.filter(user=self.user)
        if carbon_logs.exists():
            total_points = carbon_logs.aggregate(Sum('points_earned'))['points_earned__sum'] or 0
            total_carbon = carbon_logs.aggregate(Sum('carbon_saved_kg'))['carbon_saved_kg__sum'] or 0
            
            if total_carbon > 0:
                efficiency = total_points / total_carbon
                avg_efficiency = 15.0  # Platform average
                performance = self._get_performance_level(efficiency, avg_efficiency)
                
                # Use AI to generate personalized insights
                user_data = {
                    'total_points': total_points,
                    'total_carbon': total_carbon,
                    'efficiency_score': efficiency,
                    'avg_efficiency': avg_efficiency,
                    'performance_level': performance,
                    'activity_count': ActivitySubmission.objects.filter(user=self.user, status='APPROVED').count()
                }
                
                # Generate AI insights
                ai_insights = self._generate_ai_efficiency_insights(user_data)
                
                # Create insight record with AI content
                EfficiencyInsight.objects.create(
                    user=self.user,
                    insight_type='AI_EFFICIENCY_ANALYSIS',
                    title=f'AI Efficiency Analysis: {efficiency:.1f} pts/kg CO₂',
                    description=ai_insights,
                    efficiency_score=efficiency
                )
                
                return {
                    'efficiency_score': efficiency,
                    'efficiency_trend': 'improving' if efficiency > avg_efficiency else 'stable',
                    'performance_level': performance,
                    'total_points': total_points,
                    'total_carbon': total_carbon,
                    'avg_efficiency': avg_efficiency,
                    'ai_insights': ai_insights,
                    'ai_generated': True
                }
        
        # Default for new users with AI welcome message
        welcome_insights = self._generate_new_user_ai_insights()
        return {
            'efficiency_score': 0,
            'efficiency_trend': 'stable',
            'performance_level': 'New user - start logging activities!',
            'total_points': 0,
            'total_carbon': 0,
            'avg_efficiency': 15.0,
            'ai_insights': welcome_insights,
            'ai_generated': True
        }
    
    def _get_performance_level(self, user_efficiency: float, avg_efficiency: float) -> str:
        """Determine performance level"""
        ratio = user_efficiency / avg_efficiency if avg_efficiency > 0 else 1
        
        if ratio >= 1.5:
            return "Outstanding! Top tier performance! 🏆"
        elif ratio >= 1.2:
            return "Excellent efficiency! Above average! 🌟"
        elif ratio >= 0.8:
            return "Good efficiency! Solid performance! 👍"
        else:
            return "Room for improvement! Focus on high-impact activities! 💪"
    
    def _generate_ai_efficiency_insights(self, user_data: Dict) -> str:
        """Generate AI-powered efficiency insights"""
        context = f"""
You are an AI efficiency analyst for an eco-friendly campus tracker. Generate personalized efficiency insights.

User Data:
- Total Points: {user_data['total_points']}
- Carbon Saved: {user_data['total_carbon']}kg CO₂
- Efficiency Score: {user_data['efficiency_score']:.2f} pts/kg CO₂
- Platform Average: {user_data['avg_efficiency']} pts/kg CO₂
- Performance Level: {user_data['performance_level']}
- Activities Completed: {user_data['activity_count']}

Provide 2-3 specific, actionable insights about their efficiency and improvement suggestions.
Include comparisons to platform average and specific tips for improvement.
Be encouraging and use relevant eco facts. Keep under 120 words with emojis.
"""
        
        prompt = "Generate personalized efficiency insights for this eco-tracker user"
        result = self.openrouter.generate_content(prompt, context)
        
        if result['success']:
            return result['content']
        else:
            # Fallback insights
            ratio = user_data['efficiency_score'] / user_data['avg_efficiency']
            if ratio >= 1.2:
                return f"🌟 Excellent work! Your {user_data['efficiency_score']:.1f} pts/kg CO₂ is {((ratio-1)*100):.0f}% above average! Keep focusing on high-impact activities like tree planting and energy saving. 💡"
            elif ratio >= 0.8:
                return f"👍 Good efficiency at {user_data['efficiency_score']:.1f} pts/kg CO₂! Try combining activities for better results. Consider awareness campaigns - they have great multiplier effects! 📢"
            else:
                return f"💪 Room to grow! Your {user_data['efficiency_score']:.1f} pts/kg CO₂ can improve. Focus on tree planting (22kg CO₂/tree) and energy saving for better efficiency! 🌳⚡"
    
    def _generate_new_user_ai_insights(self) -> str:
        """Generate AI insights for new users"""
        context = """
Generate encouraging insights for a new user of an eco-friendly campus tracker app.
Explain what efficiency means and provide 2-3 specific tips to get started.
Be welcoming, motivating, and actionable. Keep under 100 words with emojis.
"""
        
        prompt = "Welcome message and efficiency tips for new eco-tracker user"
        result = self.openrouter.generate_content(prompt, context)
        
        if result['success']:
            return result['content']
        else:
            return "🌱 Welcome to your eco journey! Efficiency measures points earned per kg CO₂ saved. Start with tree planting (high impact) or recycling (easy start). Track consistently for better insights! 🎯"


class ChallengeGeneratorAI:
    """Dynamic Challenge Generation Service with OpenRouter AI"""
    
    def __init__(self, user: User):
        self.user = user
        self.profile = getattr(user, 'profile', None)
        self.openrouter = OpenRouterAI()
        
    def generate_weekly_challenge(self, force_new: bool = False) -> Dict:
        
        # If force_new is True, mark existing active challenges as completed
        if force_new:
            DynamicChallenge.objects.filter(
                user=self.user,
                is_completed=False,
                expires_at__gt=timezone.now()
            ).update(is_completed=True)
        
        user_level = self._assess_user_level()
        
        # Prepare user context for AI
        user_context = {
            'total_points': self.profile.total_points if self.profile else 0,
            'total_carbon': self.profile.total_carbon_saved if self.profile else 0,
            'level': user_level,
            'activity_history': self._get_activity_summary()
        }
        
        # Try AI-generated challenge first
        ai_result = self.openrouter.generate_dynamic_challenge(user_context, user_level.lower())
        
        if ai_result['success']:
            challenge_data = ai_result['challenge']
            # Add difficulty mapping
            difficulty_map = {'beginner': 'EASY', 'novice': 'EASY', 'intermediate': 'MEDIUM', 'expert': 'HARD'}
            challenge_data['difficulty'] = difficulty_map.get(user_level.lower(), 'MEDIUM')
        else:
            # Fallback to rule-based challenge
            challenge_data = self._create_challenge_by_level(user_level, force_new)
        
        # Create challenge in database
        expires_at = timezone.now() + timedelta(days=7)
        challenge = DynamicChallenge.objects.create(
            user=self.user,
            challenge_type='WEEKLY',
            difficulty=challenge_data['difficulty'],
            title=challenge_data['title'],
            description=challenge_data['description'],
            target_value=challenge_data['target_value'],
            target_metric=challenge_data.get('target_metric', 'activities'),
            reward_points=challenge_data['reward_points'],
            expires_at=expires_at
        )
        
        return {
            'id': challenge.id,
            'title': challenge_data['title'],
            'description': challenge_data['description'],
            'target_value': challenge_data['target_value'],
            'reward_points': challenge_data['reward_points'],
            'difficulty': challenge_data['difficulty'],
            'ai_generated': ai_result['success']
        }
    
    def _get_activity_summary(self) -> str:
        """Get summary of user's recent activities"""
        recent_activities = ActivitySubmission.objects.filter(
            user=self.user, 
            status='APPROVED',
            submitted_at__gte=timezone.now() - timedelta(days=30)
        ).values_list('activity_type', flat=True)
        
        if recent_activities:
            activity_counts = {}
            for activity in recent_activities:
                activity_counts[activity] = activity_counts.get(activity, 0) + 1
            return ', '.join([f"{k}: {v}" for k, v in activity_counts.items()])
        return "No recent activities"
    
    def _assess_user_level(self) -> str:
        """Assess user experience level"""
        if not self.profile:
            return 'BEGINNER'
        
        total_points = self.profile.total_points
        activity_count = ActivitySubmission.objects.filter(user=self.user, status='APPROVED').count()
        
        if total_points >= 1000 and activity_count >= 20:
            return 'EXPERT'
        elif total_points >= 500 and activity_count >= 10:
            return 'INTERMEDIATE'
        elif total_points >= 100 and activity_count >= 3:
            return 'NOVICE'
        else:
            return 'BEGINNER'
    
    def _create_challenge_by_level(self, level: str, force_new: bool = False) -> Dict:
        """Create unique challenge based on user level and activity history"""
        
        # Get user's recent activities to avoid repetition
        recent_activities = ActivitySubmission.objects.filter(
            user=self.user, 
            status='APPROVED',
            submitted_at__gte=timezone.now() - timedelta(days=30)
        ).values_list('activity_type', flat=True)
        
        # Get user's preferred activity types
        activity_preferences = list(set(recent_activities))
        
        # Generate unique challenge based on level and preferences
        current_time = timezone.now()
        # Add randomness based on force_new to ensure different challenges
        random_factor = int(time.time()) if force_new else 0
        challenge_seed = f"{self.user.id}_{current_time.isocalendar()[1]}_{level}_{random_factor}"  # user_id + week_number + level + timestamp
        random.seed(hash(challenge_seed))  # Deterministic but unique per user per week
        
        base_challenges = {
            'BEGINNER': [
                {
                    'title': 'First Steps Green Challenge 🌱',
                    'description': 'Begin your eco journey! Complete 3 different eco-activities this week.',
                    'target_value': 3,
                    'target_metric': 'activities',
                    'reward_points': 75,
                    'difficulty': 'EASY'
                },
                {
                    'title': 'Paper Trail Challenge 📄',
                    'description': 'Go paperless! Recycle or avoid using 5kg of paper products.',
                    'target_value': 5,
                    'target_metric': 'kg_paper',
                    'reward_points': 60,
                    'difficulty': 'EASY'
                },
                {
                    'title': 'Water Wise Beginner 💧',
                    'description': 'Save water! Reduce consumption by 50 liters this week.',
                    'target_value': 50,
                    'target_metric': 'liters_water',
                    'reward_points': 80,
                    'difficulty': 'EASY'
                }
            ],
            'NOVICE': [
                {
                    'title': 'Energy Detective Challenge 🔍',
                    'description': 'Hunt down energy waste! Save 20kWh through smart choices.',
                    'target_value': 20,
                    'target_metric': 'kwh_saved',
                    'reward_points': 140,
                    'difficulty': 'MEDIUM'
                },
                {
                    'title': 'Plastic-Free Week Challenge 🚫',
                    'description': 'Reduce plastic use! Avoid or recycle 8 plastic items.',
                    'target_value': 8,
                    'target_metric': 'plastic_items',
                    'reward_points': 120,
                    'difficulty': 'MEDIUM'
                },
                {
                    'title': 'Commute Green Challenge 🚲',
                    'description': 'Eco-friendly transport! Use sustainable transport 5 times.',
                    'target_value': 5,
                    'target_metric': 'green_trips',
                    'reward_points': 150,
                    'difficulty': 'MEDIUM'
                }
            ],
            'INTERMEDIATE': [
                {
                    'title': 'Community Impact Leader 👥',
                    'description': 'Lead by example! Organize 2 community eco-events.',
                    'target_value': 2,
                    'target_metric': 'events',
                    'reward_points': 250,
                    'difficulty': 'MEDIUM'
                },
                {
                    'title': 'Waste Reduction Master 🗑️',
                    'description': 'Minimize waste! Reduce total waste output by 15kg.',
                    'target_value': 15,
                    'target_metric': 'kg_waste_reduced',
                    'reward_points': 220,
                    'difficulty': 'MEDIUM'
                },
                {
                    'title': 'Renewable Energy Advocate ⚡',
                    'description': 'Promote renewables! Generate or promote 30kWh renewable energy.',
                    'target_value': 30,
                    'target_metric': 'kwh_renewable',
                    'reward_points': 280,
                    'difficulty': 'HARD'
                }
            ],
            'EXPERT': [
                {
                    'title': 'Carbon Neutral Champion 🌍',
                    'description': 'Ultimate challenge! Achieve 100kg CO₂ savings this week.',
                    'target_value': 100,
                    'target_metric': 'kg_co2',
                    'reward_points': 600,
                    'difficulty': 'HARD'
                },
                {
                    'title': 'Ecosystem Builder 🏞️',
                    'description': 'Create lasting impact! Plant 20 trees or restore habitat.',
                    'target_value': 20,
                    'target_metric': 'trees_habitat',
                    'reward_points': 750,
                    'difficulty': 'HARD'
                },
                {
                    'title': 'Innovation Pioneer 💡',
                    'description': 'Lead innovation! Implement 3 new sustainability solutions.',
                    'target_value': 3,
                    'target_metric': 'innovations',
                    'reward_points': 800,
                    'difficulty': 'HARD'
                }
            ]
        }
        
        # Select a random challenge from the appropriate level
        available_challenges = base_challenges.get(level, base_challenges['BEGINNER'])
        selected_challenge = random.choice(available_challenges)
        
        # Add some randomization to make it more unique
        variation_factor = random.uniform(0.8, 1.3)
        selected_challenge['target_value'] = max(1, int(selected_challenge['target_value'] * variation_factor))
        selected_challenge['reward_points'] = int(selected_challenge['reward_points'] * variation_factor)
        
        # Add user-specific customization
        if activity_preferences:
            activity_focus = random.choice(activity_preferences)
            selected_challenge['description'] += f" Focus on {activity_focus.replace('_', ' ').title()} activities!"
        
        return selected_challenge
        


class OpenRouterAI:
    """OpenRouter AI Integration Service (OpenAI-compatible)"""
    
    def __init__(self):
        # Using Grok AI API via OpenRouter with provided API key
        self.api_key = "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"
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "anthropic/claude-3-haiku"  # Reliable fallback model via OpenRouter
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'HTTP-Referer': 'https://ecotracker.app',
            'X-Title': 'EcoTracker Campus Sustainability'
        }
        print(f"🤖 Grok AI initialized via OpenRouter")
    
    def generate_content(self, prompt: str, context: str = None) -> Dict:
        """Generate content using Grok AI via OpenRouter"""
        try:
            # Prepare the messages with context if provided
            messages = []
            if context:
                messages.append({
                    "role": "system",
                    "content": context
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            print(f"🚀 Making request to Grok API via OpenRouter...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30  # Increased timeout
            )
            
            print(f"📝 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and result['choices']:
                    content = result['choices'][0]['message']['content']
                    print(f"✅ Grok AI response received successfully")
                    return {
                        'success': True,
                        'content': content.strip(),
                        'raw_response': result
                    }
                else:
                    print(f"❌ No choices in API response: {result}")
            else:
                print(f"❌ API Error: {response.status_code} - {response.text}")
            
            return {
                'success': False,
                'error': f'API Error: {response.status_code} - {response.text}',
                'content': 'Sorry, Grok AI is temporarily unavailable. Here\'s a helpful eco-tip instead! 🌱'
            }
            
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout to Grok API")
            return {
                'success': False,
                'error': 'Request timeout',
                'content': 'Grok AI is taking too long to respond. Try asking about specific eco-topics like recycling or energy saving! 🚀'
            }
        except requests.exceptions.RequestException as e:
            print(f"🚫 Network error: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'content': 'Having network issues connecting to Grok AI. I can still help with basic eco-tips! 🌍'
            }
        except Exception as e:
            print(f"⚠️ Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'content': 'Something went wrong with Grok AI. Try asking simpler questions about sustainability! 🤖'
            }
    
    def generate_eco_chatbot_response(self, user_query: str, user_context: Dict) -> str:
        """Generate personalized eco chatbot response"""
        context = f"""
You are EcoBot, an AI assistant for an eco-friendly campus tracker app. Help users with:
- Eco-friendly activities and sustainability tips
- Carbon footprint reduction advice
- Environmental challenges and goals
- Points and achievements in their eco journey

User Profile:
- Total Points: {user_context.get('total_points', 0)}
- Carbon Saved: {user_context.get('total_carbon', 0)}kg CO₂
- Recent Activities: {user_context.get('recent_activities', 'None')}
- Current Level: {user_context.get('level', 'Beginner')}

Be encouraging, provide specific actionable advice, and keep responses under 100 words.
Use emojis appropriately and be enthusiastic about environmental action!
"""
        
        result = self.generate_content(user_query, context)
        return result['content']
    
    def generate_dynamic_challenge(self, user_context: Dict, difficulty: str) -> Dict:
        """Generate personalized eco challenge using AI"""
        context = f"""
Create a personalized eco-friendly challenge for a campus sustainability app user.

User Profile:
- Total Points: {user_context.get('total_points', 0)}
- Carbon Saved: {user_context.get('total_carbon', 0)}kg CO₂  
- Activity History: {user_context.get('activity_history', 'New user')}
- Level: {user_context.get('level', 'Beginner')}
- Difficulty: {difficulty}

Create a challenge with:
1. Catchy title with emoji
2. Clear description (2-3 sentences)
3. Specific target (number + unit)
4. Points reward (50-500 based on difficulty)
5. Activity type focus

Format as JSON:
{{
  "title": "Challenge Title 🌱",
  "description": "Challenge description...",
  "target_value": 10,
  "target_metric": "kg_recycled",
  "reward_points": 150,
  "activity_focus": "recycling"
}}
"""
        
        result = self.generate_content("Generate an eco challenge", context)
        
        try:
            # Try to parse JSON response
            challenge_data = json.loads(result['content'])
            return {
                'success': True,
                'challenge': challenge_data
            }
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            return {
                'success': False,
                'challenge': {
                    'title': 'AI-Generated Eco Challenge 🤖',
                    'description': result['content'][:200] + '...',
                    'target_value': 5,
                    'target_metric': 'activities',
                    'reward_points': 100,
                    'activity_focus': 'general'
                }
            }
    
    def generate_eco_insights(self, user_data: Dict) -> str:
        """Generate personalized eco insights and tips"""
        context = f"""
Provide personalized sustainability insights for a campus eco-tracker user.

User Statistics:
- Total Points: {user_data.get('total_points', 0)}
- Carbon Saved: {user_data.get('total_carbon', 0)}kg CO₂
- Activities Completed: {user_data.get('activity_count', 0)}
- Efficiency Score: {user_data.get('efficiency_score', 0)} pts/kg CO₂
- Recent Trend: {user_data.get('trend', 'stable')}

Provide 2-3 specific, actionable insights about their performance and improvement suggestions.
Be encouraging and include relevant environmental facts or tips.
Keep response under 150 words and use emojis appropriately.
"""
        
        result = self.generate_content("Generate eco insights", context)
        return result['content']


class AICalculatorService:
    """AI-based Carbon Savings Calculator Service"""
    
    def __init__(self, user: User = None):
        self.user = user
        
    def calculate_activity_impact(self, activity_type: str, quantity: float, duration_hours: float = None) -> Dict:
        """Calculate carbon impact for a specific activity using AI logic"""
        
        # AI-enhanced calculation coefficients based on research data
        base_coefficients = {
            'TREE': {
                'carbon_per_unit': 22.0,  # kg CO2 absorbed per tree per year
                'points_multiplier': 50,
                'complexity_factor': 1.5,
                'longevity_bonus': 10.0  # Additional CO2 for long-term impact
            },
            'RECYCLE': {
                'carbon_per_unit': 1.5,  # kg CO2 saved per kg recycled
                'points_multiplier': 15,
                'complexity_factor': 1.0,
                'material_bonus': 0.5  # Additional CO2 for complex materials
            },
            'CLEANUP': {
                'carbon_per_unit': 0.5,  # kg CO2 impact per kg waste cleaned
                'points_multiplier': 5,
                'complexity_factor': 1.2,
                'prevention_bonus': 0.3  # Additional CO2 for preventing pollution
            },
            'AWARENESS': {
                'carbon_per_unit': 5.0,  # kg CO2 per hour of awareness activity
                'points_multiplier': 50,
                'complexity_factor': 2.0,
                'multiplier_effect': 1.5  # Amplification effect
            },
            'ENERGY_SAVING': {
                'carbon_per_unit': 0.85,  # kg CO2 per kWh saved
                'points_multiplier': 4,
                'complexity_factor': 1.3,
                'efficiency_bonus': 0.2  # Additional CO2 for high efficiency
            }
        }
        
        if activity_type not in base_coefficients:
            return self._default_calculation(quantity)
        
        coeffs = base_coefficients[activity_type]
        
        # Base calculation
        base_carbon = quantity * coeffs['carbon_per_unit']
        base_points = quantity * coeffs['points_multiplier']
        
        # AI enhancements
        ai_enhanced_carbon = self._apply_ai_enhancements(base_carbon, coeffs, activity_type, quantity, duration_hours)
        ai_enhanced_points = self._calculate_smart_points(base_points, ai_enhanced_carbon, activity_type)
        
        # User-specific adjustments
        if self.user:
            ai_enhanced_carbon, ai_enhanced_points = self._apply_user_context(ai_enhanced_carbon, ai_enhanced_points)
        
        return {
            'activity_type': activity_type,
            'quantity': quantity,
            'duration_hours': duration_hours,
            'carbon_saved_kg': round(ai_enhanced_carbon, 2),
            'points_earned': int(ai_enhanced_points),
            'efficiency_score': round(ai_enhanced_points / max(0.1, ai_enhanced_carbon), 2),
            'impact_level': self._get_impact_level(ai_enhanced_carbon),
            'ai_insights': self._generate_ai_insights(activity_type, ai_enhanced_carbon, ai_enhanced_points),
            'equivalent_impact': self._calculate_equivalent_impact(ai_enhanced_carbon)
        }
    
    def calculate_compound_activities(self, activities: List[Dict]) -> Dict:
        """Calculate impact for multiple activities with compound effects"""
        
        total_carbon = 0
        total_points = 0
        activity_breakdown = []
        
        # Calculate individual activities
        for activity in activities:
            result = self.calculate_activity_impact(
                activity['activity_type'],
                activity['quantity'],
                activity.get('duration_hours')
            )
            activity_breakdown.append(result)
            total_carbon += result['carbon_saved_kg']
            total_points += result['points_earned']
        
        # AI compound effect calculation
        diversity_bonus = self._calculate_diversity_bonus(activities)
        synergy_multiplier = self._calculate_synergy_multiplier(activities)
        
        compound_carbon = total_carbon * (1 + diversity_bonus) * synergy_multiplier
        compound_points = total_points * (1 + diversity_bonus * 0.5) * synergy_multiplier
        
        return {
            'total_activities': len(activities),
            'individual_breakdown': activity_breakdown,
            'base_carbon_saved': round(total_carbon, 2),
            'compound_carbon_saved': round(compound_carbon, 2),
            'base_points': int(total_points),
            'compound_points': int(compound_points),
            'diversity_bonus': round(diversity_bonus * 100, 1),  # as percentage
            'synergy_multiplier': round(synergy_multiplier, 2),
            'overall_efficiency': round(compound_points / max(0.1, compound_carbon), 2),
            'impact_level': self._get_impact_level(compound_carbon),
            'ai_recommendations': self._generate_compound_recommendations(activities, compound_carbon)
        }
    
    def predict_activity_outcomes(self, activity_type: str, target_quantity: float) -> Dict:
        """Predict outcomes for planned activities"""
        
        # Calculate expected impact
        expected_result = self.calculate_activity_impact(activity_type, target_quantity)
        
        # AI prediction enhancements
        success_probability = self._calculate_success_probability(activity_type, target_quantity)
        optimal_approach = self._suggest_optimal_approach(activity_type, target_quantity)
        timeline_estimate = self._estimate_completion_timeline(activity_type, target_quantity)
        
        return {
            'expected_result': expected_result,
            'success_probability': round(success_probability * 100, 1),  # as percentage
            'optimal_approach': optimal_approach,
            'estimated_timeline_days': timeline_estimate,
            'risk_factors': self._identify_risk_factors(activity_type),
            'success_tips': self._generate_success_tips(activity_type, target_quantity)
        }
    
    def _apply_ai_enhancements(self, base_carbon: float, coeffs: Dict, activity_type: str, quantity: float, duration_hours: float) -> float:
        """Apply AI enhancements to base calculation"""
        enhanced_carbon = base_carbon * coeffs['complexity_factor']
        
        # Add activity-specific bonuses
        if activity_type == 'TREE' and quantity >= 5:
            enhanced_carbon += coeffs['longevity_bonus'] * (quantity / 5)
        elif activity_type == 'RECYCLE' and quantity >= 10:
            enhanced_carbon += coeffs['material_bonus'] * quantity
        elif activity_type == 'CLEANUP' and quantity >= 20:
            enhanced_carbon += coeffs['prevention_bonus'] * quantity
        elif activity_type == 'AWARENESS' and duration_hours and duration_hours >= 2:
            enhanced_carbon *= coeffs['multiplier_effect']
        elif activity_type == 'ENERGY_SAVING' and quantity >= 50:
            enhanced_carbon += coeffs['efficiency_bonus'] * quantity
        
        return enhanced_carbon
    
    def _calculate_smart_points(self, base_points: float, carbon_saved: float, activity_type: str) -> float:
        """Calculate points using AI-enhanced logic"""
        # Efficiency-based point adjustment
        efficiency_ratio = carbon_saved / max(1, base_points / 10)  # Normalize
        smart_points = base_points * (1 + min(0.5, efficiency_ratio * 0.1))
        
        # Activity-specific bonuses
        if activity_type in ['TREE', 'AWARENESS']:
            smart_points *= 1.2  # High-impact activities bonus
        
        return smart_points
    
    def _apply_user_context(self, carbon: float, points: float) -> tuple:
        """Apply user-specific context to calculations"""
        if not self.user or not hasattr(self.user, 'profile'):
            return carbon, points
        
        profile = self.user.profile
        
        # Experience bonus
        total_activities = ActivitySubmission.objects.filter(user=self.user, status='APPROVED').count()
        if total_activities >= 20:
            experience_multiplier = 1.15
        elif total_activities >= 10:
            experience_multiplier = 1.1
        elif total_activities >= 5:
            experience_multiplier = 1.05
        else:
            experience_multiplier = 1.0
        
        # Consistency bonus
        recent_activities = ActivitySubmission.objects.filter(
            user=self.user,
            status='APPROVED',
            submitted_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        consistency_bonus = min(0.2, recent_activities * 0.02)  # Up to 20% bonus
        
        final_carbon = carbon * experience_multiplier * (1 + consistency_bonus)
        final_points = points * experience_multiplier * (1 + consistency_bonus)
        
        return final_carbon, final_points
    
    def _get_impact_level(self, carbon_saved: float) -> str:
        """Determine impact level based on carbon saved"""
        if carbon_saved >= 50:
            return 'TRANSFORMATIONAL'
        elif carbon_saved >= 20:
            return 'HIGH'
        elif carbon_saved >= 10:
            return 'MODERATE'
        elif carbon_saved >= 5:
            return 'GOOD'
        else:
            return 'STARTING'
    
    def _generate_ai_insights(self, activity_type: str, carbon: float, points: float) -> List[str]:
        """Generate AI-powered insights"""
        insights = []
        
        efficiency = points / max(0.1, carbon)
        
        if efficiency > 30:
            insights.append("🎯 Excellent efficiency! This activity gives great points per CO₂ saved.")
        elif efficiency > 15:
            insights.append("📈 Good efficiency! Solid environmental and point return.")
        else:
            insights.append("💡 Consider combining with other activities for better efficiency.")
        
        # Activity-specific insights
        if activity_type == 'TREE':
            insights.append("🌳 Trees provide long-term carbon absorption - great for lasting impact!")
        elif activity_type == 'AWARENESS':
            insights.append("📢 Awareness activities have multiplier effects through community impact!")
        elif activity_type == 'ENERGY_SAVING':
            insights.append("⚡ Energy savings create ongoing environmental benefits!")
        
        return insights
    
    def _calculate_equivalent_impact(self, carbon_saved: float) -> Dict:
        """Calculate equivalent environmental impacts"""
        return {
            'trees_planted_equivalent': round(carbon_saved / 22, 1),
            'miles_driven_offset': round(carbon_saved * 2.31, 1),  # miles offset
            'led_bulbs_year_equivalent': round(carbon_saved / 0.1, 1),
            'plastic_bottles_recycled': round(carbon_saved / 0.04, 0)
        }
    
    def _calculate_diversity_bonus(self, activities: List[Dict]) -> float:
        """Calculate bonus for diverse activities"""
        unique_types = len(set(activity['activity_type'] for activity in activities))
        return min(0.3, unique_types * 0.05)  # Up to 30% bonus
    
    def _calculate_synergy_multiplier(self, activities: List[Dict]) -> float:
        """Calculate synergy effects between activities"""
        activity_types = [activity['activity_type'] for activity in activities]
        
        # Synergistic combinations
        synergies = {
            ('TREE', 'CLEANUP'): 1.15,
            ('AWARENESS', 'RECYCLE'): 1.1,
            ('ENERGY_SAVING', 'AWARENESS'): 1.12
        }
        
        multiplier = 1.0
        for combo, bonus in synergies.items():
            if all(activity_type in activity_types for activity_type in combo):
                multiplier *= bonus
        
        return multiplier
    
    def _calculate_success_probability(self, activity_type: str, quantity: float) -> float:
        """Calculate probability of successful completion"""
        base_difficulty = {
            'TREE': 0.7,
            'RECYCLE': 0.9,
            'CLEANUP': 0.8,
            'AWARENESS': 0.75,
            'ENERGY_SAVING': 0.85
        }
        
        base_prob = base_difficulty.get(activity_type, 0.8)
        
        # Adjust for quantity
        if quantity > 20:
            base_prob *= 0.8
        elif quantity > 10:
            base_prob *= 0.9
        
        return max(0.1, min(0.95, base_prob))
    
    def _suggest_optimal_approach(self, activity_type: str, quantity: float) -> str:
        """Suggest optimal approach for activity"""
        approaches = {
            'TREE': 'Partner with local environmental groups for maximum impact and support.',
            'RECYCLE': 'Sort materials by type and find specialized recycling centers for better impact.',
            'CLEANUP': 'Organize group efforts and document before/after for awareness impact.',
            'AWARENESS': 'Use social media and local events to amplify your message reach.',
            'ENERGY_SAVING': 'Start with biggest energy users and track savings with smart meters.'
        }
        return approaches.get(activity_type, 'Plan systematically and track progress regularly.')
    
    def _estimate_completion_timeline(self, activity_type: str, quantity: float) -> int:
        """Estimate completion timeline in days"""
        daily_capacity = {
            'TREE': 2,  # trees per day
            'RECYCLE': 5,  # kg per day
            'CLEANUP': 10,  # kg per day
            'AWARENESS': 3,  # hours per day
            'ENERGY_SAVING': 8  # kWh per day
        }
        
        capacity = daily_capacity.get(activity_type, 5)
        return max(1, int(quantity / capacity))
    
    def _identify_risk_factors(self, activity_type: str) -> List[str]:
        """Identify potential risk factors"""
        risks = {
            'TREE': ['Weather conditions', 'Soil quality', 'Permit requirements'],
            'RECYCLE': ['Material contamination', 'Limited recycling facilities'],
            'CLEANUP': ['Safety hazards', 'Weather conditions', 'Equipment availability'],
            'AWARENESS': ['Audience engagement', 'Message clarity', 'Platform limitations'],
            'ENERGY_SAVING': ['Baseline measurement', 'Behavior change resistance', 'Technical issues']
        }
        return risks.get(activity_type, ['Planning complexity', 'Resource availability'])
    
    def _generate_success_tips(self, activity_type: str, quantity: float) -> List[str]:
        """Generate AI-powered success tips"""
        tips = {
            'TREE': [
                'Choose native species for better survival rates',
                'Plant during optimal seasons (spring/fall)',
                'Ensure proper spacing and aftercare'
            ],
            'RECYCLE': [
                'Clean containers thoroughly before recycling',
                'Learn local recycling guidelines',
                'Track and weigh materials for accurate reporting'
            ],
            'AWARENESS': [
                'Use compelling visuals and statistics',
                'Engage with your audience through questions',
                'Follow up with actionable next steps'
            ]
        }
        
        base_tips = tips.get(activity_type, ['Plan ahead', 'Stay consistent', 'Document progress'])
        
        if quantity > 10:
            base_tips.append('Break large goals into smaller, manageable chunks')
        
        return base_tips
    
    def _default_calculation(self, quantity: float) -> Dict:
        """Default calculation for unknown activity types"""
        return {
            'carbon_saved_kg': round(quantity * 1.0, 2),
            'points_earned': int(quantity * 10),
            'efficiency_score': 10.0,
            'impact_level': 'MODERATE',
            'ai_insights': ['Custom activity - impact estimated based on quantity'],
            'equivalent_impact': self._calculate_equivalent_impact(quantity * 1.0)
        }