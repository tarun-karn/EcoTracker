from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import ActivitySubmission, CarbonLog

@admin.register(ActivitySubmission)
class ActivitySubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_display', 'get_activity_display', 'quantity', 
        'get_status_display', 'points_awarded', 'carbon_saved_kg', 'submitted_at'
    )
    list_filter = ('status', 'activity_type', 'submitted_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('points_awarded', 'carbon_saved_kg', 'submitted_at', 'get_evidence_preview')
    ordering = ('-submitted_at',)
    actions_on_top = True
    actions_on_bottom = True
    
    # Make sure actions are always visible
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['has_add_permission'] = self.has_add_permission(request)
        return super().changelist_view(request, extra_context)
    
    fieldsets = (
        ('Submission Details', {
            'fields': ('user', 'activity_type', 'quantity', 'description')
        }),
        ('Evidence', {
            'fields': ('evidence', 'get_evidence_preview'),
            'classes': ('collapse',)
        }),
        ('Review', {
            'fields': ('status', 'feedback', 'points_awarded', 'carbon_saved_kg'),
            'description': 'Review and approve/reject this submission'
        }),
        ('Timestamps', {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.user.get_full_name() or obj.user.username,
            obj.user.email
        )
    get_user_display.short_description = 'User'
    
    def get_activity_display(self, obj):
        icons = {
            'TREE': '🌳',
            'RECYCLE': '♻️',
            'CLEANUP': '🧹',
            'AWARENESS': '📢',
            'ENERGY_SAVING': '⚡'
        }
        icon = icons.get(obj.activity_type, '🌱')
        return format_html(
            '{} {}',
            icon,
            obj.get_activity_type_display()
        )
    get_activity_display.short_description = 'Activity Type'
    
    def get_status_display(self, obj):
        colors = {
            'PENDING': '#f59e0b',
            'APPROVED': '#10b981',
            'REJECTED': '#ef4444'
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_display.short_description = 'Status'
    
    def get_evidence_preview(self, obj):
        if obj.evidence:
            return format_html(
                '<a href="{}" target="_blank">View Evidence</a>',
                obj.evidence.url
            )
        return 'No evidence uploaded'
    get_evidence_preview.short_description = 'Evidence Preview'
    
    actions = ['approve_submissions', 'reject_submissions']
    
    def approve_submissions(self, request, queryset):
        approved = 0
        for submission in queryset.filter(status='PENDING'):
            submission.approve()
            approved += 1
        self.message_user(request, f'Approved {approved} submissions.')
    approve_submissions.short_description = 'Approve selected submissions'
    
    def reject_submissions(self, request, queryset):
        rejected = 0
        for submission in queryset.filter(status='PENDING'):
            submission.status = ActivitySubmission.Status.REJECTED
            submission.feedback = "Rejected by admin bulk action"
            submission.save()
            rejected += 1
        self.message_user(request, f'Rejected {rejected} submissions.')
    reject_submissions.short_description = 'Reject selected submissions'

@admin.register(CarbonLog)
class CarbonLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'carbon_saved_kg', 'points_earned', 'get_submission_info', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    
    def get_submission_info(self, obj):
        if obj.submission:
            return format_html(
                '{} ({})',
                obj.submission.get_activity_type_display(),
                obj.submission.quantity
            )
        return 'Event/Manual Entry'
    get_submission_info.short_description = 'Source'
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation of carbon logs
    
    def has_change_permission(self, request, obj=None):
        return False  # Make carbon logs read-only
