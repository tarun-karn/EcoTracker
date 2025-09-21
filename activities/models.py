from django.db import models
from django.conf import settings
from django.utils import timezone

class ActivityType(models.TextChoices):
    TREE_PLANTATION = 'TREE', 'Tree Plantation'
    RECYCLING = 'RECYCLE', 'Recycling'
    CLEANUP_DRIVE = 'CLEANUP', 'Clean-up Drive'
    AWARENESS_CAMPAIGN = 'AWARENESS', 'Awareness Campaign'
    ENERGY_SAVING = 'ENERGY_SAVING', 'Energy Saving Initiative'

class ActivitySubmission(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    activity_type = models.CharField(max_length=50, choices=ActivityType.choices)
    quantity = models.FloatField(default=1.0, help_text="e.g., number of trees, kg of recycling, hours of awareness")
    description = models.TextField(blank=True)
    evidence = models.FileField(upload_to='evidence/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    points_awarded = models.IntegerField(default=0)
    carbon_saved_kg = models.FloatField(default=0.0)
    submitted_at = models.DateTimeField(default=timezone.now)
    feedback = models.TextField(blank=True, help_text="Feedback from admin on rejection.")

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

    def approve(self):
        """Calculates points and carbon saved, then marks as approved."""
        # Simple point system: 10 points per unit of activity
        self.points_awarded = int(self.quantity * 10)

        # Calculate carbon saved based on factors in settings
        carbon_factor = settings.CARBON_FACTORS.get(self.activity_type, 0)
        self.carbon_saved_kg = self.quantity * carbon_factor

        self.status = self.Status.APPROVED
        self.save()

        # Create a log entry
        carbon_log = CarbonLog.objects.create(
            user=self.user,
            submission=self,
            carbon_saved_kg=self.carbon_saved_kg,
            points_earned=self.points_awarded
        )
        
        # Award badges when activity is approved
        from users.badge_service import BadgeService
        BadgeService.check_and_award_badges(self.user)


class CarbonLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission = models.ForeignKey(ActivitySubmission, on_delete=models.SET_NULL, null=True, blank=True)
    carbon_saved_kg = models.FloatField()
    points_earned = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for {self.user.username} at {self.timestamp.strftime('%Y-%m-%d')}"
