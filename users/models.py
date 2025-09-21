from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum

class BadgeType(models.TextChoices):
    BRONZE = 'BRONZE', 'Bronze Badge'
    SILVER = 'SILVER', 'Silver Badge'
    GOLD = 'GOLD', 'Gold Badge'
    PLATINUM = 'PLATINUM', 'Platinum Badge'
    ECO_CHAMPION = 'ECO_CHAMPION', 'Eco Champion'
    TREE_LOVER = 'TREE_LOVER', 'Tree Lover'
    RECYCLING_HERO = 'RECYCLING_HERO', 'Recycling Hero'
    CLEANUP_MASTER = 'CLEANUP_MASTER', 'Cleanup Master'
    AWARENESS_ADVOCATE = 'AWARENESS_ADVOCATE', 'Awareness Advocate'
    ENERGY_SAVER = 'ENERGY_SAVER', 'Energy Saver'
    EVENT_PARTICIPANT = 'EVENT_PARTICIPANT', 'Event Participant'
    TEAM_PLAYER = 'TEAM_PLAYER', 'Team Player'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    student_id = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    year_of_study = models.CharField(
        max_length=20,
        choices=[
            ('1st Year', '1st Year'),
            ('2nd Year', '2nd Year'),
            ('3rd Year', '3rd Year'),
            ('4th Year', '4th Year'),
            ('Graduate', 'Graduate'),
            ('Faculty', 'Faculty'),
        ],
        blank=True
    )
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    total_points = models.IntegerField(default=0)
    total_carbon_saved = models.FloatField(default=0.0)
    certificates_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def current_level(self):
        """Determine user's current level based on points"""
        if self.total_points >= 2000:
            return 'Eco Champion'
        elif self.total_points >= 1000:
            return 'Platinum'
        elif self.total_points >= 500:
            return 'Gold'
        elif self.total_points >= 200:
            return 'Silver'
        elif self.total_points >= 50:
            return 'Bronze'
        else:
            return 'Newbie'

    @property
    def next_level_points(self):
        """Points needed for next level"""
        current = self.total_points
        if current < 50:
            return 50 - current
        elif current < 200:
            return 200 - current
        elif current < 500:
            return 500 - current
        elif current < 1000:
            return 1000 - current
        elif current < 2000:
            return 2000 - current
        else:
            return 0  # Max level reached

    @property
    def level_progress_percentage(self):
        """Progress percentage towards next level"""
        current = self.total_points
        if current < 50:
            return (current / 50) * 100
        elif current < 200:
            return ((current - 50) / 150) * 100
        elif current < 500:
            return ((current - 200) / 300) * 100
        elif current < 1000:
            return ((current - 500) / 500) * 100
        elif current < 2000:
            return ((current - 1000) / 1000) * 100
        else:
            return 100  # Max level

    def update_stats(self):
        """Update total points and carbon saved from CarbonLog"""
        from activities.models import CarbonLog
        stats = CarbonLog.objects.filter(user=self.user).aggregate(
            total_points=Sum('points_earned'),
            total_carbon=Sum('carbon_saved_kg')
        )
        self.total_points = stats['total_points'] or 0
        self.total_carbon_saved = stats['total_carbon'] or 0.0
        self.save()

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge_type = models.CharField(max_length=50, choices=BadgeType.choices)
    earned_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'badge_type')

    def __str__(self):
        return f"{self.user.username} - {self.get_badge_type_display()}"

class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=50, choices=BadgeType.choices)
    threshold_points = models.IntegerField(null=True, blank=True)
    threshold_activities = models.IntegerField(null=True, blank=True)
    activity_type = models.CharField(max_length=50, blank=True)  # Specific activity type for badge
    icon = models.CharField(max_length=50, default='🏆')  # Emoji or icon class
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
