import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from typing import List, Dict
from datetime import datetime
import time

# Download required nltk data (only first time)
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

STOPWORDS = set(stopwords.words('english'))
LEMMATIZER = WordNetLemmatizer()

def preprocess_text(text: str) -> str:
    # Lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    # Tokenize by splitting on whitespace
    tokens = text.split()

    # Remove stopwords and lemmatize
    tokens = [LEMMATIZER.lemmatize(token) for token in tokens if token not in STOPWORDS]

    # Join back to string
    return ' '.join(tokens)

def preprocess_titles(articles: List[Dict]) -> List[str]:
    """
    Takes a list of article dicts with a 'title' key and returns
    a list of preprocessed titles as strings.
    """
    processed = []
    for article in articles:
        title = article.get('title', '')
        if title:
            processed_title = preprocess_text(title)
            processed.append(processed_title)
    return processed

def normalize_articles(articles: List[Dict]) -> List[Dict]:
    """
    Normalize articles by adding a 'timestamp' field as UNIX int timestamp.
    Converts 'publishedAt' ISO8601 strings if necessary.
    """
    for article in articles:
        if 'timestamp' in article and isinstance(article['timestamp'], int):
            continue  # already normalized
        elif 'publishedAt' in article:
            try:
                dt = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                article['timestamp'] = int(dt.timestamp())
            except Exception:
                article['timestamp'] = int(time.time())
        else:
            # If no timestamp info, fallback to current time
            article['timestamp'] = int(time.time())
    return articles
