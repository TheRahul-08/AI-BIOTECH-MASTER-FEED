from flask import Flask, Response
import feedparser
import requests
import time
import pytz
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

app = Flask(__name__)

# === Your Master Feed List ===
FEEDS = [
    "https://www.fiercebiotech.com/rss/xml",
    "https://www.statnews.com/feed/",
    "https://endpts.com/feed/",
    "https://www.biospace.com/rss-feeds/all-news/",
    "https://www.biopharmadive.com/feeds/news/",
    "https://www.genengnews.com/feed/",
    "https://www.labiotech.eu/feed/",
    "https://www.bio-itworld.com/rss/topic/all",
    "https://www.the-scientist.com/rss/feed",
    "https://medcitynews.com/feed/",
    "https://xconomy.com/feed/",
    "https://www.nature.com/nbt/rss/news",
    "https://www.nature.com/nm/rss/news",
    "https://www.nature.com/articles.rss",
    "https://www.sciencedaily.com/rss/top/technology.xml",
    "https://www.sciencedaily.com/rss/plants_animals/biotechnology.xml",
    "https://www.biorxiv.org/rss/current",
    "https://rss.arxiv.org/rss/cs.AI",
    "https://rss.arxiv.org/rss/q-bio",
    "https://rss.arxiv.org/rss/cs.LG",
    "https://www.medrxiv.org/rss/current",
    "https://www.technologyreview.com/c/biotechnology/feed/",
    "https://www.technologyreview.com/c/artificial-intelligence/feed/",
    "https://techcrunch.com/category/health/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/ai/feed/",
    "https://a16z.com/category/bio-health/feed/",
    "https://news.crunchbase.com/feed/",
    "https://www.fda.gov/about-fda/fda-newsroom/press-releases.xml",
    "https://www.ema.europa.eu/en/news-events/rss",
    "https://www.who.int/rss-feeds/news-rss.xml",
    "https://www.globenewswire.com/Feeds/RSS/Category/8181",
    "https://www.prnewswire.com/rss/categories/biotechnology.rss",
    "https://www.wired.com/feed/category/science/rss",
    "https://www.theguardian.com/science/rss",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://cloud.google.com/blog/products/ai-machine-learning/rss",
    "https://blogs.microsoft.com/ai/feed/",
    "https://blogs.nvidia.com/blog/category/healthcare/feed/",
    "https://blog.google/technology/ai/rss/",
    "https://deepmind.google/blog/feed/",
    "https://openai.com/blog/rss.xml",
    "https://www.wsj.com/xml/rss/3_7455.xml",
    "https://timmermanreport.com/feed/",
    "https://www.beckershospitalreview.com/digital-health.rss",
    "https://hitconsultant.net/feed/",
    "https://mhealthintelligence.com/feed",
    "https://www.mobihealthnews.com/feed",
    "https://www.healthcareitnews.com/feed",
    "https://www.darkreading.com/rss_simple.asp",
    "https://www.schneier.com/feed/",
    "https://feeds.feedburner.com/CoinDesk",
    "https://cointelegraph.com/rss",
    "https://blockworks.co/feed",
    "https://www.theblock.co/rss.xml",
    "https://www.ncbi.nlm.nih.gov/pubmed/rss/NlmNewandNoteworthy.xml",
    "https://www.fiercepharma.com/rss/xml",
    "https://www.pharmaceutical-technology.com/feed/",
    "https://www.drugdiscoverytrends.com/feed/",
    "https://www.dddmag.com/rss-feed/",
    "https://www.outsourcing-pharma.com/rss",
    "https://www.clinicaltrialsarena.com/feed/",
    "https://www.pharmaceutical-journal.com/feed",
    "https://www.healthexec.com/rss",
    "https://www.nationalhealthexecutive.com/rss",
    "https://www.gavi.org/news-resources/newsletters/rss",
    "https://www.gatesfoundation.org/feed/",
    "https://www.wellcome.org/news/rss.xml",
    "https://www.broadinstitute.org/rss/news.xml",
    "https://www.sanger.ac.uk/news/rss.xml",
    "https://www.scripps.edu/news-and-events/rss.xml",
    "https://www.jpmorgan.com/insights/rss",
    "https://www.goldmansachs.com/insights/rss.xml",
    "https://www.morganstanley.com/ideas/rss",
    "https://www.cbinsights.com/research/feed/",
    "https://www.fierceelectronics.com/rss/xml",
    "https://www.eetimes.com/feed/",
    "https://spectrum.ieee.org/rss/full-text",
    "https://techxplore.com/rss-feed/",
    "https://singularityhub.com/feed/",
    "https://www.forbes.com/innovation/feed/",
    "https://www.forbes.com/healthcare/feed/",
    "https://www.economist.com/science-and-technology/rss.xml",
    "https://www.ft.com/health?format=rss",
    "https://www.ft.com/technology?format=rss",
    "https://www.pharmavoice.com/feed/",
    "https://www.pmlive.com/rss"
]

# Cache storage
CACHE = {"data": "", "timestamp": 0}

def fetch_all_feeds():
    headers = {"User-Agent": "Mozilla/5.0 (RSS Aggregator Bot)"}
    items = []
    for url in FEEDS:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.content)
            for entry in feed.entries[:5]:  # Limit per feed
                item = {
                    "title": entry.get("title", "No title"),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", datetime.now().isoformat()),
                    "source": feed.feed.get("title", url)
                }
                items.append(item)
        except Exception as e:
            print(f"⚠️ Skipped {url}: {e}")
            continue
    return items

def generate_rss():
    root = Element("rss", version="2.0")
    channel = SubElement(root, "channel")
    SubElement(channel, "title").text = "AI Biotech Master Feed"
    SubElement(channel, "link").text = "https://ai-biotech-master-feed.onrender.com"
    SubElement(channel, "description").text = "Aggregated feed from AI, biotech, and pharma sources."
    SubElement(channel, "lastBuildDate").text = datetime.now(pytz.utc).strftime("%a, %d %b %Y %H:%M:%S %z")

    for item in fetch_all_feeds():
        entry = SubElement(channel, "item")
        SubElement(entry, "title").text = item["title"]
        SubElement(entry, "link").text = item["link"]
        SubElement(entry, "pubDate").text = item["published"]
        SubElement(entry, "source").text = item["source"]

    return tostring(root, encoding="utf-8", xml_declaration=True)

@app.route("/")
def home():
    return "<h3>✅ AI Biotech Master Feed is Live! Visit /master.rss</h3>"

@app.route("/master.rss")
def master_rss():
    now = time.time()
    # 15-minute cache refresh
    if now - CACHE["timestamp"] > 900 or not CACHE["data"]:
        try:
            CACHE["data"] = generate_rss()
            CACHE["timestamp"] = now
        except Exception as e:
            return Response(f"Internal error: {e}", status=500)
    return Response(CACHE["data"], mimetype="application/rss+xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
