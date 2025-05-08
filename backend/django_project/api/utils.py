"""
utils.py

This module contains the functions for game logic and NLP libraries, supporting API responses.

*Possibly use rapidfuzz down the line if needed down the line
*Possibly use an image editing library if needed down the line.
"""

import spacy
import random
from game.models import ArticleCache, DailyArticle, GameState, UserGuess, UserProfile
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

nlp = spacy.load("en_core_web_lg") # python -m spacy download en_core_web_lg
FULL_THRESH = 0.7          # Absolute similarity threshold for a word to be completely unscrambled
PARTIAL_THRESH = 0.4        # Partial similarity threshold for a word to be partially unscrambled
FULL_MULTIPLIER = 1.2         # Multiplier for full threshold reduction based on how close the guess is to title
PARTIAL_MULTIPLIER = 2    # Mulitplier for partial threshold reduction based on how close the guess is to title
WIN_THRESH = 0.95           # Threshold to pass to win the game
PUNCT_THRESH = 2            # Length threshold for punctuation to be considered a word instead (for weird formattings)

MAX_GUESSES = 8             # Maximum number of guesses a user can make before game ends

def get_daily_article():
    """
    get_daily_article returns the current daily article from the database

    For UTIL use, NOT USER.

    Format is Dictionary/JSON:
    article = {
        "main-text" : <main text>,
        "header" : <header - optional>,
        "header-text" : <header text - if header>,
        "image-url" : <img url - optional>,
        "image-title" : <img title - if image url>,
        "captions" : {
            "caption1" : <caption 1 - if image url>,
            ...
        }
    }
    """
    # Get the name of the daily article from the database
    article_title = get_daily_article_title()

    # Use the name of the article to get the article data from the database
    article_data = ArticleCache.objects.get(title=article_title)

    # Return the article data in proper JSON format
    output = {
        "main-text" : article_data.content[:1000],       # Cap characters at 1000 for testing
    }

    if (len(article_data.image_urls) > 0):
        output["image-url"] = article_data.image_urls[0]

    return output

def get_daily_article_title():
    """
    get_daily_article_title returns the current daily article title from the database

    For UTIL use, NOT USER.
    """
    today = timezone.now().date()
    daily_article = DailyArticle.objects.get(date=today)
    title = daily_article.article.title
    return title

def get_user_article(user_id):
    """
    get_user_article formats and returns the user's current article with appropriate scrambling.

    For API/USER use.

    Format is JSON:
    {
        "request": "get_scrambled_article",
        "article": {
            "main-text" : <main text>,
            "header" : <header - optional>,
            "header-text" : <header text - if header>,
            "image-url" : <img url - optional>,
            "image-title" : <img title - if image url>,
            "captions" : {
                "caption1" : <caption 1 - if image url>,
                ...
            }
        }
    }
    """
    user = User.objects.get(id=user_id)

    # Access user state
    game_state = None
    try: # Look into logic further later
        game_state = GameState.objects.get(user=user)
    except: # pragma: no cover
        # User has no initialized game, initialize a game for them and update database
        print("LOG: Generating game for UID: " + str(user_id))
        article_text = get_daily_article()["main-text"]
        new_state = generate_game(article_text) # TESTING behavior
        init_random(new_state, get_letter_bag(article_text))

        # Create new game state
        GameState.objects.create(
            user=user,
            article=ArticleCache.objects.get(title=get_daily_article_title()),
            word_mapping=new_state
        )
        game_state = GameState.objects.get(user=user) # pragma: no cover

    # IF ARTICLE HAS CHANGED, FLUSH ALL CURRENT STATE AND SCORES FOR USER AND CREATE NEW GAME STATE
    if (get_daily_article_title() != game_state.article.title):
        print("LOG: Article has changed, flushing state and scores for UID: " + str(user_id))
        game_state.delete()
        game_state = None

        # Create new game state
        # We can consider keeping the game state in the database later for the user to track progress in a more detailed manner
        print("LOG: Generating game for UID: " + str(user_id))
        article_text = get_daily_article()["main-text"]
        new_state = generate_game(article_text) # TESTING behavior
        init_random(new_state, get_letter_bag(article_text))

        GameState.objects.create(
            user=user,
            article=ArticleCache.objects.get(title=get_daily_article_title()),
            word_mapping=new_state
        )
        game_state = GameState.objects.get(user=user)
        
    # Scramble output text based on state
    user_state = game_state.word_mapping
    maintext_out = stringify_state(get_daily_article()["main-text"], user_state)

    # Format output
    article_out = get_daily_article()
    article_out["main-text"] = maintext_out

    return {
        "request": "get_scrambled_article",
        "article": article_out
    }

