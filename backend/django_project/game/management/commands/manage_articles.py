from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from ...models import ArticleCache, DailyArticle
from ...article_service import ArticleService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Manage Wikipedia articles (select daily, cleanup, etc.)'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--select-daily",
            action="store_true",
            help="Select a daily article if none exists for today",
        )

        parser.add_argument(
            "--select-for-days",
            type=int,
            help="Select daily articles for X days ahead",
        )

        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="Clean up old articles from cache",
        )

        parser.add_argument(
            "--max-age",
            type=int,
            default=30,
            help="Maximum age in days for articles to keep (default: 30)",
        )

        parser.add_argument(
            "--date",
            type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
            help="Specific date to select article for (format: YYYY-MM-DD)",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List all cached articles",
        )

        parser.add_argument(
            "--show",
            type=str,
            help="Show details of a single article by article ID",
        )

        parser.add_argument(
            "--clear-all",
            action="store_true",
            help="Clear ALL articles from cache (use with caution)",
        )

    def handle(self, *args, **options):
        if options["select_daily"]:
            self._select_daily_article(options["date"])

        if options["select_for_days"]:
            self._select_articles_for_days(options["select_for_days"])

        if options["cleanup"]:
            self._cleanup_old_articles(options["max_age"])

        if options["list"]:
            self._list_articles()

        if options["show"]:
            self._show_article(options["show"])

        if options["clear_all"]:
            self._clear_all_articles()

        if not any(
            [
                options["select_daily"],
                options["select_for_days"],
                options["cleanup"],
                options["list"],
                options["show"],
                options["clear_all"],
            ]
        ):
            self.stdout.write(
                self.style.WARNING(
                    "No action specified. Use --help for available options."
                )
            )

    def _select_daily_article(self, date=None):
        """Select a daily article for specified date or today"""
        if date is None:
            date = timezone.now().date()

        daily_article, created = ArticleService.ensure_daily_article(date)

        if created and daily_article:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully selected new daily article for {date}: {daily_article.article.title}"
                )
            )
        elif daily_article:
            self.stdout.write(
                self.style.WARNING(
                    f"Daily article already exists for {date}: {daily_article.article.title}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to select daily article for {date}. Check if there are articles in cache."
                )
            )

    def _select_articles_for_days(self, days_ahead):
        """Select daily articles for multiple days ahead"""
        today = timezone.now().date()
        selected_count = 0

        for i in range(days_ahead):
            target_date = today + timedelta(days=i)
            daily_article, created = ArticleService.ensure_daily_article(
                target_date
            )

            if created and daily_article:
                selected_count += 1
                self.stdout.write(
                    f"Selected article for {target_date}: {daily_article.article.title}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully selected {selected_count} new daily articles"
            )
        )

    def _cleanup_old_articles(self, max_age_days=30):
        """Clean up old articles from cache"""
        deleted_count = ArticleService.cleanup_old_articles(
            max_age_days, preserve_used=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully cleaned up {deleted_count} old articles from cache"
            )
        )

    def _list_articles(self):
        articles = ArticleCache.objects.all()
        if not articles.exists():
            self.stdout.write("No articles in cache.")
            return
        for article in articles:
            self.stdout.write(f"{article.article_id}: {article.title}")

    def _clear_all_articles(self):
        from django.db.models import ProtectedError

        confirm = input(
            "Are you sure you want to delete ALL cached articles? This action cannot be undone. (y/N): "
        )
        if confirm.lower() != "y":
            self.stdout.write(self.style.WARNING("Aborted."))
            return

        remove_daily = (
            input(
                "Also remove daily article entries that block deletion? (y/N): "
            ).lower()
            == "y"
        )

        if remove_daily:
            DailyArticle.objects.all().delete()
            self.stdout.write(
                self.style.WARNING("All DailyArticle entries removed.")
            )

        count = 0
        for article in ArticleCache.objects.all():
            try:
                article.delete()
                count += 1
            except ProtectedError:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped protected article: {article.title} ({article.article_id})"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(f"Deleted {count} articles from cache.")
        )

    def _show_article(self, article_id):
        try:
            article = ArticleCache.objects.get(article_id=article_id)
            self.stdout.write(self.style.SUCCESS(f"Title: {article.title}"))
            self.stdout.write(
                f"\nContent Preview:\n{article.content[:1000]}..."
            )
            self.stdout.write("\nImages:")
            for url in article.image_urls:
                self.stdout.write(f" - {url}")
        except ArticleCache.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Article with ID {article_id} not found.")
            )
