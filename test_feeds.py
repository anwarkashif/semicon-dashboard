# -*- coding: utf-8 -*-
import os
import requests
import feedparser

# ==========================================
# 0. CONFIGURATION & SETUP
# ==========================================
os.makedirs('data/today_snippet', exist_ok=True)

# Consolidating 34 verified feeds + 1 New Indo-Pacific Replacement (Total 35)
RSS_FEEDS = [
    # --- 1. Geopolitics & Macro Policy ---
    "https://www.ft.com/technology?format=rss",
    "https://www.atlanticcouncil.org/feed/",
    "https://foreignpolicy.com/feed/",
    "https://moderndiplomacy.eu/feed/",
    "https://www.worldpoliticsreview.com/feed/", 

    # --- 2. Military & Conflict ---
    "https://www.defenseone.com/rss/all/",
    "https://warontherocks.com/feed/",
    "https://www.realcleardefense.com/index.xml",
    "https://www.c4isrnet.com/arc/outboundfeeds/rss/",
    "https://www.defensenews.com/arc/outboundfeeds/rss/", 

    # --- 3. Outer Space ---
    "https://spacepolicyonline.com/feed/",
    "https://www.space.com/feeds/all",
    "https://spacewatch.global/feed/", 
    "https://spaceflightnow.com/feed/", 
    "https://www.satellitetoday.com/feed/", 

    # --- 4. Lithography & Raw Materials ---
    "https://semiwiki.com/feed/",
    "https://semiengineering.com/feed/",
    "https://www.mining.com/feed/",
    "https://www.eetimes.com/feed/",
    "https://www.supplychaindive.com/feeds/news/", 

    # --- 5. Indo-Pacific & Country Actions ---
    "https://thediplomat.com/feed/",
    "https://technode.com/feed/",
    "https://asiatimes.com/feed/",
    "https://www.aspistrategist.org.au/feed/", 
    "https://fulcrum.sg/feed/", # NEW Replacement (ISEAS-Yusof Ishak Institute)

    # --- 6. Logistics & West Asia ---
    "https://gcaptain.com/feed/",
    "https://www.middleeasteye.net/rss",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.al-monitor.com/rss.xml",
    "https://splash247.com/feed/", 
    
    # --- 7. Next-Gen Compute (AI, ML & Quantum) ---
    "https://www.nextplatform.com/feed/",
    "https://thequantuminsider.com/feed/",            
    "https://spectrum.ieee.org/feeds/feed.rss",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/"
] 

def run_diagnostic(feeds):
    print("\n🔍 Initiating Geopolitics-OSINT RSS Feed Diagnostic...\n")
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    successful_feeds = []
    failed_feeds = []

    for url in feeds:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                parsed_feed = feedparser.parse(response.content)
                if parsed_feed.entries:
                    print(f"✅ SUCCESS: {url} (Found {len(parsed_feed.entries)} articles)")
                    successful_feeds.append(url)
                else:
                    print(f"⚠️ EMPTY: {url} (Connected, but no XML articles found)")
                    failed_feeds.append(url)
            else:
                print(f"❌ HTTP {response.status_code} ERROR: {url}")
                failed_feeds.append(url)
        except Exception as e:
            print(f"❌ FATAL ERROR: {url} ({type(e).__name__})")
            failed_feeds.append(url)

    print("\n" + "="*50)
    print("📊 LIVE PIPELINE DIAGNOSTIC SUMMARY")
    print("="*50)
    print(f"Total Tested: {len(feeds)}")
    print(f"Working: {len(successful_feeds)}")
    print(f"Failed/Empty: {len(failed_feeds)}")
    print("\n⬇️ EXACT CODE TO COPY INTO YOUR LIVE_PIPELINE FILES ⬇️\n")
    
    print("RSS_FEEDS = [")
    for feed in successful_feeds:
        print(f'    "{feed}",')
    print("]")

if __name__ == "__main__":
    run_diagnostic(RSS_FEEDS)