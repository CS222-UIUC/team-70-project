from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

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

    # def test_example_view_post(self):
    #     """Test the example_view with POST request."""
    #     url = reverse('example_view')  # Ensure this matches the name in your urls.py
    #     response = self.client.post(url, {'name': 'Bob'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['name'], 'Bob')

    # def test_get_user_info(self):
    #     """Test the get_user_info view."""
    #     self.client.login(username='testuser', password='testpassword')  # Log in the user
    #     url = reverse('user_info')  # Adjusted to match the name in your urls.py
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['username'], 'testuser')

    # def test_get_scrambled_article(self):
    #     """Test the get_scrambled_article view."""
    #     url = reverse('scrambled_article')  # Adjusted to match the name in your urls.py
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_get_guess_scoreboard(self):
    #     """Test the get_guess_scoreboard view."""
    #     url = reverse('guess_scoreboard')  # Adjusted to match the name in your urls.py
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_get_friend_scoreboard(self):
    #     """Test the get_friend_scoreboard view."""
    #     url = reverse('friend_scoreboard')  # Adjusted to match the name in your urls.py
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_process_guess(self):
    #     """Test the process_guess view."""
    #     url = reverse('process_guess')  # Adjusted to match the name in your urls.py
    #     response = self.client.post(url, {'guess': 'some_guess'})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['guess'], 'some_guess')
