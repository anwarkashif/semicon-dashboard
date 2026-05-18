# -*- coding: utf-8 -*-
import os
import json
import time
import feedparser
import requests
from datetime import datetime
from google import genai

# ==========================================
# 1. CONFIGURATION & SETUP (EXECUTIVE HOME)
# ==========================================
# Isolated data directory for Executive Home operations
os.makedirs('data/executive_home', exist_ok=True)

RSS_FEEDS = [
    # --- 1. Geopolitics & Macro Policy ---
    "https://www.brookings.edu/feed/",
    "https://www.ft.com/technology?format=rss",
    "https://www.atlanticcouncil.org/feed/",         # Replaced: CFR

    # --- 2. Military & Conflict ---
    "https://www.defenseone.com/rss/all/",
    "https://warontherocks.com/feed/",
    "https://www.realcleardefense.com/index.xml",    # Replaced: Breaking Defense

    # --- 3. Outer Space ---
    "https://spacepolicyonline.com/feed/",           # Replaced: SpaceNews

    # --- 4. Lithography & Raw Materials ---
    "https://semiwiki.com/feed/",
    "https://semiengineering.com/feed/",
    "https://www.mining.com/feed/",

    # --- 5. Indo-Pacific & Country Actions ---
    "https://thediplomat.com/feed/",
    "https://technode.com/feed/",

    # --- 6. Logistics & West Asia ---
    "https://gcaptain.com/feed/",
    "https://www.middleeasteye.net/rss",
    "https://www.aljazeera.com/xml/rss/all.xml",
    
    # --- 7. Next-Gen Compute (AI, ML & Quantum) ---
    "https://www.nextplatform.com/feed/",            # Replaced: HPCwire
    "https://thequantuminsider.com/feed/",            
    "https://spectrum.ieee.org/feeds/feed.rss"        
]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 2. DATA SCRAPING (ANTI-BOT BYPASS)
# ==========================================
def fetch_daily_intelligence():
    print("🌍 Scraping strategic RSS feeds for Executive Home...")
    aggregated_news = ""
    total_articles = 0
    
    # A full browser profile to trick Cloudflare and strict firewalls
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for url in RSS_FEEDS:
        try:
            # 1. Fetch the raw XML like a normal web browser
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status() # Check for 403 or 404 errors
            
            # 2. Pass the raw XML text into feedparser
            feed = feedparser.parse(response.text)
            
            # 3. Extract the top 5
            for entry in feed.entries[:5]:
                aggregated_news += f"- {entry.title}\n"
                total_articles += 1
                
        except Exception as e:
            print(f"⚠️ Warning: Could not fetch {url} - {e}")
            
    print(f"📰 Successfully grabbed {total_articles} raw headlines from RSS feeds.")
    return aggregated_news, total_articles

# ==========================================
# 3. AI EXTRACTION PIPELINE (WITH AUTO-RETRY)
# ==========================================
def extract_tactical_events(news_text):
    print("🧠 Pushing data to Gemini for tactical extraction...")
    
    prompt = f"""
    You are an elite Geopolitics-OSINT analyst. 
    Review the following news headlines from the last 24 hours. Extract 4 to 6 of the most critical geopolitical, defense, semiconductor, or supply chain events.
    
    You MUST output the result as a raw JSON array of objects. Do not include markdown formatting like ```json.
    
    Each object must have exactly these keys:
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
                sleep_time = 15 * (attempt + 1) # Wait 15s, then 30s...
                print(f"⏳ Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print("❌ Max retries reached. Aborting AI extraction.")
                raise e # Fail completely if all 3 tries fail

# ==========================================
# 4. EXECUTE & SAVE
# ==========================================
if __name__ == "__main__":
    try:
        news_data, article_count = fetch_daily_intelligence()
        
        # THE KILL SWITCH: If no articles, stop the script so AI doesn't hallucinate fake news
        if article_count == 0:
            print("❌ ABORTING: No articles scraped. Preventing AI hallucination.")
            exit(1)
            
        tactical_events = extract_tactical_events(news_data)
        
        # Target the isolated Executive Home data folder
        output_file = 'data/executive_home/tactical_events_24h.json'
        with open(output_file, 'w') as f:
            json.dump(tactical_events, f, indent=4)
            
        print(f"✅ Success! Wrote {len(tactical_events)} tactical events to {output_file}.")
        
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")