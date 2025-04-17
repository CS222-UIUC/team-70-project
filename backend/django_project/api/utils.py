"""
utils.py

This module contains the functions for game logic and NLP libraries, supporting API responses.

*Possibly use rapidfuzz down the line if needed down the line
*Possibly use an image editing library if needed down the line.
"""

import spacy
import random

nlp = spacy.load("en_core_web_lg") # python -m spacy download en_core_web_lg
FULL_THRESH = 0.55          # Absolute similarity threshold for a word to be completely unscrambled
PARTIAL_THRESH = 0.4        # Partial similarity threshold for a word to be partially unscrambled
FULL_MULTIPLIER = 1         # Multiplier for full threshold reduction based on how close the guess is to title
PARTIAL_MULTIPLIER = 1.5    # Mulitplier for partial threshold reduction based on how close the guess is to title
WIN_THRESH = 0.95           # Threshold to pass to win the game
PUNCT_THRESH = 2            # Length threshold for punctuation to be considered a word instead (for weird formattings)

### TESTING VARIABLES ###
test_title = "Lorem ipsum"
test_text = '''
Lorem ipsum (/ˌlɔː.rəm ˈɪp.səm/ LOR-əm IP-səm) is a dummy or placeholder text commonly used in graphic design, publishing, and web development. Its purpose is to permit a page layout to be designed, independently of the copy that will subsequently populate it, or to demonstrate various fonts of a typeface without meaningful text that could be distracting. \n

Lorem ipsum is typically a corrupted version of De finibus bonorum et malorum, a 1st-century BC text by the Roman statesman and philosopher Cicero, with words altered, added, and removed to make it nonsensical and improper Latin. The first two words themselves are a truncation of dolorem ipsum ("pain itself"). \n

Versions of the Lorem ipsum text have been used in typesetting at least since the 1960s, when it was popularized by advertisements for Letraset transfer sheets.[1] Lorem ipsum was introduced to the digital world in the mid-1980s, when Aldus employed it in graphic and word-processing templates for its desktop publishing program PageMaker. Other popular word processors, including Pages and Microsoft Word, have since adopted Lorem ipsum,[2] as have many LaTeX packages,[3][4][5] web content managers such as Joomla! and WordPress, and CSS libraries such as Semantic UI.

A common form of Lorem ipsum reads:

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
'''

test_state = None     # Dictionary of str:str
test_scores = {}    # Dicitonary of str:int

### END TESTING VARS ###

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
    global test_text
    return {
        "main-text" : test_text
    } # TESTING output (should access stored daily article)

def get_daily_article_title():
    """
    get_daily_article_title returns the current daily article title from the database

    For UTIL use, NOT USER.
    """
    global test_title
    return test_title # TESTING output (should access stored daily article)

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
    global test_state
    if (user_id): # Dummy usage of user_id for now
        pass 

    # Access user state
    user_state = test_state

    # If user has no initialized game, initialize a game for them and update database
    if not user_state: # ALL TESTING BEHAVIOR CURRENTLY
        print("LOG: Generating game for UID: " + str(user_id))
        article_text = get_daily_article()["main-text"]
        user_state = generate_game(article_text) # TESTING behavior
        init_random(user_state, get_letter_bag(article_text))
        test_state = user_state

    #print("----- CURRENT USER STATE -----")
    #print(user_state)
    #print("------------------------------")
        
    # Scramble output text based on state
    maintext_out = stringify_state(get_daily_article()["main-text"], user_state)

    return {
        "request": "get_scrambled_article",
        "article": {
            "main-text" : maintext_out
        }
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
    global test_scores
    if (user_id): # Dummy usage of user_id for now
        pass 

    # Acess user scores
    user_scores = test_scores # TESTING behavior

    return {
        "request" : "get_guess_scoreboard",
        "scores" : user_scores
    }

def process_guess(user_id, guess: str):
    """
    process_guess processes guess for the user identified by user_id and updates their information in the database.

    For UTIL use, NOT USER.
    """
    global test_state, test_scores
    print("Processing guess: " + guess + " for " + str(user_id))
    
    # Acess user state and scores
    user_state = test_state     # TESTING input (should access stored state dict)
    user_scores = test_scores   # TESTING input (should access stored scores dict)

    # Update user state and scores with game logic
    score = guess_update(user_state, guess, get_daily_article_title()) * 1000
    score = int(score)
    print("Score: " + str(score))
    if score < 0:
        score = 0
    user_scores[guess] = score

    print("New state:")
    print(user_state)

    # Update database with new state and scores
    test_state = user_state     # TESTING behavior
    test_scores = user_scores   # TESTING behavior

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
    