def get_user_scores(user_id):
    """
    get_user_scores formats and returns the user's current scores.

    For API/USER use.

    Format is JSON:
    {
        "request" : "get_guess_scoreboard",
        "scores" : {
            <guess1> : <score1>,
            <guess2> : <score2>,
            ...
        }
    }
    """
    user = User.objects.get(id=user_id)

    # Acess user scores
    scores = {}
    try:
        game_state = GameState.objects.get(user=user)
        for guess in game_state.guesses.all():
            scores[guess.guess_text] = guess.score
    except:
        pass

    return {
        "request" : "get_guess_scoreboard",
        "scores" : scores
    }

def process_guess(user_id, guess: str):
    """
    process_guess processes guess for the user identified by user_id and updates their information in the database.

    For UTIL use, NOT USER.
    """
    print("Processing guess: " + guess + " for id = " + str(user_id))
    
    # Acess user state and scores
    user = User.objects.get(id=user_id)
    game_state = GameState.objects.get(user=user)
    user_state = GameState.objects.get(user=user).word_mapping
    user_scores = {}
    try:
        for g in game_state.guesses.all():
            print("LOG: Found guess: " + g.guess_text)
            user_scores[g.guess_text] = g.score
    except:
        pass

    # If the guess has already been made, don't process it
    if guess in user_scores:
        print("LOG: Guess already made, skipping")
        return

    # If the guess exceeds the maximum number of guesses, don't process it
    if len(user_scores) >= MAX_GUESSES:
        print("LOG: Guess exceeds maximum number of guesses, skipping")
        return

    # If a guess is made after the user has already won the game, don't process it
    # We know the user has won if the last guess has a score of 1000
    if len(user_scores) > 0 and user_scores[list(user_scores.keys())[-1]] == 1000:
        print("LOG: Guess made after user has already won, skipping")
        return

    # Update user state and scores with game logic
    similarity = guess_update(user_state, guess, get_daily_article_title())
    score = similarity * 1000
    score = int(score)
    print("Score: " + str(score))
    if score < 0:
        score = 0
    user_scores[guess] = score

    # Update database with new state and scores
    game_state = GameState.objects.get(user=user)
    game_state.word_mapping = user_state # Update wordmapping in database
    game_state.save()
    UserGuess.objects.create(game_state=game_state, guess_text=guess, score=score, similarity_score=similarity) # Add a guess

    # If the user finished the game, update the user's profile
    if score == 1000:
        update_user_profile(user_id, score)
    if len(user_scores) >= MAX_GUESSES:
        # Use user's maximum score as the score for the game if they hit the max number of guesses
        update_user_profile(user_id, max(user_scores.values()))

def update_user_profile(user_id, score: int):
    """
    update_user_profile updates the user's profile after they have completed a game.

    For UTIL use, NOT USER.
    """
    # Get user profile
    user = User.objects.get(id=user_id)
    user_profile = UserProfile.objects.get(user=user)

    # Update total games played and won
    user_profile.total_games_played += 1
    if score == 1000:
        user_profile.total_wins += 1

    # Update last played date, current streak, and max streak
    # Access yesterday's date
    yesterday = timezone.now().date() - timedelta(days=1)

    if user_profile.last_played_date == yesterday:
        user_profile.current_streak += 1
    else:
        user_profile.current_streak = 1

    # Access today's date
    today = timezone.now().date()
    # Update last played date
    user_profile.last_played_date = today

    if user_profile.current_streak > user_profile.max_streak:
        user_profile.max_streak = user_profile.current_streak

    # Update average and best score
    user_profile.average_score = (user_profile.average_score * (user_profile.total_games_played - 1) + score) / user_profile.total_games_played
    if score > user_profile.best_score:
        user_profile.best_score = score

    # Save user profile
    user_profile.save()

    # DEBUG: Print user profile
    print("Updated user profile:")
    print("Current streak: " + str(user_profile.current_streak))
    print("Max streak: " + str(user_profile.max_streak))
    print("Last played date: " + str(user_profile.last_played_date))
    print("Total games played: " + str(user_profile.total_games_played))
    print("Total wins: " + str(user_profile.total_wins))
    print("Average score: " + str(user_profile.average_score))
    print("Best score: " + str(user_profile.best_score))


