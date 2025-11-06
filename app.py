from flask import Flask, Response
import feedparser
import requests
import pytz
from datetime import datetime
from xml.sax.saxutils import escape
import urllib3
import sys
import traceback

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

FEED_FILE = "feeds.txt"

def load_feeds():
    try:
        with open(FEED_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"❌ Error loading feeds.txt: {e}")
        return []

def safe_parse_feed(content, url):
    """Safely parse XML feed and catch all fatal errors."""
    try:
        feed = feedparser.parse(content)
        if feed.bozo or not getattr(feed, "entries", None):
            print(f"⚠️ Invalid or empty feed: {url}")
            return []
        return feed.entries
    except Exception as e:
        print(f"💥 XML parse failed for {url}: {e}")
        traceback.print_exc()
        return []

def fetch_feed(url):
    try:
        response = requests.get(url, timeout=15, verify=False)
        response.raise_for_status()
        return safe_parse_feed(response.content, url)
    except requests.exceptions.RequestException as e:
        print(f"🚫 Network error for {url}: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Unexpected error fetching {url}: {e}")
        traceback.print_exc()
        return []

@app.route("/")
def home():
    return """
    <h2>🚀 AI Biotech Master Feed is Live ✅</h2>
    <p>Visit <a href='/master.rss'>/master.rss</a> for the combined RSS feed.</p>
    """

@app.route("/master.rss")
def master_feed():
    try:
        feeds = load_feeds()
        if not feeds:
            return Response("feeds.txt missing or empty.", mimetype="text/plain")

        all_items = []
        for url in feeds:
            try:
                entries = fetch_feed(url)
                for entry in entries:
                    title = escape(entry.get("title", "No Title"))
                    link = escape(entry.get("link", ""))
                    description = escape(entry.get("summary", ""))
                    pub_date = entry.get("published", datetime.now().isoformat())
                    all_items.append((pub_date, title, link, description))
            except Exception as e:
                print(f"⚠️ Error processing {url}: {e}")
                traceback.print_exc()

        if not all_items:
            return Response("No valid feeds found.", mimetype="text/plain")

        # Sort by date (descending)
        all_items.sort(key=lambda x: x[0], reverse=True)

        rss_items = "".join(
            f"""
            <item>
                <title>{t}</title>
                <link>{l}</link>
                <description>{d}</description>
                <pubDate>{p}</pubDate>
            </item>"""
            for p, t, l, d in all_items[:100]
        )

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

    except SystemExit:
        print("❌ SystemExit blocked (feedparser abort). Continuing safely.")
        return Response("Internal error blocked. Some feeds are corrupted.", mimetype="text/plain")

    except Exception as e:
        print(f"💥 Top-level error: {e}")
        traceback.print_exc()
        return Response(f"Error: {e}", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
