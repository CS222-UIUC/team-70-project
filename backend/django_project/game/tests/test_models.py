from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import datetime
import json
import random
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from game.models import UserDevice, UserVerification

from game.models import (
    UserProfile,
    DailyScore,
    ArticleCache,
    DailyArticle,
    GlobalLeaderboard,
    GameState,
    UserGuess,
)


class UserProfileModelTest(TestCase):
    """Test the UserProfile model"""

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

    def test_profile_creation(self):
        """Test that a profile is automatically created when a user is created"""
        # Signal should have created a profile
        self.assertTrue(hasattr(self.test_user, "profile"))
        self.assertIsInstance(self.test_user.profile, UserProfile)

    def test_string_representation(self):
        """Test the string representation method"""
        self.assertEqual(str(self.test_user.profile), "testuser's profile")

    def test_default_values(self):
        """Test that default values are set correctly"""
        profile = self.test_user.profile
        self.assertEqual(profile.current_streak, 0)
        self.assertEqual(profile.max_streak, 0)
        self.assertEqual(profile.total_games_played, 0)
        self.assertEqual(profile.total_wins, 0)
        self.assertEqual(profile.average_score, 0.0)
        self.assertEqual(profile.best_score, 0)
        self.assertTrue(profile.daily_reminder)
        self.assertTrue(profile.friend_activity_notifications)
        self.assertFalse(profile.dark_mode)
        self.assertTrue(profile.public_profile)
        self.assertTrue(profile.show_on_leaderboard)

    def test_calculate_average_score(self):
        """Test the average score calculation method"""
        profile = self.test_user.profile
        today = timezone.now().date()

        # Create three score records for different dates
        DailyScore.objects.create(
            user=self.test_user,
            date=today - datetime.timedelta(days=2),
            score=100,
            completed=True,
        )

        DailyScore.objects.create(
            user=self.test_user,
            date=today - datetime.timedelta(days=1),
            score=200,
            completed=True,
        )

        DailyScore.objects.create(
            user=self.test_user, date=today, score=300, completed=True
        )

        # Update total games played (in a real application this might be
        # handled by view logic)
        profile.total_games_played = 3
        profile.save()

        # Calculate average score
        avg_score = profile.calculate_average_score()

        # Verify average score is calculated correctly (100 + 200 + 300) / 3 =
        # 200
        self.assertEqual(avg_score, 200.0)
        self.assertEqual(profile.average_score, 200.0)

    def test_update_streak_first_play(self):
        """Test streak update for first-time play"""
        profile = self.test_user.profile
        today = timezone.now().date()

        profile.update_streak(today)

        self.assertEqual(profile.current_streak, 1)
        self.assertEqual(profile.max_streak, 1)
        self.assertEqual(profile.last_played_date, today)

    def test_update_streak_consecutive_days(self):
        """Test streak update for consecutive days"""
        profile = self.test_user.profile
        today = timezone.now().date()
        yesterday = today - datetime.timedelta(days=1)

        # Set up as if played yesterday
        profile.last_played_date = yesterday
        profile.current_streak = 3
        profile.max_streak = 5
        profile.save()

        # Update streak for today
        profile.update_streak(today)

        self.assertEqual(profile.current_streak, 4)  # Increased by 1
        self.assertEqual(profile.max_streak, 5)  # Unchanged
        self.assertEqual(profile.last_played_date, today)

    def test_update_streak_after_gap(self):
        """Test streak reset after a gap in play"""
        profile = self.test_user.profile
        today = timezone.now().date()
        two_days_ago = today - datetime.timedelta(days=2)

        # Set up as if played two days ago
        profile.last_played_date = two_days_ago
        profile.current_streak = 5
        profile.max_streak = 5
        profile.save()

        # Update streak for today (missing yesterday)
        profile.update_streak(today)

        self.assertEqual(profile.current_streak, 1)  # Reset to 1
        self.assertEqual(profile.max_streak, 5)  # Unchanged
        self.assertEqual(profile.last_played_date, today)

    def test_update_streak_new_max(self):
        """Test update of max streak record"""
        profile = self.test_user.profile
        today = timezone.now().date()
        yesterday = today - datetime.timedelta(days=1)

        # Set up as if played yesterday with current streak equal to max streak
        profile.last_played_date = yesterday
        profile.current_streak = 5
        profile.max_streak = 5
        profile.save()

        # Update streak for today
        profile.update_streak(today)

        self.assertEqual(profile.current_streak, 6)  # Increased by 1
        self.assertEqual(profile.max_streak, 6)  # Also increased by 1
        self.assertEqual(profile.last_played_date, today)


