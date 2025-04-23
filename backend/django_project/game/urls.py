from django.urls import path
from .views import GameStateView, UserGuessView, ScrambledDictionaryView, SetArticleView

urlpatterns = [
    path('game-state/', GameStateView.as_view(), name='game-state'),
    path('guess/', UserGuessView.as_view(), name='user-guess'),
    path('scrambled-dictionary/', ScrambledDictionaryView.as_view(), name='scrambled-dictionary'),
    path('set-article/', SetArticleView.as_view(), name='set-article'),
]
