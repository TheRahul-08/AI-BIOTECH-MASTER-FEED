from flask import Flask, Response
import feedparser, requests, time, logging
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ---- paste the FEED_URLS list here ----
FEED_URLS = [
    # Biotech / Pharma
    "https://www.fiercebiotech.com/rss/xml",
    "https://www.biospace.com/rss-feeds/all-news/",
    "https://www.biopharmadive.com/feeds/news/",
    "https://www.genengnews.com/feed/",
    "https://www.labiotech.eu/feed/",
    "https://www.bio-itworld.com/rss/topic/all",
    "https://www.the-scientist.com/rss/feed",
    "https://medcitynews.com/feed/",
    "https://www.pharmaceutical-technology.com/feed/",
    "https://www.drugdiscoverytrends.com/feed/",
    "https://www.clinicaltrialsarena.com/feed/",
    "https://www.healthexec.com/rss",
    "https://www.nationalhealthexecutive.com/rss",

    # AI / Tech
    "https://venturebeat.com/ai/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://techcrunch.com/category/health/feed/",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://cloud.google.com/blog/products/ai-machine-learning/rss/",
    "https://blog.google/technology/ai/rss/",
    "https://blogs.microsoft.com/ai/feed/",
    "https://blogs.nvidia.com/blog/category/healthcare/feed/",
    "https://deepmind.google/blog/feed/",
    "https://openai.com/blog/rss.xml",
    "https://singularityhub.com/feed/",
    "https://spectrum.ieee.org/rss/full-text",
    "https://techxplore.com/rss-feed/",
    "https://www.eetimes.com/feed/",
    "https://www.fierceelectronics.com/rss/xml",

    # Science / Research
    "https://rss.arxiv.org/rss/cs.AI",
    "https://rss.arxiv.org/rss/cs.LG",
    "https://rss.arxiv.org/rss/q-bio",
    "https://www.biorxiv.org/rss/current",
    "https://www.medrxiv.org/rss/current",
    "https://www.sciencedaily.com/rss/top/health.xml",
    "https://www.sciencedaily.com/rss/plants_animals/biotechnology.xml",
    "https://www.nature.com/nbt/rss/news",
    "https://www.nature.com/nm/rss/news",
    "https://www.sanger.ac.uk/news/rss.xml",
    "https://www.scripps.edu/news-and-events/rss.xml",
    "https://www.broadinstitute.org/rss/news.xml",

    # Health IT / Digital Health
    "https://hitconsultant.net/feed/",
    "https://mhealthintelligence.com/feed",
    "https://www.mobihealthnews.com/feed",
    "https://www.healthcareitnews.com/feed",
    "https://www.beckershospitalreview.com/digital-health.rss",

    # Cyber & Blockchain (light)
    "https://www.darkreading.com/rss_simple.asp",
    "https://www.schneier.com/feed/",
    "https://feeds.feedburner.com/CoinDesk",
    "https://cointelegraph.com/rss",
    "https://blockworks.co/feed",

    # Major orgs / regulators
    "https://www.fda.gov/about-fda/fda-newsroom/press-releases.xml",
    "https://www.ema.europa.eu/en/news-events/rss",
    "https://www.who.int/rss-feeds/news-rss.xml",
    "https://www.gavi.org/news-resources/newsletters/rss",
    "https://www.gatesfoundation.org/feed/",
    "https://www.wellcome.org/news/rss.xml",

    # Finance / VC insights
    "https://a16z.com/feed/",
    "https://www.cbinsights.com/research/feed/",
    "https://www.goldmansachs.com/insights/rss.xml",
    "https://www.morganstanley.com/ideas/rss",
    "https://www.jpmorgan.com/insights/rss",

    # Media / General Science
    "https://www.theguardian.com/science/rss",
    "https://www.wired.com/feed/category/science/rss",
    "https://www.economist.com/science-and-technology/rss.xml",
    "https://www.ft.com/health?format=rss",
    "https://www.ft.com/technology?format=rss",
    "https://www.forbes.com/innovation/feed/",
    "https://www.forbes.com/healthcare/feed/",
    "https://www.pharmavoice.com/feed/",
    "https://www.pmlive.com/rss"
]

def fetch_feed(url):
    """Fetch a single RSS feed safely."""
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        feed = feedparser.parse(r.content)
        if not feed.entries:
            logging.warning(f"⚠️ Empty or invalid feed: {url}")
            return []
        return feed.entries
    except Exception as e:
        logging.warning(f"🚫 Skipped {url}: {e}")
        return []

@app.route("/")
def home():
    return "<h3>✅ AI + Biotech Master Feed is running</h3>"

@app.route("/master.rss")
def master_feed():
    logging.info("🔄 Refreshing all feeds...")
    entries = []
    start = time.time()

    with ThreadPoolExecutor(max_workers=8) as executor:
        for feed_entries in executor.map(fetch_feed, FEED_URLS):
            entries.extend(feed_entries)

    # Sort newest first
    entries.sort(key=lambda e: e.get("published_parsed", time.gmtime(0)), reverse=True)

    rss_items = []
    for e in entries[:100]:
        title = e.get("title", "Untitled")
        link = e.get("link", "")
        desc = e.get("summary", "")
        pub = time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                            e.get("published_parsed", time.gmtime()))
        rss_items.append(f"<item><title>{title}</title><link>{link}</link>"
                         f"<description><![CDATA[{desc}]]></description>"
                         f"<pubDate>{pub}</pubDate></item>")

    rss = ("<?xml version='1.0' encoding='UTF-8'?>"
           "<rss version='2.0'><channel>"
           "<title>AI + Biotech Master Feed</title>"
           "<link>https://yourdomain.onrender.com/</link>"
           "<description>Unified Feed for AI & Biotech News</description>"
           f"{''.join(rss_items)}"
           "</channel></rss>")

    logging.info(f"✅ Built {len(entries)} entries in {time.time()-start:.1f}s")
    return Response(rss, mimetype="application/rss+xml")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
