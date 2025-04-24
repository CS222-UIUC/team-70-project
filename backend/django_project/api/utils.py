"""
utils.py

This module contains the functions for game logic and NLP libraries, supporting API responses.

*Possibly use rapidfuzz down the line if needed down the line
*Possibly use an image editing library if needed down the line.
"""

import spacy
import random
from game.models import ArticleCache, DailyArticle, GameState, UserGuess
from django.contrib.auth.models import User
from django.utils import timezone

nlp = spacy.load("en_core_web_lg") # python -m spacy download en_core_web_lg
FULL_THRESH = 0.55          # Absolute similarity threshold for a word to be completely unscrambled
PARTIAL_THRESH = 0.3        # Partial similarity threshold for a word to be partially unscrambled
FULL_MULTIPLIER = 1         # Multiplier for full threshold reduction based on how close the guess is to title
PARTIAL_MULTIPLIER = 1.5    # Mulitplier for partial threshold reduction based on how close the guess is to title
WIN_THRESH = 0.95           # Threshold to pass to win the game
PUNCT_THRESH = 2            # Length threshold for punctuation to be considered a word instead (for weird formattings)

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
    except:
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
        game_state = GameState.objects.get(user=user)

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
        user_state = GameState.objects.get(user=user)
        for guess in user_state.guesses.all():
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
    user_state = GameState.objects.get(user=user).word_mapping
    user_scores = {}
    try:
        for guess in user_state.guesses.all():
            user_scores[guess.guess_text] = guess.score
    except:
        pass

    # Update user state and scores with game logic
    similarity = guess_update(user_state, guess, get_daily_article_title())
    score = similarity * 1000
    score = int(score)
    print("Score: " + str(score))
    if score < 0:
        score = 0
    user_scores[guess] = score

    
    print("New state:")
    print(user_state)


    # Update database with new state and scores
    game_state = GameState.objects.get(user=user)
    game_state.word_mapping = user_state # Update wordmapping in database
    game_state.save()
    UserGuess.objects.create(game_state=game_state, guess_text=guess, score=score, similarity_score=similarity) # Add a guess

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
    
    return title_sim
    