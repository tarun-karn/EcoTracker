from django.core.management.base import BaseCommand
from users.models import Achievement, BadgeType


class Command(BaseCommand):
    help = 'Create initial achievement data'

    def handle(self, *args, **options):
        achievements = [
            # Level-based achievements
            {
                'name': 'Bronze Achiever',
                'description': 'Earn your first 50 eco-points',
                'badge_type': BadgeType.BRONZE,
                'threshold_points': 50,
                'icon': '🥉',
            },
            {
                'name': 'Silver Star',
                'description': 'Reach 200 eco-points milestone',
                'badge_type': BadgeType.SILVER,
                'threshold_points': 200,
                'icon': '🥈',
            },
            {
                'name': 'Gold Standard',
                'description': 'Achieve 500 eco-points - gold level!',
                'badge_type': BadgeType.GOLD,
                'threshold_points': 500,
                'icon': '🥇',
            },
            {
                'name': 'Platinum Elite',
                'description': 'Earn 1000 eco-points - platinum status!',
                'badge_type': BadgeType.PLATINUM,
                'threshold_points': 1000,
                'icon': '💎',
            },
            {
                'name': 'Eco Champion',
                'description': 'Ultimate achievement: 2000+ eco-points!',
                'badge_type': BadgeType.ECO_CHAMPION,
                'threshold_points': 2000,
                'icon': '🌟',
            },
            
            # Activity-specific achievements
            {
                'name': 'Tree Lover',
                'description': 'Plant 10 or more trees',
                'badge_type': BadgeType.TREE_LOVER,
                'threshold_activities': 10,
                'activity_type': 'TREE',
                'icon': '🌳',
            },
            {
                'name': 'Recycling Hero',
                'description': 'Recycle 50kg or more of materials',
                'badge_type': BadgeType.RECYCLING_HERO,
                'threshold_activities': 50,
                'activity_type': 'RECYCLE',
                'icon': '♻️',
            },
            {
                'name': 'Cleanup Master',
                'description': 'Clean up 25kg or more of waste',
                'badge_type': BadgeType.CLEANUP_MASTER,
                'threshold_activities': 25,
                'activity_type': 'CLEANUP',
                'icon': '🧹',
            },
            {
                'name': 'Awareness Advocate',
                'description': 'Participate in 20+ hours of awareness campaigns',
                'badge_type': BadgeType.AWARENESS_ADVOCATE,
                'threshold_activities': 20,
                'activity_type': 'AWARENESS',
                'icon': '📢',
            },
            {
                'name': 'Energy Saver',
                'description': 'Save 100+ kWh of energy',
                'badge_type': BadgeType.ENERGY_SAVER,
                'threshold_activities': 100,
                'activity_type': 'ENERGY_SAVING',
                'icon': '⚡',
            },
            
            # Special achievements
            {
                'name': 'Event Participant',
                'description': 'Attend 5 or more eco-events',
                'badge_type': BadgeType.EVENT_PARTICIPANT,
                'threshold_activities': 5,
                'icon': '🎭',
            },
            {
                'name': 'Team Player',
                'description': 'Active member of an eco-team',
                'badge_type': BadgeType.TEAM_PLAYER,
                'threshold_activities': 1,
                'icon': '👥',
            },
        ]

        created_count = 0
        for achievement_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created achievement: {achievement.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} achievements')
        )