# -*- coding: utf-8 -*-
import os
import json
import time
import feedparser
import requests
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime
from google import genai

# ==========================================
# 1. CONFIGURATION & SETUP (TODAY'S SNIPPET)
# ==========================================
os.makedirs('data/today_snippet', exist_ok=True)

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
    "https://fulcrum.sg/feed/", 

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

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 1.5. PSYOPOLY SUPABASE EXTRACTION
# ==========================================
def fetch_psyopoly_data():
    print("🔍 Siphoning West Asia intelligence from Psyopoly...")
    SUPABASE_URL = "https://lojirolzkshoqgccrwyh.supabase.co/rest/v1/breaking_news?select=id%2Cheadline%2Cposted_at%2Curl&order=posted_at.desc&limit=20"
    ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvamlyb2x6a3Nob3FnY2Nyd3loIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwODQyNjQsImV4cCI6MjA4OTY2MDI2NH0.DzdBr_d69SSlRxtnxH8DRqc0hLNQfb4wL5t1Qe96UMo"
    
    headers = {
        "apikey": ANON_KEY,
        "authorization": f"Bearer {ANON_KEY}",
        "accept": "application/json",
        "origin": "https://www.psyopoly.pro"
    }
    formatted_events = []
    raw_text_block = "\n\n=== LIVE PSYOPOLY WEST ASIA INTEL ===\n"
    
    try:
        res = requests.get(SUPABASE_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            raw_data = res.json()
            for item in raw_data:
                headline = item.get("headline", "No Headline Provided")
                raw_text_block += f"- [PSYOPOLY] {headline}\n"
                
                formatted_events.append({
                    "Date": item.get("posted_at", "").split("T")[0],
                    "Actor": "Psyopoly/West Asia",
                    "Location": "Middle East",
                    "Event": "Strategic Update",
                    "Action": headline[:60] + "..." if len(headline) > 60 else headline,
                    "Summary": headline,
                    "Risk": "HIGH",
                    "Source": item.get("url", "https://www.psyopoly.pro/middle-east")
                })
            return formatted_events, raw_text_block
    except Exception as e:
        print(f"⚠️ Psyopoly extraction failed: {e}")
        
    return [], ""

# ==========================================
# 2. DATA SCRAPING (ANTI-BOT + LIVE BOOLEAN + DEEP SCRAPE)
# ==========================================
def fetch_daily_intelligence():
    print("🌍 Scraping strategic RSS & LIVE Boolean feeds...")
    aggregated_news = ""
    total_articles = 0
    
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
                aggregated_news += f"- [MACRO] {entry.title}\n"
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
                aggregated_news += f"- [LIVE 1H] {entry.title}\n"
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
            url = entry.link
            try:
                page_res = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(page_res.text, 'html.parser')
                
                paragraphs = soup.find_all('p')
                extracted_text = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30])
                
                if extracted_text:
                    snippet = extracted_text[:800] + "..." if len(extracted_text) > 800 else extracted_text
                    aggregated_news += f"\n- [LIVE MARITIME ALERT - {entry.title}]\n  DEEP EXTRACTION DATA: {snippet}\n"
                else:
                    aggregated_news += f"\n- [LIVE MARITIME ALERT] {entry.title}\n"
                
                total_articles += 1
            except Exception as e:
                aggregated_news += f"\n- [LIVE MARITIME ALERT] {entry.title}\n"
                total_articles += 1
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch Maritime Boolean - {e}")

    # --- PHASE 5: PSYOPOLY WEST ASIA INTEGRATION ---
    psy_events, psy_text = fetch_psyopoly_data()
    if psy_text:
        aggregated_news += psy_text
        total_articles += len(psy_events)

    print(f"📰 Successfully grabbed {total_articles} raw headlines and deep-scraped data.")
    return aggregated_news, total_articles, psy_events

# ==========================================
# 3. AI EXTRACTION PIPELINE
# ==========================================
def extract_tactical_events(news_text):
    print("🧠 Pushing data to Gemini for tactical extraction...")
    
    prompt = f"""
    You are an elite Geopolitics-OSINT analyst. 
    Review the following news headlines from the last 24 hours. Extract EXACTLY 8 of the most critical geopolitical, defense, semiconductor, or supply chain events.
    
    CRITICAL RULE: Ensure maximum diversity. Mix maritime, semiconductor, geopolitical, and military events. Do not pull everything from one region.
    
    You MUST output the result as a raw JSON array of objects. Do not include markdown formatting like ```json.
    
    Each object must have exactly these keys:
    "Date": The current date (use {datetime.now().strftime('%Y-%m-%d')})
    "Actor": The country, company, or entity taking the action.
    "Action": A concise, 5-8 word description of the event.
    "Location": A specific country, region, or chokepoint (e.g., "Taiwan", "Red Sea", "Global").
    "Risk": Must be strictly one of: "CRITICAL", "HIGH", or "ELEVATED".
    "Headline": The original or highly summarized headline of the event.
    
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

def generate_shift_brief(tactical_events):
    print("🧠 Pushing data to Gemini for 12H Strategic Shift Brief generation...")
    
    prompt = f"""
    You are a senior Geopolitics-OSINT intelligence analyst.
    Review the following tactical alerts from the last 12 hours:
    {json.dumps(tactical_events)}

    Synthesize a deeply analytical 12-Hour Strategic Snippet.
    CRITICAL INSTRUCTION: You must write extremely detailed, long-form content. Use strict Markdown formatting (use dashes '-' for bullet points). DO NOT USE HTML TAGS.

    Return ONLY a valid JSON object with the following keys exactly as written:
    - "date": Current date/time
    - "bluf": Write a structured Actionable Intelligence BLUF using strict Markdown. Format exactly as: **BLUF:** [1-2 sentences on main threat/insight]. **Impact:** [1-2 sentences]. **Evidence:** [2 brief bullets]. **Action:** [1-2 immediate actions].
    - "executive_summary": Write exactly 3 paragraphs detailing the macro threat landscape and supply chain resilience.
    - "escalation_indicators": A detailed Markdown bulleted list (- ) of warning signs. Provide 3 sentences of context for each bullet point.
    - "strategic_outlook": Write exactly 4 paragraphs providing a predictive assessment for the next 24-48 hours.
    - "threat_level": String, e.g., "ELEVATED", "MODERATE", "CRITICAL".

    Do not include markdown blocks like ```json. Just output the raw JSON.
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
                time.sleep(15 * (attempt + 1))
            else:
                raise e 

# ==========================================
# 4. EXECUTE & SAVE
# ==========================================
if __name__ == "__main__":
    try:
        news_data, article_count, psy_events = fetch_daily_intelligence()
        
        if article_count == 0:
            print("❌ ABORTING: No articles scraped. Preventing AI hallucination.")
            exit(1)
            
        tactical_events = extract_tactical_events(news_data)
        
        # Inject Psyopoly Intel natively into the JSON structure (CAPPED AT 2)
        if psy_events:
            tactical_events = psy_events[:2] + tactical_events
            print(f"✅ Injected top 2 native Psyopoly variables into the tactical payload.")
        
        output_file_tactical = 'data/today_snippet/tactical_events_24h.json'
        with open(output_file_tactical, 'w') as f:
            json.dump(tactical_events, f, indent=4)
            
        print(f"✅ Success! Wrote {len(tactical_events)} tactical events.")

        # Pass the newly enriched tactical events directly into the AI brief generator
        shift_brief_data = generate_shift_brief(tactical_events)
        output_file_brief = 'data/today_snippet/shift_brief.json'
        with open(output_file_brief, 'w') as f:
            json.dump(shift_brief_data, f, indent=4)

        print("✅ Success! Wrote 12H Strategic Shift Brief.")
        
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")