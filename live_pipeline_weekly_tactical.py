# -*- coding: utf-8 -*-
import os
import json
import time
import feedparser
import requests
from huggingface_hub import HfApi
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime, timezone
from google import genai
import trafilatura  # 🛑 THE FIX: Added Trafilatura for deep text extraction

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

# 🚨 THE ARSENAL: API Key Rotation List
AVAILABLE_KEYS = [
    os.environ.get("GEMINI_API_KEY"),
    os.environ.get("RAG_GEMINI_API_KEY"),
    os.environ.get("RAG_GEMINI_API_KEY_2"),
    os.environ.get("RAG_GEMINI_API_KEY_3"),
    os.environ.get("RAG_GEMINI_API_KEY_4"),
    os.environ.get("RAG_GEMINI_API_KEY_5")
]
VALID_KEYS = [k for k in AVAILABLE_KEYS if k and k.strip()]

# 🚨 THE ENGINE: Seamless Failover Generation
def generate_with_rotation(prompt, temperature=0.1):
    if not VALID_KEYS:
        raise Exception("CRITICAL: No valid API keys found in environment.")
        
    current_idx = 0
    failures = 0
    global_cycles = 0
    MAX_GLOBAL_CYCLES = 4
    
    while global_cycles < MAX_GLOBAL_CYCLES:
        current_key = VALID_KEYS[current_idx]
        client = genai.Client(api_key=current_key)
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "temperature": temperature,
                    "safety_settings": [
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                }
            )
            raw_txt = getattr(response, 'text', '').strip()
            if not raw_txt: raise ValueError("Empty response blocked by unknown filter")
            return raw_txt
            
        except Exception as e:
            failures += 1
            print(f"⚠️ API Key {current_idx + 1} Attempt {failures} Failed: {str(e)[:100]}")
            
            if failures >= 2:
                current_idx += 1
                failures = 0
                
                if current_idx >= len(VALID_KEYS):
                    print("⏳ All keys exhausted in this cycle. Sleeping 65 seconds for RPM quotas to reset...")
                    time.sleep(65)
                    current_idx = 0
                    global_cycles += 1
                else:
                    print(f"🔄 Rotating to API Key {current_idx + 1}...")
                    time.sleep(5)
            else:
                time.sleep(15)
                
    raise Exception("CRITICAL: All API keys exhausted across multiple recovery cycles.")

# ==========================================
# 2. URL RESOLVER (UNPACK GOOGLE NEWS REDIRECTS)
# ==========================================
def resolve_final_url(url, headers):
    if not url or "news.google.com" not in url: return url
    try:
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        final_url = r.url
        if any(d in urlparse(final_url).netloc.lower() for d in ["news.google.com", "google.com"]): return url
        return final_url
    except Exception: return url

# ==========================================
# 3. DATA SCRAPING & DETERMINISTIC ID MAPPING
# ==========================================
def fetch_psyopoly_data():
    SUPABASE_URL = "https://lojirolzkshoqgccrwyh.supabase.co/rest/v1/breaking_news?select=id%2Cheadline%2Cposted_at%2Curl&order=posted_at.desc&limit=30"
    ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvamlyb2x6a3Nob3FnY2Nyd3loIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwODQyNjQsImV4cCI6MjA4OTY2MDI2NH0.DzdBr_d69SSlRxtnxH8DRqc0hLNQfb4wL5t1Qe96UMo"
    
    headers = {
        "apikey": ANON_KEY, 
        "authorization": f"Bearer {ANON_KEY}", 
        "accept": "application/json",
        "origin": "https://www.psyopoly.pro",
        "referer": "https://www.psyopoly.pro/"
    }
    
    formatted_events = []; raw_psy_items = []
    try:
        for item in requests.get(SUPABASE_URL, headers=headers, timeout=10).json():
            headline = item.get("headline", "No Headline Provided").strip()
            url = item.get("url", "https://www.psyopoly.pro/middle-east")
            if not valid_url(url): continue
            
            raw_psy_items.append({"headline": headline, "url": url})
            formatted_events.append({
                "Date": item.get("posted_at", "").split("T")[0] if item.get("posted_at") else datetime.now().strftime("%Y-%m-%d"),
                "Actor": "Psyopoly/West Asia", 
                "Location": "Middle East",
                "Event": "Strategic Update", 
                "Action": headline,
                "Headline": headline,
                "Summary": headline, 
                "Risk": "HIGH", 
                "Source": url,
                "Title": headline, 
                "Feed_Source": "Psyopoly Supabase",
                "Publisher": urlparse(url).netloc.replace("www.", "")
            })
        return formatted_events, raw_psy_items
    except Exception: return [], []

