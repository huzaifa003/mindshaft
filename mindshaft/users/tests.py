from django.test import TestCase
from rest_framework.test import APIClient
from django.utils.timezone import now, timedelta
from users.models import CustomUser

class DailyLimitResetMiddlewareTest(TestCase):
    def setUp(self):
        """
        Set up test data for the test case.
        """
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email="user@example.com",
            password="password123",
            credits_used_today=5000,
            last_reset_date=now().date() - timedelta(days=1),  # Simulate last reset as yesterday
            is_premium=False,
        )
        self.client = APIClient()

        # Obtain a JWT token for the test user
        response = self.client.post('/api/token/', {
            "email": "user@example.com",
            "password": "password123",
        })
        self.assertEqual(response.status_code, 200, "Token generation failed.")
        self.access_token = response.data['access']  # Extract access token

        # Add the Authorization header with the JWT token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_daily_limit_resets(self):
        """
        Test that the daily limit is reset for authenticated users when the day changes.
        """
        # Send a GET request to the Get Profile endpoint
        response = self.client.get('/api/users/profile/')  # Replace with your actual profile endpoint

        # Refresh user data from the database
        self.user.refresh_from_db()

        # Assert that credits_used_today is reset to 0
        self.assertEqual(self.user.credits_used_today, 0, "Daily credits should reset to 0.")

        # Assert that last_reset_date is updated to today
        self.assertEqual(self.user.last_reset_date, now().date(), "Last reset date should be updated to today.")

        # Assert that the request returns the correct profile data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['credits_used_today'], 0)
        self.assertEqual(response.data['last_reset_date'], str(now().date()))

    def test_daily_limit_not_reset_same_day(self):
        """
        Test that the daily limit is not reset if the last reset date is today.
        """
        # Update last_reset_date to today
        self.user.last_reset_date = now().date()
        self.user.save()

        # Send a GET request to the Get Profile endpoint
        response = self.client.get('/api/users/profile/')

        # Refresh user data from the database
        self.user.refresh_from_db()

        # Assert that credits_used_today remains unchanged
        self.assertEqual(self.user.credits_used_today, 5000, "Daily credits should not reset if it's the same day.")

        # Assert that the request returns the correct profile data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['credits_used_today'], 5000)
        self.assertEqual(response.data['last_reset_date'], str(now().date()))
