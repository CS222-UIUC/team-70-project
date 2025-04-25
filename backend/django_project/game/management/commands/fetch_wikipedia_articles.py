from django.core.management.base import BaseCommand
import logging
from ...wikipedia_service import WikipediaService
from ...new_wikipedia_service import NewWikipediaService  # Import the new service

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
        parser.add_argument(
            "--old",
            action="store_true",
            help="Use the old Wikipedia service implementation instead of the new one",
        )

    def handle(self, *args, **options):
        count = options["count"]
        use_old_service = options["old"]

        self.stdout.write(f"Fetching {count} random Wikipedia articles...")

        # Select the appropriate service based on the --old flag
        if use_old_service:
            self.stdout.write("Using original Wikipedia service...")
            service = WikipediaService
        else:
            self.stdout.write("Using enhanced Wikipedia service (Wikipedia-API)...")
            service = NewWikipediaService

        # Use the selected service to fetch articles
        cached_articles = service.fetch_and_cache_random_articles(count)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully fetched and cached {len(cached_articles)} articles:"
            )
        )

        for article in cached_articles:
            self.stdout.write(f"- {article.title}")