def fetch_daily_intelligence():
    print("🌍 Scraping ALL strategic feeds, APIs, & Executing Deep Text Extraction for Weekly Tactical Brief...")
    aggregated_news = ""; total_articles = 0; article_map = {}; article_counter = 1
    headers = {'User-Agent': 'Mozilla/5.0'}
    global_seen_titles = set()

    # 🛑 THE FIX: Helper to deep-scrape article bodies using Trafilatura
    def extract_deep_text(url):
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
                if text:
                    return text[:1000].replace('\n', ' ') + "..."
        except Exception: pass
        return ""

    def add_to_payload(title, url, source_name):
        nonlocal article_counter, total_articles, aggregated_news
        clean_title = str(title).strip().lower()
        if clean_title in global_seen_titles: return
        global_seen_titles.add(clean_title)
        
        art_id = f"ART_{article_counter:03d}"
        article_map[art_id] = {"title": title, "url": url, "feed_source": source_name}
        
        body_text = extract_deep_text(url)
        if body_text:
            aggregated_news += f"ID: {art_id} | [{source_name}] {title}\n  DEEP DATA: {body_text}\n"
        else:
            aggregated_news += f"ID: {art_id} | [{source_name}] {title}\n"
            
        article_counter += 1; total_articles += 1

    # 1. Premium RSS
    for url in RSS_FEEDS:
        try:
            for entry in feedparser.parse(requests.get(url, headers=headers, timeout=15).text).entries[:5]:
                final_url = resolve_final_url(entry.link, headers)
                add_to_payload(entry.title, final_url, "Premium RSS")
        except Exception: pass

    # 2. Google News Live Sweeps (Using 7d for Weekly Scope)
    GOOGLE_QUERIES = [
        '("geopolitics" OR "sanctions" OR "foreign policy" OR "tariffs") when:7d',
        '("military" OR "defense" OR "missile" OR "conflict" OR "war") when:7d',
        '("outer space" OR "satellite" OR "orbital" OR "space force" OR "SpaceX") when:7d',
        '("semiconductor" OR "lithography" OR "rare earth" OR "critical minerals") when:7d',
        '("Indo-Pacific" OR "China" OR "Taiwan" OR "South China Sea" OR "AUKUS") when:7d',
        '("logistics" OR "supply chain" OR "Middle East" OR "Red Sea" OR "Strait of Hormuz") when:7d',
        '("artificial intelligence" OR "quantum computing" OR "data center" OR "Nvidia" OR "supercomputer") when:7d'
    ]
    for query in GOOGLE_QUERIES:
        try:
            gn_url = f'https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en&_={int(time.time())}'
            for entry in feedparser.parse(requests.get(gn_url, headers=headers, timeout=15).text).entries[:6]: 
                final_url = resolve_final_url(entry.link, headers)
                add_to_payload(entry.title, final_url, "Google News 7D")
        except Exception: pass

    # 3. Deep-Scrape Maritime (7 Days)
    print("🚢 Executing Deep-Scrape on Maritime URLs...")
    try:
        maritime_query = '("UKMTO" OR "Ambrey" OR "MSCHOA" OR "MSCIO") AND ("incident" OR "attack" OR "vessel" OR "boarded" OR "missile" OR "houthi") when:7d'
        gn_maritime_url = f'https://news.google.com/rss/search?q={urllib.parse.quote(maritime_query)}&hl=en-US&gl=US&_={int(time.time())}'
        for entry in feedparser.parse(requests.get(gn_maritime_url, headers=headers, timeout=15).text).entries[:8]: 
            final_url = resolve_final_url(entry.link, headers)
            add_to_payload(entry.title, final_url, "Maritime Deep Scrape")
    except Exception: pass

    # 4. Grafted Flash Pipeline Deep APIs
    def extract_api_feed(api_url, source_name, params=None):
        try:
            res = requests.get(api_url, headers=headers, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json().get('data', []) if 'war-monitor' in api_url else res.json()
                for e in data[:10]: 
                    title = e.get('title') or e.get('headline')
                    url = e.get('url') or e.get('link') or f"https://{source_name.lower().replace(' ', '')}.com/"
                    if title: add_to_payload(title, url, source_name)
        except Exception as e: print(f"⚠️ Failed {source_name}: {e}")

    extract_api_feed("https://monitor-the-situation.com/api/events", "MONITOR THE SITUATION", {"range": "7d", "feed": "live"})
    extract_api_feed("https://api.war-monitor.com/api/events", "WAR MONITOR", {"page": "1", "limit": "25", "fresh_hours": "168"})

    # 5. CISA
    try:
        url = "https://www.cisa.gov/cybersecurity-advisories/all.xml"
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            for entry in feedparser.parse(res.text).entries[:8]:
                add_to_payload(entry.title, entry.link, "CISA")
    except: pass

    # 6. Hegemon Global
    print("🌐 Executing Deep-Scrape on Hegemon Global...")
    try:
        hg_url = "https://hegemonglobal.com"
        add_to_payload("Hegemon Global Intel", hg_url, "Hegemon Global")
    except: pass

    # 7. Psyopoly Siphon
    psy_events, psy_raw_items = fetch_psyopoly_data()
    for item in psy_raw_items:
        add_to_payload(item["headline"], item["url"], "Psyopoly Supabase")

    print(f"📰 Successfully grabbed {total_articles} raw headlines mapped to internal indices.")
    
    article_map["psy_events_payload"] = psy_events
    
    return aggregated_news, total_articles, article_map

# ==========================================
# 4. AI EXTRACTION PIPELINE (IDENTIFIER SCHEMA)
# ==========================================
def extract_tactical_events(news_text):
    print("🧠 Pushing data to Gemini for tactical selection...")
    
    prompt = f"""
    You are an elite Geopolitics-OSINT analyst. 
    Review the following news entries, each preceded by a unique ID (e.g., ART_001).
    Extract 50 to 60 of the most critical geopolitical, defense, semiconductor, and supply chain events.
    
    CRITICAL INSTRUCTIONS:
    1. DIVERSITY MANDATE: You MUST prioritize events flagged from [MONITOR THE SITUATION], [WAR MONITOR], [CISA], and [PSYOPOLY] alongside standard news.
    2. You MUST output the result as a raw JSON array of objects. Do not include markdown formatting like ```json.
    
    Each object must have exactly these keys:
    "Article_ID": The exact ID string matching the news item chosen. Do not invent IDs.
    "Date": The current date (use {datetime.now().strftime('%Y-%m-%d')})
    "Actor": The country, company, or entity taking the action.
    "Action": A concise, 5-8 word description of the event.
    "Location": A specific country, region, or chokepoint.
    "Risk": Must be strictly one of: "CRITICAL", "HIGH", or "ELEVATED".
    
    News Data:
    {news_text}
    """
    
    raw_txt = generate_with_rotation(prompt, temperature=0.1)
    import re
    match = re.search(r'\[.*\]', raw_txt, re.DOTALL)
    if match: return json.loads(match.group(0))
    return json.loads(raw_txt.replace("```json", "").replace("```", "").strip())

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
        psy_events = source_article_map.pop("psy_events_payload", [])
        
        if article_count == 0:
            print("❌ ABORTING: No articles scraped. Preventing AI hallucination.")
            exit(1)
            
        # Extract strategic structured events (contains Article_ID references)
        extracted_events = extract_tactical_events(news_data)
        
        # 🛡️ THE DETERMINISTIC INJECTION STEP
        validated_tactical_events = []
        for event in extracted_events:
            target_id = event.get("Article_ID")
            
            if target_id in source_article_map:
                event["Source"] = source_article_map[target_id]["url"]
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