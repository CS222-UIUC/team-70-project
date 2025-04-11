from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
import datetime
from unittest.mock import patch, MagicMock

from game.models import DailyScore, GlobalLeaderboard


class LeaderboardServiceTest(TestCase):
    """Test for leaderboard functionality"""

    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = User.objects.create_user(username="user1", password="password")
        cls.user2 = User.objects.create_user(username="user2", password="password")
        cls.user3 = User.objects.create_user(username="user3", password="password")

        # Set user profile parameters
        cls.user1.profile.show_on_leaderboard = True
        cls.user1.profile.save()
        cls.user2.profile.show_on_leaderboard = True
        cls.user2.profile.save()
        cls.user3.profile.show_on_leaderboard = False  # Not shown on leaderboard
        cls.user3.profile.save()

        cls.today = timezone.now().date()
        cls.yesterday = cls.today - datetime.timedelta(days=1)

    def setUp(self):
        # Create daily scores for today
        DailyScore.objects.create(
            user=self.user1,
            date=self.today,
            score=850,
            guesses=2,
            time_taken=240,
            completed=True,
        )

        DailyScore.objects.create(
            user=self.user2,
            date=self.today,
            score=750,
            guesses=3,
            time_taken=300,
            completed=True,
        )

        DailyScore.objects.create(
            user=self.user3,
            date=self.today,
            score=900,  # Higher score, but won't show on leaderboard
            guesses=1,
            time_taken=200,
            completed=True,
        )

        # Create daily scores for yesterday
        DailyScore.objects.create(
            user=self.user1,
            date=self.yesterday,
            score=600,
            guesses=4,
            time_taken=350,
            completed=True,
        )

        DailyScore.objects.create(
            user=self.user2,
            date=self.yesterday,
            score=700,
            guesses=3,
            time_taken=280,
            completed=True,
        )

    def test_global_leaderboard_creation(self):
        """Test creating a global leaderboard"""
        leaderboard = GlobalLeaderboard.objects.create(date=self.today)
        self.assertEqual(leaderboard.date, self.today)
        self.assertEqual(leaderboard.leaderboard_data, {})  # Initially empty

    def test_global_leaderboard_update(self):
        """Test updating the global leaderboard"""
        leaderboard = GlobalLeaderboard.objects.create(date=self.today)
        leaderboard.update_leaderboard()

        # Verify leaderboard data
        self.assertIn("scores", leaderboard.leaderboard_data)
        self.assertIn("total_players", leaderboard.leaderboard_data)
        self.assertIn("average_score", leaderboard.leaderboard_data)

        scores = leaderboard.leaderboard_data["scores"]
        self.assertEqual(len(scores), 2)  # Only two users with display enabled

        # Verify ranking order (by score descending)
        self.assertEqual(scores[0]["username"], "user1")
        self.assertEqual(scores[0]["score"], 850)
        self.assertEqual(scores[0]["rank"], 1)

        self.assertEqual(scores[1]["username"], "user2")
        self.assertEqual(scores[1]["score"], 750)
        self.assertEqual(scores[1]["rank"], 2)

        # Verify total player count includes all players
        self.assertEqual(leaderboard.leaderboard_data["total_players"], 3)

        # Verify the average score calculation
        # Average score: (850 + 750 + 900) / 3 = 833.33...
        self.assertAlmostEqual(leaderboard.leaderboard_data["average_score"], 833.33, places=2)

    def test_multiple_date_leaderboards(self):
        """Test leaderboards for multiple dates"""
        # Create and update leaderboards for today and yesterday
        today_board = GlobalLeaderboard.objects.create(date=self.today)
        today_board.update_leaderboard()

        yesterday_board = GlobalLeaderboard.objects.create(date=self.yesterday)
        yesterday_board.update_leaderboard()

        # Verify both leaderboards exist
        self.assertEqual(GlobalLeaderboard.objects.count(), 2)

        # Verify the content of yesterday's leaderboard
        scores = yesterday_board.leaderboard_data["scores"]

        # Verify ranking order for yesterday
        self.assertEqual(scores[0]["username"], "user2")
        self.assertEqual(scores[0]["score"], 700)
        self.assertEqual(scores[1]["username"], "user1")
        self.assertEqual(scores[1]["score"], 600)

    def test_user_not_on_leaderboard(self):
        """Test that users who opt out don't appear on leaderboard"""
        leaderboard = GlobalLeaderboard.objects.create(date=self.today)
        leaderboard.update_leaderboard()

        # Get usernames from leaderboard
        usernames = [score["username"] for score in leaderboard.leaderboard_data["scores"]]

        # Verify user3 is not on the leaderboard
        self.assertNotIn("user3", usernames)
