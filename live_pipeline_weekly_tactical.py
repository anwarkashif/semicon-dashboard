# -*- coding: utf-8 -*-
import os
import json
import time
import feedparser
import requests
from huggingface_hub import HfApi
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime
from google import genai

# ==========================================
# 1. CONFIGURATION & SETUP (WEEKLY TACTICAL BRIEF)
# ==========================================
os.makedirs('data/friday_snippet', exist_ok=True)

RSS_FEEDS = [
    "https://www.ft.com/technology?format=rss",
    "https://www.atlanticcouncil.org/feed/",
    "https://foreignpolicy.com/feed/",
    "https://moderndiplomacy.eu/feed/",
    "https://www.worldpoliticsreview.com/feed/", 
    "https://www.defenseone.com/rss/all/",
    "https://warontherocks.com/feed/",
    "https://www.realcleardefense.com/index.xml",
    "https://www.c4isrnet.com/arc/outboundfeeds/rss/",
    "https://www.defensenews.com/arc/outboundfeeds/rss/", 
    "https://spacepolicyonline.com/feed/",
    "https://www.space.com/feeds/all",
    "https://spacewatch.global/feed/", 
    "https://spaceflightnow.com/feed/", 
    "https://www.satellitetoday.com/feed/", 
    "https://semiwiki.com/feed/",
    "https://semiengineering.com/feed/",
    "https://www.mining.com/feed/",
    "https://www.eetimes.com/feed/",
    "https://www.supplychaindive.com/feeds/news/", 
    "https://thediplomat.com/feed/",
    "https://technode.com/feed/",
    "https://asiatimes.com/feed/",
    "https://www.aspistrategist.org.au/feed/", 
    "https://fulcrum.sg/feed/", 
    "https://gcaptain.com/feed/",
    "https://www.middleeasteye.net/rss",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.al-monitor.com/rss.xml",
    "https://splash247.com/feed/", 
    "https://www.nextplatform.com/feed/",
    "https://thequantuminsider.com/feed/",            
    "https://spectrum.ieee.org/feeds/feed.rss",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/"
]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 2. URL RESOLVER (UNPACK GOOGLE NEWS REDIRECTS)
# ==========================================
def resolve_final_url(url, headers):
    """
    Follows redirects to unpack the actual publisher URL.
    Optimized to explicitly target Google News redirect URLs.
    """
    if "news.google.com" not in url:
        return url
        
    try:
        # Follow the redirect to get the true destination (e.g., Reuters, FT)
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        return response.url
    except Exception:
        # If the resolution fails, gracefully fallback to the original link
        return url

