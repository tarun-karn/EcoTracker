from django.contrib import admin
from django.utils.html import format_html
from .models import (
    AIRecommendation, CarbonPrediction, EfficiencyInsight, 
    DynamicChallenge, AIInsightCache, UserAIPreferences
)


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommendation_type', 'title', 'is_active', 'created_at', 'expires_at')
    list_filter = ('recommendation_type', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'content')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'recommendation_type', 'title', 'is_active')
        }),
        ('Content', {
            'fields': ('content', 'metadata')
        }),
        ('Timing', {
            'fields': ('created_at', 'expires_at')
        }),
    )


@admin.register(CarbonPrediction)
class CarbonPredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'prediction_date', 'predicted_daily_savings', 'predicted_weekly_savings', 'confidence_score', 'actual_savings')
    list_filter = ('prediction_date', 'confidence_score')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    ordering = ('-prediction_date',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user', 'prediction_date')
        return self.readonly_fields


@admin.register(EfficiencyInsight)
class EfficiencyInsightAdmin(admin.ModelAdmin):
    list_display = ('user', 'insight_type', 'title', 'efficiency_score', 'created_at')
    list_filter = ('insight_type', 'created_at', 'efficiency_score')
    search_fields = ('user__username', 'user__email', 'title')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def get_efficiency_display(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2f}</span>',
            '#10b981' if obj.efficiency_score >= 15 else '#f59e0b' if obj.efficiency_score >= 10 else '#ef4444',
            obj.efficiency_score
        )
    get_efficiency_display.short_description = 'Efficiency Score'


@admin.register(DynamicChallenge)
class DynamicChallengeAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'challenge_type', 'difficulty', 'progress_display', 'is_completed', 'expires_at')
    list_filter = ('challenge_type', 'difficulty', 'is_completed', 'created_at')
    search_fields = ('user__username', 'user__email', 'title')
    readonly_fields = ('created_at', 'progress_percentage')
    ordering = ('-created_at',)
    
    def progress_display(self, obj):
        percentage = obj.progress_percentage
        color = '#10b981' if percentage >= 80 else '#f59e0b' if percentage >= 50 else '#ef4444'
        return format_html(
            '<div style="width: 100px; background: #e5e7eb; border-radius: 4px;">'
            '<div style="width: {}%; background: {}; height: 20px; border-radius: 4px; text-align: center; color: white; font-size: 12px; line-height: 20px;">'
            '{}%</div></div>',
            percentage, color, int(percentage)
        )
    progress_display.short_description = 'Progress'
    
    actions = ['mark_completed', 'extend_deadline']
    
    def mark_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_completed=True, completed_at=timezone.now())
        self.message_user(request, f'{updated} challenges marked as completed.')
    mark_completed.short_description = 'Mark selected challenges as completed'
    
    def extend_deadline(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone
        for challenge in queryset:
            challenge.expires_at = challenge.expires_at + timedelta(days=7)
            challenge.save()
        self.message_user(request, f'Extended deadline for {queryset.count()} challenges by 7 days.')
    extend_deadline.short_description = 'Extend deadline by 7 days'


@admin.register(AIInsightCache)
class AIInsightCacheAdmin(admin.ModelAdmin):
    list_display = ('cache_key', 'created_at', 'expires_at', 'is_expired')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('cache_key',)
    readonly_fields = ('created_at', 'is_expired')
    ordering = ('-created_at',)
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    actions = ['clear_expired_cache']
    
    def clear_expired_cache(self, request, queryset):
        expired_count = 0
        for cache_obj in queryset:
            if cache_obj.is_expired:
                cache_obj.delete()
                expired_count += 1
        self.message_user(request, f'Cleared {expired_count} expired cache entries.')
    clear_expired_cache.short_description = 'Clear expired cache entries'


@admin.register(UserAIPreferences)
class UserAIPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'enable_recommendations', 'enable_predictions', 'enable_challenges', 'notification_frequency', 'openai_enabled')
    list_filter = ('enable_recommendations', 'enable_predictions', 'enable_challenges', 'notification_frequency', 'openai_enabled')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('user__username',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('AI Features', {
            'fields': ('enable_recommendations', 'enable_predictions', 'enable_challenges')
        }),
        ('Preferences', {
            'fields': ('notification_frequency', 'preferred_challenge_difficulty', 'openai_enabled')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )