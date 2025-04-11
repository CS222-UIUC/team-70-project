from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import json
from ...models import GlobalLeaderboard, DailyScore


class Command(BaseCommand):
    help = 'Display global leaderboard data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=lambda s: datetime.strptime(s, '%Y-%m-%d').date(),
            help='Specific date to display leaderboard for (format: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Number of past days to display leaderboards for'
        )
        parser.add_argument(
            '--top',
            type=int,
            default=10,
            help='Display top N players'
        )
        parser.add_argument(
            '--format',
            choices=['table', 'json'],
            default='table',
            help='Output format: table or JSON'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Find a specific user\'s ranking'
        )

    def handle(self, *args, **options):
        date = options['date']
        days = options['days']
        top_n = options['top']
        output_format = options['format']
        username = options['username']

        if date:
            # Display leaderboard for specific date
            self._display_leaderboard_for_date(date, top_n, output_format, username)
        else:
            # Display leaderboards for past days
            today = timezone.now().date()
            for i in range(days):
                target_date = today - timedelta(days=i)
                self._display_leaderboard_for_date(target_date, top_n, output_format, username)
                # Add separator between days if showing multiple
                if i < days - 1:
                    self.stdout.write('\n' + '-' * 50 + '\n')

    def _display_leaderboard_for_date(self, date, top_n, output_format, username=None):
        """Display leaderboard for a specific date"""
        try:
            leaderboard = GlobalLeaderboard.objects.get(date=date)

            if not leaderboard.leaderboard_data:
                self.stdout.write(self.style.WARNING(f"Leaderboard data for {date} is empty"))
                return

            data = leaderboard.leaderboard_data
            scores = data.get('scores', [])

            if not scores:
                self.stdout.write(self.style.WARNING(f"Leaderboard for {date} doesn't contain any scores"))
                return

            # If username is specified, find that user's ranking
            if username:
                user_found = False
                for score in scores:
                    if score['username'].lower() == username.lower():
                        user_found = True
                        self.stdout.write(self.style.SUCCESS(
                            f"{date} - User {username} ranking: #{score['rank']}, "
                            f"Score: {score['score']}, Guesses: {score['guesses']}, "
                            f"Time: {self._format_time(score['time_taken'])}"
                        ))
                        break

                if not user_found:
                    self.stdout.write(self.style.WARNING(f"User {username} not found in leaderboard for {date}"))
                return

            # Limit number of scores to display
            displayed_scores = scores[:top_n]

            # Stats
            total_players = data.get('total_players', 0)
            avg_score = data.get('average_score', 0)

            # Output based on format
            if output_format == 'json':
                # JSON output
                output_data = {
                    'date': str(date),
                    'top_scores': displayed_scores,
                    'total_players': total_players,
                    'average_score': avg_score,
                    'last_updated': str(leaderboard.last_updated)
                }
                self.stdout.write(json.dumps(output_data, indent=2))
            else:
                # Table output using plain string formatting
                self.stdout.write(self.style.SUCCESS(f"\nLeaderboard for {date} - {total_players} total players - Average score: {avg_score:.1f}\n"))

                # Calculate column widths based on data
                rank_width = max(4, len(str(displayed_scores[-1]['rank'])) if displayed_scores else 4)
                username_width = max(8, max(len(score['username']) for score in displayed_scores) if displayed_scores else 8)
                score_width = max(5, max(len(str(score['score'])) for score in displayed_scores) if displayed_scores else 5)
                guesses_width = max(7, max(len(str(score['guesses'])) for score in displayed_scores) if displayed_scores else 7)
                time_width = max(4, max(len(self._format_time(score['time_taken'])) for score in displayed_scores) if displayed_scores else 4)

                # Create header row
                header = f"| {'Rank'.ljust(rank_width)} | {'Username'.ljust(username_width)} | {'Score'.ljust(score_width)} | {'Guesses'.ljust(guesses_width)} | {'Time'.ljust(time_width)} |"
                separator = f"+-{'-' * rank_width}-+-{'-' * username_width}-+-{'-' * score_width}-+-{'-' * guesses_width}-+-{'-' * time_width}-+"

                self.stdout.write(separator)
                self.stdout.write(header)
                self.stdout.write(separator)

                # Create data rows
                for score in displayed_scores:
                    row = f"| {str(score['rank']).ljust(rank_width)} | {score['username'].ljust(username_width)} | {str(score['score']).ljust(score_width)} | {str(score['guesses']).ljust(guesses_width)} | {self._format_time(score['time_taken']).ljust(time_width)} |"
                    self.stdout.write(row)

                self.stdout.write(separator)
                self.stdout.write(f"\nLast updated: {leaderboard.last_updated}")

        except GlobalLeaderboard.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No leaderboard found for {date}"))
            total_scores = DailyScore.objects.filter(date=date).count()
            if total_scores > 0:
                self.stdout.write(f"There are {total_scores} score records for this date, but the leaderboard hasn't been updated. Run 'python manage.py update_leaderboard --date={date}' to update it.")
            else:
                self.stdout.write("No score records found for this date.")

    def _format_time(self, seconds):
        """Format seconds into readable time format"""
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
