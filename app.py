from flask import Flask, Response
import feedparser
import requests
from datetime import datetime
import pytz
from xml.sax.saxutils import escape

app = Flask(__name__)

# ==============================
# 1️⃣ HOME ROUTE
# ==============================
@app.route('/')
def home():
    return "✅ AI Biotech Master Feed is running. Visit /master.rss for the merged RSS feed."

# ==============================
# 2️⃣ MAIN RSS ROUTE
# ==============================
@app.route('/master.rss')
def master_rss():
    return Response(generate_master_rss(), mimetype='application/rss+xml')

# ==============================
# 3️⃣ FUNCTION TO MERGE ALL FEEDS
# ==============================
def generate_master_rss():
    feeds = [
        "https://www.nature.com/subjects/biotechnology/rss.xml",
        "https://www.nature.com/subjects/artificial-intelligence/rss.xml",
        "https://feeds.feedburner.com/sciencedaily/biotechnology",
        "https://feeds.feedburner.com/sciencedaily/artificial_intelligence",
        "https://www.sciencedaily.com/rss/mind_brain/artificial_intelligence.xml",
        "https://www.sciencedaily.com/rss/plants_animals/biotechnology.xml",
        "https://www.genengnews.com/feed/",
        "https://synbiobeta.com/feed/",
        "https://www.frontiersin.org/journals/artificial-intelligence/rss",
        "https://www.frontiersin.org/journals/bioengineering-and-biotechnology/rss",
        "https://www.biorxiv.org/rss/current.xml",
        "https://www.medrxiv.org/rss/current.xml",
        "https://www.nature.com/nbt/current_issue/rss",
        "https://www.cell.com/trends/biotechnology/rss",
        "https://www.cell.com/trends/pharmacological-sciences/rss",
        "https://www.genomeweb.com/rss.xml",
        "https://blogs.nvidia.com/feed/",
        "https://www.ibm.com/blogs/research/feed/",
        "https://deepmind.google/feed",
        "https://openai.com/blog/rss/",
        "https://www.analyticsvidhya.com/blog/feed/",
        "https://venturebeat.com/category/ai/feed/",
        "https://techcrunch.com/tag/artificial-intelligence/feed/",
        "https://techcrunch.com/tag/biotech/feed/",
        "https://www.biopharmadive.com/feeds/news/",
        "https://www.fiercebiotech.com/rss.xml",
        "https://www.fiercepharma.com/rss.xml",
        "https://www.biospace.com/rss/news",
        "https://lifesciencesworld.com/feed/",
        "https://clinicaltrials.gov/ct2/results/rss.xml",
        "https://news.mit.edu/rss/topic/artificial-intelligence",
        "https://news.mit.edu/rss/topic/biotechnology",
        "https://www.wired.com/feed/category/science/latest/rss",
        "https://www.wired.com/feed/tag/biotech/latest/rss",
        "https://www.eurekalert.org/rss/technology_engineering.xml",
        "https://www.eurekalert.org/rss/medicine_health.xml",
        "https://medicalxpress.com/rss-feed/biotechnology-news/",
        "https://medicalxpress.com/rss-feed/artificial-intelligence-news/",
        "https://www.the-scientist.com/rss/news",
        "https://www.genomeweb.com/rss.xml",
        "https://pharmafield.co.uk/feed/",
        "https://www.nature.com/nature/articles?type=research-highlight&format=rss",
        "https://www.scientificamerican.com/rss/feed/",
        "https://feeds.feedburner.com/aiweekly",
        "https://feeds.feedburner.com/Biotechniques",
        "https://www.news-medical.net/tag/feed/biotechnology.aspx",
        "https://www.news-medical.net/tag/feed/artificial-intelligence.aspx",
        "https://www.biospace.com/rss/biotechnology-news/",
        "https://www.genengnews.com/feed/",
        "https://feeds.feedburner.com/Medgadget",
        "https://www.fiercebiotech.com/rss.xml"
    ]

    items = []
    for url in feeds:
        try:
            response = requests.get(url, timeout=10)
            feed = feedparser.parse(response.content)

            for entry in feed.entries[:5]:  # take top 5 from each feed
                title = escape(entry.get("title", "No title"))
                link = escape(entry.get("link", ""))
                summary = escape(entry.get("summary", ""))
                published = entry.get("published", datetime.now().isoformat())

                items.append(f"""
                    <item>
                        <title>{title}</title>
                        <link>{link}</link>
                        <description>{summary}</description>
                        <pubDate>{published}</pubDate>
                    </item>
                """)
        except Exception as e:
            print(f"⚠️ Skipped {url}: {e}")

    # Sort (roughly by most recent)
    items.sort(reverse=True)

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>AI Biotech Master Feed</title>
            <link>https://ai-biotech-master-feed.onrender.com/master.rss</link>
            <description>Merged feed combining 50+ top sources in AI & Biotech</description>
            {''.join(items)}
        </channel>
    </rss>"""
    return rss

# ==============================
# 4️⃣ RENDER ENTRY POINT
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
