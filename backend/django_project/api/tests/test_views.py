# Created with help from Cursor

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class ApiViewsTestCase(APITestCase):
    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_example_view_get(self):
        """Test the example_view with GET request."""
        url = reverse('example_view')  # Ensure this matches the name in your urls.py
        response = self.client.get(url, {'name': 'Alice'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Alice')

    def test_example_view_post(self):
        """Test the example_view with POST request."""
        url = reverse('example_view')  # Ensure this matches the name in your urls.py
        response = self.client.post(url, {'name': 'Bob'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Bob')

    def test_get_user_info(self):
        """Test the get_user_info view."""
        self.client.login(username='testuser', password='testpassword')  # Log in the user
        
        url = reverse('user_info')  # URL name matches urls.py
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Parse the JSON response
        response_data = response.json()
        self.assertEqual(response_data['id'], self.user.id)
        self.assertEqual(response_data['username'], self.user.username)
        self.assertEqual(response_data['email'], self.user.email)
        self.assertEqual(response_data['streak'], 0)

    @patch('api.views.utils.get_user_article')
    def test_get_scrambled_article(self, mock_get_user_article):
        """Test the get_scrambled_article view."""
        mock_get_user_article.return_value = {
            "request": "get_scrambled_article",
            "article": {
                "main-text": "This is a scrambled article.",
                "header": "Sample Header",
                "image-url": "http://example.com/image.jpg"
            }
        }
        
        url = reverse('scrambled_article')  # URL name matches urls.py
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Parse the JSON response
        response_data = response.json()
        self.assertEqual(response_data['article']['main-text'], "This is a scrambled article.")
        self.assertEqual(response_data['article']['header'], "Sample Header")
        self.assertEqual(response_data['article']['image-url'], "http://example.com/image.jpg")

    @patch('api.views.utils.get_user_scores')
    def test_get_guess_scoreboard(self, mock_get_user_scores):
        """Test the get_guess_scoreboard view."""
        mock_get_user_scores.return_value = {
            "request": "get_guess_scoreboard",
            "scores": {
                "guess1": 100,
                "guess2": 200
            }
        }
        
        url = reverse('guess_scoreboard')  # URL name matches urls.py
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Parse the JSON response
        response_data = response.json()
        self.assertEqual(response_data['request'], "get_guess_scoreboard")
        self.assertEqual(response_data['scores']['guess1'], 100)
        self.assertEqual(response_data['scores']['guess2'], 200)

    def test_get_friend_scoreboard(self):
        """Test the get_friend_scoreboard view."""
        url = reverse('friend_scoreboard')  # URL name matches urls.py
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Parse the JSON response
        response_data = response.json()
        self.assertIn('request', response_data)
        self.assertIn('scores', response_data)

    @patch('api.views.utils.process_guess')
    def test_process_guess(self, mock_process_guess):
        """Test the process_guess view."""
        mock_process_guess.return_value = None  # Assuming process_guess does not return anything
        
        url = reverse('process_guess')  # URL name matches urls.py
        response = self.client.post(url, {'guess': 'This is a guess'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Parse the JSON response
        response_data = response.json()
        self.assertEqual(response_data['request'], "process_guess")
        self.assertEqual(response_data['guess'], 'This is a guess')
