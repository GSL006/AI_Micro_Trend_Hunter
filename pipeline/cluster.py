import numpy as np
import hdbscan
import time
from typing import List, Dict

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
    Group articles by their cluster label.
    Cluster label -1 means noise (unclustered).
    """
    clusters = {}
    for idx, label in enumerate(cluster_labels):
        if label == -1:
            continue  # skip noise
        clusters.setdefault(label, []).append(articles[idx])
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
    Extract simple keywords from article titles using frequency.
    Placeholder: you can replace with TF-IDF or other NLP methods.
    """
    from collections import Counter
    import re

    words = []
    for a in articles:
        # Basic tokenize: split on non-alphabetic chars and lowercase
        tokens = re.findall(r'\b[a-z]{3,}\b', a['title'].lower())
        words.extend(tokens)
    most_common = [w for w, _ in Counter(words).most_common(top_n)]
    return most_common

def find_microtrends(
    clusters,
    velocity_threshold=0.4,    # lower normalized velocity threshold
    min_cluster_size=3,        # smaller cluster allowed
    min_recent_articles=2,     # fewer recent articles required
    time_window_seconds=3600,
    tau=1800,                  # slower decay for velocity
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
        velocity_norm = velocity / len(articles)

        recent_articles = sum(1 for a in articles if (now - a.get('timestamp', now)) <= time_window_seconds)

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
