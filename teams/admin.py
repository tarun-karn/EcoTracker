from django.contrib import admin
from django.utils.html import format_html
from .models import Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'get_members_count', 'get_total_points', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'leader__username', 'members__username')
    filter_horizontal = ('members',)
    ordering = ('-created_at',)
    
    def get_members_count(self, obj):
        count = obj.members.count()
        return format_html(
            '<span style="background: #3b82f6; color: white; padding: 2px 6px; border-radius: 3px;">{} members</span>',
            count
        )
    get_members_count.short_description = 'Members'
    
    def get_total_points(self, obj):
        points = obj.total_points
        return format_html(
            '<strong>{}</strong> points',
            points or 0
        )
    get_total_points.short_description = 'Total Points'
