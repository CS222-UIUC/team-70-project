import requests  # Need to import requests to mock its exceptions
from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY

from game.new_wikipedia_service import NewWikipediaService

from game.article_service import ArticleService


class MockArticleCache:
    """A simple mock for ArticleCache to use as return value for patches."""

    def __init__(self, title="Mock Title", article_id="mock_id"):
        self.title = title
        self.article_id = str(article_id)  # Ensure article_id is a string

    def __str__(self):
        return self.title


class NewWikipediaServiceTest(TestCase):
    """Test suite for the NewWikipediaService."""

    @patch("game.new_wikipedia_service.requests.get")
    def test_get_random_articles_success(self, mock_get):
        """Test successful fetching of random articles."""
        mock_get.return_value.json.return_value = {
            "query": {
                "random": [
                    {"id": 123, "title": "Test Article 1"},
                    {"id": 456, "title": "Test Article 2"},
                ]
            }
        }
        # Mock the method to raise for status correctly
        mock_get.return_value.raise_for_status = MagicMock()

        articles = NewWikipediaService.get_random_articles(count=2)
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]["title"], "Test Article 1")
        # Verify the API call parameters
        mock_get.assert_called_once_with(ANY, params=ANY)
        call_params = mock_get.call_args[1]['params']
        self.assertEqual(call_params['action'], 'query')
        self.assertEqual(call_params['list'], 'random')
        # The service requests double the count to account for filtering stubs
        self.assertEqual(call_params['rnlimit'], 4)
        self.assertEqual(call_params['rnnamespace'], 0)

    @patch("game.new_wikipedia_service.requests.get")
    def test_get_random_articles_request_exception(self, mock_get):
        """Test error handling for RequestException in get_random_articles (covers lines 58-60)."""
        mock_get.side_effect = requests.exceptions.RequestException("Network Error")

        articles = NewWikipediaService.get_random_articles(count=2)
        self.assertEqual(articles, [])  # Should return empty list on error

    @patch("game.new_wikipedia_service.requests.get")
    def test_get_random_articles_malformed_response(self, mock_get):
        """Test handling of unexpected API response format in get_random_articles."""
        # Simulate a response missing 'query' or 'random'
        mock_get.return_value.json.return_value = {"error": "Some API error"}
        mock_get.return_value.raise_for_status = MagicMock()

        articles = NewWikipediaService.get_random_articles(count=2)
        self.assertEqual(articles, [])  # Should return empty list

    @patch("game.new_wikipedia_service.requests.get")
    @patch("game.new_wikipedia_service.NewWikipediaService._get_image_urls", return_value=["http://image.com/img1.jpg"])
    @patch("game.new_wikipedia_service.wikipediaapi.Wikipedia")  # Mock the wikipediaapi class
    def test_get_article_content_success(self, mock_wikipedia_class, mock_image_urls, mock_get):
        """Test successful fetching of article content."""
        # --- Mocking wikipediaapi ---
        # Mock the instance returned by Wikipedia(...)
        mock_wiki_instance = MagicMock()
        # Mock the page object returned by wiki_instance.page(...)
        mock_page_object = MagicMock()
        mock_page_object.exists.return_value = True
        # FIX: Make content longer than 1000 characters to avoid false stub detection
        mock_page_object.text = "This is non-stub article content. " * 100
        mock_wiki_instance.page.return_value = mock_page_object
        # Make the Wikipedia class return our mocked instance
        mock_wikipedia_class.return_value = mock_wiki_instance
        # ---------------------------

        # Mock the requests.get call for page info
        mock_get.return_value.json.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "pageid": 123,
                        "title": "Test Title",
                        # FIX: Ensure no stub category is present
                        "categories": [{"title": "Category:Valid Articles"}]
                    }
                }
            }
        }
        mock_get.return_value.raise_for_status = MagicMock()

        # Create an instance of the service to call the method
        # service_instance = NewWikipediaService() # No longer needed as method is classmethod
        article = NewWikipediaService.get_article_content(pageid=123)

        self.assertIsNotNone(article)
        self.assertEqual(article["title"], "Test Title")
        # Verify the longer content is used
        self.assertTrue(len(article["content"]) > 1000)
        self.assertEqual(article["images"], ["http://image.com/img1.jpg"])
        # FIX: This assertion should now pass because content is long and no stub category
        self.assertFalse(article["is_stub"], "Article should not be detected as stub")
        mock_image_urls.assert_called_once_with("Test Title")

    @patch("game.new_wikipedia_service.requests.get")
    def test_get_article_content_request_exception(self, mock_get):
        """Test RequestException during page info fetch in get_article_content (covers lines 127-129)."""
        # Simulate error on the first API call (fetching page info)
        mock_get.side_effect = requests.exceptions.RequestException("Network Error")

        article = NewWikipediaService.get_article_content(pageid=123)
        self.assertIsNone(article)

    @patch("game.new_wikipedia_service.requests.get")
    def test_get_article_content_malformed_response(self, mock_get):
        """Test malformed API response for page info in get_article_content (covers lines 100-101)."""
        # Simulate a response missing 'query' or 'pages'
        mock_get.return_value.json.return_value = {"unexpected": "data"}
        mock_get.return_value.raise_for_status = MagicMock()

        article = NewWikipediaService.get_article_content(pageid=123)
        self.assertIsNone(article)

    @patch("game.new_wikipedia_service.requests.get")
    @patch("game.new_wikipedia_service.wikipediaapi.Wikipedia")
    def test_get_article_content_page_does_not_exist(self, mock_wikipedia_class, mock_get):
        """Test handling when wikipediaapi says page doesn't exist (covers lines 110-111)."""
        # Mock the page info call to succeed
        mock_get.return_value.json.return_value = {
            "query": {"pages": {"123": {"pageid": 123, "title": "NonExistent Title"}}}
        }
        mock_get.return_value.raise_for_status = MagicMock()

        # Mock wikipediaapi to say the page doesn't exist
        mock_wiki_instance = MagicMock()
        mock_page_object = MagicMock()
        mock_page_object.exists.return_value = False  # The crucial part
        mock_wiki_instance.page.return_value = mock_page_object
        mock_wikipedia_class.return_value = mock_wiki_instance

        article = NewWikipediaService.get_article_content(pageid=123)
        self.assertIsNone(article)

    @patch("game.new_wikipedia_service.requests.get")
    @patch("game.new_wikipedia_service.wikipediaapi.Wikipedia")
    def test_get_article_content_general_exception(self, mock_wikipedia_class, mock_get):
        """Test general exception handling in get_article_content (covers lines 127-129)."""
        # Mock the page info call to succeed
        mock_get.return_value.json.return_value = {
            "query": {"pages": {"123": {"pageid": 123, "title": "Test Title"}}}
        }
        mock_get.return_value.raise_for_status = MagicMock()

        # Mock wikipediaapi page access to raise a generic exception
        mock_wiki_instance = MagicMock()
        mock_wiki_instance.page.side_effect = Exception("Something went wrong")
        mock_wikipedia_class.return_value = mock_wiki_instance

        article = NewWikipediaService.get_article_content(pageid=123)
        self.assertIsNone(article)

    # --- Tests for _is_article_stub ---

    def test_is_article_stub_by_category(self):
        """Test stub detection via category."""
        page_data = {"categories": [{"title": "Category:Physics stubs"}]}
        content = "This is a long article content..." * 100  # Long content
        self.assertTrue(NewWikipediaService._is_article_stub(page_data, content))

    def test_is_article_stub_by_pattern(self):
        """Test stub detection via template patterns."""
        page_data = {"categories": []}  # No stub category
        content_stub = "Article info... {{Physics-stub}} More info."  # Long enough content
        content_stub_caps = "Article info... {{STUB}} More info."  # Long enough content
        content_no_stub = "Article info... {{Infobox}} More info." * 100
        self.assertTrue(NewWikipediaService._is_article_stub(page_data, content_stub * 50))
        self.assertTrue(NewWikipediaService._is_article_stub(page_data, content_stub_caps * 50))
        self.assertFalse(NewWikipediaService._is_article_stub(page_data, content_no_stub))

    def test_is_article_stub_by_length(self):
        """Test stub detection via content length (covers line 159)."""
        page_data = {"categories": []}  # No stub category
        short_content = "Very short."  # No stub pattern
        long_content = "This is much longer content that should not be considered a stub based on length alone. " * 50
        boundary_content_short = "a" * 999
        boundary_content_long = "a" * 1000

        self.assertTrue(NewWikipediaService._is_article_stub(page_data, short_content))
        self.assertTrue(NewWikipediaService._is_article_stub(page_data, boundary_content_short))
        self.assertFalse(NewWikipediaService._is_article_stub(page_data, long_content))
        self.assertFalse(NewWikipediaService._is_article_stub(page_data, boundary_content_long))

    def test_is_article_stub_not_stub(self):
        """Test case where article is definitely not a stub."""
        page_data = {"categories": [{"title": "Category:Physics"}]}  # Non-stub category
        content = "This is a full article about physics..." * 100  # Long content, no pattern
        self.assertFalse(NewWikipediaService._is_article_stub(page_data, content))

    # --- Tests for _get_image_urls ---

    @patch("game.new_wikipedia_service.requests.get")
    def test_get_image_urls_success(self, mock_get):
        """Test successful fetching of image URLs."""
        # Mock response for the first call (getting image titles)
        mock_response_titles = MagicMock()
        mock_response_titles.json.return_value = {
            "query": {
                "pages": {
                    "page1": {
                        "pageid": 1, "title": "Some Article Title",
                        "images": [
                            {"title": "File:Image1.jpg"},
                            {"title": "File:Icon-something.png"},  # Should be filtered
                            {"title": "File:Image2.png"},
                            {"title": "File:Data.txt"}  # Should be filtered
                        ]
                    }
                }
            }
        }
        mock_response_titles.raise_for_status = MagicMock()

        # Mock response for the second call (getting image URLs)
        mock_response_urls = MagicMock()
        mock_response_urls.json.return_value = {
            "query": {
                "pages": {
                    # API uses arbitrary page IDs here, not filenames
                    "img1": {"pageid": 101, "title": "File:Image1.jpg", "imageinfo": [{"url": "http://example.com/Image1.jpg"}]},
                    "img2": {"pageid": 102, "title": "File:Image2.png", "imageinfo": [{"url": "http://example.com/Image2.png"}]},
                }
            }
        }
        mock_response_urls.raise_for_status = MagicMock()

        # Configure mock_get to return different responses for calls
        mock_get.side_effect = [mock_response_titles, mock_response_urls]

        urls = NewWikipediaService._get_image_urls("Some Article Title")

        self.assertEqual(len(urls), 2)
        self.assertIn("http://example.com/Image1.jpg", urls)
        self.assertIn("http://example.com/Image2.png", urls)

        # Check API call parameters
        first_call_params = mock_get.call_args_list[0][1]['params']
        second_call_params = mock_get.call_args_list[1][1]['params']

        self.assertEqual(first_call_params['prop'], 'images')
        self.assertEqual(first_call_params['titles'], 'Some Article Title')

        self.assertEqual(second_call_params['prop'], 'imageinfo')
        # The titles parameter should contain the filtered image titles
        expected_titles = "File:Image1.jpg|File:Image2.png"
        self.assertEqual(second_call_params['titles'], expected_titles)

    @patch("game.new_wikipedia_service.requests.get")
    def test_get_image_urls_request_exception(self, mock_get):
        """Test RequestException in _get_image_urls (covers lines 224-226)."""
        # Simulate error on the first API call (fetching image titles)
        mock_get.side_effect = requests.exceptions.RequestException("Network Error")

        urls = NewWikipediaService._get_image_urls("Some Title")
        self.assertEqual(urls, [])  # Should return empty list on error

    @patch("game.new_wikipedia_service.requests.get")
    def test_get_image_urls_request_exception_info(self, mock_get):
        """Test RequestException when fetching image info in _get_image_urls (covers lines 224-226)."""
        # Mock response for the first call (getting image titles) - SUCCESS
        mock_response_titles = MagicMock()
        mock_response_titles.json.return_value = {
            "query": {
                "pages": {"page1": {"pageid": 1, "title": "Some Title", "images": [{"title": "File:Image1.jpg"}]}}
            }
        }
        mock_response_titles.raise_for_status = MagicMock()

        # Configure mock_get to succeed first, then fail on second call
        mock_get.side_effect = [
            mock_response_titles,
            requests.exceptions.RequestException("Network Error on URL fetch")
        ]

        urls = NewWikipediaService._get_image_urls("Some Title")
        self.assertEqual(urls, [])  # Should return empty list on error

    def test_get_image_urls_no_valid_images_found(self):
        """Test _get_image_urls when API returns no valid image titles."""
        # Mock response for the first call (getting image titles)
        mock_response_titles = MagicMock()
        mock_response_titles.json.return_value = {
            "query": {
                "pages": {
                    "page1": {
                        "pageid": 1, "title": "Some Article Title",
                        "images": [
                            {"title": "File:Icon-something.png"},  # Should be filtered
                            {"title": "File:Data.txt"}  # Should be filtered
                        ]
                    }
                }
            }
        }
        mock_response_titles.raise_for_status = MagicMock()

        # Patch requests.get just for this test
        with patch("game.new_wikipedia_service.requests.get", return_value=mock_response_titles) as mock_get_local:
            urls = NewWikipediaService._get_image_urls("Some Article Title")
            self.assertEqual(urls, [])
            # Only one call should be made, as there are no valid titles to get URLs for
            mock_get_local.assert_called_once()

    # --- Tests for fetch_and_cache_random_articles ---

    # FIX: Update the mock cache decorator return value to match article 'B'
    @patch("game.new_wikipedia_service.ArticleService.cache_article", return_value=MockArticleCache(title="B", article_id="2"))
    @patch("game.new_wikipedia_service.ArticleService.get_article_by_id", return_value=None)  # Assume nothing is cached initially
    @patch("game.new_wikipedia_service.NewWikipediaService.get_article_content")
    @patch("game.new_wikipedia_service.NewWikipediaService.get_random_articles")
    def test_fetch_and_cache_random_articles_success(
        self, mock_get_random, mock_get_content, mock_get_by_id, mock_cache
    ):
        """Test successful fetching and caching, including logging (covers line 258)."""
        mock_get_random.return_value = [
            {"id": 1, "title": "A"},  # Will attempt to fetch, but get_content returns None
            {"id": 2, "title": "B"}  # Will be fetched and cached
        ]

        # FIX: Use side_effect for get_article_content to handle multiple calls
        mock_get_content.side_effect = [
            # Result for get_article_content(1) -> Simulate failure
            None,
            # Result for get_article_content(2) -> Simulate success
            {
                "pageid": "2",
                "title": "B",
                "content": "Some content B",
                "images": [],
                "is_stub": False
            }
        ]

        # Call the method requesting 1 article.
        # It needs to process until 1 valid (non-stub, fetchable) article is found.
        # Since A fails, it will process B to meet the count=1 requirement.
        results = NewWikipediaService.fetch_and_cache_random_articles(count=1)

        self.assertEqual(len(results), 1)
        # FIX: Assert the correct title based on the cached article (B)
        self.assertEqual(results[0].title, "B")
        self.assertEqual(results[0].article_id, "2")
        # -----------------------------------------------------------------
        mock_get_random.assert_called_once_with(2)  # count * 2
        # Should check cache for both 1 and 2 because mock_get_by_id returns None
        mock_get_by_id.assert_any_call('1')
        mock_get_by_id.assert_any_call('2')
        # FIX: Assert get_content was called for both IDs
        self.assertEqual(mock_get_content.call_count, 2)
        mock_get_content.assert_any_call(1)
        mock_get_content.assert_any_call(2)
        # --------------------------------------------------
        # Should cache article 2 (since article 1's content fetch returned None)
        mock_cache.assert_called_once_with(
            article_id='2',
            title='B',
            content='Some content B',
            image_urls=[]
        )

    @patch("game.new_wikipedia_service.ArticleService.cache_article")
    @patch("game.new_wikipedia_service.ArticleService.get_article_by_id", return_value=None)  # Assume nothing is cached
    @patch("game.new_wikipedia_service.NewWikipediaService.get_article_content")
    @patch("game.new_wikipedia_service.NewWikipediaService.get_random_articles")
    def test_fetch_and_cache_skips_failed_content_fetch(
        self, mock_get_random, mock_get_content, mock_get_by_id, mock_cache
    ):
        """Test that fetch_and_cache skips articles if get_content fails (covers lines 252-253)."""
        mock_get_random.return_value = [
            {"id": 1, "title": "A"},  # get_content will fail for this one
            {"id": 2, "title": "B"}  # get_content will succeed for this one
        ]
        # Simulate get_content failing for id 1 and succeeding for id 2
        mock_get_content.side_effect = [
            None,  # Fails for id 1
            {"pageid": "2", "title": "B", "content": "Content B", "images": [], "is_stub": False}
        ]
        # Mock cache_article to return a mock object when called for article B
        mock_cache.return_value = MockArticleCache(title="B", article_id="2")

        # Request 2 articles, but only B should be cached
        results = NewWikipediaService.fetch_and_cache_random_articles(count=2)

        self.assertEqual(len(results), 1)  # Only article B was successfully processed and cached
        self.assertEqual(results[0].title, "B")
        mock_get_random.assert_called_once_with(4)  # count * 2
        # Should attempt to get content for both
        self.assertEqual(mock_get_content.call_count, 2)
        mock_get_content.assert_any_call(1)
        mock_get_content.assert_any_call(2)
        # cache_article should only be called once (for article B)
        mock_cache.assert_called_once_with(
            article_id='2', title='B', content='Content B', image_urls=[]
        )

    @patch("game.new_wikipedia_service.ArticleService.cache_article")
    @patch("game.new_wikipedia_service.ArticleService.get_article_by_id", return_value=None)  # Assume nothing cached
    @patch("game.new_wikipedia_service.NewWikipediaService.get_article_content")
    @patch("game.new_wikipedia_service.NewWikipediaService.get_random_articles")
    def test_fetch_and_cache_skips_stub(
        self, mock_get_random, mock_get_content, mock_get_by_id, mock_cache
    ):
        """Test that fetch_and_cache skips stub articles."""
        mock_get_random.return_value = [
            {"id": 1, "title": "Stubby"},  # This will be marked as a stub
            {"id": 2, "title": "NotAStub"}  # This will be cached
        ]
        # Simulate get_content returning stub=True for id 1 and stub=False for id 2
        mock_get_content.side_effect = [
            {"pageid": "1", "title": "Stubby", "content": "{{stub}}", "images": [], "is_stub": True},
            {"pageid": "2", "title": "NotAStub", "content": "Real content", "images": [], "is_stub": False}
        ]
        mock_cache.return_value = MockArticleCache(title="NotAStub", article_id="2")

        # Request 2 articles, but only NotAStub should be cached
        results = NewWikipediaService.fetch_and_cache_random_articles(count=2)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "NotAStub")
        mock_get_random.assert_called_once_with(4)  # count * 2
        # Should attempt to get content for both
        self.assertEqual(mock_get_content.call_count, 2)
        mock_get_content.assert_any_call(1)
        mock_get_content.assert_any_call(2)
        # cache_article should only be called once (for article 2, since 1 was a stub)
        mock_cache.assert_called_once_with(
            article_id='2', title='NotAStub', content='Real content', image_urls=[]
        )

    @patch("game.new_wikipedia_service.ArticleService.cache_article")  # Need to patch cache even if not called
    @patch("game.new_wikipedia_service.ArticleService.get_article_by_id")  # Mock this specifically
    @patch("game.new_wikipedia_service.NewWikipediaService.get_article_content")
    @patch("game.new_wikipedia_service.NewWikipediaService.get_random_articles")
    def test_fetch_and_cache_uses_existing(
        self, mock_get_random, mock_get_content, mock_get_by_id, mock_cache  # mock_cache is patched but not used
    ):
        """Test that fetch_and_cache uses already cached articles."""
        mock_get_random.return_value = [
            {"id": 1, "title": "AlreadyCached"},
            {"id": 2, "title": "NeedsFetching"}  # Needs to provide enough for count=1
        ]
        # Simulate article 1 already being in cache, article 2 not
        mock_existing_article = MockArticleCache(title="AlreadyCached", article_id="1")
        mock_get_by_id.side_effect = [
            mock_existing_article,  # Return existing for ID '1'
            None                 # Return None for ID '2'
        ]
        # Mock get_content to succeed for article 2
        mock_get_content.return_value = {
            "pageid": "2", "title": "NeedsFetching", "content": "Content", "images": [], "is_stub": False
        }

        # Request 1 article
        results = NewWikipediaService.fetch_and_cache_random_articles(count=1)

        # It should find article 1 in the cache and return immediately
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], mock_existing_article)  # Should be the existing one
        mock_get_random.assert_called_once_with(2)  # count * 2
        # Should only check cache for ID '1' before returning
        mock_get_by_id.assert_called_once_with('1')
        # get_article_content should NOT be called because article 1 was found in cache
        mock_get_content.assert_not_called()
        # cache_article should NOT be called
        mock_cache.assert_not_called()
