# api/tests/test_apps.py

# Created with help from Cursor

from django.test import TestCase
from api.apps import ApiConfig

class ApiConfigTest(TestCase):
    def test_app_config(self):
        """Test that the API app is configured correctly."""
        self.assertEqual(ApiConfig.name, 'api')