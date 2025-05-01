from io import StringIO
from django.test import TestCase
from django.core.management import call_command
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import json

from game.models import GlobalLeaderboard, DailyScore, UserProfile


class DisplayLeaderboardCommandTest(TestCase):
    """Test cases for the display_leaderboard management command."""

    def setUp(self):
        """Set up test data."""
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', password='password123')
        self.user3 = User.objects.create_user(username='testuser3', password='password123')

        # Set today's date
        self.today = timezone.now().date()
        self.yesterday = self.today - timedelta(days=1)

        # Create some test scores
        DailyScore.objects.create(
            user=self.user1,
            date=self.today,
            score=850,
            time_taken=120,
            guesses=3,
            completed=True,
            article_title="Test Article 1",
            hints_used=1
        )

        DailyScore.objects.create(
            user=self.user2,
            date=self.today,
            score=750,
            time_taken=150,
            guesses=4,
            completed=True,
            article_title="Test Article 1",
            hints_used=2
        )

        DailyScore.objects.create(
            user=self.user3,
            date=self.today,
            score=950,
            time_taken=90,
            guesses=2,
            completed=True,
            article_title="Test Article 1",
            hints_used=0
        )

        # Create test scores for yesterday
        DailyScore.objects.create(
            user=self.user1,
            date=self.yesterday,
            score=800,
            time_taken=110,
            guesses=3,
            completed=True,
            article_title="Test Article 2",
            hints_used=1
        )

        DailyScore.objects.create(
            user=self.user2,
            date=self.yesterday,
            score=700,
            time_taken=160,
            guesses=5,
            completed=True,
            article_title="Test Article 2",
            hints_used=2
        )

        # Create global leaderboard data
        GlobalLeaderboard.objects.create(
            date=self.today,
            leaderboard_data={
                'scores': [
                    {'rank': 1, 'username': 'testuser3', 'score': 950, 'guesses': 2, 'time_taken': 90},
                    {'rank': 2, 'username': 'testuser1', 'score': 850, 'guesses': 3, 'time_taken': 120},
                    {'rank': 3, 'username': 'testuser2', 'score': 750, 'guesses': 4, 'time_taken': 150},
                ],
                'total_players': 3,
                'average_score': 850.0,
            }
        )

        GlobalLeaderboard.objects.create(
            date=self.yesterday,
            leaderboard_data={
                'scores': [
                    {'rank': 1, 'username': 'testuser1', 'score': 800, 'guesses': 3, 'time_taken': 110},
                    {'rank': 2, 'username': 'testuser2', 'score': 700, 'guesses': 5, 'time_taken': 160},
                ],
                'total_players': 2,
                'average_score': 750.0,
            }
        )

    def call_command(self, *args, **kwargs):
        """Call the management command and return output."""
        out = StringIO()
        call_command('display_leaderboard', *args, stdout=out, **kwargs)
        return out.getvalue()

    def test_display_leaderboard_default(self):
        """Test the command with default options."""
        output = self.call_command()

        # Check if output contains basic info
        self.assertIn(f"Leaderboard for {self.today}", output)
        self.assertIn("testuser3", output)
        self.assertIn("testuser1", output)
        self.assertIn("testuser2", output)

    def test_display_leaderboard_specific_date(self):
        """Test the command with a specific date."""
        date_str = self.yesterday.strftime('%Y-%m-%d')
        output = self.call_command(date=date_str)

        # Check if output contains correct date and users
        self.assertIn(f"Leaderboard for {self.yesterday}", output)
        self.assertIn("testuser1", output)
        self.assertIn("testuser2", output)
        self.assertNotIn("testuser3", output)  # testuser3 has no record for yesterday

    def test_display_leaderboard_multiple_days(self):
        """Test the command showing multiple days."""
        output = self.call_command(days=2)

        # Check if output contains both dates
        self.assertIn(f"Leaderboard for {self.today}", output)
        self.assertIn(f"Leaderboard for {self.yesterday}", output)

    def test_display_leaderboard_json_format(self):
        """Test the command with JSON output format."""
        output = self.call_command(format='json')

        # Check if output is valid JSON
        try:
            data = json.loads(output)
            self.assertEqual(data['date'], str(self.today))
            self.assertEqual(len(data['top_scores']), 3)
            self.assertEqual(data['total_players'], 3)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_display_leaderboard_specific_username(self):
        """Test the command searching for a specific username."""
        output = self.call_command(username='testuser1')

        # Check if output contains user's rank
        self.assertIn("User testuser1 ranking: #2", output)
        self.assertIn("Score: 850", output)

    def test_display_leaderboard_non_existent_date(self):
        """Test the command with a date that has no leaderboard."""
        future_date = (self.today + timedelta(days=5)).strftime('%Y-%m-%d')
        output = self.call_command(date=future_date)

        # Check if output indicates no leaderboard found
        self.assertIn(f"No leaderboard found for {future_date}", output)

    def test_display_leaderboard_limited_entries(self):
        """Test the command with limited number of entries."""
        output = self.call_command(top=2)

        # Check if output only shows top 2 entries
        self.assertIn("testuser3", output)
        self.assertIn("testuser1", output)
        self.assertNotIn("testuser2", output)  # Should be excluded due to top=2

    def test_display_leaderboard_non_existent_username(self):
        """Test the command with a username that doesn't exist in leaderboard."""
        output = self.call_command(username='nonexistentuser')

        # Check if output indicates user not found
        self.assertIn("User nonexistentuser not found in leaderboard", output)

    def test_display_leaderboard_empty_data(self):
        """Test the command with a leaderboard that has empty data."""
        # Create empty leaderboard
        empty_date = self.today - timedelta(days=2)
        GlobalLeaderboard.objects.create(
            date=empty_date,
            leaderboard_data={}
        )

        date_str = empty_date.strftime('%Y-%m-%d')
        output = self.call_command(date=date_str)

        # Check if output indicates empty data
        self.assertIn(f"Leaderboard data for {empty_date} is empty", output)

    def test_display_leaderboard_update_suggestion(self):
        """Test the command when leaderboard doesn't exist but scores do."""
        # Create a date with scores but no leaderboard
        future_date = self.today + timedelta(days=3)

        # Create score for that date
        DailyScore.objects.create(
            user=self.user1,
            date=future_date,
            score=800,
            time_taken=110,
            guesses=3,
            completed=True,
            article_title="Future Article",
            hints_used=1
        )

        # Format the date for command argument
        date_str = future_date.strftime('%Y-%m-%d')
        output = self.call_command(date=date_str)

        # Check if output suggests updating the leaderboard
        self.assertIn(f"No leaderboard found for {future_date}", output)
        self.assertIn("There are 1 score records for this date", output)
        self.assertIn(f"Run 'python manage.py update_leaderboard --date={future_date}'", output)

    def test_display_leaderboard_no_scores(self):
        """Test the command when neither leaderboard nor scores exist."""
        # Create a date with no data
        empty_date = self.today + timedelta(days=5)
        date_str = empty_date.strftime('%Y-%m-%d')
        output = self.call_command(date=date_str)

        # Check if output indicates no scores
        self.assertIn(f"No leaderboard found for {empty_date}", output)
        self.assertIn("No score records found for this date.", output)

    def test_display_leaderboard_with_empty_scores(self):
        """Test the command with a leaderboard that has an empty scores list."""
        # Create leaderboard with empty scores list
        empty_scores_date = self.today - timedelta(days=3)
        GlobalLeaderboard.objects.create(
            date=empty_scores_date,
            leaderboard_data={
                'scores': [],
                'total_players': 0,
                'average_score': 0,
            }
        )

        date_str = empty_scores_date.strftime('%Y-%m-%d')
        output = self.call_command(date=date_str)

        # Check if output indicates empty scores list
        self.assertIn(f"Leaderboard for {empty_scores_date} doesn't contain any scores", output)

    def test_display_leaderboard_time_format_hours(self):
        """Test the time formatting with hours."""
        # Create a score with more than an hour of play time
        long_time_date = self.today - timedelta(days=4)
        long_time_user = User.objects.create_user(username='longtime', password='password123')

        DailyScore.objects.create(
            user=long_time_user,
            date=long_time_date,
            score=500,
            time_taken=3725,  # 1h 2m 5s
            guesses=10,
            completed=True,
            article_title="Long Time Article",
            hints_used=5
        )

        # Create leaderboard with this data
        GlobalLeaderboard.objects.create(
            date=long_time_date,
            leaderboard_data={
                'scores': [
                    {'rank': 1, 'username': 'longtime', 'score': 500, 'guesses': 10, 'time_taken': 3725},
                ],
                'total_players': 1,
                'average_score': 500.0,
            }
        )

        date_str = long_time_date.strftime('%Y-%m-%d')
        output = self.call_command(date=date_str)

        # Check if hours format appears in output
        self.assertIn("1h 2m 5s", output)

    def test_display_leaderboard_time_format_minutes(self):
        """Test the time formatting with minutes but no hours."""
        # Create a score with minutes
        mid_time_date = self.today - timedelta(days=5)
        mid_time_user = User.objects.create_user(username='midtime', password='password123')

        DailyScore.objects.create(
            user=mid_time_user,
            date=mid_time_date,
            score=700,
            time_taken=125,  # 2m 5s
            guesses=5,
            completed=True,
            article_title="Mid Time Article",
            hints_used=2
        )

        # Create leaderboard with this data
        GlobalLeaderboard.objects.create(
            date=mid_time_date,
            leaderboard_data={
                'scores': [
                    {'rank': 1, 'username': 'midtime', 'score': 700, 'guesses': 5, 'time_taken': 125},
                ],
                'total_players': 1,
                'average_score': 700.0,
            }
        )

        date_str = mid_time_date.strftime('%Y-%m-%d')
        output = self.call_command(date=date_str)

        # Check if minutes format appears in output
        self.assertIn("2m 5s", output)

    def test_display_leaderboard_time_format_seconds_only(self):
        """Test the time formatting with seconds only."""
        # Create a score with just seconds
        seconds_only_date = self.today - timedelta(days=6)
        seconds_only_user = User.objects.create_user(username='quickuser', password='password123')

        DailyScore.objects.create(
            user=seconds_only_user,
            date=seconds_only_date,
            score=950,
            time_taken=45,  # 45s
            guesses=1,
            completed=True,
            article_title="Quick Solve Article",
            hints_used=0
        )

        # Create leaderboard with this data
        GlobalLeaderboard.objects.create(
            date=seconds_only_date,
            leaderboard_data={
                'scores': [
                    {'rank': 1, 'username': 'quickuser', 'score': 950, 'guesses': 1, 'time_taken': 45},
                ],
                'total_players': 1,
                'average_score': 950.0,
            }
        )

        date_str = seconds_only_date.strftime('%Y-%m-%d')
        output = self.call_command(date=date_str)

        # Check if seconds-only format appears in output
        self.assertIn("45s", output)
