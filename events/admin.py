from django.contrib import admin
from django.utils.html import format_html
from .models import Event, EventParticipant

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'organizer', 'points_for_attendance', 'get_participants_count')
    list_filter = ('date', 'organizer')
    search_fields = ('name', 'description', 'location')
    ordering = ('-date',)
    
    def get_participants_count(self, obj):
        count = obj.participants.count()
        return format_html(
            '<span style="background: #10b981; color: white; padding: 2px 6px; border-radius: 3px;">{} participants</span>',
            count
        )
    get_participants_count.short_description = 'Participants'

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'checked_in_at')
    list_filter = ('event', 'checked_in_at')
    search_fields = ('event__name', 'user__username', 'user__email')
    readonly_fields = ('checked_in_at',)
    ordering = ('-checked_in_at',)
