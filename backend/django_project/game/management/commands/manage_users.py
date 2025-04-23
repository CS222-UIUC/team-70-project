from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import logging
from django.contrib.auth.models import User
from ...models import UserProfile, DailyScore

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage user data and statistics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-streak',
            action='store_true',
            help='Reset streak for users who missed yesterday'
        )
        parser.add_argument(
            '--recalculate-stats',
            action='store_true',
            help='Recalculate stats for all users'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Specify username for operations that target a single user'
        )
        parser.add_argument(
            '--inactive-days',
            type=int,
            default=30,
            help='Number of days of inactivity to consider a user inactive'
        )
        parser.add_argument(
            '--list-inactive',
            action='store_true',
            help='List inactive users'
        )

    def handle(self, *args, **options):
        if options['reset_streak']:
            self._reset_streaks()

        if options['recalculate_stats']:
            if options['user']:
                self._recalculate_user_stats(options['user'])
            else:
                self._recalculate_all_stats()

        if options['list_inactive']:
            self._list_inactive_users(options['inactive_days'])

    def _reset_streaks(self):
        """Reset streaks for users who didn't play yesterday"""
        yesterday = timezone.now().date() - timedelta(days=1)
        active_users = DailyScore.objects.filter(date=yesterday).values_list('user_id', flat=True)

        # Find users who didn't play yesterday
        profiles = UserProfile.objects.exclude(user_id__in=active_users)
        count = 0

        for profile in profiles:
            if profile.current_streak > 0:
                profile.current_streak = 0
                profile.save()
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Reset streaks for {count} users"))

    def _recalculate_user_stats(self, username):
        """Recalculate stats for a specific user"""
        try:
            user = User.objects.get(username=username)
            profile = user.profile

            # Recalculate total games and wins
            profile.total_games_played = DailyScore.objects.filter(user=user).count()
            profile.total_wins = DailyScore.objects.filter(user=user, completed=True).count()

            # Recalculate average score
            profile.calculate_average_score()

            # Update best score
            best_score = DailyScore.objects.filter(user=user).order_by('-score').first()
            if best_score:
                profile.best_score = best_score.score

            profile.save()
            self.stdout.write(self.style.SUCCESS(f"Recalculated stats for user: {username}"))

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User not found: {username}"))

    def _recalculate_all_stats(self):
        """Recalculate stats for all users"""
        count = 0
        for user in User.objects.all():
            try:
                self._recalculate_user_stats(user.username)
                count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error recalculating stats for {user.username}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Recalculated stats for {count} users"))

    def _list_inactive_users(self, days):
        """List users who haven't played in X days"""
        threshold_date = timezone.now().date() - timedelta(days=days)

        # Get users who have played recently
        active_user_ids = DailyScore.objects.filter(date__gt=threshold_date).values_list('user_id', flat=True).distinct()

        # Find inactive users
        inactive_users = User.objects.exclude(id__in=active_user_ids)

        if inactive_users.exists():
            self.stdout.write(f"Users inactive for more than {days} days:")
            for user in inactive_users:
                last_played = user.profile.last_played_date or "Never played"
                self.stdout.write(f"- {user.username} (Last played: {last_played})")
            self.stdout.write(self.style.SUCCESS(f"Found {inactive_users.count()} inactive users"))
        else:
            self.stdout.write(self.style.SUCCESS(f"No users inactive for more than {days} days"))
