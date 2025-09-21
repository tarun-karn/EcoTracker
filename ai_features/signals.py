from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserAIPreferences


@receiver(post_save, sender=User)
def create_ai_preferences(sender, instance, created, **kwargs):
    """Create AI preferences when a new user is created"""
    if created:
        UserAIPreferences.objects.create(user=instance)