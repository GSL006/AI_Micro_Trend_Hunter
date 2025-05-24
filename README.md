Sure! Here's a clear, professional, and informative README.md file for your **MicroTrendHunter** GitHub repo:

---

# MicroTrendHunter

**Real-time AI Microtrend Detection and Alert System**

---

## Overview

MicroTrendHunter is a lightweight pipeline that automatically fetches recent AI-related news articles, clusters them using semantic embeddings, and detects *microtrends*—small, emerging trends that have growing momentum but aren’t mainstream yet.

It analyzes article velocity and freshness to surface trends early, helping you stay ahead in the fast-moving AI landscape.

---

## Features

* **Automated hourly fetching** of AI news from multiple sources (GNews, Hacker News, etc.)
* **Semantic clustering** using HDBSCAN on article embeddings
* **Velocity-based microtrend detection** focusing on recent and fast-growing clusters
* **Real-time alerts** sent to a Telegram channel *only when* new microtrends are detected
* **Zero-cost, hands-free operation** deployed via GitHub Actions with no manual intervention

---

## Tech Stack

* Python 3.10
* [HDBSCAN](https://hdbscan.readthedocs.io/en/latest/) for clustering
* [Sentence Transformers](https://www.sbert.net/) or similar for embeddings
* Requests and other standard libs for data fetching
* GitHub Actions for automated scheduling and deployment
* Telegram Bot API for notifications

---

## How It Works

1. **Fetch articles**: Pulls recent AI-related articles every hour using APIs like GNews.
2. **Embed & cluster**: Converts article titles/text to embeddings and clusters them with HDBSCAN.
3. **Compute velocity**: Scores clusters by recency-weighted article velocity (exponential decay).
4. **Filter microtrends**: Clusters with minimum size, fresh article count, and velocity threshold are flagged as microtrends.
5. **Send alerts**: Posts detected microtrends summaries to a Telegram channel in real-time.

---

## Setup & Usage

1. **Clone the repo**

   ```bash
   git clone https://github.com/yourusername/MicroTrendHunter.git
   cd MicroTrendHunter
   ```

2. **Create `.env` file** and add your API keys

   ```env
   GNEWS_API=your_gnews_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHANNEL_ID=your_telegram_channel_id
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the pipeline manually**

   ```bash
   python main.py
   ```

5. **Deploy with GitHub Actions**

   The workflow runs every hour automatically and sends alerts when microtrends are detected.

---

## Join the Telegram Channel for Live Alerts

[https://t.me/AI\_Micro\_Trend\_Hunter](https://t.me/AI_Micro_Trend_Hunter)
