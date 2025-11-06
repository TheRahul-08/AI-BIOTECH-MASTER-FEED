from flask import Flask, Response
import feedparser
import requests
import pytz
from datetime import datetime
from xml.sax.saxutils import escape
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

FEED_FILE = "feeds.txt"

def load_feeds():
    with open(FEED_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def fetch_feed(url):
    try:
        # Ignore SSL certificate issues
        response = requests.get(url, timeout=15, verify=False)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        if feed.bozo:
            print(f"⚠️ Skipped {url}: {feed.bozo_exception}")
            return []
        return feed.entries
    except Exception as e:
        print(f"⚠️ Skipped {url}: {e}")
        return []

@app.route("/")
def home():
    return """
    <h2>🚀 AI Biotech Master Feed is Live ✅</h2>
    <p>Visit <a href='/master.rss'>/master.rss</a> for the combined feed.</p>
    """

@app.route("/master.rss")
def master_feed():
    feeds = load_feeds()
    all_items = []

    for url in feeds:
        entries = fetch_feed(url)
        for entry in entries:
            try:
                title = escape(entry.get("title", "No Title"))
                link = escape(entry.get("link", ""))
                description = escape(entry.get("summary", ""))
                pub_date = entry.get("published", datetime.now().isoformat())
                all_items.append((pub_date, title, link, description))
            except Exception as e:
                print(f"⚠️ Error parsing entry from {url}: {e}")

    if not all_items:
        return Response("No valid feeds available.", mimetype="text/plain")

    # Sort by date (descending)
    all_items.sort(key=lambda x: x[0], reverse=True)

    rss_items = ""
    for pub_date, title, link, description in all_items[:100]:
        rss_items += f"""
        <item>
            <title>{title}</title>
            <link>{link}</link>
            <description>{description}</description>
            <pubDate>{pub_date}</pubDate>
        </item>"""

    rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>AI Biotech Master Feed</title>
            <link>https://ai-biotech-master-feed.onrender.com/master.rss</link>
            <description>Aggregated AI + Biotech News Feed</description>
            {rss_items}
        </channel>
    </rss>"""

    return Response(rss_feed, mimetype="application/rss+xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
