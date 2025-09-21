from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import ActivitySubmission, ActivityType

User = get_user_model()

class ActivitySubmissionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_approve_calculates_points_and_carbon(self):
        """Test that the approve() method correctly calculates points and carbon."""
        submission = ActivitySubmission.objects.create(
            user=self.user,
            activity_type=ActivityType.TREE_PLANTATION,
            quantity=5
        )
        self.assertEqual(submission.status, 'PENDING')

        # Approve the submission
        submission.approve()

        # Refresh from DB to get updated values
        submission.refresh_from_db()

        self.assertEqual(submission.status, 'APPROVED')
        self.assertEqual(submission.points_awarded, 50) # 5 trees * 10 points/tree
        self.assertEqual(submission.carbon_saved_kg, 110.0) # 5 trees * 22.0 kg/tree

class DashboardViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_dashboard_loads_for_logged_in_user(self):
        """Test that the dashboard page loads correctly."""
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
        self.assertContains(response, 'My Recent Activities')
