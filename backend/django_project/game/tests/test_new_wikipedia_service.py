from unittest import TestCase
from unittest.mock import patch, MagicMock

from game.new_wikipedia_service import NewWikipediaService


class NewWikipediaServiceTest(TestCase):

    @patch("game.new_wikipedia_service.requests.get")
    def test_get_random_articles(self, mock_get):
        mock_get.return_value.json.return_value = {
            "query": {
                "random": [
                    {"id": 123, "title": "Test Article 1"},
                    {"id": 456, "title": "Test Article 2"},
                ]
            }
        }
        mock_get.return_value.raise_for_status = MagicMock()

        articles = NewWikipediaService.get_random_articles(count=2)
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]["title"], "Test Article 1")

    @patch("game.new_wikipedia_service.requests.get")
    @patch("game.new_wikipedia_service.NewWikipediaService._get_image_urls", return_value=["http://image.com/img1.jpg"])
    @patch("game.new_wikipedia_service.wikipediaapi.Wikipedia.page")
    def test_get_article_content(self, mock_page, mock_image_urls, mock_get):
        page_mock = MagicMock()
        page_mock.exists.return_value = True
        page_mock.text = "This is article content"
        mock_page.return_value = page_mock

        mock_get.return_value.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "pageid": 123,
                        "title": "Test Title",
                        "categories": [{"title": "Some Category"}]
                    }
                }
            }
        }
        mock_get.return_value.raise_for_status = MagicMock()

        article = NewWikipediaService.get_article_content(pageid=123)
        self.assertIsNotNone(article)
        self.assertEqual(article["title"], "Test Title")
        self.assertIn("content", article)
        self.assertEqual(article["images"], ["http://image.com/img1.jpg"])

    @patch("game.new_wikipedia_service.NewWikipediaService.get_article_content")
    @patch("game.new_wikipedia_service.NewWikipediaService.get_random_articles")
    @patch("game.new_wikipedia_service.ArticleService.get_article_by_id", return_value=None)
    @patch("game.new_wikipedia_service.ArticleService.cache_article")
    def test_fetch_and_cache_random_articles(
        self, mock_cache, mock_get_by_id, mock_get_random, mock_get_content
    ):
        mock_get_random.return_value = [
            {"id": 1, "title": "A"},
            {"id": 2, "title": "B"}
        ]
        mock_get_content.side_effect = [
            {
                "pageid": "1",
                "title": "A",
                "content": "Some content A",
                "images": [],
                "is_stub": False
            },
            None  # simulate failed fetch for B
        ]
        mock_cache.return_value = MagicMock(title="A")

        results = NewWikipediaService.fetch_and_cache_random_articles(count=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "A")
