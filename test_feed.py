import feedparser
import requests

FEEDS = {
    "Recorded Future": "https://therecord.media/feed/",
    "Flashpoint": "https://flashpoint.io/blog/feed/",
    "Sintelix (Global Eye)": "https://sintelix.com/feed/",
    
    # User's Suggestions (testing for native feeds)
    "War-Monitor": "https://war-monitor.com/feed/",
    "Monitor The Situation": "https://monitor-the-situation.com/feed/",
    
    # 24/7 Global OSINT Alternatives
    "Liveuamap (Kinetic OSINT)": "https://liveuamap.com/rss",
    "CISA (Global Cyber Threats)": "https://www.cisa.gov/uscert/ncas/alerts.xml",
    "The Hacker News (Real-time Breaches)": "https://feeds.feedburner.com/TheHackersNews"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def test_feeds():
    print("🔍 TESTING ENTERPRISE OSINT FEEDS...\n")
    for name, url in FEEDS.items():
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                feed = feedparser.parse(res.text)
                if feed.entries:
                    print(f"✅ {name}: SUCCESS")
                    print(f"   Latest: {feed.entries[0].title}")
                    print(f"   URL: {feed.entries[0].link}\n")
                else:
                    print(f"⚠️ {name}: Feed reachable, but empty.\n")
            else:
                print(f"❌ {name}: FAILED (Status {res.status_code})\n")
        except Exception as e:
            print(f"❌ {name}: FAILED (Error: {e})\n")

if __name__ == "__main__":
    test_feeds()