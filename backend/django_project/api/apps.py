"""
apps.py

This module defines the configuration for the API application in the Django project.
It inherits from Django's AppConfig and is used to set application-specific settings
and behaviors.
"""
from django.apps import AppConfig  # pylint: disable=unused-import


class ApiConfig(AppConfig):
    """Filler docstring for the ApiConfig class.

    This class configures the API application, setting up necessary parameters
    and behaviors specific to the application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
