from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class DailyArticleMiddleware:
    """Middleware to ensure daily articles are created when days change"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.last_check_date = None  # Track the last date we checked

    def __call__(self, request):
        today = timezone.now().date()

        # Only check once per day
        if self.last_check_date != today:
            self.last_check_date = today
            self.ensure_daily_article()

        return self.get_response(request)

    def ensure_daily_article(self):
        # Import here to avoid circular imports
        from .article_service import ArticleService

        # Create a new daily article if none exists for today
        daily_article, created = ArticleService.ensure_daily_article()

        # Handle possible None return value
        if daily_article is None:
            logger.error("Middleware failed to create daily article. No articles in cache.")
        elif created:
            logger.info(f"Middleware created new daily article: {daily_article.article.title}")
