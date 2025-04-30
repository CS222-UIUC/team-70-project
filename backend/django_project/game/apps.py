from django.apps import AppConfig
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class GameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'game'

    def ready(self):
        # Skip during management commands
        import sys
        if 'runserver' in sys.argv or 'uwsgi' in sys.argv or 'asgi' in sys.argv:
            logger.info("Server starting - checking article cache and daily article")
            # Always ensure cache has articles FIRST
            self.ensure_article_cache()
            # Then try to set daily article
            self.ensure_daily_articles()

    def ensure_article_cache(self):
        # Import here to avoid circular imports
        from .models import ArticleCache
        from .new_wikipedia_service import NewWikipediaService

        min_cache_size = 5  # Minimum articles in cache
        cache_count = ArticleCache.objects.count()

        if cache_count < min_cache_size:
            logger.info(f"Article cache low ({cache_count}/{min_cache_size}) - fetching more articles")
            needed_count = min_cache_size - cache_count
            try:
                articles = NewWikipediaService.fetch_and_cache_random_articles(needed_count)
                logger.info(f"Added {len(articles)} new articles to cache")
            except Exception as e:
                logger.error(f"Failed to fetch articles: {e}")

    def ensure_daily_articles(self):
        # Import here to avoid circular imports
        from .article_service import ArticleService

        # Ensure today's article
        today = timezone.now().date()
        daily_article, created = ArticleService.ensure_daily_article(today)

        # Handle possible None return value
        if daily_article is None:
            logger.error(f"Failed to create daily article for {today}. No articles in cache.")
        elif created:
            logger.info(f"Created new daily article for {today}: {daily_article.article.title}")
        else:
            logger.info(f"Daily article already exists for {today}: {daily_article.article.title}")
