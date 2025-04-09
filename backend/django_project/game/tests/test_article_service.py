from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from game.models import ArticleCache, DailyArticle
from game.article_service import ArticleService


class ArticleServiceTest(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.article1 = ArticleCache.objects.create(
            article_id="a1", title="Article 1", content="Some content"
        )

        # Manually override the retrieved_date of article2 to simulate an old
        # article
        self.article2 = ArticleCache.objects.create(
            article_id="a2", title="Article 2", content="Other content"
        )
        self.article2.retrieved_date = timezone.now() - timedelta(days=90)
        self.article2.save(update_fields=["retrieved_date"])

    def test_get_article_by_id_found(self):
        """Should retrieve an article by its ID."""
        article = ArticleService.get_article_by_id("a1")
        self.assertIsNotNone(article)
        self.assertEqual(article.title, "Article 1")

    def test_get_article_by_id_not_found(self):
        """Should return None if the article ID does not exist."""
        article = ArticleService.get_article_by_id("missing")
        self.assertIsNone(article)

    def test_cache_article_create_and_update(self):
        """Should create a new article and update it if it already exists."""
        new_article = ArticleService.cache_article(
            "new", "New Title", "New content"
        )
        self.assertEqual(new_article.article_id, "new")

        updated = ArticleService.cache_article(
            "new", "Updated Title", "Updated content"
        )
        self.assertEqual(updated.title, "Updated Title")

    def test_get_random_cached_article(self):
        """Should return a random article from the cache."""
        article = ArticleService.get_random_cached_article()
        self.assertIn(article, [self.article1, self.article2])

    def test_get_random_cached_article_empty(self):
        """Should return None if the cache is empty."""
        ArticleCache.objects.all().delete()
        article = ArticleService.get_random_cached_article()
        self.assertIsNone(article)

    def test_get_daily_article_found(self):
        """Should retrieve a daily article by date."""
        DailyArticle.objects.create(date=self.today, article=self.article1)
        daily = ArticleService.get_daily_article(self.today)
        self.assertEqual(daily.article.article_id, "a1")

    def test_get_daily_article_not_found(self):
        """Should return None if no daily article is found."""
        result = ArticleService.get_daily_article(self.today)
        self.assertIsNone(result)

    def test_set_daily_article_create_and_update(self):
        """Should create and then update a daily article for a specific date."""
        daily = ArticleService.set_daily_article(self.article1, self.today)
        self.assertEqual(daily.article, self.article1)

        updated = ArticleService.set_daily_article(self.article2, self.today)
        self.assertEqual(updated.article, self.article2)

    def test_ensure_daily_article_when_exists(self):
        """Should return existing daily article without creating a new one."""
        DailyArticle.objects.create(date=self.today, article=self.article1)
        article, created = ArticleService.ensure_daily_article(self.today)
        self.assertFalse(created)
        self.assertEqual(article.article, self.article1)

    def test_ensure_daily_article_when_missing(self):
        """Should create a new daily article if one doesn't exist."""
        article, created = ArticleService.ensure_daily_article(self.today)
        self.assertTrue(created)
        self.assertIsNotNone(article.article)

    def test_ensure_daily_article_when_no_articles(self):
        """Should fail gracefully if no cached articles exist."""
        ArticleCache.objects.all().delete()
        article, created = ArticleService.ensure_daily_article(self.today)
        self.assertIsNone(article)
        self.assertFalse(created)

    def test_get_articles_by_age(self):
        """Should return only articles older than the specified age."""
        result = ArticleService.get_articles_by_age(max_age_days=60)
        self.assertIn(self.article2, result)
        self.assertNotIn(self.article1, result)

    def test_cleanup_old_articles_preserve_false(self):
        """Should delete old articles when preserve_used=False."""
        deleted_count = ArticleService.cleanup_old_articles(
            max_age_days=60, preserve_used=False
        )
        self.assertEqual(deleted_count, 1)
        self.assertFalse(ArticleCache.objects.filter(article_id="a2").exists())

    def test_cleanup_old_articles_preserve_true(self):
        """Should not delete articles used as daily articles when preserve_used=True."""
        DailyArticle.objects.create(date=self.today, article=self.article2)
        deleted_count = ArticleService.cleanup_old_articles(
            max_age_days=60, preserve_used=True
        )
        self.assertEqual(deleted_count, 0)
        self.assertTrue(ArticleCache.objects.filter(article_id="a2").exists())


def test_get_daily_article_with_none_date(self):
    """Explicitly test get_daily_article(None) to cover the None path"""
    DailyArticle.objects.create(date=self.today, article=self.article1)
    result = ArticleService.get_daily_article(None)
    self.assertIsNotNone(result)
    self.assertEqual(result.date, self.today)


def test_set_daily_article_with_none_date(self):
    """Explicitly test set_daily_article(..., None) to cover default date"""
    result = ArticleService.set_daily_article(self.article1, None)
    self.assertEqual(result.date, self.today)


def test_ensure_daily_article_with_none_date(self):
    """Explicitly call ensure_daily_article(None) to trigger date defaulting"""
    DailyArticle.objects.all().delete()
    article, created = ArticleService.ensure_daily_article(None)
    self.assertTrue(created)
    self.assertEqual(article.date, self.today)
