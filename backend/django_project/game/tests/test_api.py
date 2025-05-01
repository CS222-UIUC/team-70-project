from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import datetime
import json
import random
from unittest.mock import patch, MagicMock

from rest_framework.test import APITestCase
from rest_framework import status

from game.models import (
    UserProfile,
    ArticleCache,
    DailyArticle,
    GameState,
    UserGuess,
)

# Test helper functions - these will be replaced by mocks


def mock_generate_scrambled_text(content):
    """Mock function for testing"""
    return {"test": "tset", "article": "elcitra"}


def mock_calculate_guess_score(guess, actual):
    """Mock function for testing"""
    return 500, 0.75


class GameStateAPITest(APITestCase):
    """Test the GameState API endpoints"""

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

        # Create test article
        cls.test_article = ArticleCache.objects.create(
            article_id="12345",
            title="Test Article",
            content="This is the content of a test article.",
        )

        # Create test word mapping
        cls.test_word_mapping = {
            "content": "ntnetoc",
            "test": "ttse",
            "article": "elitacr"
        }

    def setUp(self):
        # Log in the test user for each test
        self.client.force_authenticate(user=self.test_user)

    @patch('game.text_utils.generate_scrambled_text', mock_generate_scrambled_text)
    def test_create_game_state(self):
        """Test creating a new game state via API"""
        url = reverse('game-state')
        data = {
            'article_id': self.test_article.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['article_title'], self.test_article.title)

    def test_get_game_state(self):
        """Test retrieving a game state via API"""
        game_state = GameState.objects.create(
            user=self.test_user,
            article=self.test_article,
            word_mapping=self.test_word_mapping
        )

        url = reverse('game-state')
        response = self.client.get(f"{url}?game_id={game_state.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], game_state.id)
        self.assertEqual(response.data['article_title'], self.test_article.title)

    def test_get_all_game_states(self):
        """Test retrieving all game states for a user"""
        GameState.objects.create(
            user=self.test_user,
            article=self.test_article,
            word_mapping=self.test_word_mapping
        )

        second_article = ArticleCache.objects.create(
            article_id="67890",
            title="Second Article",
            content="Another article",
        )

        GameState.objects.create(
            user=self.test_user,
            article=second_article,
            word_mapping={"another": "rehtona"}
        )

        url = reverse('game-state')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class UserGuessAPITest(APITestCase):
    """Test the UserGuess API endpoints"""

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.test_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

        # Create test article
        cls.test_article = ArticleCache.objects.create(
            article_id="12345",
            title="Test Article",
            content="This is the content of a test article.",
        )

    def setUp(self):
        # Log in the test user for each test
        self.client.force_authenticate(user=self.test_user)

        # Create a fresh game state for each test
        self.game_state = GameState.objects.create(
            user=self.test_user,
            article=self.test_article,
            word_mapping={"test": "ttse"},
            max_guesses=3
        )

    @patch('game.text_utils.calculate_guess_score', mock_calculate_guess_score)
    def test_submit_guess(self):
        """Test submitting a guess via API"""
        url = reverse('user-guess')
        data = {
            'game_id': self.game_state.id,
            'guess': 'Testing Article'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['guess'], 'Testing Article')
        # Just verify that score exists and is an integer
        self.assertIn('score', response.data)
        self.assertIsInstance(response.data['score'], int)
        # Verify similarity exists and is a float
        self.assertIn('similarity', response.data)
        self.assertIsInstance(response.data['similarity'], float)
        self.assertEqual(response.data['attempt'], 1)

    def test_max_guesses_limit(self):
        """Test that users can't exceed the maximum guess limit"""
        url = reverse('user-guess')

        # Create max_guesses number of guesses already
        for i in range(self.game_state.max_guesses):
            UserGuess.objects.create(
                game_state=self.game_state,
                guess_text=f"Guess {i+1}"
            )

        # Try to submit one more guess
        data = {
            'game_id': self.game_state.id,
            'guess': 'One too many'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Maximum guess attempts reached', response.data['error'])

    def test_completed_game(self):
        """Test that guesses are rejected for completed games"""
        self.game_state.is_completed = True
        self.game_state.save()

        url = reverse('user-guess')
        data = {
            'game_id': self.game_state.id,
            'guess': 'Too late'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Game is already completed', response.data['error'])


class ScrambledDictionaryAPITest(APITestCase):
    """Test the ScrambledDictionary API endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

        self.article = ArticleCache.objects.create(
            article_id="12345",
            title="Test Article",
            content="Test content",
        )

        self.word_mapping = {
            "test": "tset",
            "content": "tnetnoc"
        }

        self.client.force_authenticate(user=self.user)

        self.game_state = GameState.objects.create(
            user=self.user,
            article=self.article,
            word_mapping=self.word_mapping
        )

    def test_get_scrambled_dictionary(self):
        """Test retrieving the scrambled dictionary for a game"""
        url = reverse('scrambled-dictionary')
        response = self.client.get(f"{url}?game_id={self.game_state.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['word_mapping'], self.word_mapping)

    def test_game_id_required(self):
        """Test that game_id is required"""
        url = reverse('scrambled-dictionary')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Game ID is required', response.data['error'])


class SetArticleAPITest(APITestCase):
    """Test the SetArticle API endpoint"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword"
        )

        self.article = ArticleCache.objects.create(
            article_id="12345",
            title="Test Article",
            content="Test content",
        )

        self.today = timezone.now().date()
        self.daily_article = DailyArticle.objects.create(
            date=self.today,
            article=self.article
        )

        self.client.force_authenticate(user=self.user)

    def test_set_article_by_id(self):
        """Test setting article by ID"""
        url = reverse('set-article')
        data = {
            'article_id': self.article.id
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['article_id'], self.article.id)
        self.assertEqual(response.data['title'], self.article.title)
