from flask import Flask, Response
import feedparser
import requests
from bs4 import BeautifulSoup
import time
import threading
import traceback
import html

app = Flask(__name__)

# ✅ Stable & verified AI + Biotech feeds
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

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AI-BioFeedBot/1.0; +https://your-site.com)"}


@app.route('/')
def home():
    return "<h3>🧬 AI + Biotech Master Feed is Live</h3><p>Visit <a href='/master.rss'>/master.rss</a> to view combined RSS.</p>"


@app.route('/master.rss')
def master_feed():
    all_entries = []
    bad_feeds = []

    for url in FEEDS:
        try:
            print(f"🔗 Fetching: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()

            feed = feedparser.parse(response.content)
            if not feed.entries:
                bad_feeds.append(url)
                print(f"⚠️ Empty or invalid feed: {url}")
                continue

            for entry in feed.entries[:5]:
                title = entry.get("title", "No Title")
                link = entry.get("link", "")
                published = entry.get("published", "No date")
                summary = entry.get("summary", "")

                # Sanitize HTML and handle broken Unicode
                clean_summary = BeautifulSoup(summary, "html.parser").get_text()
                clean_summary = html.escape(clean_summary)
                clean_title = html.escape(title)

                all_entries.append((published, clean_title, link, clean_summary))

        except Exception as e:
            bad_feeds.append(url)
            print(f"🚫 Failed {url}: {e}")
            traceback.print_exc()
            continue

    # Sort and build RSS
    all_entries.sort(key=lambda x: x[0], reverse=True)
    rss_items = ""
    for pub, title, link, summary in all_entries:
        rss_items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <description><![CDATA[{summary}]]></description>
            <pubDate>{pub}</pubDate>
        </item>
        """

    # If all feeds failed
    if not all_entries:
        rss_items = "<item><title>No feeds available</title><description>All sources failed or blocked.</description></item>"

    bad_msg = "".join([f"<li>{b}</li>" for b in bad_feeds])
    rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>AI + Biotech Master Feed</title>
            <link>https://ai-biotech-master-feed.onrender.com/</link>
            <description>Combined RSS feed of AI and Biotech news</description>
            <badfeeds>{bad_msg}</badfeeds>
            {rss_items}
        </channel>
    </rss>"""

    return Response(rss_feed, mimetype="application/rss+xml")


# 🌐 Keep-alive system for Render
def keep_alive():
    while True:
        try:
            requests.get("https://ai-biotech-master-feed.onrender.com/", timeout=10)
            print("💤 Self-ping success.")
        except Exception as e:
            print(f"Keep-alive failed: {e}")
        time.sleep(300)  # every 5 mins


if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
