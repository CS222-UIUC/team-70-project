from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
import datetime
from unittest.mock import patch, MagicMock

from game.models import ArticleCache


class FetchWikipediaArticlesCommandTest(TestCase):
    """Test the fetch_wikipedia_articles management command"""

    @patch(
        "game.new_wikipedia_service.NewWikipediaService.fetch_and_cache_random_articles"
    )
    def test_fetch_articles(self, mock_fetch):
        """Test that the command fetches articles from Wikipedia API"""
        mock_articles = [
            MagicMock(title="Test Article 1"),
            MagicMock(title="Test Article 2"),
        ]
        mock_fetch.return_value = mock_articles

        out = StringIO()
        call_command("fetch_wikipedia_articles", count=2, stdout=out)

        mock_fetch.assert_called_once_with(2)
        output = out.getvalue()
        self.assertIn("Successfully fetched and cached 2 articles", output)
        self.assertIn("Test Article 1", output)
        self.assertIn("Test Article 2", output)

    @patch(
        "game.wikipedia_service.WikipediaService.fetch_and_cache_random_articles"
    )
    def test_fetch_articles_old(self, mock_fetch):
        """Test the --old flag uses the original Wikipedia service"""
        mock_articles = [
            MagicMock(title="Old Article 1"),
            MagicMock(title="Old Article 2"),
        ]
        mock_fetch.return_value = mock_articles

        out = StringIO()
        call_command("fetch_wikipedia_articles", count=2, old=True, stdout=out)

        mock_fetch.assert_called_once_with(2)
        output = out.getvalue()
        self.assertIn("Successfully fetched and cached 2 articles", output)
        self.assertIn("Old Article 1", output)
        self.assertIn("Old Article 2", output)


