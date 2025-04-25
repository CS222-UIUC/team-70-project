# Created with help from Cursor

from django.test import TestCase
from unittest.mock import patch
from api.utils import get_daily_article, get_daily_article_title, generate_game, get_letter_bag, get_user_article, get_user_scores, process_guess, update_user_profile, user_finished_game, get_doc, init_random, stringify_state, guess_update
from django.utils import timezone
import spacy  # Import spacy

nlp = spacy.load("en_core_web_lg") # python -m spacy download en_core_web_lg
FULL_THRESH = 0.7          # Absolute similarity threshold for a word to be completely unscrambled
PARTIAL_THRESH = 0.4        # Partial similarity threshold for a word to be partially unscrambled
FULL_MULTIPLIER = 1.2         # Multiplier for full threshold reduction based on how close the guess is to title
PARTIAL_MULTIPLIER = 2    # Mulitplier for partial threshold reduction based on how close the guess is to title
WIN_THRESH = 0.95           # Threshold to pass to win the game
PUNCT_THRESH = 2            # Length threshold for punctuation to be considered a word instead (for weird formattings)

class UtilsTestCase(TestCase):
    @patch('api.utils.DailyArticle')
    @patch('api.utils.ArticleCache')
    def test_get_daily_article_title(self, MockArticleCache, MockDailyArticle):
        """Test that the daily article title is returned correctly."""
        # Set up the mock for DailyArticle
        mock_daily_article_instance = MockDailyArticle.return_value
        mock_daily_article_instance.article.title = 'Mock Daily Article Title'
        MockDailyArticle.objects.get.return_value = mock_daily_article_instance

        # Set up the mock for ArticleCache
        mock_article_instance = MockArticleCache.return_value
        mock_article_instance.content = 'This is the main content of the article.'
        mock_article_instance.image_urls = ['http://example.com/image.jpg']
        MockArticleCache.objects.get.return_value = mock_article_instance

        # Call the function to test
        title = get_daily_article_title()
        self.assertEqual(title, 'Mock Daily Article Title')  # Check that the title matches the mock

    @patch('api.utils.DailyArticle')
    @patch('api.utils.ArticleCache')
    def test_get_daily_article(self, MockArticleCache, MockDailyArticle):
        """Test that the daily article is returned correctly."""
        # Set up the mock for DailyArticle
        mock_daily_article_instance = MockDailyArticle.return_value
        mock_daily_article_instance.article.title = 'Mock Daily Article Title'
        MockDailyArticle.objects.get.return_value = mock_daily_article_instance

        # Set up the mock for ArticleCache
        mock_article_instance = MockArticleCache.return_value
        mock_article_instance.content = 'This is the main content of the article.'
        mock_article_instance.image_urls = ['http://example.com/image.jpg']
        MockArticleCache.objects.get.return_value = mock_article_instance

        # Call the function to test
        article = get_daily_article()
        self.assertIn("main-text", article)  # Check that 'main-text' is in the returned article
        self.assertEqual(article["main-text"], 'This is the main content of the article.')  # Check content
        self.assertIn("image-url", article)  # Check that 'image-url' is in the returned article
        self.assertEqual(article["image-url"], 'http://example.com/image.jpg')  # Check image URL

    @patch('api.utils.User')
    @patch('api.utils.GameState')
    @patch('api.utils.ArticleCache')
    @patch('api.utils.get_daily_article')
    @patch('api.utils.DailyArticle')
    def test_get_user_article(self, MockDailyArticle, MockGetDailyArticle, MockArticleCache, MockGameState, MockUser):
        """Test that the user's current article is returned correctly."""
        # Set up the mock for User
        mock_user_instance = MockUser.return_value
        mock_user_instance.id = 1
        MockUser.objects.get.return_value = mock_user_instance

        # Set up the mock for GameState
        mock_game_state_instance = MockGameState.return_value
        mock_game_state_instance.word_mapping = {'This': 'This'}
        mock_game_state_instance.article.title = 'Mock Daily Article Title'
        MockGameState.objects.get.return_value = mock_game_state_instance

        # Set up the mock for ArticleCache
        mock_article_instance = MockArticleCache.return_value
        mock_article_instance.content = 'This is the main content of the article.'
        mock_article_instance.image_urls = ['http://example.com/image.jpg']
        MockArticleCache.objects.get.return_value = mock_article_instance

        # Set up the mock for DailyArticle
        mock_daily_article_instance = MockDailyArticle.return_value
        mock_daily_article_instance.article.title = 'Mock Daily Article Title'
        MockDailyArticle.objects.get.return_value = mock_daily_article_instance

        # Set up the mock for get_daily_article
        MockGetDailyArticle.return_value = {
            "main-text": 'This is the main content of the article.',
            "image-url": 'http://example.com/image.jpg'
        }

        # Call the function to test
        user_id = 1
        article = get_user_article(user_id)
        self.assertIn("request", article)  # Check that 'request' is in the returned article
        self.assertEqual(article["request"], "get_scrambled_article")  # Check request type
        self.assertIn("article", article)  # Check that 'article' is in the returned article
        self.assertEqual(article["article"]["main-text"], ' This is the main content of the article.')  # Check content
        self.assertIn("image-url", article["article"])  # Check that 'image-url' is in the returned article
        self.assertEqual(article["article"]["image-url"], 'http://example.com/image.jpg')  # Check image URL
    
    @patch('api.utils.User')
    @patch('api.utils.GameState')
    @patch('api.utils.ArticleCache')
    @patch('api.utils.get_daily_article')
    @patch('api.utils.DailyArticle')
    def test_get_user_article_different_article(self, MockDailyArticle, MockGetDailyArticle, MockArticleCache, MockGameState, MockUser):
        """Test that the user's current article is initialized correctly."""
        # Set up the mock for User
        mock_user_instance = MockUser.return_value
        mock_user_instance.id = 1
        MockUser.objects.get.return_value = mock_user_instance

        # Set up the mock for GameState
        mock_game_state_instance = MockGameState.return_value
        mock_game_state_instance.word_mapping = {'This': 'This'}
        mock_game_state_instance.article.title = 'Mock Daily Article Title'
        MockGameState.objects.get.return_value = mock_game_state_instance

        # Set up the mock for ArticleCache
        mock_article_instance = MockArticleCache.return_value
        mock_article_instance.content = 'This is the main content of the article.'
        mock_article_instance.image_urls = ['http://example.com/image.jpg']
        MockArticleCache.objects.get.return_value = mock_article_instance

        # Set up the mock for DailyArticle
        mock_daily_article_instance = MockDailyArticle.return_value
        mock_daily_article_instance.article.title = 'Different Article Title'
        MockDailyArticle.objects.get.return_value = mock_daily_article_instance

        # Set up the mock for get_daily_article
        MockGetDailyArticle.return_value = {
            "main-text": 'This is the main content of the different article.',
            "image-url": 'http://example.com/different-image.jpg'
        }

        # Call the function to test
        user_id = 1
        article = get_user_article(user_id)
        self.assertIn("request", article)  # Check that 'request' is in the returned article
        self.assertEqual(article["request"], "get_scrambled_article")  # Check request type
        self.assertIn("article", article)  # Check that 'article' is in the returned article
        self.assertEqual(article["article"]["main-text"], ' This is the main content of the different article.')  # Check content
        self.assertIn("image-url", article["article"])  # Check that 'image-url' is in the returned article
        self.assertEqual(article["article"]["image-url"], 'http://example.com/different-image.jpg')  # Check image URL


    @patch('api.utils.User')
    @patch('api.utils.GameState')
    @patch('api.utils.UserGuess')  # Mock UserGuess to simulate user scores
    def test_get_user_scores(self, MockUserGuess, MockGameState, MockUser):
        """Test that the user's current scores are returned correctly."""
        # Set up the mock for User
        mock_user_instance = MockUser.return_value
        mock_user_instance.id = 1
        MockUser.objects.get.return_value = mock_user_instance

        # Set up the mock for GameState
        mock_game_state_instance = MockGameState.return_value
        mock_game_state_instance.guesses.all.return_value = None  # No guesses initially
        MockGameState.objects.get.return_value = mock_game_state_instance

        # Call the function to test
        user_id = 1
        scores = get_user_scores(user_id)
        self.assertIn("request", scores)  # Check that 'request' is in the returned scores
        self.assertEqual(scores["request"], "get_guess_scoreboard")  # Check request type
        self.assertIn("scores", scores)  # Check that 'scores' is in the returned scores
        self.assertEqual(scores["scores"], {})  # Check that scores are empty initially

        # Now, let's add some mock guesses
        mock_guess_instance = MockUserGuess.return_value
        mock_guess_instance.guess_text = 'Test Guess'
        mock_guess_instance.score = 500
        mock_game_state_instance.guesses.all.return_value = [mock_guess_instance]

        # Call the function again to test with guesses
        scores = get_user_scores(user_id)
        self.assertIn("scores", scores)  # Check that 'scores' is in the returned scores
        self.assertEqual(scores["scores"], {'Test Guess': 500})  # Check that the score is returned correctly

    @patch('api.utils.User')
    @patch('api.utils.GameState')
    @patch('api.utils.UserGuess')
    @patch('api.utils.get_daily_article_title')
    @patch('api.utils.guess_update')
    def test_process_guess(self, MockGuessUpdate, MockGetDailyArticleTitle, MockUserGuess, MockGameState, MockUser):
        """Test that the process_guess function updates the user's guess correctly."""
        # Set up the mock for User
        mock_user_instance = MockUser.return_value
        mock_user_instance.id = 1
        MockUser.objects.get.return_value = mock_user_instance

        # Set up the mock for GameState
        mock_game_state_instance = MockGameState.return_value
        mock_game_state_instance.word_mapping = {'This': 'This'}
        mock_game_state_instance.guesses.all.return_value = None  # No guesses initially
        MockGameState.objects.get.return_value = mock_game_state_instance

        # Set up the mock for UserGuess
        mock_guess_instance = MockUserGuess.return_value
        MockUserGuess.objects.create.return_value = mock_guess_instance

        # Mock the return value of get_daily_article_title
        MockGetDailyArticleTitle.return_value = 'Mock Daily Article Title'

        # Mock the return value of guess_update
        MockGuessUpdate.return_value = 0.8  # Simulate a similarity score

        # Call the function to test
        user_id = 1
        guess = 'This is a guess'
        process_guess(user_id, guess)
        
        # Check that the game state was updated
        mock_game_state_instance.save.assert_called_once()  # Ensure save was called
    
    @patch('api.utils.User')
    @patch('api.utils.GameState')
    @patch('api.utils.UserGuess')
    @patch('api.utils.get_daily_article_title')
    @patch('api.utils.guess_update')
    def test_process_guess_already_guessed(self, MockGuessUpdate, MockGetDailyArticleTitle, MockUserGuess, MockGameState, MockUser):
        """Test that the process_guess function updates the user's guess correctly."""
        # Set up the mock for User
        mock_user_instance = MockUser.return_value
        mock_user_instance.id = 1
        MockUser.objects.get.return_value = mock_user_instance

        # Set up mock for a user guess as a class with a guess_text and score attribute
        class MockUserGuess:
            def __init__(self, guess_text, score):
                self.guess_text = guess_text
                self.score = score

        # Set up the mock for GameState
        mock_game_state_instance = MockGameState.return_value
        mock_game_state_instance.word_mapping = {'This': 'This'}
        mock_game_state_instance.guesses.all.return_value = [MockUserGuess('This is a guess', 500)]  # Same guess
        MockGameState.objects.get.return_value = mock_game_state_instance

        # Mock the return value of get_daily_article_title
        MockGetDailyArticleTitle.return_value = 'Mock Daily Article Title'

        # Mock the return value of guess_update
        MockGuessUpdate.return_value = 0.8  # Simulate a similarity score

        # Call the function to test
        user_id = 1
        guess = 'This is a guess'
        process_guess(user_id, guess)
        
        # Check that the game state was not updated
        mock_game_state_instance.save.assert_not_called()  # Ensure save was not called

    @patch('api.utils.User')
    @patch('api.utils.GameState')
    @patch('api.utils.UserGuess')
    @patch('api.utils.get_daily_article_title')
    @patch('api.utils.guess_update')
    def test_process_guess_already_won(self, MockGuessUpdate, MockGetDailyArticleTitle, MockUserGuess, MockGameState, MockUser):
        """Test that the process_guess function updates the user's guess correctly."""
        # Set up the mock for User
        mock_user_instance = MockUser.return_value
        mock_user_instance.id = 1
        MockUser.objects.get.return_value = mock_user_instance

        # Set up mock for a user guess as a class with a guess_text and score attribute
        class MockUserGuess:
            def __init__(self, guess_text, score):
                self.guess_text = guess_text
                self.score = score

        # Set up the mock for GameState
        mock_game_state_instance = MockGameState.return_value
        mock_game_state_instance.word_mapping = {'This': 'This'}
        mock_game_state_instance.guesses.all.return_value = [MockUserGuess('Winning guess', 1000)]  # Winning guess
        MockGameState.objects.get.return_value = mock_game_state_instance

        # Mock the return value of get_daily_article_title
        MockGetDailyArticleTitle.return_value = 'Mock Daily Article Title'

        # Mock the return value of guess_update
        MockGuessUpdate.return_value = 0.8  # Simulate a similarity score

        # Call the function to test
        user_id = 1
        guess = 'This is a guess'
        process_guess(user_id, guess)
        
        # Check that the game state was not updated
        mock_game_state_instance.save.assert_not_called()  # Ensure save was not called

    @patch('api.utils.User')
    @patch('api.utils.GameState')
    @patch('api.utils.UserGuess')
    @patch('api.utils.get_daily_article_title')
    @patch('api.utils.guess_update')
    def test_process_guess_exceeds_max_guesses(self, MockGuessUpdate, MockGetDailyArticleTitle, MockUserGuess, MockGameState, MockUser):
        """Test that the process_guess function updates the user's guess correctly."""
        # Set up the mock for User
        mock_user_instance = MockUser.return_value
        mock_user_instance.id = 1
        MockUser.objects.get.return_value = mock_user_instance

        # Set up mock for a user guess as a class with a guess_text and score attribute
        class MockUserGuess:
            def __init__(self, guess_text, score):
                self.guess_text = guess_text
                self.score = score

        # Set up the mock for GameState
        mock_game_state_instance = MockGameState.return_value
        mock_game_state_instance.word_mapping = {'This': 'This'}
        mock_game_state_instance.guesses.all.return_value = [
            MockUserGuess('Other guess 1', 500),
            MockUserGuess('Other guess 2', 500),
            MockUserGuess('Other guess 3', 500),
            MockUserGuess('Other guess 4', 500),
            MockUserGuess('Other guess 5', 500),
            MockUserGuess('Other guess 6', 500),
            MockUserGuess('Other guess 7', 500),
            MockUserGuess('Other guess 8', 500),
        ]  # Eight guesses
        MockGameState.objects.get.return_value = mock_game_state_instance

        # Mock the return value of get_daily_article_title
        MockGetDailyArticleTitle.return_value = 'Mock Daily Article Title'

        # Mock the return value of guess_update
        MockGuessUpdate.return_value = 0.8  # Simulate a similarity score

        # Call the function to test
        user_id = 1
        guess = 'This is a guess'
        process_guess(user_id, guess)
        
        # Check that the game state was not updated
        mock_game_state_instance.save.assert_not_called()  # Ensure save was not called


    @patch('api.utils.User')
    @patch('api.utils.UserProfile')
    def test_update_user_profile(self, MockUserProfile, MockUser):
        """Test that the update_user_profile function updates the user's profile correctly."""
        # Set up the mock for User
        mock_user_instance = MockUser.return_value
        mock_user_instance.id = 1
        MockUser.objects.get.return_value = mock_user_instance

        # Set up the mock for UserProfile
        mock_user_profile_instance = MockUserProfile.return_value
        mock_user_profile_instance.total_games_played = 0
        mock_user_profile_instance.total_wins = 0
        mock_user_profile_instance.current_streak = 0
        mock_user_profile_instance.max_streak = 0
        mock_user_profile_instance.average_score = 0
        mock_user_profile_instance.best_score = 0
        MockUserProfile.objects.get.return_value = mock_user_profile_instance

        # Call the function to test
        user_id = 1
        score = 1000  # Simulate a winning score
        update_user_profile(user_id, score)

        # Check that the user profile was updated correctly
        self.assertEqual(mock_user_profile_instance.total_games_played, 1)  # Total games played should increment
        self.assertEqual(mock_user_profile_instance.total_wins, 1)  # Total wins should increment
        self.assertEqual(mock_user_profile_instance.last_played_date, timezone.now().date())  # Last played date should be updated
        self.assertEqual(mock_user_profile_instance.average_score, 1000)  # Average score should be updated
        self.assertEqual(mock_user_profile_instance.best_score, 1000)  # Best score should be updated

        # Check that the user profile was saved
        mock_user_profile_instance.save.assert_called_once()  # Ensure save was called

    @patch('api.utils.User')
    @patch('api.utils.GameState')
    @patch('api.utils.UserGuess')
    def test_user_finished_game(self, MockUserGuess, MockGameState, MockUser):
        """Test that the user_finished_game function correctly identifies a winning scenario."""
        # Set up the mock for User
        mock_user_instance = MockUser.return_value
        mock_user_instance.id = 1
        MockUser.objects.get.return_value = mock_user_instance

        # Set up the mock for GameState
        mock_game_state_instance = MockGameState.return_value
        mock_game_state_instance.guesses.all.return_value = []  # No guesses initially
        MockGameState.objects.get.return_value = mock_game_state_instance

        # Set up the mock for UserGuess with a winning score
        mock_guess_instance = MockUserGuess.return_value
        mock_guess_instance.guess_text = 'Winning Guess'
        mock_guess_instance.score = 1000  # Winning score
        mock_game_state_instance.guesses.all.return_value = [mock_guess_instance]

        # Call the function to test
        user_id = 1
        finished, score = user_finished_game(user_id)

        # Check that the user has finished the game and the score is 1000
        self.assertTrue(finished)  # User should have finished the game
        self.assertEqual(score, 1000)  # Score should be 1000

        # Now test for a scenario where the user has not finished the game
        mock_game_state_instance.guesses.all.return_value = []  # No guesses
        finished, score = user_finished_game(user_id)

        # Check that the user has not finished the game
        self.assertFalse(finished)  # User should not have finished the game
        self.assertEqual(score, 0)  # Score should be 0
        
    # Scrambling/Unscrambling tests
    def test_generate_game(self):
        """Test that the game state is generated correctly."""
        text = "This is a test."
        game_state = generate_game(text)
        self.assertIsInstance(game_state, dict)  # Check that the game state is a dictionary
        self.assertIn("This", game_state)  # Check that the word "This" is in the game state

    def test_get_doc(self):
        """Test that the get_doc function returns a Spacy doc."""
        text = "This is a test."
        doc = get_doc(text)
        doc_ground_truth = nlp(text)
        self.assertIsInstance(doc, type(doc_ground_truth))

    def test_get_letter_bag(self):
        """Test that the get_letter_bag function returns a list of unique letters."""
        text = "This is a test."
        letter_bag = get_letter_bag(text)
        self.assertEqual(set(letter_bag), set(['T', 'h', 'i', 's', 'i', 's', 'a', 't', 'e', 's', 't']))

    def test_init_random(self):
        """Test that the init_random function returns a list of unique letters."""
        text = "This is a test."
        letter_bag = get_letter_bag(text)
        game_state = generate_game(text)
        self.assertIsInstance(game_state, dict)  # Check that the game state is a dictionary
        init_random(game_state, letter_bag)
        self.assertIn("This", game_state)  # Check that the word "This" is in the game state
        self.assertNotEqual(game_state["This"], "This")  # Check that the word "This" is not the same as the original word

    def test_stringify_state(self):
        """Test that the stringify_state function returns a string."""
        text = "This is a test."
        test = generate_game(text)
        stringified = stringify_state(text, test)
        self.assertIsInstance(stringified, str)  # Check that the stringified state is a string
        self.assertEqual(stringified.strip(), "This is a test.")  # Check that the stringified state is the same as the original text

    def test_guess_update(self):
        """Test that the guess_update function returns a similarity score."""
        text = "This is a test."
        test_state = generate_game(text)
        letter_bag = get_letter_bag(text)
        init_random(test_state, letter_bag)
        guess = "This"
        guess_update(test_state, guess, "Something else")
        self.assertEqual(test_state["This"], "This")  # Check that the word "This" is fully unscrambled
    
    def test_guess_update_win(self):
        """Test that the guess_update function returns a win."""
        text = "This is a test."
        test_state = generate_game(text)
        letter_bag = get_letter_bag(text)
        init_random(test_state, letter_bag)
        guess = "This"
        guess_update(test_state, guess, guess)
        self.assertEqual(test_state["This"], "This")  # Check that the word "This"is fully unscrambled
        self.assertEqual(test_state["is"], "is")  # Check that the word "is" is fully unscrambled
        self.assertEqual(test_state["a"], "a")  # Check that the word "a" is fully unscrambled
        self.assertEqual(test_state["test"], "test")  # Check that the word "test" is fully unscrambled

