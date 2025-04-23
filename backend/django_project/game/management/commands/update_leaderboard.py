from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from ...models import GlobalLeaderboard, DailyScore

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update global leaderboard for specific dates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
            help='Specific date to update leaderboard for (format: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of past days to update leaderboards for'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if leaderboard was recently updated'
        )

    def handle(self, *args, **options):
        if options['date']:
            self._update_leaderboard_for_date(options['date'], options['force'])
        else:
            self._update_leaderboards_for_past_days(options['days'], options['force'])

    def _update_leaderboard_for_date(self, date, force=False):
        """Update leaderboard for a specific date"""
        # Check if there are scores for this date
        if not DailyScore.objects.filter(date=date).exists():
            self.stdout.write(self.style.WARNING(f"No scores found for {date}"))
            return False

        # Get or create leaderboard
        leaderboard, created = GlobalLeaderboard.objects.get_or_create(date=date)

        # Check if update is needed
        if not force and not created and timezone.now() - leaderboard.last_updated < timedelta(hours=1):
            self.stdout.write(f"Leaderboard for {date} was updated recently. Use --force to update anyway.")
            return False

        # Update leaderboard
        leaderboard.update_leaderboard()
        self.stdout.write(self.style.SUCCESS(f"Successfully updated leaderboard for {date}"))
        return True

    def _update_leaderboards_for_past_days(self, days, force=False):
        """Update leaderboards for the past X days"""
        today = timezone.now().date()
        updated_count = 0

        for i in range(days):
            target_date = today - timedelta(days=i)
            if self._update_leaderboard_for_date(target_date, force):
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} leaderboards"))
