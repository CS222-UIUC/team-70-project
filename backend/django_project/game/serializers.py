from rest_framework import serializers
from .models import GameState, UserGuess


class UserGuessSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGuess
        fields = ['id', 'guess_text', 'score', 'similarity_score', 'timestamp']


class GameStateSerializer(serializers.ModelSerializer):
    guesses = UserGuessSerializer(many=True, read_only=True)
    article_title = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = GameState
        fields = ['id', 'article_title', 'date', 'max_guesses',
                  'is_completed', 'best_score', 'guesses',
                  'created_at', 'updated_at']
