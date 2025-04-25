import logging
import wikipediaapi
import requests
import re
from .article_service import ArticleService

logger = logging.getLogger(__name__)


class NewWikipediaService:
    """
    Enhanced Wikipedia service using the Wikipedia-API library.
    Provides more accurate and comprehensive content while maintaining
    a compatible interface with the original WikipediaService.
    """

    BASE_API_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self):
        """Initialize the Wikipedia API client"""
        self.wiki = wikipediaapi.Wikipedia(
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='YourAppName/1.0'  # Replace with your actual application name
        )

    @classmethod
    def get_random_articles(cls, count=1):
        """
        Fetch random articles from Wikipedia API.
        Maintains the same interface as the original service.

        Args:
            count (int): Number of random articles to fetch

        Returns:
            list: List of article data dictionaries
        """
        # Request more articles than needed to account for filtering stubs
        requested_count = min(count * 2, 20)  # Double the requested count, up to API limit

        params = {
            "action": "query",
            "format": "json",
            "list": "random",
            "rnlimit": requested_count,
            "rnnamespace": 0,
        }

        try:
            response = requests.get(cls.BASE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if "query" in data and "random" in data["query"]:
                return data["query"]["random"]
            else:
                logger.error(f"Unexpected response format from Wikipedia API: {data}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching random articles from Wikipedia: {e}")
            return []

    @classmethod
    def get_article_content(cls, pageid):
        """
        Use Wikipedia-API to fetch more complete article content.

        Args:
            pageid (int): Wikipedia page ID

        Returns:
            dict: Article data with keys:
                - pageid: Wikipedia page ID
                - title: Article title
                - content: Article text content
                - images: List of image URLs
                - is_stub: Boolean indicating if article is a stub
        """
        # Create a service instance to access the wiki property
        service = cls()

        try:
            # First get the page title via API
            params = {
                "action": "query",
                "format": "json",
                "pageids": pageid,
                "prop": "info|categories",
                "inprop": "url|displaytitle",
                "cllimit": 50  # Get up to 50 categories
            }

            response = requests.get(cls.BASE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

            if "query" not in data or "pages" not in data["query"]:
                logger.error(f"Error getting page title: {data}")
                return None

            page_data = data["query"]["pages"][str(pageid)]
            title = page_data["title"]

            # Use Wikipedia-API to get full content
            page = service.wiki.page(title)

            if not page.exists():
                logger.error(f"Page does not exist: {title}")
                return None

            # Check if article is a stub by examining categories and content
            is_stub = cls._is_article_stub(page_data, page.text)

            # Get article content and images
            article_data = {
                "pageid": str(pageid),
                "title": title,
                "content": page.text,  # Full text content
                "images": cls._get_image_urls(page_data["title"]),
                "is_stub": is_stub
            }

            return article_data

        except Exception as e:
            logger.error(f"Error getting article content: {e}")
            return None

    @staticmethod
    def _is_article_stub(page_data, content):
        """
        Determine if an article is a stub based on categories and content.

        Args:
            page_data (dict): Page data from the API
            content (str): Article content

        Returns:
            bool: True if article is a stub, False otherwise
        """
        # Check categories for stub indicators
        if "categories" in page_data:
            for category in page_data["categories"]:
                category_title = category.get("title", "")
                if "stub" in category_title.lower():
                    return True

        # Check content for stub templates
        stub_patterns = [
            r'\{\{stub\}\}',
            r'\{\{[^}]*-stub\}\}',
            r'\{\{[^}]*stub[^}]*\}\}'
        ]

        for pattern in stub_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        # Check content length as an additional indicator (very short articles are likely stubs)
        if len(content) < 1000:  # Arbitrary threshold, adjust as needed
            return True

        return False

    @classmethod
    def _get_image_urls(cls, title):
        """
        Get a list of image URLs for the page.

        Args:
            title (str): Article title

        Returns:
            list: List of image URLs
        """
        try:
            # Use API to get page image list
            params = {
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "images",
                "imlimit": 20  # Increased limit to get more images
            }

            response = requests.get(cls.BASE_API_URL, params=params)
            data = response.json()

            image_titles = []
            if "query" in data and "pages" in data["query"]:
                for page_id in data["query"]["pages"]:
                    if "images" in data["query"]["pages"][page_id]:
                        for image in data["query"]["pages"][page_id]["images"]:
                            image_title = image["title"]
                            if any(image_title.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                                if not image_title.startswith("File:Icon"):
                                    image_titles.append(image_title)

            # Get image URLs
            if not image_titles:
                return []

            params = {
                "action": "query",
                "format": "json",
                "titles": "|".join(image_titles[:10]),  # Limit to first 10 images
                "prop": "imageinfo",
                "iiprop": "url"
            }

            response = requests.get(cls.BASE_API_URL, params=params)
            data = response.json()

            image_urls = []
            if "query" in data and "pages" in data["query"]:
                for page_id, page_data in data["query"]["pages"].items():
                    if "imageinfo" in page_data and page_data["imageinfo"]:
                        image_urls.append(page_data["imageinfo"][0]["url"])

            return image_urls

        except Exception as e:
            logger.error(f"Error getting images: {e}")
            return []

    @classmethod
    def fetch_and_cache_random_articles(cls, count=5):
        """
        Fetch random articles and cache them in the database.
        Filters out stub articles.

        Args:
            count (int): Number of articles to fetch and cache

        Returns:
            list: List of cached ArticleCache objects
        """
        random_articles = cls.get_random_articles(count * 2)  # Get more to account for filtering
        cached_articles = []
        processed_count = 0

        for article in random_articles:
            # Check if we've reached the requested count
            if len(cached_articles) >= count:
                break

            # Check if already cached
            existing = ArticleService.get_article_by_id(str(article['id']))
            if existing:
                cached_articles.append(existing)
                continue

            # Fetch full content
            article_data = cls.get_article_content(article["id"])
            if not article_data:
                continue

            # Skip stub articles
            if article_data.get("is_stub", False):
                logger.info(f"Skipping stub article: {article_data['title']}")
                continue

            # Cache the article
            cached = ArticleService.cache_article(
                article_id=article_data["pageid"],
                title=article_data["title"],
                content=article_data["content"],
                image_urls=article_data["images"]
            )

            cached_articles.append(cached)
            processed_count += 1

            # Log progress
            logger.info(f"Cached article {processed_count}/{count}: {article_data['title']}")

        return cached_articles
