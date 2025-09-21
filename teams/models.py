from django.db import models
from django.conf import settings
from django.db.models import Sum

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='led_teams')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_points(self):
        return self.members.aggregate(total=Sum('submissions__points_awarded'))['total'] or 0
