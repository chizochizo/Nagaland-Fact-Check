import re

# Common English stopwords (standard set)
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "is", "if", "then", "else", "at", "by",
    "from", "for", "in", "out", "on", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can",
    "will", "just", "don", "should", "now"
}


def clean_and_tokenize(text):
    """
    Standardizes text for both indexing and searching:
    1. Lowercase
    2. Remove punctuation
    3. Remove extra whitespace
    4. Remove stopwords
    """
    if not text:
        return []

    # Lowercase and remove punctuation/special characters
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Split into words and remove extra whitespace
    tokens = text.split()

    # Remove stopwords
    tokens = [t for t in tokens if t not in STOPWORDS]

    return tokens