class DailyScoreModelTest(TestCase):
    """Test the DailyScore model"""

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.test_user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        cls.today = timezone.now().date()

    def test_string_representation(self):
        """Test the string representation method"""
        score = DailyScore.objects.create(
            user=self.test_user, date=self.today, score=750
        )
        self.assertEqual(str(score), f"testuser - {self.today} - 750 points")

    def test_calculate_score_complete(self):
        """Test score calculation for completed games"""
        # Create test score record
        score = DailyScore.objects.create(
            user=self.test_user,
            date=self.today,
            time_taken=300,  # 5 minutes
            guesses=3,
            hints_used=2,
            completed=True,
        )

        # Calculate score
        calculated_score = score.calculate_score()

        # Expected score: 1000 - (300/10) - (3*50) - (2*40) = 1000 - 30 - 150 -
        # 80 = 740
        self.assertEqual(calculated_score, 740)
        self.assertEqual(score.score, 740)

    def test_calculate_score_incomplete(self):
        """Test score calculation for incomplete games"""
        # Create test score record
        score = DailyScore.objects.create(
            user=self.test_user,
            date=self.today,
            time_taken=300,
            guesses=3,
            hints_used=2,
            completed=False,
        )

        # Calculate score
        calculated_score = score.calculate_score()

        # Score for incomplete games should be 0
        self.assertEqual(calculated_score, 0)
        self.assertEqual(score.score, 0)

    def test_max_penalties(self):
        """Test penalty caps"""
        # Create test score record with extreme values
        score = DailyScore.objects.create(
            user=self.test_user,
            date=self.today,
            time_taken=10000,  # Very long time
            guesses=10,  # Many guesses
            hints_used=10,  # Many hints
            completed=True,
        )

        # Calculate score
        calculated_score = score.calculate_score()

        # Expected score: 1000 - 500 (max time penalty) - 300 (max guess
        # penalty) - 200 (max hint penalty) = 0
        self.assertEqual(calculated_score, 0)

    def test_calculate_score_time_penalty_cap(self):
        """Test that time penalty is capped at 500."""
        score = DailyScore.objects.create(
            user=self.test_user, date=self.today,
            time_taken=6000,  # 6000/10 = 600, should be capped at 500
            guesses=1, hints_used=0, completed=True
        )
        # Expected: 1000 (base) - 500 (max time) - (1*50) - 0 = 450
        self.assertEqual(score.calculate_score(), 450)

    def test_calculate_score_guess_penalty_cap(self):
        """Test that guess penalty is capped at 300."""
        score = DailyScore.objects.create(
            user=self.test_user, date=self.today,
            time_taken=100,  # 100/10 = 10
            guesses=10,    # 10*50 = 500, should be capped at 300
            hints_used=0, completed=True
        )
        # Expected: 1000 (base) - 10 (time) - 300 (max guess) - 0 = 690
        self.assertEqual(score.calculate_score(), 690)

    def test_calculate_score_normal_penalties(self):
        """Test penalties below the cap."""
        score = DailyScore.objects.create(
            user=self.test_user, date=self.today,
            time_taken=2000,  # 2000/10 = 200 ( < 500)
            guesses=3,     # 3*50 = 150 ( < 300)
            hints_used=1,  # 1*40 = 40
            completed=True
        )
        # Expected: 1000 - 200 - 150 - 40 = 610
        self.assertEqual(score.calculate_score(), 610)


