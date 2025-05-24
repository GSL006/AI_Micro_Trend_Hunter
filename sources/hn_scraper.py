import requests
from tqdm import tqdm
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

AI_KEYWORDS = ["AI", "artificial intelligence", "machine learning", "deep learning", "neural", "LLM", "GPT", "agent"]

DATA_PATH = Path(__file__).parent.parent / "data"
DATA_PATH.mkdir(exist_ok=True)
HN_JSON_FILE = DATA_PATH / "hn_ai_stories.json"

def fetch_story_ids(endpoint="topstories", limit=200):
    url = f"{HN_API_BASE}/{endpoint}.json"
    response = requests.get(url)
    return response.json()[:limit]

def fetch_story_details(story_id):
    url = HN_ITEM_URL.format(story_id)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def is_ai_related(title):
    title = title.lower()
    return any(keyword.lower() in title for keyword in AI_KEYWORDS)

def scrape_hackernews_ai_stories(limit=200):
    story_ids = fetch_story_ids("newstories", limit)
    ai_stories = []

    for sid in tqdm(story_ids, desc="Fetching HN stories"):
        story = fetch_story_details(sid)
        if story and story.get("title") and is_ai_related(story["title"]):
            ai_stories.append({
                "title": story["title"],
                "url": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                "timestamp": story["time"]
            })

    return ai_stories

def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_from_json(filename):
    if filename.exists():
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

if __name__ == "__main__":
    stories = scrape_hackernews_ai_stories(limit=200)
    save_to_json(stories, HN_JSON_FILE)
    print(f"\n✅ Found {len(stories)} AI-related stories. Saved to {HN_JSON_FILE}\n")
    for s in stories:
        print(f"- {s['title']}\n  🔗 {s['url']}\n")
