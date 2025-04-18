def generate_scrambled_text(content):
    """Generate scrambled text from article content

    This function takes the article content and creates a word mapping dictionary
    where keys are original words and values are scrambled versions.
    """
    words = content.lower().split()
    word_mapping = {}

    for word in words:
        if word not in word_mapping:
            # Simple scrambling for demonstration - in real implementation,
            # use more sophisticated NLP techniques
            if len(word) > 3:
                letters = list(word)
                # Keep first and last letter, scramble the rest
                middle = letters[1:-1]
                import random
                random.shuffle(middle)
                scrambled = letters[0] + ''.join(middle) + letters[-1]
                word_mapping[word] = scrambled
            else:
                # For short words, just reverse them
                word_mapping[word] = word[::-1]

    return word_mapping


def calculate_guess_score(guess, actual):
    """Calculate score and similarity between guess and actual article title

    Returns a tuple of (score, similarity)
    """
    guess = guess.lower()
    actual = actual.lower()

    # Simple similarity measure - in real implementation,
    # use more sophisticated NLP techniques like word embeddings
    import difflib
    similarity = difflib.SequenceMatcher(None, guess, actual).ratio()

    # Calculate score based on similarity
    score = int(similarity * 1000)

    return score, similarity
