# game/tests/test_testusers.py

from io import StringIO
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

from game.models import UserProfile, DailyScore


# Helper Mock Class for QuerySet behavior
class MockQuerySet:
    def __init__(self, items):
        self._items = items

    def count(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def exists(self):
        return len(self._items) > 0


class ManageTestUsersCommandTest(TestCase):
    """Test cases for the manage_test_users management command."""

    def setUp(self):
        """Set up test data."""
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='password123'
        )

    def call_command(self, *args, **kwargs):
        """Helper method to call the management command and capture output."""
        out = StringIO()
        err = StringIO()
        call_command('manage_test_users', *args, stdout=out, stderr=err, **kwargs)
        return out.getvalue()

    def test_command_with_no_options(self):
        """Test the command with no options displays help."""
        try:
            output = self.call_command()
            self.assertEqual(output.strip(), "")
        except Exception as e:
            self.fail(f"Command raised an unexpected exception: {e}")

    @patch('builtins.input', return_value='y')
    def test_add_test_users(self, mock_input):
        """Test adding test users successfully."""
        self.assertEqual(User.objects.count(), 1)

        output = self.call_command(add=3)

        self.assertIn("Successfully created 3 test users", output)
        self.assertEqual(User.objects.count(), 4)
        self.assertTrue(User.objects.filter(username='test_user_1').exists())
        self.assertTrue(User.objects.filter(username='test_user_2').exists())
        self.assertTrue(User.objects.filter(username='test_user_3').exists())

        for i in range(1, 4):
            user = User.objects.get(username=f'test_user_{i}')
            profile = user.profile
            self.assertGreaterEqual(profile.max_streak, profile.current_streak)
            self.assertGreaterEqual(profile.total_games_played, 10)
            self.assertGreaterEqual(profile.total_wins, 5)
            self.assertLessEqual(profile.total_wins, profile.total_games_played)
            self.assertGreater(DailyScore.objects.filter(user=user).count(), 0)

    @patch('builtins.input', return_value='y')
    @patch('django.contrib.auth.models.User.objects.create_user')
    def test_add_test_users_creation_error(self, mock_create_user, mock_input):
        """Test error handling during user creation (covers lines 97-98)."""
        expected_username_1 = "test_user_1"
        expected_username_2 = "test_user_2"
        expected_password_1 = 'testpass123'

        def side_effect(*args, **kwargs):
            username = kwargs.get('username') or args[0]
            if username == expected_username_1:
                mock_user = MagicMock(spec=User)
                mock_user.username = username
                mock_user.profile = MagicMock(spec=UserProfile)
                return mock_user
            elif username == expected_username_2:
                raise Exception("Database connection lost")
            else:
                raise ValueError(f"Unexpected call to create_user with username: {username}")

        mock_create_user.side_effect = side_effect

        with patch('game.management.commands.manage_test_users.Command._generate_random_data') as mock_gen_data:
            output = self.call_command(add=2, password=expected_password_1)
            mock_gen_data.assert_called_once()

        self.assertIn("Error creating user: Database connection lost", output)
        self.assertIn("Successfully created 1 test users", output)
        self.assertEqual(mock_create_user.call_count, 2)
        self.assertEqual(User.objects.filter(username__startswith="test_user_").count(), 0)

    @patch('builtins.input', return_value='y')
    def test_add_duplicate_test_users(self, mock_input):
        """Test adding test users when some already exist."""
        self.call_command(add=2)
        output = self.call_command(add=3)

        self.assertIn("User 'test_user_1' already exists, skipping", output)
        self.assertIn("User 'test_user_2' already exists, skipping", output)
        self.assertIn("Created user: test_user_3", output)
        self.assertIn("Successfully created 1 test users", output)
        self.assertEqual(User.objects.count(), 4)

    def test_list_test_users_when_none_exist(self):
        """Test listing test users when none are present."""
        output = self.call_command(list=True)
        self.assertIn("No test users found", output)

    def test_list_test_users(self):
        """Test listing existing test users."""
        self.call_command(add=2)
        output = self.call_command(list=True)

        self.assertIn("Found 2 test users", output)
        self.assertIn("test_user_1", output)
        self.assertIn("test_user_2", output)
        self.assertIn("Username", output)
        self.assertIn("Email", output)
        self.assertIn("Streak", output)

    @patch('builtins.input', return_value='y')
    def test_delete_test_users(self, mock_input):
        """Test deleting all test users."""
        self.call_command(add=3)
        self.assertEqual(User.objects.count(), 4)

        output = self.call_command(delete=True)

        self.assertIn("Successfully deleted 3 test users", output)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'regularuser')

    @patch('builtins.input', return_value='n')
    def test_delete_test_users_cancelled(self, mock_input):
        """Test cancelling the deletion of test users."""
        self.call_command(add=2)
        self.assertEqual(User.objects.count(), 3)

        output = self.call_command(delete=True)

        self.assertIn("Operation cancelled", output)
        self.assertEqual(User.objects.count(), 3)

    @patch('builtins.input', return_value='y')
    def test_reset_test_users(self, mock_input):
        """Test resetting data for test users."""
        self.call_command(add=2)
        user1 = User.objects.get(username='test_user_1')
        initial_streak = user1.profile.current_streak
        initial_scores_count = DailyScore.objects.filter(user=user1).count()

        output = self.call_command(reset=True)

        self.assertIn("Successfully reset data for 2 test users", output)
        user1.refresh_from_db()
        new_scores_count = DailyScore.objects.filter(user=user1).count()
        self.assertGreater(new_scores_count, 0)

    @patch('builtins.input', return_value='y')
    def test_reset_test_users_hits_continue(self, mock_input):
        """Test that resetting twice runs without error, potentially hitting the 'continue' for existing scores (line 120)."""
        self.call_command(add=1)
        user1 = User.objects.get(username='test_user_1')
        initial_score_count = DailyScore.objects.filter(user=user1).count()
        self.assertGreater(initial_score_count, 0)

        output_reset1 = self.call_command(reset=True)
        self.assertIn("Successfully reset data for 1 test users", output_reset1)
        count_after_reset1 = DailyScore.objects.filter(user=user1).count()
        self.assertGreater(count_after_reset1, 0)

        output_reset2 = self.call_command(reset=True)
        self.assertIn("Successfully reset data for 1 test users", output_reset2)
        count_after_reset2 = DailyScore.objects.filter(user=user1).count()
        self.assertGreater(count_after_reset2, 0)

    @patch('builtins.input', return_value='y')
    @patch('game.management.commands.manage_test_users.Command._generate_random_data')
    def test_reset_test_users_error(self, mock_generate_data, mock_input):
        """Test error handling during user data reset (covers lines 226-227)."""
        self.call_command(add=2)

        mock_generate_data.side_effect = [
            Exception("Failed to generate random data"),
            None
        ]

        output = self.call_command(reset=True)

        self.assertIn("Error resetting data for user test_user_1: Failed to generate random data", output)
        self.assertIn("Reset data for user: test_user_2", output)

    @patch('builtins.input', return_value='n')
    def test_reset_test_users_cancelled(self, mock_input):
        """Test cancelling the reset of test users."""
        self.call_command(add=2)
        user1 = User.objects.get(username='test_user_1')
        initial_streak = user1.profile.current_streak

        output = self.call_command(reset=True)

        self.assertIn("Operation cancelled", output)
        user1.refresh_from_db()
        self.assertEqual(user1.profile.current_streak, initial_streak)

    def test_set_custom_password(self):
        """Test adding test users with a custom password."""
        output = self.call_command(add=1, password='custom123')
        self.assertIn("Successfully created 1 test users", output)
        user = User.objects.get(username='test_user_1')
        self.assertTrue(user.check_password('custom123'))

    @patch('builtins.input', return_value='y')
    def test_reset_with_password(self, mock_input):
        """Test resetting test users and setting a new password."""
        self.call_command(add=1)
        user = User.objects.get(username='test_user_1')
        self.assertTrue(user.check_password('testpass123'))

        output = self.call_command(reset=True, password='newpass123')
        self.assertIn("Successfully reset data for 1 test users", output)

        user.refresh_from_db()
        self.assertTrue(user.check_password('newpass123'))

    def test_no_test_users_to_delete(self):
        """Test attempting to delete when no test users exist."""
        output = self.call_command(delete=True)
        self.assertIn("No test users found", output)

    def test_no_test_users_to_reset(self):
        """Test attempting to reset when no test users exist."""
        output = self.call_command(reset=True)
        self.assertIn("No test users found", output)
