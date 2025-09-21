import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from activities.models import ActivitySubmission, ActivityType, CarbonLog
from teams.models import Team
from events.models import Event, EventParticipant
from users.models import UserProfile, UserBadge, BadgeType
from users.badge_service import BadgeService

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive sample data for demo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before seeding',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write("Resetting database...")
            self.reset_data()
        
        self.stdout.write("Creating comprehensive demo data...")
        
        # Create users with profiles
        users = self.create_demo_users()
        
        # Create teams
        teams = self.create_demo_teams(users)
        
        # Create events
        events = self.create_demo_events(users)
        
        # Create activities and logs
        self.create_demo_activities(users)
        
        # Create event participants
        self.create_event_participants(users, events)
        
        # Award badges to users
        self.award_demo_badges(users)
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database with demo data!'))
        self.print_demo_info(users, teams, events)

    def reset_data(self):
        """Reset all data for clean demo"""
        models_to_reset = [
            ActivitySubmission, CarbonLog, EventParticipant, 
            Event, UserBadge, UserProfile, Team
        ]
        
        for model in models_to_reset:
            model.objects.all().delete()
            
        # Delete non-superuser users
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write("Database reset complete.")

    def create_demo_users(self):
        """Create diverse demo users"""
        users_data = [
            {
                'username': 'tarun', 'password': 'password123',
                'first_name': 'Tarun', 'last_name': 'Sharma',
                'email': 'tarun@university.edu',
                'profile_data': {
                    'department': 'Environmental Science',
                    'year_of_study': '3rd Year',
                    'bio': 'Passionate about sustainability and climate action!'
                }
            },
            {
                'username': 'aashish', 'password': 'password123',
                'first_name': 'Aashish', 'last_name': 'Patel',
                'email': 'aashish@university.edu',
                'profile_data': {
                    'department': 'Engineering',
                    'year_of_study': '2nd Year',
                    'bio': 'Love building eco-friendly solutions.'
                }
            },
            {
                'username': 'yuvraj', 'password': 'password123',
                'first_name': 'Yuvraj', 'last_name': 'Singh',
                'email': 'yuvraj@university.edu',
                'profile_data': {
                    'department': 'Business',
                    'year_of_study': '4th Year',
                    'bio': 'Interested in sustainable business practices.'
                }
            },
            {
                'username': 'diana', 'password': 'password123',
                'first_name': 'Diana', 'last_name': 'Wilson',
                'email': 'diana@university.edu',
                'profile_data': {
                    'department': 'Biology',
                    'year_of_study': 'Graduate',
                    'bio': 'Researching renewable energy systems.'
                }
            },
            {
                'username': 'eve', 'password': 'password123',
                'first_name': 'Eve', 'last_name': 'Davis',
                'email': 'eve@university.edu',
                'profile_data': {
                    'department': 'Chemistry',
                    'year_of_study': '1st Year',
                    'bio': 'New to sustainability but eager to learn!'
                }
            }
        ]
        
        created_users = []
        for user_data in users_data:
            # Delete user if already exists
            User.objects.filter(username=user_data['username']).delete()
            
            profile_data = user_data.pop('profile_data')
            user = User.objects.create_user(**user_data)
            
            # Create/update profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.save()
            
            created_users.append(user)
            self.stdout.write(f"Created user: {user.username}")
        
        return created_users

    def create_demo_teams(self, users):
        """Create demo teams with members"""
        # Delete existing teams first
        Team.objects.all().delete()
        
        teams_data = [
            {
                'name': 'Green Giants',
                'leader': users[0],  # Tarun
                'members': [users[0], users[1], users[2]]  # Tarun, Aashish, Yuvraj
            },
            {
                'name': 'Eco Warriors',
                'leader': users[3],  # Diana
                'members': [users[3], users[4]]  # Diana, Eve
            },
            {
                'name': 'Sustainability Squad',
                'leader': users[1],  # Aashish
                'members': [users[1]]  # Aashish only (single member team)
            }
        ]
        
        created_teams = []
        for team_data in teams_data:
            team = Team.objects.create(
                name=team_data['name'],
                leader=team_data['leader']
            )
            team.members.set(team_data['members'])
            created_teams.append(team)
            self.stdout.write(f"Created team: {team.name} with {team.members.count()} members")
        
        return created_teams

    def create_demo_events(self, users):
        """Create demo events"""
        # Delete existing events first
        Event.objects.all().delete()
        
        now = timezone.now()
        events_data = [
            {
                'name': 'Campus Tree Planting Day',
                'description': 'Join us for a campus-wide tree planting initiative to improve air quality and beautify our grounds.',
                'date': now + timedelta(days=7),
                'location': 'Main Campus Quad',
                'organizer': users[0],  # Tarun
                'points_for_attendance': 50
            },
            {
                'name': 'Sustainability Workshop',
                'description': 'Learn about renewable energy, waste reduction, and sustainable living practices.',
                'date': now + timedelta(days=14),
                'location': 'Environmental Science Building, Room 201',
                'organizer': users[3],  # Diana
                'points_for_attendance': 30
            },
            {
                'name': 'Beach Clean-up Drive',
                'description': 'Help clean the local beach and protect marine life from plastic pollution.',
                'date': now - timedelta(days=3),  # Past event
                'location': 'Sunrise Beach',
                'organizer': users[1],  # Aashish
                'points_for_attendance': 40
            },
            {
                'name': 'Green Energy Fair',
                'description': 'Showcase of renewable energy projects and sustainable technologies.',
                'date': now + timedelta(days=21),
                'location': 'Student Center',
                'organizer': users[2],  # Yuvraj
                'points_for_attendance': 35
            }
        ]
        
        created_events = []
        for event_data in events_data:
            event = Event.objects.create(**event_data)
            created_events.append(event)
            self.stdout.write(f"Created event: {event.name}")
        
        return created_events

    def create_demo_activities(self, users):
        """Create comprehensive activity submissions"""
        # Delete existing activities first
        ActivitySubmission.objects.all().delete()
        CarbonLog.objects.all().delete()
        
        activities_data = [
            # Tarun's activities (high performer)
            {'user': users[0], 'activity_type': ActivityType.TREE_PLANTATION, 'quantity': 15, 'status': 'APPROVED', 'days_ago': 30},
            {'user': users[0], 'activity_type': ActivityType.RECYCLING, 'quantity': 25.5, 'status': 'APPROVED', 'days_ago': 25},
            {'user': users[0], 'activity_type': ActivityType.CLEANUP_DRIVE, 'quantity': 8, 'status': 'APPROVED', 'days_ago': 20},
            {'user': users[0], 'activity_type': ActivityType.AWARENESS_CAMPAIGN, 'quantity': 12, 'status': 'APPROVED', 'days_ago': 15},
            {'user': users[0], 'activity_type': ActivityType.ENERGY_SAVING, 'quantity': 150, 'status': 'APPROVED', 'days_ago': 10},
            {'user': users[0], 'activity_type': ActivityType.TREE_PLANTATION, 'quantity': 5, 'status': 'PENDING', 'days_ago': 2},
            
            # Aashish's activities (moderate performer)
            {'user': users[1], 'activity_type': ActivityType.RECYCLING, 'quantity': 18.2, 'status': 'APPROVED', 'days_ago': 28},
            {'user': users[1], 'activity_type': ActivityType.ENERGY_SAVING, 'quantity': 80, 'status': 'APPROVED', 'days_ago': 22},
            {'user': users[1], 'activity_type': ActivityType.CLEANUP_DRIVE, 'quantity': 12, 'status': 'APPROVED', 'days_ago': 18},
            {'user': users[1], 'activity_type': ActivityType.AWARENESS_CAMPAIGN, 'quantity': 6, 'status': 'APPROVED', 'days_ago': 12},
            {'user': users[1], 'activity_type': ActivityType.RECYCLING, 'quantity': 10.5, 'status': 'REJECTED', 'days_ago': 5},
            
            # Yuvraj's activities (lower performer)
            {'user': users[2], 'activity_type': ActivityType.TREE_PLANTATION, 'quantity': 3, 'status': 'APPROVED', 'days_ago': 26},
            {'user': users[2], 'activity_type': ActivityType.AWARENESS_CAMPAIGN, 'quantity': 8, 'status': 'APPROVED', 'days_ago': 20},
            {'user': users[2], 'activity_type': ActivityType.RECYCLING, 'quantity': 12.0, 'status': 'APPROVED', 'days_ago': 14},
            {'user': users[2], 'activity_type': ActivityType.CLEANUP_DRIVE, 'quantity': 3, 'status': 'PENDING', 'days_ago': 1},
            
            # Diana's activities (very high performer)
            {'user': users[3], 'activity_type': ActivityType.ENERGY_SAVING, 'quantity': 200, 'status': 'APPROVED', 'days_ago': 35},
            {'user': users[3], 'activity_type': ActivityType.TREE_PLANTATION, 'quantity': 20, 'status': 'APPROVED', 'days_ago': 32},
            {'user': users[3], 'activity_type': ActivityType.RECYCLING, 'quantity': 45.7, 'status': 'APPROVED', 'days_ago': 28},
            {'user': users[3], 'activity_type': ActivityType.CLEANUP_DRIVE, 'quantity': 15, 'status': 'APPROVED', 'days_ago': 24},
            {'user': users[3], 'activity_type': ActivityType.AWARENESS_CAMPAIGN, 'quantity': 25, 'status': 'APPROVED', 'days_ago': 18},
            {'user': users[3], 'activity_type': ActivityType.TREE_PLANTATION, 'quantity': 8, 'status': 'APPROVED', 'days_ago': 12},
            
            # Eve's activities (new user)
            {'user': users[4], 'activity_type': ActivityType.RECYCLING, 'quantity': 5.5, 'status': 'APPROVED', 'days_ago': 8},
            {'user': users[4], 'activity_type': ActivityType.AWARENESS_CAMPAIGN, 'quantity': 3, 'status': 'APPROVED', 'days_ago': 5},
            {'user': users[4], 'activity_type': ActivityType.TREE_PLANTATION, 'quantity': 2, 'status': 'PENDING', 'days_ago': 1},
        ]
        
        for activity_data in activities_data:
            days_ago = activity_data.pop('days_ago')
            submission_date = timezone.now() - timedelta(days=days_ago)
            
            submission = ActivitySubmission.objects.create(
                **activity_data,
                submitted_at=submission_date
            )
            
            if activity_data['status'] == 'APPROVED':
                submission.approve()
            elif activity_data['status'] == 'REJECTED':
                submission.status = ActivitySubmission.Status.REJECTED
                submission.feedback = "Evidence not clear enough. Please resubmit with better documentation."
                submission.save()
        
        # Update user stats after creating all activities
        for user in users:
            user.profile.update_stats()
        
        self.stdout.write(f"Created {len(activities_data)} activity submissions")

    def create_event_participants(self, users, events):
        """Create event participants for past events"""
        # Delete existing event participants first
        EventParticipant.objects.all().delete()
        CarbonLog.objects.filter(carbon_saved_kg=0).delete()  # Remove existing attendance logs
        
        # For the beach cleanup (past event)
        beach_cleanup = events[2]  # Past event
        participants = [users[0], users[1], users[3]]  # Tarun, Aashish, Diana attended
        
        for user in participants:
            EventParticipant.objects.create(
                event=beach_cleanup,
                user=user,
                checked_in_at=beach_cleanup.date
            )
            
            # Award points for attendance
            CarbonLog.objects.create(
                user=user,
                carbon_saved_kg=0,  # Event attendance doesn't directly save carbon
                points_earned=beach_cleanup.points_for_attendance
            )
        
        self.stdout.write(f"Created event participants for {beach_cleanup.name}")

    def award_demo_badges(self, users):
        """Award badges to users based on their activities"""
        # Delete existing badges first
        UserBadge.objects.all().delete()
        
        for user in users:
            BadgeService.check_and_award_badges(user)
            badges_count = UserBadge.objects.filter(user=user).count()
            self.stdout.write(f"Awarded {badges_count} badges to {user.username}")

    def print_demo_info(self, users, teams, events):
        """Print demo information for users"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("DEMO SETUP COMPLETE!"))
        self.stdout.write("="*50)
        
        self.stdout.write("\n📊 DEMO STATISTICS:")
        self.stdout.write(f"Users created: {len(users)}")
        self.stdout.write(f"Teams created: {len(teams)}")
        self.stdout.write(f"Events created: {len(events)}")
        self.stdout.write(f"Activities created: {ActivitySubmission.objects.count()}")
        
        self.stdout.write("\n👥 DEMO USERS (username/password):")
        for user in users:
            profile = user.profile
            total_points = profile.total_points
            level = profile.current_level
            badges = UserBadge.objects.filter(user=user).count()
            self.stdout.write(f"  {user.username}/password123 - {total_points} points, {level} level, {badges} badges")
        
        self.stdout.write("\n🏆 TOP PERFORMERS:")
        sorted_users = sorted(users, key=lambda u: u.profile.total_points, reverse=True)
        for i, user in enumerate(sorted_users[:3], 1):
            self.stdout.write(f"  {i}. {user.username} - {user.profile.total_points} points")
        
        self.stdout.write("\n🎯 DEMO WALKTHROUGH:")
        self.stdout.write("1. Login as 'tarun' (high performer with multiple badges)")
        self.stdout.write("2. Check dashboard to see carbon chart and activities")
        self.stdout.write("3. Visit profile to see badges and level progress")
        self.stdout.write("4. Check leaderboards to see team rankings")
        self.stdout.write("5. Try the chatbot for eco-tips")
        self.stdout.write("6. Visit events page for QR code functionality")
        self.stdout.write("7. Admin can approve pending activities")
        
        self.stdout.write("\n🌟 Ready for your demo presentation!")