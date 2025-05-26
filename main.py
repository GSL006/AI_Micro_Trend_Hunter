import json
import os
import numpy as np
from sources import hn_scraper, gnews_fetcher
from pipeline.preprocess import preprocess_titles, normalize_articles  # import normalize_articles
from pipeline.embed import embed_titles
from pipeline import cluster
from alerting import telegram_bot
import time

DATA_DIR = "data"

def save_json(data, filename):
    with open(os.path.join(DATA_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filename):
    path = os.path.join(DATA_DIR, filename) 
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("=== Starting MicroTrendHunter ===")

    # Scrape & save raw data
    print("Scraping Hacker News AI stories...")
    hn_stories = hn_scraper.scrape_hackernews_ai_stories(limit=200)
    save_json(hn_stories, "hn_stories.json")

    print("Scraping GNews AI articles...")
    gnews_articles = gnews_fetcher.fetch_gnews_ai_articles(max_pages=2, page_size=50)
    save_json(gnews_articles, "gnews_articles.json")

    all_articles = hn_stories + gnews_articles

    # Normalize timestamps (adds 'timestamp' key in UNIX int format)
    print("Normalizing article timestamps...")
    normalized_articles = normalize_articles(all_articles)

    # Preprocess titles from normalized articles
    print("Preprocessing article titles...")
    clean_titles = preprocess_titles(normalized_articles)

    # Embed titles
    print("Embedding titles...")
    embeddings = embed_titles(clean_titles)
    np.save(os.path.join(DATA_DIR, "embeddings.npy"), embeddings)

    # Cluster embeddings
    print("Clustering embeddings...")
    cluster_labels = cluster.cluster_embeddings(embeddings, min_cluster_size=2, verbose=True)

    # Group articles by clusters
    clusters = cluster.group_articles_by_cluster(normalized_articles, cluster_labels)

    # Detect microtrends based on velocity
    print("Detecting microtrends...")
    microtrends = cluster.find_microtrends(
        clusters,
        velocity_threshold=0.5,     # allow velocity_norm >= 0.3 (30% "freshness")
        time_window_seconds=3600,   # last 1 hour articles considered recent
        min_cluster_size=3,         # clusters at least size 3
        min_recent_articles=1,      # at least 2 recent articles
        tau=1800,                  # slower decay (30 min)
        verbose=True
    )

    print(f"✅ Detected {len(microtrends)} microtrends.")

    # Save for inspection
    # Convert non-serializable keys (like numpy.int64) to int
    microtrends_serializable = {int(k): v for k, v in microtrends.items()}
    save_json(microtrends_serializable, "microtrends.json")

    # Alerting
    if microtrends:
        print("Sending alerts for microtrends...")
        telegram_bot.send_microtrend_alerts(microtrends)

    print("=== Pipeline complete ===")

if __name__ == "__main__":
    main()
