from flask import Flask, Response
import feedparser
import requests
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

app = Flask(__name__)

# === CONFIGURATION ===
FEED_TITLE = "AI Biotech Master Feed"
FEED_DESCRIPTION = "Unified feed of all AI and Biotech updates"
FEED_LINKS = [
    "https://www.forbes.com/sites/brucebooth/feed/",
    "https://www.forbes.com/sites/luketimmerman/feed/",
    "https://news.crunchbase.com/sections/ai/feed/",
    "https://news.crunchbase.com/feed/",
    "https://atlasventure.com/feed",
    "https://news.google.com/news/rss/search?q=Andreessen%20Horowitz&hl=en",
    "https://a16z.com/feed/",
    "https://www.iarpa.gov/?format=feed&type=rss",
    "https://medium.com/feed/@arpa",
    "https://www.darpa.mil/rss.xml",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCOIHBHRbvncMo7Bf0Vx1zEQ",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCK8f1CUe8y403u3b0gCINww",
    "http://feed43.com/7331305475826068.xml",
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCZD1LLp6e838Iw_UTMcxQiQ",
    "http://www.admin.cam.ac.uk/news/newsfeeds/all.xml",
    "https://www.hopkinsmedicine.org/RSS/HopkinsRSS.xml",
    "https://podcasts.hopkinsmedicine.org/category/podcasts/feed/",
    "https://news.harvard.edu/gazette/section/health-medicine/feed/",
    "https://www.trumba.com/calendars/harvardmedicalschool.rss",
    "https://news.harvard.edu/gazette/section/science-technology/feed/",
    "https://news.mit.edu/rss/topic/health-sciences-and-technology",
    "https://web.mit.edu/newsoffice/topic/mitcomputers-rss.xml",
    "https://cordis.europa.eu/search/result_en?format=rss&srt=/news/contentUpdateDate:decreasing&q=contenttype=%27news%27%20AND%20language=%27en%27",
    "https://grants.nih.gov/grants/guide/newsfeed/fundingopps.xml",
    "https://www.nih.gov/news-releases/feed.xml",
    "https://www.who.int/rss-feeds/news-english.xml",
    "https://clinicaltrials.gov/ct2/results/rss.xml",
    "https://worldwide.espacenet.com/websyndication/searchFeed?DB=EPODOC&ST=singleline&locale=en_EP&query=additive+manufacturing+metal",
    "https://research.microsoft.com/rss/news.xml",
    "https://devblogs.nvidia.com/feed/",
    "https://blogs.nvidia.com/feed/",
    "https://blogs.nvidia.com/blog/category/deep-learning/feed/",
    "https://developer.nvidia.com/blog/category/generative-ai/feed/",
    "https://deepmind.google/blog/feed/basic/",
    "https://www.thelancet.com/rssfeed/lanonc_online.xml",
    "https://www.thelancet.com/rssfeed/lanpsy_online.xml",
    "https://www.thelancet.com/rssfeed/laninf_online.xml",
    "https://www.thelancet.com/rssfeed/lanpub_current.xml",
    "https://www.thelancet.com/rssfeed/lanres_online.xml",
    "https://www.thelancet.com/rssfeed/langlo_online.xml",
    "https://www.thelancet.com/rssfeed/lanhiv_online.xml",
    "https://www.thelancet.com/rssfeed/landia_online.xml",
    "https://www.thelancet.com/rssfeed/laneur_online.xml",
    "https://www.thelancet.com/rssfeed/lanhae_online.xml",
    "http://feeds.nature.com/nrd/rss/current",
    "https://www.nature.com/nbt/current_issue/rss/",
    "https://www.nature.com/subjects/computational-biology-and-bioinformatics.rss",
    "https://www.biomedcentral.com/bmcbioinformatics/latest/rss",
    "https://techcrunch.com/tag/healthtech/feed/",
    "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "https://techcrunch.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://venturebeat.com/feed/",
    "https://www.genengnews.com/feed/",
    "https://www.biospace.com/articlesrss/",
    "https://www.biopharmadive.com/feeds/news/",
    "https://www.bioworld.com/rss/articles",
    "https://pharmaphorum.com/rssfeed/news-and-features",
    "https://www.pharmavoice.com/feed/",
    "https://investors.pfizer.com/rss/pressrelease.aspx",
    "https://www.roche.com/med_news_xml.xml",
    "https://www.gsk.com/en-gb/media/rss/",
    "http://www.novartis.com/rss/en.xml",
    "http://feeds.plos.org/ploscompbiol/NewArticles",
    "https://chemrxiv.org/engage/rss/chemrxiv?categoryId=605c72ef153207001f6470ce",
    "https://connect.medrxiv.org/medrxiv_xml.php?subject=all",
    "https://arxiv.org/rss/q-bio",
    "https://arxiv.org/rss/cs.AI",
    "https://arxiv.org/rss/cs.LG",
    "https://arxiv.org/rss/cs.CL",
    "https://arxiv.org/rss/quant-ph"
]

UPDATE_INTERVAL_MINUTES = 15  # how often Make.com will check


@app.route('/')
def home():
    return "✅ AI Biotech Master Feed is live! Visit /master.rss to access the combined RSS feed."


@app.route('/master.rss')
def master_feed():
    items = []

    for url in FEED_LINKS:
        try:
            d = feedparser.parse(url)
            for entry in d.entries:
                items.append({
                    "title": entry.get("title", "No Title"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", "")
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # Sort items by published date (if available)
    items = sorted(items, key=lambda x: x.get("published", ""), reverse=True)[:100]

    # === Build RSS XML ===
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = FEED_TITLE
    SubElement(channel, "description").text = FEED_DESCRIPTION
    SubElement(channel, "link").text = "https://render.com"

    for item in items:
        i = SubElement(channel, "item")
        SubElement(i, "title").text = item["title"]
        SubElement(i, "link").text = item["link"]
        SubElement(i, "description").text = item["summary"]
        SubElement(i, "pubDate").text = item["published"]

    xml = tostring(rss, encoding="utf-8")
    return Response(xml, mimetype="application/rss+xml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
