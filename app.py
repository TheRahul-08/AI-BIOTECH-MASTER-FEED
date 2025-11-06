from flask import Flask, Response
import feedparser
import pytz
from datetime import datetime
import requests

app = Flask(__name__)

# List of all your RSS feed URLs
RSS_FEEDS = [
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

@app.route("/master.rss")
def master_rss():
    combined_items = []
    now = datetime.now(pytz.utc)

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)

            # If feed parsing fails (network or SSL)
            if feed.bozo:
                print(f"⚠️ Skipped {url}: {feed.bozo_exception}")
                continue

            for entry in feed.entries[:5]:  # take top 5 per feed
                published = getattr(entry, "published", None)
                title = getattr(entry, "title", "No title")
                link = getattr(entry, "link", "#")
                summary = getattr(entry, "summary", "No summary")

                combined_items.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "published": published or now.isoformat()
                })
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            continue

    # Sort by date (if available)
    combined_items = sorted(
        combined_items, key=lambda x: x["published"], reverse=True
    )

    # Build XML safely
    rss = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss += '<rss version="2.0">\n<channel>\n'
    rss += "<title>AI Biotech Master Feed</title>\n"
    rss += "<description>Aggregated feed from biotech news sources</description>\n"
    rss += "<link>https://ai-biotech-master-feed.onrender.com/</link>\n"

    for item in combined_items:
        rss += f"<item>\n<title>{item['title']}</title>\n"
        rss += f"<link>{item['link']}</link>\n"
        rss += f"<description>{item['summary']}</description>\n"
        rss += f"<pubDate>{item['published']}</pubDate>\n</item>\n"

    rss += "</channel>\n</rss>"

    return Response(rss, mimetype="application/rss+xml")


# 🔹 Render entry point (important)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
