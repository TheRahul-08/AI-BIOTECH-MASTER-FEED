from flask import Flask, Response
import feedparser
import requests
from bs4 import BeautifulSoup
import time
import threading

app = Flask(__name__)

# ✅ Reliable AI + Biotech RSS sources
FEEDS = [
    "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
    "https://www.sciencedaily.com/rss/health_medicine/biotechnology.xml",
    "https://www.genengnews.com/feed/",
    "https://www.fiercebiotech.com/rss",
    "https://www.nature.com/subjects/artificial-intelligence.rss",
    "https://www.nature.com/subjects/biotechnology.rss",
    "https://www.biopharmadive.com/feeds/news/",
    "https://www.statnews.com/feed/",
    "https://feeds.feedburner.com/TechCrunch/artificial-intelligence",
    "https://venturebeat.com/category/ai/feed/"
]

USER_AGENT = {"User-Agent": "Mozilla/5.0 (compatible; AI-BioFeedBot/1.0; +https://your-site.com)"}


@app.route('/')
def home():
    return "<h3>🧬 AI + Biotech Master Feed is Live</h3><p>Visit <a href='/master.rss'>/master.rss</a> to view combined RSS.</p>"


@app.route('/master.rss')
def master_feed():
    all_entries = []

    for url in FEEDS:
        try:
            print(f"🔗 Fetching: {url}")
            response = requests.get(url, headers=USER_AGENT, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.content)

            if not feed.entries:
                print(f"⚠️ Invalid or empty feed: {url}")
                continue

            for entry in feed.entries[:5]:  # limit to 5 per source
                title = entry.get("title", "No title")
                link = entry.get("link", "#")
                published = entry.get("published", "No date")
                summary = entry.get("summary", "")
                all_entries.append((published, title, link, summary))

        except Exception as e:
            print(f"🚫 Error fetching {url}: {e}")
            continue

    # Sort by date (if available)
    all_entries.sort(key=lambda x: x[0], reverse=True)

    # Build combined RSS XML
    rss_items = ""
    for pub, title, link, summary in all_entries:
        clean_summary = BeautifulSoup(summary, "html.parser").get_text()
        rss_items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <description><![CDATA[{clean_summary}]]></description>
            <pubDate>{pub}</pubDate>
        </item>
        """

    rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>AI + Biotech Master Feed</title>
            <link>https://ai-biotech-master-feed.onrender.com/</link>
            <description>Combined RSS feed of AI and Biotech news</description>
            {rss_items}
        </channel>
    </rss>"""

    return Response(rss_feed, mimetype='application/rss+xml')


# 🌐 Keep-alive thread for Render
def keep_alive():
    while True:
        try:
            url = "https://ai-biotech-master-feed.onrender.com/"
            requests.get(url, timeout=10)
            print("💤 Pinged self to stay awake.")
        except Exception as e:
            print(f"Keep-alive error: {e}")
        time.sleep(300)  # every 5 minutes


if __name__ == "__main__":
    # Start keep-alive thread
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
