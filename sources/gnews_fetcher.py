import requests
from tqdm import tqdm
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import os
import json

sys.stdout.reconfigure(encoding='utf-8')

# Load .env from current file's directory
# env_path = Path(__file__).parent / '.env'
# load_dotenv(dotenv_path=env_path)

GNEWS_API_URL = "https://gnews.io/api/v4/search"
API_KEY = os.getenv("GNEWS_API")

if not API_KEY:
    raise ValueError("GNEWS_API key not found in .env file")

AI_QUERY = "artificial intelligence OR machine learning OR deep learning OR GPT OR LLM OR agent OR neural"

DATA_PATH = Path(__file__).parent.parent / "data"
DATA_PATH.mkdir(exist_ok=True)
GNEWS_JSON_FILE = DATA_PATH / "gnews_ai_stories.json"

def fetch_gnews_ai_articles(max_pages=2, page_size=50):
    all_articles = []

    for page in tqdm(range(1, max_pages + 1), desc="Fetching GNews pages"):
        params = {
            "q": AI_QUERY,
            "lang": "en",
            "max": page_size,
            "page": page,
            "token": API_KEY
        }
        resp = requests.get(GNEWS_API_URL, params=params)
        if resp.status_code != 200:
            print(f"Error fetching GNews page {page}: {resp.status_code} {resp.text}")
            break

        data = resp.json()
        articles = data.get("articles", [])
        if not articles:
            break

        for a in articles:
            all_articles.append({
                "title": a.get("title"),
                "url": a.get("url"),
                "source": a.get("source", {}).get("name"),
                "publishedAt": a.get("publishedAt")
            })

        time.sleep(1)

    return all_articles

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_from_json(filename):
    if filename.exists():
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

if __name__ == "__main__":
    articles = fetch_gnews_ai_articles()
    save_to_json(articles, GNEWS_JSON_FILE)
    print(f"\n✅ Found {len(articles)} AI-related news articles on GNews. Saved to {GNEWS_JSON_FILE}\n")
    for art in articles:
        print(f"- {art['title']}\n  🔗 {art['url']}\n  📰 Source: {art['source']}\n  📅 Published: {art['publishedAt']}\n")
