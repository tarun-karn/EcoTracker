from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile, UserBadge, Achievement
from .badge_service import BadgeService

# Inline for UserProfile in User admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'bio', 'phone_number', 'student_id', 'department', 'year_of_study',
        'profile_picture', 'total_points', 'total_carbon_saved', 'certificates_earned'
    )
    readonly_fields = ('total_points', 'total_carbon_saved', 'certificates_earned')

# Inline for UserBadge in User admin
class UserBadgeInline(admin.TabularInline):
    model = UserBadge
    extra = 0
    readonly_fields = ('badge_type', 'earned_at', 'description')
    can_delete = False

# Enhanced User Admin
class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline, UserBadgeInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_points', 'get_level', 'get_badges_count', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__year_of_study', 'profile__department')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__student_id')
    ordering = ('-profile__total_points',)
    
    def get_points(self, obj):
        return getattr(obj.profile, 'total_points', 0) if hasattr(obj, 'profile') else 0
    get_points.short_description = 'Points'
    get_points.admin_order_field = 'profile__total_points'
    
    def get_level(self, obj):
        if hasattr(obj, 'profile'):
            level = obj.profile.current_level
            colors = {
                'Newbie': '#6b7280',
                'Bronze': '#d97706',
                'Silver': '#6b7280',
                'Gold': '#f59e0b',
                'Platinum': '#8b5cf6',
                'Eco Champion': '#10b981'
            }
            color = colors.get(level, '#6b7280')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, level
            )
        return 'No Profile'
    get_level.short_description = 'Level'
    
    def get_badges_count(self, obj):
        count = obj.badges.count() if hasattr(obj, 'badges') else 0
        if count > 0:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 2px 6px; border-radius: 3px;">{} 🏆</span>',
                count
            )
        return '0'
    get_badges_count.short_description = 'Badges'
    
    actions = ['update_user_stats', 'award_badges']
    
    def update_user_stats(self, request, queryset):
        updated = 0
        for user in queryset:
            if hasattr(user, 'profile'):
                user.profile.update_stats()
                updated += 1
        self.message_user(request, f'Updated stats for {updated} users.')
    update_user_stats.short_description = 'Update user statistics'
    
    def award_badges(self, request, queryset):
        awarded = 0
        for user in queryset:
            BadgeService.check_and_award_badges(user)
            awarded += 1
        self.message_user(request, f'Checked and awarded badges for {awarded} users.')
    award_badges.short_description = 'Award eligible badges'

# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'year_of_study', 'total_points', 'total_carbon_saved', 'current_level')
    list_filter = ('department', 'year_of_study', 'created_at')
    search_fields = ('user__username', 'user__email', 'student_id', 'department')
    readonly_fields = ('total_points', 'total_carbon_saved', 'certificates_earned', 'created_at', 'updated_at')
    ordering = ('-total_points',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'bio', 'profile_picture')
        }),
        ('Academic Information', {
            'fields': ('student_id', 'department', 'year_of_study', 'phone_number')
        }),
        ('Statistics', {
            'fields': ('total_points', 'total_carbon_saved', 'certificates_earned'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['update_stats']
    
    def update_stats(self, request, queryset):
        for profile in queryset:
            profile.update_stats()
        self.message_user(request, f'Updated stats for {queryset.count()} profiles.')
    update_stats.short_description = 'Update statistics'

# UserBadge Admin
@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_badge_display', 'earned_at', 'description')
    list_filter = ('badge_type', 'earned_at')
    search_fields = ('user__username', 'user__email', 'badge_type')
    readonly_fields = ('earned_at',)
    ordering = ('-earned_at',)
    
    def get_badge_display(self, obj):
        from .badge_service import BadgeService
        icon = BadgeService.get_badge_icon(obj.badge_type)
        color = BadgeService.get_badge_color(obj.badge_type)
        return format_html(
            '<span class="{}" style="padding: 4px 8px; border-radius: 4px;">{} {}</span>',
            color.replace('bg-', 'background-color: ').replace('text-', 'color: '),
            icon,
            obj.get_badge_type_display()
        )
    get_badge_display.short_description = 'Badge'

# Achievement Admin
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge_type', 'get_icon', 'threshold_points', 'threshold_activities', 'is_active')
    list_filter = ('badge_type', 'is_active', 'activity_type')
    search_fields = ('name', 'description', 'badge_type')
    ordering = ('badge_type', 'threshold_points')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'badge_type', 'icon', 'is_active')
        }),
        ('Criteria', {
            'fields': ('threshold_points', 'threshold_activities', 'activity_type'),
            'description': 'Set the criteria for earning this achievement. Use either points OR activities threshold.'
        }),
    )
    
    def get_icon(self, obj):
        return format_html(
            '<span style="font-size: 1.5em;">{}</span>',
            obj.icon
        )
    get_icon.short_description = 'Icon'

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
