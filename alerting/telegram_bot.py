import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from this file's directory
# env_path = Path(__file__).parent / '.env'
# load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("Bot token or channel ID missing from .env")

def send_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    resp = requests.post(url, data=payload)
    if not resp.ok:
        print(f"Failed to send message: {resp.status_code} {resp.text}")

def send_microtrend_alerts(microtrends: dict):
    if not microtrends:
        send_message("⚠️ <b>No microtrends detected.</b>")
        return

    for cluster_id, info in microtrends.items():
        title_lines = [f"📌 <b>{a['title']}</b>\n🔗 {a['url']}" for a in info["articles"]]
        message = (
            f"🚨 <b>New Microtrend Detected</b> (Cluster {cluster_id})\n"
            f"🧠 Velocity: {info['velocity']}\n"
            f"📰 Count: {info['count']}\n\n"
            + "\n\n".join(title_lines[:5])
        )
        send_message(message)