# ==========================================
# 3. DATA SCRAPING & DETERMINISTIC ID MAPPING
# ==========================================
def fetch_daily_intelligence():
    print("🌍 Scraping strategic RSS & LIVE Boolean feeds for Weekly Tactical Brief...")
    aggregated_news = ""
    total_articles = 0
    article_map = {}
    article_counter = 1
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # --- PHASE 1: Premium Think-Tank & Media Feeds ---
    for url in RSS_FEEDS:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status() 
            feed = feedparser.parse(response.text)
            for entry in feed.entries[:5]:
                art_id = f"ART_{article_counter:03d}"
                # Direct RSS feeds generally don't use heavy redirects, but we pass it through safely
                final_url = resolve_final_url(entry.link, headers)
                article_map[art_id] = {"title": entry.title, "url": final_url}
                
                aggregated_news += f"ID: {art_id} | [MACRO] {entry.title}\n"
                article_counter += 1
                total_articles += 1
        except Exception as e:
            print(f"⚠️ Warning: Could not fetch {url} - {e}")

    # --- PHASE 2: Live Google News Boolean Radar (Past 1 Hour) ---
    GOOGLE_QUERIES = [
        '("geopolitics" OR "sanctions" OR "foreign policy" OR "tariffs") when:1h',
        '("military" OR "defense" OR "missile" OR "conflict" OR "war") when:1h',
        '("outer space" OR "satellite" OR "orbital" OR "space force" OR "SpaceX") when:1h',
        '("semiconductor" OR "lithography" OR "rare earth" OR "critical minerals") when:1h',
        '("Indo-Pacific" OR "China" OR "Taiwan" OR "South China Sea" OR "AUKUS") when:1h',
        '("logistics" OR "supply chain" OR "Middle East" OR "Red Sea" OR "Strait of Hormuz") when:1h',
        '("artificial intelligence" OR "quantum computing" OR "data center" OR "Nvidia" OR "supercomputer") when:1h'
    ]

    for query in GOOGLE_QUERIES:
        encoded_query = urllib.parse.quote(query)
        gn_url = f'https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en&_={int(time.time())}'
        
        try:
            response = requests.get(gn_url, headers=headers, timeout=15)
            response.raise_for_status()
            feed = feedparser.parse(response.text)
            for entry in feed.entries[:5]: 
                art_id = f"ART_{article_counter:03d}"
                # 🛑 CRITICAL FIX: Unpack Google News redirect BEFORE saving to map
                final_url = resolve_final_url(entry.link, headers)
                article_map[art_id] = {"title": entry.title, "url": final_url}
                
                aggregated_news += f"ID: {art_id} | [LIVE 1H] {entry.title}\n"
                article_counter += 1
                total_articles += 1
        except Exception as e:
            print(f"⚠️ Warning: Could not fetch Google News for {query} - {e}")
            
    # --- PHASE 3: DEEP-SCRAPE MARITIME ALERTS ---
    print("🚢 Executing Deep-Scrape on Live Maritime URLs...")
    maritime_query = '("UKMTO" OR "Ambrey" OR "MSCHOA" OR "MSCIO") AND ("incident" OR "attack" OR "vessel" OR "boarded" OR "missile" OR "houthi") when:24h'
    encoded_m_query = urllib.parse.quote(maritime_query)
    gn_maritime_url = f'https://news.google.com/rss/search?q={encoded_m_query}&hl=en-US&gl=US&ceid=US:en&_={int(time.time())}'
    
    try:
        m_res = requests.get(gn_maritime_url, headers=headers, timeout=15)
        m_res.raise_for_status()
        m_feed = feedparser.parse(m_res.text)
        
        for entry in m_feed.entries[:6]: 
            # 🛑 CRITICAL FIX: Unpack redirect BEFORE scraping the actual page content
            final_url = resolve_final_url(entry.link, headers)
            art_id = f"ART_{article_counter:03d}"
            article_map[art_id] = {"title": entry.title, "url": final_url}
            
            try:
                # Scrape using the true publisher URL
                page_res = requests.get(final_url, headers=headers, timeout=10)
                soup = BeautifulSoup(page_res.text, 'html.parser')
                
                paragraphs = soup.find_all('p')
                extracted_text = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30])
                
                if extracted_text:
                    snippet = extracted_text[:800] + "..." if len(extracted_text) > 800 else extracted_text
                    aggregated_news += f"ID: {art_id} | [LIVE MARITIME ALERT - {entry.title}]\n  DEEP EXTRACTION DATA: {snippet}\n"
                else:
                    aggregated_news += f"ID: {art_id} | [LIVE MARITIME ALERT] {entry.title}\n"
                
                article_counter += 1
                total_articles += 1
            except Exception as e:
                aggregated_news += f"ID: {art_id} | [LIVE MARITIME ALERT] {entry.title}\n"
                article_counter += 1
                total_articles += 1
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch Maritime Boolean - {e}")

    print(f"📰 Successfully grabbed {total_articles} raw headlines mapped to internal indices.")
    return aggregated_news, total_articles, article_map

