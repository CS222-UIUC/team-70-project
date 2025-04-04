import requests
import logging
import re
from bs4 import BeautifulSoup
from django.conf import settings
from .article_service import ArticleService

logger = logging.getLogger(__name__)

class WikipediaService:
    """
    Service for interacting with Wikipedia API to fetch articles and images.
    """
    
    BASE_API_URL = "https://en.wikipedia.org/w/api.php"
    
    @classmethod
    def get_random_articles(cls, count=1):
        """
        Fetch random article(s) from Wikipedia API.
        
        Args:
            count (int): Number of random articles to fetch
            
        Returns:
            list: List of article data dictionaries with keys:
                - pageid: Wikipedia page ID
                - title: Article title
        """
        params = {
            "action": "query",
            "format": "json",
            "list": "random",
            "rnlimit": min(count, 10),  # API limit is usually 10
            "rnnamespace": 0  # Main namespace only
        }
        
        try:
            response = requests.get(cls.BASE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'query' in data and 'random' in data['query']:
                return data['query']['random']
            else:
                logger.error(f"Unexpected response format from Wikipedia API: {data}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching random articles from Wikipedia: {e}")
            return []
    
    @classmethod
    def get_article_content(cls, pageid):
        """
        Fetch article content from Wikipedia API.
        
        Args:
            pageid (int): Wikipedia page ID
            
        Returns:
            dict: Article data with keys:
                - pageid: Wikipedia page ID
                - title: Article title
                - content: Article text content
                - images: List of image URLs
        """
        # First, get the article content
        params = {
            "action": "parse",
            "format": "json",
            "pageid": pageid,
            "prop": "text|images"
        }
        
        try:
            response = requests.get(cls.BASE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'parse' not in data:
                logger.error(f"Error getting article content, unexpected response: {data}")
                return None
                
            # Extract basic info
            article_data = {
                'pageid': str(pageid),
                'title': data['parse']['title'],
                'content': '',
                'images': []
            }
            
            # Extract text content
            if 'text' in data['parse'] and '*' in data['parse']['text']:
                html_content = data['parse']['text']['*']
                article_data['content'] = cls._extract_text_from_html(html_content)
            
            # Get image URLs if available
            if 'images' in data['parse']:
                article_data['images'] = cls._get_image_urls(data['parse']['images'])
                
            return article_data
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching article content from Wikipedia: {e}")
            return None
    
    @classmethod
    def fetch_and_cache_random_articles(cls, count=5):
        """
        Fetch random articles from Wikipedia and cache them in the database.
        
        Args:
            count (int): Number of articles to fetch and cache
            
        Returns:
            list: List of cached ArticleCache objects
        """
        random_articles = cls.get_random_articles(count)
        cached_articles = []
        
        for article in random_articles:
            # Check if already cached
            existing = ArticleService.get_article_by_id(str(article['pageid']))
            if existing:
                cached_articles.append(existing)
                continue
                
            # Fetch full content
            article_data = cls.get_article_content(article['id'])
            if not article_data:
                continue
                
            # Cache the article
            cached = ArticleService.cache_article(
                article_id=article_data['pageid'],
                title=article_data['title'],
                content=article_data['content'],
                image_urls=article_data['images']
            )
            
            cached_articles.append(cached)
            
        return cached_articles
    
    @staticmethod
    def _extract_text_from_html(html_content):
        """
        Extract clean text from Wikipedia HTML content.
        Keeps paragraphs, list items, and headers for structure.
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Only remove clearly non-informative tags
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()

        # Accumulate content
        content_parts = []

        for tag in soup.find_all(['h2', 'h3', 'p', 'li']):
            text = tag.get_text(strip=True)
            if text:
                if tag.name in ['h2', 'h3']:
                    content_parts.append(f"\n{text.upper()}\n")
                elif tag.name == 'li':
                    content_parts.append(f"- {text}")
                else:
                    content_parts.append(text)

        # Combine and clean
        text = '\n\n'.join(content_parts)
        text = re.sub(r'\[\d+\]', '', text)  # Remove [1], [2], etc.
        text = re.sub(r'\n{3,}', '\n\n', text)  # Avoid excessive line breaks

        return text.strip()

    
    @classmethod
    def _get_image_urls(cls, image_filenames):
        """
        Get full URLs for Wikipedia images.
        
        Args:
            image_filenames (list): List of image filenames
            
        Returns:
            list: List of image URLs
        """
        if not image_filenames:
            return []
            
        # Filter out unwanted image types (icons, etc.)
        filtered_images = [img for img in image_filenames 
                          if img.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')) 
                          and not img.startswith('Icon')]
        
        if not filtered_images:
            return []
            
        # Get URLs for images
        params = {
            "action": "query",
            "format": "json",
            "titles": '|'.join(['File:' + img for img in filtered_images[:10]]),  # Limit to 10
            "prop": "imageinfo",
            "iiprop": "url"
        }
        
        try:
            response = requests.get(cls.BASE_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            image_urls = []
            if 'query' in data and 'pages' in data['query']:
                for page_id, page_data in data['query']['pages'].items():
                    if 'imageinfo' in page_data and page_data['imageinfo']:
                        image_urls.append(page_data['imageinfo'][0]['url'])
            
            return image_urls
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching image URLs from Wikipedia: {e}")
            return []