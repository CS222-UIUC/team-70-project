from django.utils import timezone
from datetime import timedelta
import logging
import random
from .models import ArticleCache, DailyArticle, GlobalLeaderboard

logger = logging.getLogger(__name__)

class ArticleService:
    """
    Service class for managing article-related database operations.
    This handles caching and retrieving articles, as well as managing daily article selection.
    """
    
    @staticmethod
    def get_article_by_id(article_id):
        """
        Get an article from cache by ID
        
        Args:
            article_id (str): Wikipedia article ID
            
        Returns:
            ArticleCache or None: The cached article if found
        """
        try:
            return ArticleCache.objects.get(article_id=article_id)
        except ArticleCache.DoesNotExist:
            logger.info(f"Article {article_id} not found in cache")
            return None
    
    @staticmethod
    def cache_article(article_id, title, content, image_urls=None):
        """
        Store or update an article in the cache
        
        Args:
            article_id (str): Wikipedia article ID
            title (str): Article title
            content (str): Article content
            image_urls (list): List of image URLs from the article
            
        Returns:
            ArticleCache: The created or updated article cache instance
        """
        if image_urls is None:
            image_urls = []
            
        article, created = ArticleCache.objects.update_or_create(
            article_id=article_id,
            defaults={
                'title': title,
                'content': content,
                'image_urls': image_urls,
            }
        )
        
        if created:
            logger.info(f"Cached new article: {title}")
        else:
            logger.info(f"Updated cached article: {title}")
            
        return article
    
    @staticmethod
    def get_random_cached_article():
        """
        Get a random article from the cache
        
        Returns:
            ArticleCache or None: A random article from the cache
        """
        article_count = ArticleCache.objects.count()
        if article_count == 0:
            return None
            
        random_index = random.randint(0, article_count - 1)
        return ArticleCache.objects.all()[random_index]
    
    @staticmethod
    def get_daily_article(date=None):
        """
        Get the article for a specific day
        
        Args:
            date (datetime.date, optional): The date to get the article for. 
                                           Defaults to today.
        
        Returns:
            DailyArticle or None: The daily article object
        """
        if date is None:
            date = timezone.now().date()
            
        try:
            return DailyArticle.objects.get(date=date)
        except DailyArticle.DoesNotExist:
            logger.info(f"No daily article set for {date}")
            return None
    
    @staticmethod
    def set_daily_article(article, date=None):
        """
        Set the article for a specific day
        
        Args:
            article (ArticleCache): The article to set for the day
            date (datetime.date, optional): The date to set the article for. 
                                           Defaults to today.
        
        Returns:
            DailyArticle: The created daily article object
        """
        if date is None:
            date = timezone.now().date()
            
        daily_article, created = DailyArticle.objects.update_or_create(
            date=date,
            defaults={'article': article}
        )
        
        if created:
            logger.info(f"Set new daily article for {date}: {article.title}")
        else:
            logger.info(f"Updated daily article for {date}: {article.title}")
            
        return daily_article
    
    @staticmethod
    def ensure_daily_article(date=None):
        """
        Ensure there is a daily article for the given date.
        If none exists, select a random article from cache.
        
        Args:
            date (datetime.date, optional): The date to ensure an article for. 
                                           Defaults to today.
        
        Returns:
            DailyArticle: The daily article object
            bool: Whether a new article was created
        """
        if date is None:
            date = timezone.now().date()
            
        # Check if daily article already exists
        daily_article = ArticleService.get_daily_article(date)
        if daily_article:
            return daily_article, False
            
        # Get a random article from cache
        random_article = ArticleService.get_random_cached_article()
        if not random_article:
            logger.error("No articles in cache to select for daily article")
            return None, False
            
        # Set it as daily article
        daily_article = ArticleService.set_daily_article(random_article, date)
        return daily_article, True
    
    @staticmethod
    def get_articles_by_age(max_age_days=30):
        """
        Get articles from cache by age (for cleanup)
        
        Args:
            max_age_days (int): Maximum age in days
            
        Returns:
            QuerySet: ArticleCache objects older than max_age_days
        """
        threshold_date = timezone.now() - timedelta(days=max_age_days)
        return ArticleCache.objects.filter(retrieved_date__lt=threshold_date)
    
    @staticmethod
    def cleanup_old_articles(max_age_days=30, preserve_used=True):
        """
        Clean up old articles from cache
        
        Args:
            max_age_days (int): Maximum age in days
            preserve_used (bool): Whether to preserve articles used in daily selection
            
        Returns:
            int: Number of articles deleted
        """
        # Get IDs of articles that have been used as daily articles
        if preserve_used:
            preserved_ids = DailyArticle.objects.values_list('article__id', flat=True)
        else:
            preserved_ids = []
            
        # Get old articles except preserved ones
        old_articles = ArticleService.get_articles_by_age(max_age_days)
        if preserved_ids:
            old_articles = old_articles.exclude(id__in=preserved_ids)
            
        # Get count and delete
        count = old_articles.count()
        old_articles.delete()
        
        logger.info(f"Cleaned up {count} old articles from cache")
        return count