def user_finished_game(user_id):
    """
    user_won_today checks if the user has won today.

    returns a tuple of (bool, int) where the first element is a boolean indicating if the user has won today and the second element is the score of the user's last guess.

    For UTIL use, NOT USER.
    """
    user = User.objects.get(id=user_id)
    game_state = GameState.objects.get(user=user)
    user_scores = {}
    try:
        for g in game_state.guesses.all():
            print("LOG: Found guess: " + g.guess_text)
            user_scores[g.guess_text] = g.score
    except:
        pass
    
    # Check if user won the game
    if len(user_scores) > 0 and user_scores[list(user_scores.keys())[-1]] == 1000:
        return True, 1000

    # Check if user hit maximum number of guesses
    if len(user_scores) >= MAX_GUESSES:
        return True, user_scores[list(user_scores.keys())[-1]]

    # Otherwise, they have not finished the game
    return False, 0

def get_game_over(user_id):
    """
    get_game_over returns whether or not the game is over, and if so, the user's score and the article title

    For API/USER use.
    """
    # TODO

    return
    

##### SCRAMBLING/UNSCRAMBLING LOGIC #####
def generate_game(text: str, game_state: dict = {}):
    """
    generate_game takes a string and turns it into a game_state with nothing scrambled.

    Optionally, it takes a existing game state and appends new tokens to it.
    """
    global PUNCT_THRESH

    doc = get_doc(text)

    for token in doc:
        if token.pos_ == "SPACE":
            pass

        elif token.pos_ == "PUNCT":
            if len(token.text) > PUNCT_THRESH:
                game_state[token.text] = token.text

        else:
            game_state[token.text] = token.text

    return game_state

def get_doc(text: str):
    """
    get_doc converts a string into a Spacy doc
    """
    global nlp
    return nlp(text)

def get_letter_bag(text: str):
    """
    get_letter_bag takes a string and returns a list of unique letters, excluding common punctuation.

    This is a helper function for init_random.
    """
    letter_bag = set(text)
    letter_exclude = {'\n', '\t', '\"', '\'', '.', ',', '(', ')', '[', ']', '{', '}', '\\', '/', ' ', '*', '!', '?', ':', ' '}
    letter_bag = letter_bag.difference(letter_exclude)
    letter_bag = list(letter_bag)
    return letter_bag

def init_random(game_state: dict, letter_bag: list):
    """
    init_random takes a game state and randomizes it completely.

    This directly modifies the game_state dictionary.
    """
    for key in game_state:
        temp = ""
        for i in range(len(key)):
            temp += random.choice(letter_bag)
        game_state[key] = temp

def stringify_state(text: str, game_state: dict):
    """
    stringify_state takes some text and a game state dictionary and re-renders it with appropriate scrambling.
    """
    doc = get_doc(text)
    text = ""

    for token in doc:
        if (token.pos_ == "SPACE" and len(token.pos_) <= 2) or (token.pos_ == "PUNCT"):
            text += token.text

        else:
            if token.text in game_state:
                text += " " + game_state[token.text]
            else:
                text += " " + token.text

    return text

def guess_update(game_state: dict, guess: str, title: str):
    """
    guess_update updates the game_state based on the guess vs. title and returns the similairty between the two

    If the similarity of an individual word in the article passes the thresh_full, it is fully unscrambled.
    If the similarity of an individual word in the article passes the thresh_partial, it is half unscrambled.
    """
    global nlp, FULL_THRESH, FULL_MULTIPLIER, PARTIAL_THRESH, PARTIAL_MULTIPLIER, WIN_THRESH

    guess_spacy = nlp(guess)
    title_spacy = nlp(title)
    title_sim = guess_spacy.similarity(title_spacy)

    thresh_full = FULL_THRESH - title_sim*FULL_MULTIPLIER
    thresh_partial = PARTIAL_THRESH - title_sim*PARTIAL_MULTIPLIER

    win = title_sim > WIN_THRESH # Check if player has won

    print("thresh_full: " + str(thresh_full) + ", thresh_partial: " + str(thresh_partial))

    for key in game_state:
        key_spacy = nlp(key)
        sim = guess_spacy.similarity(key_spacy)

        blacklist = key in title # Skip full unscramble if the key is in the title unless win

        if win or (sim >= thresh_full and not blacklist):
            print("Full Unscrambling " + key)
            game_state[key] = key

        elif sim >= thresh_partial:
            print("Partial Unscrambling " + key)
            targets = random.sample(range(len(key)), int(len(key)/2))
            for i in targets:
                game_state[key] = game_state[key][:i] + key[i] + game_state[key][i+1:]
    
    # If the user has won, set the similarity score to 1.0
    if win:
        return 1.0
    
    # If the user has not won, return the similarity score
    return title_sim
    