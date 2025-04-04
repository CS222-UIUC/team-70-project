import requests
from unittest.mock import patch, MagicMock
from django.test import TestCase
from game.wikipedia_service import WikipediaService


class WikipediaServiceTest(TestCase):
    """Test the WikipediaService class"""

    @patch("game.wikipedia_service.requests.get")
    def test_get_random_articles(self, mock_get):
        """Test fetching random articles"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": {
                "random": [
                    {"id": "12345", "title": "Test Article 1"},
                    {"id": "67890", "title": "Test Article 2"},
                ]
            }
        }
        mock_get.return_value = mock_response

        # Call the method
        articles = WikipediaService.get_random_articles(count=2)

        # Verify results
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]["id"], "12345")
        self.assertEqual(articles[0]["title"], "Test Article 1")
        self.assertEqual(articles[1]["id"], "67890")
        self.assertEqual(articles[1]["title"], "Test Article 2")

        # Verify API call parameters
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs["params"]["rnlimit"], 2)
        self.assertEqual(kwargs["params"]["rnnamespace"], 0)

    @patch("game.wikipedia_service.requests.get")
    def test_get_random_articles_error(self, mock_get):
        """Test error handling when fetching random articles"""
        # Setup mock to directly raise an exception
        mock_get.side_effect = requests.exceptions.RequestException(
            "API Error"
        )

        # Call the method
        articles = WikipediaService.get_random_articles(count=2)

        # Verify empty result on error
        self.assertEqual(articles, [])

    @patch("game.wikipedia_service.requests.get")
    @patch("game.wikipedia_service.WikipediaService._get_image_urls")
    def test_get_article_content(self, mock_get_images, mock_get):
        """Test fetching article content"""
        # Setup mock response for article content
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "parse": {
                "title": "Test Article",
                "text": {"*": "<p>This is a test article.</p>"},
                "images": ["image1.jpg", "icon.png"],
            }
        }
        mock_get.return_value = mock_response

        # Mock the image URL fetching method to avoid a second HTTP call
        mock_get_images.return_value = ["http://example.com/image1.jpg"]

        # Call the method
        article_data = WikipediaService.get_article_content(12345)

        # Verify results
        self.assertEqual(article_data["pageid"], "12345")
        self.assertEqual(article_data["title"], "Test Article")
        self.assertEqual(article_data["content"], "This is a test article.")
        self.assertEqual(
            article_data["images"], ["http://example.com/image1.jpg"]
        )

    @patch("game.wikipedia_service.requests.get")
    def test_get_article_content_error(self, mock_get):
        """Test error handling when fetching article content"""
        # Setup mock to directly raise an exception
        mock_get.side_effect = requests.exceptions.RequestException(
            "API Error"
        )

        # Call the method
        article_data = WikipediaService.get_article_content(12345)

        # Verify None result on error
        self.assertIsNone(article_data)

    def test_extract_text_from_html(self):
        """Test HTML to text extraction"""
        html = """
        <html>
            <body>
                <h2>Section Title</h2>
                <p>This is paragraph 1.</p>
                <p>This is paragraph 2 with a <a href="#">link</a>.</p>
                <ul>
                    <li>List item 1</li>
                    <li>List item 2</li>
                </ul>
                <script>alert('test');</script>
                <style>.test{color:red;}</style>
            </body>
        </html>
        """

        text = WikipediaService._extract_text_from_html(html)

        # Verify text extraction
        self.assertIn("SECTION TITLE", text)
        self.assertIn("This is paragraph 1.", text)
        # Note: The actual output might combine "a" with "link" without a space
        self.assertIn("This is paragraph 2 with", text)
        self.assertIn("link", text)
        self.assertIn("List item 1", text)
        self.assertIn("List item 2", text)
        self.assertNotIn("alert", text)  # Script content removed
        self.assertNotIn("color:red", text)  # Style content removed

    @patch("game.wikipedia_service.requests.get")
    def test_get_image_urls(self, mock_get):
        """Test getting image URLs"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "imageinfo": [{"url": "http://example.com/image1.jpg"}]
                    },
                    "456": {
                        "imageinfo": [{"url": "http://example.com/image2.jpg"}]
                    },
                }
            }
        }
        mock_get.return_value = mock_response

        # Call the method with image filenames that will pass the filter
        image_filenames = ["image1.jpg", "image2.jpg", "image3.gif"]
        urls = WikipediaService._get_image_urls(image_filenames)

        # Verify results
        self.assertEqual(len(urls), 2)
        self.assertIn("http://example.com/image1.jpg", urls)
        self.assertIn("http://example.com/image2.jpg", urls)

        # Verify API call
        args, kwargs = mock_get.call_args
        self.assertIn("File:image1.jpg", kwargs["params"]["titles"])
        self.assertIn("File:image2.jpg", kwargs["params"]["titles"])
        self.assertIn("File:image3.gif", kwargs["params"]["titles"])

    @patch("game.wikipedia_service.WikipediaService.get_random_articles")
    @patch("game.wikipedia_service.WikipediaService.get_article_content")
    @patch("game.wikipedia_service.ArticleService.get_article_by_id")
    @patch("game.wikipedia_service.ArticleService.cache_article")
    def test_fetch_and_cache_random_articles(
        self, mock_cache, mock_get_by_id, mock_get_content, mock_get_random
    ):
        """Test fetching and caching random articles"""
        # Setup mocks
        mock_get_random.return_value = [
            {"id": "12345", "title": "Test Article 1"},
            {"id": "67890", "title": "Test Article 2"},
        ]

        # First article already cached
        mock_article1 = MagicMock()
        mock_article1.article_id = "12345"
        mock_article1.title = "Test Article 1"

        mock_get_by_id.side_effect = [mock_article1, None]

        # Second article needs to be fetched and cached
        mock_get_content.return_value = {
            "pageid": "67890",
            "title": "Test Article 2",
            "content": "Content of article 2",
            "images": ["image2.jpg"],
        }

        mock_article2 = MagicMock()
        mock_article2.article_id = "67890"
        mock_article2.title = "Test Article 2"
        mock_cache.return_value = mock_article2

        # Call the method
        cached_articles = WikipediaService.fetch_and_cache_random_articles(
            count=2
        )

        # Verify results
        self.assertEqual(len(cached_articles), 2)
        mock_get_random.assert_called_once_with(2)
        mock_get_by_id.assert_any_call("12345")
        mock_get_by_id.assert_any_call("67890")
        mock_get_content.assert_called_once_with("67890")
        mock_cache.assert_called_once_with(
            article_id="67890",
            title="Test Article 2",
            content="Content of article 2",
            image_urls=["image2.jpg"],
        )

    @patch("game.wikipedia_service.requests.get")
    def test_get_image_urls_error(self, mock_get):
        """Test error handling when getting image URLs"""
        # Setup mock to raise exception
        mock_get.side_effect = requests.exceptions.RequestException(
            "API Error"
        )

        # Call the method
        urls = WikipediaService._get_image_urls(["image1.jpg", "image2.jpg"])

        # Verify empty result on error
        self.assertEqual(urls, [])

    @patch("game.wikipedia_service.requests.get")
    def test_get_image_urls_empty(self, mock_get):
        """Test getting image URLs with empty input"""
        # Call with empty list
        urls = WikipediaService._get_image_urls([])

        # Verify empty result and no API call
        self.assertEqual(urls, [])
        mock_get.assert_not_called()

    @patch("game.wikipedia_service.requests.get")
    def test_get_image_urls_no_images_found(self, mock_get):
        """Test getting image URLs when no images match the filter"""
        # Call with only icon files
        urls = WikipediaService._get_image_urls(["Icon-1.png", "Icon-2.png"])

        # Should return empty list without making API call
        self.assertEqual(urls, [])
        mock_get.assert_not_called()
