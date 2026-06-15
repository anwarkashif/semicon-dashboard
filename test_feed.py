import feedparser
import requests

# The authentic public intelligence feeds for the 6 domains
FEEDS = {
    "Recorded Future": "https://therecord.media/feed/",
    "Flashpoint": "https://flashpoint.io/blog/feed/",
    "Sintelix (Global Eye)": "https://sintelix.com/feed/",
    "War on the Rocks": "https://warontherocks.com/feed/",
    "World Monitor": "https://www.understandingwar.org/rss.xml" # Premium global monitor fallback
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