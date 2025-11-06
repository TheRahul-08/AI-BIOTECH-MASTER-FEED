from flask import Flask, Response
import feedparser
from datetime import datetime
import pytz

app = Flask(__name__)

# 📰 --- Add all your feeds here ---
FEED_URLS = [
    # Tech + AI
    "https://techcrunch.com/feed/",
    "https://thenextweb.com/feed/",
    "https://venturebeat.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss",
    "https://feeds.feedburner.com/blogspot/gJZg",
    "https://www.analyticsvidhya.com/blog/feed/",
    "https://www.datacamp.com/feed",
    "https://www.technologyreview.com/feed/",
    "https://spectrum.ieee.org/rss/fulltext",

    # Climate + Energy
    "https://www.carbonbrief.org/feed/",
    "https://climate.nasa.gov/rss/news/",
    "https://cleantechnica.com/feed/",
    "https://www.greenbiz.com/rss.xml",
    "https://www.weforum.org/agenda/archive/climate-change/feed",
    "https://www.unep.org/news-and-stories/rss.xml",
    "https://www.renewableenergyworld.com/feed/",
    "https://grist.org/feed/",
    "https://www.energy.gov/rss/",
    "https://www.bloomberg.com/feed/podcast/climate-show.xml",

    # Business + Finance
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://www.moneycontrol.com/rss/MCtopnews.xml",
    "https://www.investopedia.com/feed",
    "https://feeds.feedburner.com/entrepreneur/latest",
    "https://www.bloomberg.com/feed/podcast/businessweek.xml",
    "https://www.reuters.com/business/rss",
    "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "https://fortune.com/feed/",
    "https://www.business-standard.com/rss/home_page_top_stories.rss",
    "https://www.businesstoday.in/rssfeeds/?id=0",

    # Indian Science + Tech
    "https://www.isro.gov.in/rss.xml",
    "https://www.drdo.gov.in/drdo/rss.xml",
    "https://www.csir.res.in/rss.xml",
    "https://dst.gov.in/rss.xml",
    "https://www.niti.gov.in/rss.xml",

    # Health + BioTech
    "https://www.nih.gov/news-events/news-releases/rss.xml",
    "https://www.nature.com/subjects/biotechnology.rss",
    "https://www.sciencedaily.com/rss/health_medicine.xml",
    "https://www.medicalnewstoday.com/rss",
    "https://www.fiercebiotech.com/rss",
    "https://www.biospace.com/rss/",
    "https://www.frontiersin.org/rss",
    "https://feeds.feedburner.com/geneticliteracyproject",
    "https://www.clinicaltrialsarena.com/feed/",
    "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds",

    # News + Politics
    "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
    "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    "https://www.theguardian.com/world/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.bbc.com/news/world/rss.xml",
    "https://indianexpress.com/feed/",
    "https://scroll.in/feed",
    "https://www.deccanherald.com/rss.xml",
    "https://www.ndtv.com/rss"
]

# 🧠 Helper function to merge feeds
def generate_master_rss():
    all_items = []
    for url in FEED_URLS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:  # take top 5 from each
                all_items.append({
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": feed.feed.get("title", "Unknown Source")
                })
        except Exception as e:
            print(f"Error reading {url}: {e}")

    # Sort by publish date (if available)
    all_items = sorted(all_items, key=lambda x: x["published"], reverse=True)

    # Create RSS XML
    rss_items = ""
    for item in all_items:
        rss_items += f"""
        <item>
            <title>{item['title']}</title>
            <link>{item['link']}</link>
            <description>Source: {item['source']}</description>
            <pubDate>{item['published']}</pubDate>
        </item>
        """

    rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
    <channel>
        <title>Master Global Feed</title>
        <link>https://yourapp.onrender.com/master.rss</link>
        <description>Combined AI + Climate + Business + Science Feed</description>
        <language>en-us</language>
        {rss_items}
    </channel>
    </rss>"""

    return rss_feed


@app.route("/")
def home():
    return """
    <h1>🌐 Master RSS Feed is Live!</h1>
    <p>Visit <a href='/master.rss'>/master.rss</a> to view the unified feed.</p>
    """


@app.route("/master.rss")
def master_rss():
    return Response(generate_master_rss(), mimetype="application/rss+xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