class ArticleCacheModelTest(TestCase):
    """Test the ArticleCache model"""

    def test_create_article_cache(self):
        """Test article cache creation"""
        article = ArticleCache.objects.create(
            article_id="12345",
            title="Test Article",
            content="This is the content of a test article.",
            image_urls=[
                "http://example.com/image1.jpg",
                "http://example.com/image2.jpg",
            ],
        )

        self.assertEqual(article.article_id, "12345")
        self.assertEqual(article.title, "Test Article")
        self.assertEqual(
            article.content, "This is the content of a test article."
        )
        self.assertEqual(len(article.image_urls), 2)
        self.assertEqual(
            article.image_urls[0], "http://example.com/image1.jpg"
        )

    def test_string_representation(self):
        """Test the string representation method"""
        article = ArticleCache.objects.create(
            article_id="12345", title="Test Article", content="Content"
        )
        self.assertEqual(str(article), "Test Article (12345)")


class DailyArticleModelTest(TestCase):
    """Test the DailyArticle model"""

    def setUp(self):
        # Create test article cache
        self.test_article = ArticleCache.objects.create(
            article_id="12345",
            title="Daily Article Test",
            content="This is the content of the daily article.",
        )
        self.today = timezone.now().date()

    def test_create_daily_article(self):
        """Test daily article creation"""
        daily_article = DailyArticle.objects.create(
            date=self.today, article=self.test_article
        )

        self.assertEqual(daily_article.date, self.today)
        self.assertEqual(daily_article.article, self.test_article)

    def test_string_representation(self):
        """Test the string representation method"""
        daily_article = DailyArticle.objects.create(
            date=self.today, article=self.test_article
        )
        self.assertEqual(
            str(daily_article), f"Article for {self.today}: Daily Article Test"
        )


class GlobalLeaderboardModelTest(TestCase):
    """Test the GlobalLeaderboard model"""

    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = User.objects.create_user(
            username="user1", password="password"
        )
        cls.user2 = User.objects.create_user(
            username="user2", password="password"
        )
        cls.user3 = User.objects.create_user(
            username="user3", password="password"
        )

        # Set user profile parameters
        cls.user1.profile.show_on_leaderboard = True
        cls.user1.profile.save()
        cls.user2.profile.show_on_leaderboard = True
        cls.user2.profile.save()
        cls.user3.profile.show_on_leaderboard = (
            False  # Not shown on leaderboard
        )
        cls.user3.profile.save()

        cls.today = timezone.now().date()

        # Create daily scores
        DailyScore.objects.create(
            user=cls.user1,
            date=cls.today,
            score=850,
            guesses=2,
            time_taken=240,
            completed=True,
        )

        DailyScore.objects.create(
            user=cls.user2,
            date=cls.today,
            score=750,
            guesses=3,
            time_taken=300,
            completed=True,
        )

        DailyScore.objects.create(
            user=cls.user3,
            date=cls.today,
            score=900,  # Higher score, but won't show on leaderboard
            guesses=1,
            time_taken=200,
            completed=True,
        )

    def test_create_leaderboard(self):
        """Test leaderboard creation"""
        leaderboard = GlobalLeaderboard.objects.create(date=self.today)
        self.assertEqual(leaderboard.date, self.today)
        self.assertEqual(leaderboard.leaderboard_data, {})  # Initially empty

    def test_update_leaderboard(self):
        """Test leaderboard data update"""
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

        # Verify user not on leaderboard is not included
        usernames = [score["username"] for score in scores]
        self.assertNotIn("user3", usernames)

        # Verify total player count and average score
        self.assertEqual(leaderboard.leaderboard_data["total_players"], 3)
        # Average score: (850 + 750 + 900) / 3 = 833.33...
        self.assertAlmostEqual(
            leaderboard.leaderboard_data["average_score"], 833.33, places=2
        )

    def test_string_representation(self):
        """Test the string representation method"""
        leaderboard = GlobalLeaderboard.objects.create(date=self.today)
        self.assertEqual(str(leaderboard), f"Leaderboard for {self.today}")