class ManageArticlesCommandTest(TestCase):
    """Combined tests for the manage_articles management command"""

    def setUp(self):
        self.article1 = ArticleCache.objects.create(
            article_id="article1",
            title="Test Article 1",
            content="This is the content of test article 1.",
        )
        self.article2 = ArticleCache.objects.create(
            article_id="article2",
            title="Test Article 2",
            content="This is the content of test article 2.",
        )
        self.today = timezone.now().date()

    @patch("game.article_service.ArticleService.ensure_daily_article")
    def test_select_daily_article(self, mock_ensure_daily_article):
        mock_article = MagicMock()
        mock_article.article.title = "Test Article 1"
        mock_ensure_daily_article.return_value = (mock_article, True)

        out = StringIO()
        call_command("manage_articles", select_daily=True, stdout=out)

        self.assertIn(
            "Successfully selected new daily article", out.getvalue()
        )

    @patch("game.article_service.ArticleService.ensure_daily_article")
    def test_select_daily_article_with_date(self, mock_ensure_daily_article):
        mock_article = MagicMock()
        mock_article.article.title = "Test Article 1"
        mock_ensure_daily_article.return_value = (mock_article, True)
        future_date = self.today + datetime.timedelta(days=1)

        out = StringIO()
        call_command(
            "manage_articles",
            select_daily=True,
            date=future_date.isoformat(),
            stdout=out,
        )

        mock_ensure_daily_article.assert_called_once_with(
            future_date.isoformat()
        )
        self.assertIn(
            "Successfully selected new daily article", out.getvalue()
        )

    def test_list_articles(self):
        out = StringIO()
        call_command("manage_articles", list=True, stdout=out)
        output = out.getvalue()
        self.assertIn("Test Article 1", output)
        self.assertIn("Test Article 2", output)

    @patch("game.article_service.ArticleService.cleanup_old_articles")
    def test_cleanup_old_articles(self, mock_cleanup):
        mock_cleanup.return_value = 3
        out = StringIO()
        call_command("manage_articles", cleanup=True, max_age=30, stdout=out)
        mock_cleanup.assert_called_once_with(30, preserve_used=True)
        self.assertIn("Successfully cleaned up 3 old articles", out.getvalue())

    @patch("game.article_service.ArticleService.cleanup_old_articles")
    def test_cleanup_with_max_age(self, mock_cleanup):
        mock_cleanup.return_value = 5
        out = StringIO()
        call_command("manage_articles", cleanup=True, max_age=60, stdout=out)
        mock_cleanup.assert_called_once_with(60, preserve_used=True)
        self.assertIn("Successfully cleaned up 5 old articles", out.getvalue())

    @patch("game.article_service.ArticleService.ensure_daily_article")
    def test_select_for_days(self, mock_ensure_daily_article):
        mock_article = MagicMock()
        mock_article.article.title = "Test Article"
        mock_ensure_daily_article.return_value = (mock_article, True)

        out = StringIO()
        call_command("manage_articles", select_for_days=3, stdout=out)

        self.assertEqual(mock_ensure_daily_article.call_count, 3)
        self.assertIn(
            "Successfully selected 3 new daily articles", out.getvalue()
        )

    @patch("game.article_service.ArticleService.ensure_daily_article")
    def test_select_for_days_multiple(self, mock_ensure_daily_article):
        mock_daily_article1 = MagicMock()
        mock_daily_article1.article = self.article1
        mock_daily_article2 = MagicMock()
        mock_daily_article2.article = self.article2
        mock_ensure_daily_article.side_effect = [
            (mock_daily_article1, True),
            (mock_daily_article2, True),
            (mock_daily_article1, True),
        ]

        out = StringIO()
        call_command("manage_articles", select_for_days=3, stdout=out)

        self.assertEqual(mock_ensure_daily_article.call_count, 3)
        self.assertIn(
            "Successfully selected 3 new daily articles", out.getvalue()
        )

    def test_show_article(self):
        out = StringIO()
        call_command("manage_articles", show="article1", stdout=out)
        output = out.getvalue()
        self.assertIn("Test Article 1", output)
        self.assertIn("Content Preview", output)

    def test_show_article_existing(self):
        out = StringIO()
        call_command("manage_articles", show="article1", stdout=out)
        output = out.getvalue()
        self.assertIn("Test Article 1", output)
        self.assertIn("This is the content of test article 1", output)

    def test_show_article_nonexistent(self):
        out = StringIO()
        call_command("manage_articles", show="nonexistent", stdout=out)
        self.assertIn("Article with ID nonexistent not found", out.getvalue())

    def test_no_action_specified(self):
        out = StringIO()
        call_command("manage_articles", stdout=out)
        self.assertIn("No action specified", out.getvalue())

    @patch("builtins.input", return_value="n")
    def test_clear_all_aborted(self, mock_input):
        initial_count = ArticleCache.objects.count()
        out = StringIO()
        call_command("manage_articles", clear_all=True, stdout=out)
        self.assertEqual(ArticleCache.objects.count(), initial_count)
        self.assertIn("Aborted", out.getvalue())

    def test_select_daily_article_failure(self):
        """Test the case when selecting a daily article fails"""
        with patch("game.article_service.ArticleService.ensure_daily_article") as mock_ensure_daily_article:
            mock_ensure_daily_article.return_value = (None, False)

            out = StringIO()
            call_command("manage_articles", select_daily=True, stdout=out)

            self.assertIn("Failed to select daily article", out.getvalue())

    def test_list_articles_empty_cache(self):
        """Test listing articles when the cache is empty"""
        with patch("game.models.ArticleCache.objects") as mock_objects:
            # Mock ArticleCache.objects.all() to return an empty queryset
            mock_objects.all.return_value = MagicMock()
            mock_objects.all.return_value.exists.return_value = False

            out = StringIO()
            call_command("manage_articles", list=True, stdout=out)

            self.assertIn("No articles in cache", out.getvalue())

    def test_clear_all_confirmed_with_daily(self):
        """Test confirming to clear all articles and also removing daily article entries"""
        with patch("builtins.input", side_effect=["y", "y"]):
            with patch("game.models.DailyArticle.objects.all") as mock_daily_all:
                with patch("game.models.ArticleCache.objects.all") as mock_article_all:
                    # Setup mock for DailyArticle.objects.all().delete()
                    mock_daily_queryset = MagicMock()
                    mock_daily_all.return_value = mock_daily_queryset

                    # Setup ArticleCache objects
                    mock_article1 = MagicMock()
                    mock_article1.title = "Article 1"
                    mock_article1.article_id = "id1"

                    mock_article2 = MagicMock()
                    mock_article2.title = "Article 2"
                    mock_article2.article_id = "id2"

                    # Return the list of mock articles when iterating over queryset
                    mock_article_all.return_value = [mock_article1, mock_article2]

                    # Execute command
                    out = StringIO()
                    call_command("manage_articles", clear_all=True, stdout=out)

                    # Verify the daily articles queryset's delete was called
                    mock_daily_queryset.delete.assert_called_once()

                    # Verify each article's delete method was called
                    mock_article1.delete.assert_called_once()
                    mock_article2.delete.assert_called_once()

                    # Verify output messages
                    self.assertIn("All DailyArticle entries removed", out.getvalue())
                    self.assertIn("Deleted 2 articles from cache", out.getvalue())

    def test_clear_all_confirmed_without_daily(self):
        """Test confirming to clear all articles but not removing daily article entries"""
        with patch("builtins.input", side_effect=["y", "n"]):
            with patch("game.models.DailyArticle.objects.all") as mock_daily_all:
                with patch("game.models.ArticleCache.objects.all") as mock_article_all:
                    # Setup mock for DailyArticle.objects.all().delete()
                    mock_daily_queryset = MagicMock()
                    mock_daily_all.return_value = mock_daily_queryset

                    # Setup ArticleCache objects
                    mock_article1 = MagicMock()
                    mock_article1.title = "Article 1"
                    mock_article1.article_id = "id1"

                    mock_article2 = MagicMock()
                    mock_article2.title = "Article 2"
                    mock_article2.article_id = "id2"

                    # Return the list of mock articles when iterating over queryset
                    mock_article_all.return_value = [mock_article1, mock_article2]

                    # Execute command
                    out = StringIO()
                    call_command("manage_articles", clear_all=True, stdout=out)

                    # Verify daily articles queryset's delete was NOT called
                    mock_daily_queryset.delete.assert_not_called()

                    # Verify each article's delete method was called
                    mock_article1.delete.assert_called_once()
                    mock_article2.delete.assert_called_once()

                    # Verify output message
                    self.assertIn("Deleted 2 articles from cache", out.getvalue())

    def test_clear_all_protected_error(self):
        """Test handling ProtectedError when deleting articles"""
        from django.db.models import ProtectedError

        with patch("builtins.input", side_effect=["y", "n"]):
            with patch("game.models.DailyArticle.objects.all") as mock_daily_all:
                with patch("game.models.ArticleCache.objects.all") as mock_article_all:
                    # Setup mock for DailyArticle.objects.all()
                    mock_daily_queryset = MagicMock()
                    mock_daily_all.return_value = mock_daily_queryset

                    # Setup ArticleCache objects
                    mock_article1 = MagicMock()
                    mock_article1.title = "Article 1"
                    mock_article1.article_id = "id1"

                    # This article will raise ProtectedError
                    mock_article2 = MagicMock()
                    mock_article2.title = "Protected Article"
                    mock_article2.article_id = "protected_id"
                    mock_article2.delete.side_effect = ProtectedError("Protected", None)

                    # Return the list of mock articles when iterating over queryset
                    mock_article_all.return_value = [mock_article1, mock_article2]

                    # Execute command
                    out = StringIO()
                    call_command("manage_articles", clear_all=True, stdout=out)

                    # Verify daily articles queryset's delete was NOT called
                    mock_daily_queryset.delete.assert_not_called()

                    # Verify regular article's delete method was called
                    mock_article1.delete.assert_called_once()

                    # Verify output contains warning about protected article
                    self.assertIn("Skipped protected article", out.getvalue())
                    self.assertIn("Protected Article", out.getvalue())
                    self.assertIn("protected_id", out.getvalue())
                    self.assertIn("Deleted 1 articles from cache", out.getvalue())

    def test_select_daily_article_existing(self):
        """Test selecting a daily article when one already exists for the date"""
        # Create an article in the cache
        article = ArticleCache.objects.create(
            article_id="existing_article",
            title="Existing Article",
            content="Content"
        )

        # Create a daily article for today
        today = timezone.now().date()
        daily_article = MagicMock()
        daily_article.article = article

        with patch("game.article_service.ArticleService.ensure_daily_article") as mock_ensure:
            # Return that the article exists but wasn't created
            mock_ensure.return_value = (daily_article, False)

            out = StringIO()
            call_command("manage_articles", select_daily=True, stdout=out)

            self.assertIn("already exists", out.getvalue())
            self.assertIn("Existing Article", out.getvalue())

    def test_show_article_with_images(self):
        """Test showing article details with image URLs"""
        # Create an article with image URLs
        article = ArticleCache.objects.create(
            article_id="image_article",
            title="Article With Images",
            content="Content with images",
            image_urls=["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
        )

        out = StringIO()
        call_command("manage_articles", show="image_article", stdout=out)

        output = out.getvalue()
        self.assertIn("Article With Images", output)
        self.assertIn("Images:", output)
        self.assertIn("http://example.com/image1.jpg", output)
        self.assertIn("http://example.com/image2.jpg", output)
