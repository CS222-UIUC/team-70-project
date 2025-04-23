from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging
import random
from django.contrib.auth.models import User
from ...models import UserProfile, DailyScore

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create and manage test users for development and testing'

    def add_arguments(self, parser):
        # Parameters for adding test users
        parser.add_argument(
            '--add',
            type=int,
            help='Add specified number of test users'
        )
        # Parameters for deleting test users
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete all test users (username starting with test_user_)'
        )
        # Parameters for listing test users
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all test users'
        )
        # Parameters for resetting test user data
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all test user data with new random values'
        )
        # Parameters for setting test user passwords
        parser.add_argument(
            '--password',
            type=str,
            help='Set password for test users (default: testpass123)'
        )

    def handle(self, *args, **options):
        # Add test users
        if options['add']:
            self._add_test_users(
                options['add'],
                options['password'] or 'testpass123'
            )

        # Delete test users
        if options['delete']:
            self._delete_test_users()

        # List test users
        if options['list']:
            self._list_test_users()

        # Reset test user data
        if options['reset']:
            self._reset_test_users(options['password'])

        # If no options were provided, display help
        if not any([options['add'], options['delete'], options['list'], options['reset']]):
            self.print_help('manage.py', 'manage_test_users')

    def _add_test_users(self, count, password):
        """Add specified number of test users with random data"""
        successful = 0

        for i in range(1, count + 1):
            username = f"test_user_{i}"
            email = f"test{i}@example.com"

            # Check if user already exists, skip if it does
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f"User '{username}' already exists, skipping"))
                continue

            # Create user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                successful += 1

                # Generate random data for the test user
                self._generate_random_data(user)

                self.stdout.write(f"Created user: {username}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating user: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully created {successful} test users"))

    def _generate_random_data(self, user):
        """Generate random data for a test user"""
        profile = user.profile
        profile.current_streak = random.randint(0, 10)
        profile.max_streak = max(profile.current_streak, random.randint(5, 15))
        profile.total_games_played = random.randint(10, 50)
        profile.total_wins = random.randint(5, profile.total_games_played)
        profile.average_score = random.randint(300, 800)
        profile.best_score = random.randint(800, 1000)
        profile.save()

        # Create random daily score records
        today = timezone.now().date()
        for day_offset in range(random.randint(5, 15)):
            game_date = today - timedelta(days=day_offset)

            # Check if a record for this date already exists
            if DailyScore.objects.filter(user=user, date=game_date).exists():
                continue

            completed = random.random() > 0.2  # 80% completion rate
            score = random.randint(300, 900) if completed else 0
            time_taken = random.randint(60, 300)
            guesses = random.randint(1, 6)

            DailyScore.objects.create(
                user=user,
                date=game_date,
                score=score,
                time_taken=time_taken,
                guesses=guesses,
                completed=completed,
                article_title=f"Test Article {day_offset}" if completed else "",
                hints_used=random.randint(0, 3)
            )

    def _delete_test_users(self):
        """Delete all test users (usernames starting with test_user_)"""
        # Find all test users
        test_users = User.objects.filter(username__startswith="test_user_")
        count = test_users.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No test users found"))
            return

        # Prompt for confirmation
        self.stdout.write(f"Found {count} test users. Are you sure you want to delete them? [y/N]")
        confirm = input().lower()

        if confirm not in ['y', 'yes']:
            self.stdout.write(self.style.WARNING("Operation cancelled"))
            return

        # Delete all test users and related data
        deleted_count = 0
        for user in test_users:
            username = user.username
            try:
                # Delete user (Django will handle foreign key relationships)
                user.delete()
                deleted_count += 1
                self.stdout.write(f"Deleted user: {username}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error deleting user {username}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} test users"))

    def _list_test_users(self):
        """List all test users"""
        test_users = User.objects.filter(username__startswith="test_user_").order_by('username')

        if not test_users.exists():
            self.stdout.write(self.style.SUCCESS("No test users found"))
            return

        self.stdout.write(f"Found {test_users.count()} test users:")
        self.stdout.write(f"{'ID':<5} {'Username':<15} {'Email':<25} {'Games':<10} {'Wins':<10} {'Streak':<8} {'Best':<8}")
        self.stdout.write("-" * 85)

        for user in test_users:
            profile = user.profile
            self.stdout.write(
                f"{user.id:<5} "
                f"{user.username:<15} "
                f"{user.email:<25} "
                f"{profile.total_games_played:<10} "
                f"{profile.total_wins:<10} "
                f"{profile.current_streak:<8} "
                f"{profile.best_score:<8}"
            )

    def _reset_test_users(self, password=None):
        """Reset data for all test users"""
        test_users = User.objects.filter(username__startswith="test_user_")
        count = test_users.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No test users found"))
            return

        # Prompt for confirmation
        self.stdout.write(f"Found {count} test users. Are you sure you want to reset their data? [y/N]")
        confirm = input().lower()

        if confirm not in ['y', 'yes']:
            self.stdout.write(self.style.WARNING("Operation cancelled"))
            return

        # Reset data for each test user
        for user in test_users:
            try:
                # Delete existing score records
                DailyScore.objects.filter(user=user).delete()

                # Update password if provided
                if password:
                    user.set_password(password)
                    user.save()

                # Generate new random data
                self._generate_random_data(user)

                self.stdout.write(f"Reset data for user: {user.username}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error resetting data for user {user.username}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully reset data for {count} test users"))