class ConstraintsTest(TestCase):
    """Test model constraints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )
        self.today = timezone.now().date()

    def test_dailyscore_unique_constraint(self):
        """Test that a user can only have one score record per day"""
        # Create first score record
        DailyScore.objects.create(user=self.user, date=self.today, score=100)

        # Try to create another score record for the same day
        with self.assertRaises(Exception):  # Should raise IntegrityError
            DailyScore.objects.create(
                user=self.user, date=self.today, score=200
            )

    def test_articlecache_unique_constraint(self):
        """Test article ID uniqueness constraint"""
        # Create first article cache
        ArticleCache.objects.create(
            article_id="unique123", title="Article 1", content="Content"
        )

        # Try to create another cache with the same article_id
        with self.assertRaises(Exception):  # Should raise IntegrityError
            ArticleCache.objects.create(
                article_id="unique123",
                title="Article 2",
                content="Different content",
            )

    def test_dailyarticle_unique_constraint(self):
        """Test daily article date uniqueness constraint"""
        # Create article caches
        article1 = ArticleCache.objects.create(
            article_id="article1", title="Article 1", content="Content 1"
        )

        article2 = ArticleCache.objects.create(
            article_id="article2", title="Article 2", content="Content 2"
        )

        # Create first daily article
        DailyArticle.objects.create(date=self.today, article=article1)

        # Try to create another daily article for the same day
        with self.assertRaises(Exception):  # Should raise IntegrityError
            DailyArticle.objects.create(date=self.today, article=article2)


class SignalTest(TestCase):
    """Test signal handling"""

    def test_user_profile_signal(self):
        """Test the signal that automatically creates profiles when users are created"""
        # Create a new user
        user = User.objects.create_user(
            username="signaltest", email="signal@test.com", password="password"
        )

        # Verify that a profile was automatically created
        self.assertTrue(hasattr(user, "profile"))
        self.assertIsInstance(user.profile, UserProfile)

        # Verify default values in the profile
        self.assertEqual(user.profile.current_streak, 0)
        self.assertEqual(user.profile.max_streak, 0)


# Mock NLP functions for testing
def generate_scrambled_text(content):
    """Mock function to generate scrambled text"""
    words = content.lower().split()
    word_mapping = {}

    for word in words:
        if word not in word_mapping:
            # Simple scrambling: reverse the word
            word_mapping[word] = word[::-1]

    return word_mapping


def calculate_guess_score(guess, actual):
    """Mock function to calculate guess score and similarity"""
    # Simple similarity: percentage of matching characters
    guess = guess.lower()
    actual = actual.lower()

    # Count matching characters
    matching = sum(1 for a, b in zip(guess, actual) if a == b)
    similarity = matching / max(len(guess), len(actual))

    # Base score calculation
    score = int(similarity * 1000)

    return score, similarity


class GameStateModelTest(TestCase):
    """Test the GameState model"""

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

        # Create test article
        cls.test_article = ArticleCache.objects.create(
            article_id="12345",
            title="Test Article",
            content="This is the content of a test article.",
        )

        # Create test word mapping
        cls.test_word_mapping = {
            "content": "ntnetoc",
            "test": "ttse",
            "article": "elitacr",
            "is": "si",
            "the": "het",
            "of": "fo",
            "a": "a",
            "this": "hist"
        }

    def test_create_game_state(self):
        """Test game state creation"""
        game_state = GameState.objects.create(
            user=self.test_user,
            article=self.test_article,
            word_mapping=self.test_word_mapping,
            max_guesses=6,
            is_completed=False,
            best_score=0
        )

        self.assertEqual(game_state.user, self.test_user)
        self.assertEqual(game_state.article, self.test_article)
        self.assertEqual(game_state.word_mapping, self.test_word_mapping)
        self.assertEqual(game_state.max_guesses, 6)
        self.assertFalse(game_state.is_completed)
        self.assertEqual(game_state.best_score, 0)

    def test_string_representation(self):
        """Test the string representation method"""
        game_state = GameState.objects.create(
            user=self.test_user,
            article=self.test_article,
            word_mapping=self.test_word_mapping
        )
        self.assertEqual(str(game_state), f"Game for {self.test_user.username} on article {self.test_article.title}")

    def test_default_values(self):
        """Test that default values are set correctly"""
        game_state = GameState.objects.create(
            user=self.test_user,
            article=self.test_article,
            word_mapping=self.test_word_mapping
        )

        self.assertEqual(game_state.max_guesses, 6)  # Default value
        self.assertFalse(game_state.is_completed)    # Default value
        self.assertEqual(game_state.best_score, 0)   # Default value


class UserGuessModelTest(TestCase):
    """Test the UserGuess model"""

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

        # Create test article
        cls.test_article = ArticleCache.objects.create(
            article_id="12345",
            title="Test Article",
            content="This is the content of a test article.",
        )

        # Create test game state
        cls.test_game_state = GameState.objects.create(
            user=cls.test_user,
            article=cls.test_article,
            word_mapping={"test": "ttse"}
        )

    def test_create_user_guess(self):
        """Test user guess creation"""
        user_guess = UserGuess.objects.create(
            game_state=self.test_game_state,
            guess_text="My first guess",
            score=150,
            similarity_score=0.35
        )

        self.assertEqual(user_guess.game_state, self.test_game_state)
        self.assertEqual(user_guess.guess_text, "My first guess")
        self.assertEqual(user_guess.score, 150)
        self.assertEqual(user_guess.similarity_score, 0.35)

    def test_string_representation(self):
        """Test the string representation method"""
        user_guess = UserGuess.objects.create(
            game_state=self.test_game_state,
            guess_text="My guess"
        )
        self.assertEqual(str(user_guess), f"Guess 'My guess' for game {self.test_game_state.id}")

    def test_default_values(self):
        """Test that default values are set correctly"""
        user_guess = UserGuess.objects.create(
            game_state=self.test_game_state,
            guess_text="My guess"
        )

        self.assertEqual(user_guess.score, 0)             # Default value
        self.assertEqual(user_guess.similarity_score, 0.0)  # Default value


class UserDeviceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username="testuser_ud", password="password")

    def test_string_representation(self):
        device_with_name = UserDevice.objects.create(
            user=self.test_user,
            device_name="My Phone",
            device_type="mobile"
        )
        self.assertEqual(str(device_with_name), f"{self.test_user.username} - My Phone")

        device_without_name = UserDevice.objects.create(
            user=self.test_user,
            device_name="",
            device_type="tablet"
        )
        self.assertEqual(str(device_without_name), f"{self.test_user.username} - tablet")


class UserVerificationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create_user(username="testuser_uv", password="password")
        now = timezone.now()
        cls.expires_at = now + timedelta(days=1)

    def test_string_representation(self):
        verification_active = UserVerification.objects.create(
            user=self.test_user,
            purpose="email",
            is_used=False,
            expires_at=self.expires_at
        )
        self.assertEqual(str(verification_active), f"{self.test_user.username} - email - Active")

        verification_used = UserVerification.objects.create(
            user=self.test_user,
            purpose="password",
            is_used=True,
            expires_at=self.expires_at
        )
        self.assertEqual(str(verification_used), f"{self.test_user.username} - password - Used")
