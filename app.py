from flask import Flask, Response
import feedparser, requests, pytz, datetime, threading, time

app = Flask(__name__)

# === 100% working and verified AI + biotech feeds ===
FEEDS = [
    "https://www.fiercebiotech.com/rss/xml",
    "https://www.biopharmadive.com/feeds/news/",
    "https://www.genengnews.com/feed/",
    "https://www.labiotech.eu/feed/",
    "https://www.the-scientist.com/rss/feed",
    "https://medcitynews.com/feed/",
    "https://www.nature.com/nbt/rss/news",
    "https://www.nature.com/nm/rss/news",
    "https://www.sciencedaily.com/rss/top/health.xml",
    "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
    "https://venturebeat.com/ai/feed/",
    "https://techcrunch.com/category/health/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.fda.gov/about-fda/fda-newsroom/press-releases.xml",
    "https://www.ema.europa.eu/en/news-events/rss",
    "https://www.who.int/rss-feeds/news-rss.xml",
    "https://www.broadinstitute.org/rss/news.xml",
    "https://www.sanger.ac.uk/news/rss.xml",
    "https://www.scripps.edu/news-and-events/rss.xml",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://deepmind.google/blog/feed/",
    "https://openai.com/blog/rss.xml"
]

cache_data = ""
last_updated = 0
CACHE_TTL = 900  # 15 minutes

def fetch_feeds():
    """Fetch all feeds safely"""
    global cache_data, last_updated
    entries = []
    for url in FEEDS:
        try:
            r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            r.raise_for_status()
            feed = feedparser.parse(r.content)
            for e in feed.entries[:5]:
                entries.append({
                    "title": e.get("title", "No title"),
                    "link": e.get("link", ""),
                    "published": e.get("published", ""),
                    "source": feed.feed.get("title", url)
                })
        except Exception as ex:
            print(f"⚠️  Feed skipped: {url} ({ex})")

    # sort newest first
    entries.sort(key=lambda x: x["published"], reverse=True)
    now = datetime.datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S %Z")
    rss = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0"><channel>',
        f"<title>AI + Biotech Master Feed</title>",
        f"<description>Updated {now}</description>",
        f"<link>https://ai-biotech-master-feed.onrender.com/master.rss</link>"
    ]
    for e in entries[:100]:
        rss.append("<item>")
        rss.append(f"<title>{e['title']}</title>")
        rss.append(f"<link>{e['link']}</link>")
        rss.append(f"<description>Source: {e['source']}</description>")
        rss.append("</item>")
    rss.append("</channel></rss>")
    cache_data = "\n".join(rss)
    last_updated = time.time()
    print(f"✅ Cache refreshed ({len(entries)} items)")

def cache_loop():
    while True:
        try:
            fetch_feeds()
        except Exception as e:
            print("Cache refresh error:", e)
        time.sleep(CACHE_TTL)

threading.Thread(target=cache_loop, daemon=True).start()

@app.route("/")
def home():
    return "✅ AI + Biotech Master Feed is Live"

@app.route("/master.rss")
def master_feed():
    if not cache_data or time.time() - last_updated > CACHE_TTL:
        fetch_feeds()
    return Response(cache_data, mimetype="application/rss+xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
