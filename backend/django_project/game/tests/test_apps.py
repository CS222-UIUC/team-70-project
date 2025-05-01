import pytest
import sys
from django.apps import apps
from game.apps import GameConfig
from unittest.mock import patch, MagicMock
from django.test import TestCase


class GameAppTests(TestCase):

    @patch("game.models.ArticleCache.objects.count", return_value=0)
    @patch("game.new_wikipedia_service.NewWikipediaService.fetch_and_cache_random_articles", return_value=["mock1", "mock2"])
    @patch("game.article_service.ArticleService.ensure_daily_article")
    def test_ready_runs_all_logic(self, mock_daily_article, mock_fetch_articles, mock_count):
        sys.argv = ["manage.py", "runserver"]
        mock_article = MagicMock()
        mock_article.article.title = "MockTitle"
        mock_daily_article.return_value = (mock_article, True)
        app_config = apps.get_app_config("game")
        app_config.ready()
        self.assertTrue(mock_fetch_articles.called)
        self.assertTrue(mock_daily_article.called)

    @patch("game.models.ArticleCache.objects.count", return_value=0)
    @patch("game.new_wikipedia_service.NewWikipediaService.fetch_and_cache_random_articles", side_effect=Exception("Mock Failure"))
    @patch("game.article_service.ArticleService.ensure_daily_article")
    def test_article_cache_fetch_fails(self, mock_daily_article, mock_fetch_articles, mock_count):
        sys.argv = ["manage.py", "runserver"]
        mock_article = MagicMock()
        mock_article.article.title = "MockTitle"
        mock_daily_article.return_value = (mock_article, True)
        app_config = apps.get_app_config("game")
        app_config.ready()
        self.assertTrue(mock_fetch_articles.called)
        self.assertTrue(mock_daily_article.called)

    @patch("game.models.ArticleCache.objects.count", return_value=0)
    @patch("game.new_wikipedia_service.NewWikipediaService.fetch_and_cache_random_articles", return_value=["mock1", "mock2"])
    @patch("game.article_service.ArticleService.ensure_daily_article")
    def test_no_article_in_cache(self, mock_daily_article, mock_fetch_articles, mock_count):
        sys.argv = ["manage.py", "runserver"]
        mock_daily_article.return_value = (None, True)
        app_config = apps.get_app_config("game")
        app_config.ready()
        self.assertTrue(mock_fetch_articles.called)
        self.assertTrue(mock_daily_article.called)

    @patch("game.models.ArticleCache.objects.count", return_value=0)
    @patch("game.new_wikipedia_service.NewWikipediaService.fetch_and_cache_random_articles", return_value=["mock1", "mock2"])
    @patch("game.article_service.ArticleService.ensure_daily_article")
    def test_daily_article_already_set(self, mock_daily_article, mock_fetch_articles, mock_count):
        sys.argv = ["manage.py", "runserver"]
        mock_article = MagicMock()
        mock_article.article.title = "MockTitle"
        mock_daily_article.return_value = (mock_article, False)
        app_config = apps.get_app_config("game")
        app_config.ready()
        self.assertTrue(mock_fetch_articles.called)
        self.assertTrue(mock_daily_article.called)
