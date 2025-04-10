from django.core.management.base import BaseCommand
import logging
from ...wikipedia_service import WikipediaService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Fetch and cache random Wikipedia articles"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Number of articles to fetch (default: 5)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        self.stdout.write(f"Fetching {count} random Wikipedia articles...")

        cached_articles = WikipediaService.fetch_and_cache_random_articles(
            count
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully fetched and cached {len(cached_articles)} articles:"
            )
        )

        for article in cached_articles:
            self.stdout.write(f"- {article.title}")
