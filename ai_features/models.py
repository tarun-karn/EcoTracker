from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import json


class AIRecommendation(models.Model):
    """Store AI-generated recommendations for users"""
    
    RECOMMENDATION_TYPES = [
        ('ACTIVITY', 'Activity Suggestion'),
        ('EFFICIENCY', 'Efficiency Tip'),
        ('GOAL', 'Goal Setting'),
        ('CHALLENGE', 'Challenge'),
        ('MOTIVATION', 'Motivational Message'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # Store additional data like points, carbon impact
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_recommendation_type_display()} for {self.user.username}: {self.title}"


class CarbonPrediction(models.Model):
    """Store carbon impact predictions for users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carbon_predictions')
    prediction_date = models.DateField()
    predicted_daily_savings = models.FloatField()
    predicted_weekly_savings = models.FloatField()
    predicted_monthly_savings = models.FloatField()
    confidence_score = models.FloatField(default=0.0)  # 0-1 confidence
    actual_savings = models.FloatField(null=True, blank=True)  # Fill after the date
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'prediction_date']
        ordering = ['-prediction_date']
        
    def __str__(self):
        return f"Carbon prediction for {self.user.username} on {self.prediction_date}"


class EfficiencyInsight(models.Model):
    """Store efficiency analysis for users and activities"""
    
    INSIGHT_TYPES = [
        ('USER_EFFICIENCY', 'User Overall Efficiency'),
        ('ACTIVITY_EFFICIENCY', 'Activity Type Efficiency'),
        ('TEAM_COMPARISON', 'Team Comparison'),
        ('IMPROVEMENT_TIP', 'Improvement Suggestion'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='efficiency_insights')
    insight_type = models.CharField(max_length=25, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    efficiency_score = models.FloatField()  # Points per kg CO2
    comparison_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_insight_type_display()} for {self.user.username}: {self.efficiency_score:.2f}"


class DynamicChallenge(models.Model):
    """AI-generated challenges for users"""
    
    CHALLENGE_TYPES = [
        ('WEEKLY', 'Weekly Challenge'),
        ('MONTHLY', 'Monthly Challenge'),
        ('TEAM', 'Team Challenge'),
        ('PERSONAL', 'Personal Milestone'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
        ('EXPERT', 'Expert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dynamic_challenges')
    challenge_type = models.CharField(max_length=15, choices=CHALLENGE_TYPES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS)
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_value = models.IntegerField()  # Points, activities, or carbon savings target
    target_metric = models.CharField(max_length=20)  # 'points', 'activities', 'carbon_kg'
    reward_points = models.IntegerField()
    current_progress = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} for {self.user.username}"
    
    @property
    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return min(100, (self.current_progress / self.target_value) * 100)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class AIInsightCache(models.Model):
    """Cache for expensive AI computations"""
    
    cache_key = models.CharField(max_length=255, unique=True)
    data = models.JSONField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Cache: {self.cache_key}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @classmethod
    def get_cached_data(cls, key):
        """Get cached data if not expired"""
        try:
            cache_obj = cls.objects.get(cache_key=key)
            if not cache_obj.is_expired:
                return cache_obj.data
            else:
                cache_obj.delete()
                return None
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def set_cached_data(cls, key, data, expires_in_hours=24):
        """Set cached data with expiration"""
        expires_at = timezone.now() + timedelta(hours=expires_in_hours)
        cls.objects.update_or_create(
            cache_key=key,
            defaults={'data': data, 'expires_at': expires_at}
        )


class UserAIPreferences(models.Model):
    """Store user preferences for AI features"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_preferences')
    enable_recommendations = models.BooleanField(default=True)
    enable_predictions = models.BooleanField(default=True)
    enable_challenges = models.BooleanField(default=True)
    notification_frequency = models.CharField(
        max_length=10,
        choices=[
            ('DAILY', 'Daily'),
            ('WEEKLY', 'Weekly'),
            ('MONTHLY', 'Monthly'),
        ],
        default='WEEKLY'
    )
    preferred_challenge_difficulty = models.CharField(
        max_length=10,
        choices=DynamicChallenge.DIFFICULTY_LEVELS,
        default='MEDIUM'
    )
    openai_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'AI Preferences'
        verbose_name_plural = 'AI Preferences'
        
    def __str__(self):
        return f"AI Preferences for {self.user.username}"