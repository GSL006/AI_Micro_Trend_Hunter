import numpy as np
import hdbscan
import time
from typing import List, Dict

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

def cluster_embeddings(embeddings: np.ndarray, min_cluster_size=5, verbose=False):
    """
    Cluster embeddings using HDBSCAN and return cluster labels.
    """
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size, metric='euclidean')
    cluster_labels = clusterer.fit_predict(embeddings)
    
    if verbose:
        from collections import Counter
        print(f"[Clustering] Cluster label distribution: {Counter(cluster_labels)}")
    
    return cluster_labels

def group_articles_by_cluster(articles: List[Dict], cluster_labels: np.ndarray) -> Dict[int, List[Dict]]:
    """
    Group articles by their cluster label and remove duplicates by title.
    Cluster label -1 means noise (unclustered).
    """
    clusters = {}
    seen_titles = set()

    for idx, label in enumerate(cluster_labels):
        if label == -1:
            continue  # skip noise

        article = articles[idx]
        title_key = article['title'].strip().lower()
        if title_key in seen_titles:
            continue  # skip duplicate
        seen_titles.add(title_key)

        clusters.setdefault(label, []).append(article)

    return clusters

def time_decay_velocity_score(cluster_articles: List[Dict], tau=1200, time_window_seconds=3600, verbose=False):
    """
    Compute velocity score with exponential decay on article recency.
    More recent articles contribute more.
    tau controls decay speed (smaller = faster decay).
    """
    now = time.time()
    score = 0.0
    for a in cluster_articles:
        age = now - a.get('timestamp', now)
        if age <= time_window_seconds:
            weight = np.exp(-age / tau)
            score += weight
    if verbose:
        print(f"[Velocity] Time-decay velocity score: {score:.2f} over {len(cluster_articles)} articles.")
    return score

def extract_keywords(articles: List[Dict], top_n=5):
    """
    Extract keywords using TF-IDF from article titles,
    combining sklearn and NLTK English stop words.
    """
    combined_stop_words = set(stopwords.words('english')).union(ENGLISH_STOP_WORDS)

    titles = [a['title'] for a in articles]
    vectorizer = TfidfVectorizer(stop_words=combined_stop_words, token_pattern=r'\b[a-zA-Z]{3,}\b')
    tfidf_matrix = vectorizer.fit_transform(titles)
    
    summed_tfidf = tfidf_matrix.sum(axis=0)
    scores = [(word, summed_tfidf[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    sorted_keywords = sorted(scores, key=lambda x: x[1], reverse=True)
    
    return [w for w, _ in sorted_keywords[:top_n]]

def find_microtrends(
    clusters,
    velocity_threshold=0.4,
    min_cluster_size=3,
    min_recent_articles=1,
    time_window_seconds=3600,
    tau=1800,
    verbose=True
) -> Dict[int, Dict]:
    """
    Return clusters that satisfy stricter microtrend conditions.
    """
    microtrends = {}
    now = time.time()
    for cluster_id, articles in clusters.items():
        if len(articles) < min_cluster_size:
            if verbose:
                print(f"[Filter] Cluster {cluster_id} skipped: size={len(articles)} < {min_cluster_size}")
            continue

        velocity = time_decay_velocity_score(articles, tau, time_window_seconds, verbose)

        recent_articles = sum(1 for a in articles if (now - a.get('timestamp', now)) <= time_window_seconds)
        velocity_norm = velocity / recent_articles if recent_articles > 0 else 0

        if verbose:
            print(f"[Microtrend] Cluster {cluster_id} size={len(articles)} velocity={velocity:.2f} norm={velocity_norm:.2f} recent_articles={recent_articles}")

        if velocity_norm >= velocity_threshold and recent_articles >= min_recent_articles:
            keywords = extract_keywords(articles)
            microtrends[cluster_id] = {
                "articles": articles,
                "velocity": velocity,
                "velocity_norm": velocity_norm,
                "count": len(articles),
                "recent_articles": recent_articles,
                "keywords": keywords
            }
            if verbose:
                print(f"[Microtrend] Cluster {cluster_id} accepted with keywords: {keywords}")
    return microtrends
