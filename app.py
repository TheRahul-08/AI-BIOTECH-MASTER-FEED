from flask import Flask, Response
import feedparser, time, threading, requests
from datetime import datetime

app = Flask(__name__)

CACHE = {"data": "", "timestamp": 0}
REFRESH_INTERVAL = 15 * 60  # 15 minutes
PING_INTERVAL = 600  # 10 minutes

# ------------------ FETCH FEEDS ------------------
def fetch_feeds():
    with open("feeds.txt", "r") as f:
        urls = [u.strip() for u in f.readlines() if u.strip()]

    entries = []
    for url in urls:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries:
                entries.append({
                    "title": e.get("title", "No title"),
                    "link": e.get("link", ""),
                    "published": e.get("published_parsed", time.gmtime())
                })
        except Exception as err:
            print(f"⚠️ Error fetching {url}: {err}")

    entries.sort(key=lambda e: e["published"], reverse=True)
    rss = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss += "<rss version='2.0'><channel>\n"
    rss += "<title>AI BIOTECH MASTER FEED</title>\n"
    rss += "<link>https://ai-biotech-master-feed.onrender.com/master.rss</link>\n"
    rss += "<description>Merged dynamic feed for AI + Biotech news</description>\n"

    for e in entries[:100]:
        pub = datetime.fromtimestamp(time.mktime(e["published"]))
        rss += f"<item><title><![CDATA[{e['title']}]]></title><link>{e['link']}</link><pubDate>{pub}</pubDate></item>\n"

    rss += "</channel></rss>"
    return rss

# ------------------ CACHE UPDATER ------------------
def update_cache():
    while True:
        CACHE["data"] = fetch_feeds()
        CACHE["timestamp"] = time.time()
        print("✅ Feed cache updated.")
        time.sleep(REFRESH_INTERVAL)

# ------------------ KEEP RENDER AWAKE ------------------
def keep_awake():
    while True:
        try:
            url = "https://ai-biotech-master-feed.onrender.com/master.rss"
            requests.get(url, timeout=10)
            print(f"🔁 Pinged self to keep alive at {datetime.now()}")
        except Exception as e:
            print(f"Ping error: {e}")
        time.sleep(PING_INTERVAL)

# ------------------ MAIN ROUTE ------------------
@app.route("/master.rss")
def master_feed():
    if not CACHE["data"]:
        CACHE["data"] = fetch_feeds()
        CACHE["timestamp"] = time.time()
    return Response(CACHE["data"], mimetype="application/rss+xml")

if __name__ == "__main__":
    threading.Thread(target=update_cache, daemon=True).start()
    threading.Thread(target=keep_awake, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
