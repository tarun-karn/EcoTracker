"""
Service for managing badges and achievements
"""
from django.db.models import Count, Sum
from .models import UserProfile, UserBadge, Achievement, BadgeType
from activities.models import ActivitySubmission, CarbonLog, ActivityType
from events.models import EventParticipant


class BadgeService:
    """Service to handle badge awarding logic"""
    
    @staticmethod
    def check_and_award_badges(user):
        """Check all badge criteria and award eligible badges"""
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.update_stats()
        
        # Level-based badges
        BadgeService._check_level_badges(user, profile)
        
        # Activity-specific badges
        BadgeService._check_activity_badges(user)
        
        # Special achievement badges
        BadgeService._check_special_badges(user, profile)
    
    @staticmethod
    def _check_level_badges(user, profile):
        """Award badges based on points/level"""
        badges_to_check = [
            (BadgeType.BRONZE, 50, "Earned your first 50 points!"),
            (BadgeType.SILVER, 200, "Reached 200 points - you're making a difference!"),
            (BadgeType.GOLD, 500, "Gold level achieved with 500 points!"),
            (BadgeType.PLATINUM, 1000, "Platinum status - 1000 points earned!"),
            (BadgeType.ECO_CHAMPION, 2000, "Ultimate Eco Champion - 2000+ points!"),
        ]
        
        for badge_type, threshold, description in badges_to_check:
            if profile.total_points >= threshold:
                BadgeService._award_badge(user, badge_type, description)
    
    @staticmethod
    def _check_activity_badges(user):
        """Award badges based on specific activities"""
        activity_badges = [
            (BadgeType.TREE_LOVER, ActivityType.TREE_PLANTATION, 10, "Planted 10 or more trees!"),
            (BadgeType.RECYCLING_HERO, ActivityType.RECYCLING, 50, "Recycled 50kg or more of materials!"),
            (BadgeType.CLEANUP_MASTER, ActivityType.CLEANUP_DRIVE, 25, "Cleaned up 25kg or more of waste!"),
            (BadgeType.AWARENESS_ADVOCATE, ActivityType.AWARENESS_CAMPAIGN, 20, "Participated in 20+ hours of awareness campaigns!"),
            (BadgeType.ENERGY_SAVER, ActivityType.ENERGY_SAVING, 100, "Saved 100+ kWh of energy!"),
        ]
        
        for badge_type, activity_type, threshold, description in activity_badges:
            total_quantity = ActivitySubmission.objects.filter(
                user=user,
                activity_type=activity_type,
                status=ActivitySubmission.Status.APPROVED
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            if total_quantity >= threshold:
                BadgeService._award_badge(user, badge_type, description)
    
    @staticmethod
    def _check_special_badges(user, profile):
        """Award special achievement badges"""
        # Event Participant Badge
        events_attended = EventParticipant.objects.filter(user=user).count()
        if events_attended >= 5:
            BadgeService._award_badge(
                user, 
                BadgeType.EVENT_PARTICIPANT, 
                f"Attended {events_attended} eco-events!"
            )
        
        # Team Player Badge
        if hasattr(user, 'teams') and user.teams.exists():
            BadgeService._award_badge(
                user,
                BadgeType.TEAM_PLAYER,
                "Active team member contributing to collective goals!"
            )
    
    @staticmethod
    def _award_badge(user, badge_type, description):
        """Award a badge to user if they don't already have it"""
        badge, created = UserBadge.objects.get_or_create(
            user=user,
            badge_type=badge_type,
            defaults={'description': description}
        )
        return created  # Returns True if badge was newly created
    
    @staticmethod
    def get_badge_icon(badge_type):
        """Get emoji icon for badge type"""
        icons = {
            BadgeType.BRONZE: '🥉',
            BadgeType.SILVER: '🥈',
            BadgeType.GOLD: '🥇',
            BadgeType.PLATINUM: '💎',
            BadgeType.ECO_CHAMPION: '🌟',
            BadgeType.TREE_LOVER: '🌳',
            BadgeType.RECYCLING_HERO: '♻️',
            BadgeType.CLEANUP_MASTER: '🧹',
            BadgeType.AWARENESS_ADVOCATE: '📢',
            BadgeType.ENERGY_SAVER: '⚡',
            BadgeType.EVENT_PARTICIPANT: '🎭',
            BadgeType.TEAM_PLAYER: '👥',
        }
        return icons.get(badge_type, '🏆')
    
    @staticmethod
    def get_badge_color(badge_type):
        """Get CSS color class for badge type"""
        colors = {
            BadgeType.BRONZE: 'bg-orange-100 text-orange-800',
            BadgeType.SILVER: 'bg-gray-100 text-gray-800',
            BadgeType.GOLD: 'bg-yellow-100 text-yellow-800',
            BadgeType.PLATINUM: 'bg-purple-100 text-purple-800',
            BadgeType.ECO_CHAMPION: 'bg-green-100 text-green-800',
            BadgeType.TREE_LOVER: 'bg-green-100 text-green-800',
            BadgeType.RECYCLING_HERO: 'bg-blue-100 text-blue-800',
            BadgeType.CLEANUP_MASTER: 'bg-indigo-100 text-indigo-800',
            BadgeType.AWARENESS_ADVOCATE: 'bg-pink-100 text-pink-800',
            BadgeType.ENERGY_SAVER: 'bg-yellow-100 text-yellow-800',
            BadgeType.EVENT_PARTICIPANT: 'bg-purple-100 text-purple-800',
            BadgeType.TEAM_PLAYER: 'bg-cyan-100 text-cyan-800',
        }
        return colors.get(badge_type, 'bg-gray-100 text-gray-800')


def award_badges_on_activity_approval(activity_submission):
    """Signal handler function to award badges when activity is approved"""
    if activity_submission.status == ActivitySubmission.Status.APPROVED:
        BadgeService.check_and_award_badges(activity_submission.user)


def award_badges_on_event_participation(event_participant):
    """Signal handler function to award badges when user participates in event"""
    BadgeService.check_and_award_badges(event_participant.user)