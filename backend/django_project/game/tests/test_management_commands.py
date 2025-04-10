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
        "game.wikipedia_service.WikipediaService.fetch_and_cache_random_articles"
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
