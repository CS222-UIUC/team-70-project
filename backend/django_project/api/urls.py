"""
urls.py

This module contains the logic for the URL endpoints for the backend API
"""

from django.urls import path
from .views import (
    get_user_info,
    get_scrambled_article,
    get_guess_scoreboard,
    get_friend_scoreboard,
    process_guess,
    get_game_over,
    example_view
)

urlpatterns = [
    path(
        'user_info/',
        get_user_info,
        name='user_info'),
    path(
        'scrambled_article/',
        get_scrambled_article,
        name='scrambled_article'),
    path(
        'guess_scoreboard/',
        get_guess_scoreboard,
        name='guess_scoreboard'),
    path(
        'friend_scoreboard/',
        get_friend_scoreboard,
        name='friend_scoreboard'),
    path(
        'process_guess/',
        process_guess,
        name='process_guess'),
    path(
        'game_over/',
        get_game_over,
        name='game_over'),
    path(
        'example/',
        example_view,
        name='example_view')]