# ==========================================
# 4. AI EXTRACTION PIPELINE (IDENTIFIER SCHEMA)
# ==========================================
def extract_tactical_events(news_text):
    print("🧠 Pushing data to Gemini for tactical selection...")
    
    prompt = f"""
    You are an elite Geopolitics-OSINT analyst. 
    Review the following news entries, each preceded by a unique ID (e.g., ART_001).
    Extract 4 to 6 of the most critical geopolitical, defense, semiconductor, or supply chain events.
    
    You MUST output the result as a raw JSON array of objects. Do not include markdown formatting like ```json.
    
    Each object must have exactly these keys:
    "Article_ID": The exact ID string (e.g., "ART_001") matching the news item chosen. Do not invent IDs.
    "Date": The current date (use {datetime.now().strftime('%Y-%m-%d')})
    "Actor": The country, company, or entity taking the action.
    "Action": A concise, 5-8 word description of the event.
    "Location": A specific country, region, or chokepoint (e.g., "Taiwan", "Strait of Hormuz", "United States", "China").
    "Risk": Must be strictly one of: "CRITICAL", "HIGH", or "ELEVATED".
    
    News Data:
    {news_text}
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
            
        except Exception as e:
            print(f"⚠️ API Error on attempt {attempt + 1}/{max_retries}: {e}")
            if attempt < max_retries - 1:
                sleep_time = 15 * (attempt + 1) 
                print(f"⏳ Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print("❌ Max retries reached. Aborting AI extraction.")
                raise e 

# ==========================================
# 5. EXECUTE, REATTACH TARGET URLS & SAVE
# ==========================================
if __name__ == "__main__":
    try:
        is_friday = datetime.now().weekday() == 4
        if not is_friday:
            print("⏳ Not Friday. Weekly Tactical extraction skipped to preserve static weekly snapshot.")
            exit(0)

        news_data, article_count, source_article_map = fetch_daily_intelligence()
        
        if article_count == 0:
            print("❌ ABORTING: No articles scraped. Preventing AI hallucination.")
            exit(1)
            
        # Extract strategic structured events (contains Article_ID references)
        extracted_events = extract_tactical_events(news_data)
        
        # 🛡️ THE DETERMINISTIC INJECTION STEP
        # We programmatically append the verified long-form URL directly from python memory
        validated_tactical_events = []
        for event in extracted_events:
            target_id = event.get("Article_ID")
            
            if target_id in source_article_map:
                # Reattach the exact full-path news link scraped directly from the feed
                event["Source"] = source_article_map[target_id]["url"]
                # Clean up the payload by removing the operational ID before saving to disk
                del event["Article_ID"]
                validated_tactical_events.append(event)
            else:
                print(f"⚠️ Warning: Gemini returned an unmapped ID ({target_id}). Dropping event to maintain integrity.")
        
        dynamic_date_str = datetime.now().strftime("%Y-%m-%d")
        output_file = f'data/friday_snippet/tactical_events_{dynamic_date_str}.json'
        
        with open(output_file, 'w') as f:
            json.dump(validated_tactical_events, f, indent=4)
            
        print(f"✅ Success! Wrote {len(validated_tactical_events)} tactical events with 100% verified publisher URLs to {output_file}.")
        
        # ==========================================
        # ☁️ HUGGING FACE PERMANENT RETENTION SYNC
        # ==========================================
        HF_TOKEN = os.environ.get("HF_TOKEN")
        REPO_ID = os.environ.get("SPACE_ID") or "anwarkashif/semicon-dashboard" 
        
        if HF_TOKEN and REPO_ID:
            try:
                api = HfApi()
                print(f"☁️ Uploading {output_file} to permanent storage on {REPO_ID}...")
                api.upload_file(
                    path_or_fileobj=output_file,
                    path_in_repo=output_file,
                    repo_id=REPO_ID,
                    repo_type="space",
                    token=HF_TOKEN,
                    commit_message=f"Auto-sync Tactical Events (Resolved Publisher URLs): {dynamic_date_str}"
                )
                print("✅ Successfully locked tactical events into permanent Hugging Face storage!")
            except Exception as e:
                print(f"❌ Failed to sync to Hub. File is only in temporary memory! Error: {e}")
        else:
            print("⚠️ HF_TOKEN or REPO_ID missing. File saved locally but will be lost on container restart.")
            
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")