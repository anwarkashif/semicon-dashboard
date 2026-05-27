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
# 1. CONFIGURATION & SETUP (EXECUTIVE HOME)
# ==========================================
os.makedirs('data/executive_home', exist_ok=True)

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
            
    # --- PHASE 3: DEEP-SCRAPE MARITIME ALERTS (For Gemini Analysis) ---
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

    # --- PHASE 4: HEGEMON GLOBAL LIVE EXTRACTION ---
    print("🌐 Executing Deep-Scrape on Hegemon Global...")
    try:
        hg_url = "https://hegemonglobal.com"
        hg_res = requests.get(hg_url, headers=headers, timeout=15)
        hg_res.raise_for_status()
        soup = BeautifulSoup(hg_res.text, 'html.parser')

        # Extract headings and paragraphs to capture the main intelligence text
        text_elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
        extracted_hg_text = " ".join([elem.get_text(strip=True) for elem in text_elements if len(elem.get_text(strip=True)) > 20])

        if extracted_hg_text:
            # Truncate to ~1500 characters to ensure we capture a rich summary without overloading the token limit
            snippet = extracted_hg_text[:1500] + "..." if len(extracted_hg_text) > 1500 else extracted_hg_text
            aggregated_news += f"\n- [LIVE HEGEMON GLOBAL INTEL]\n  DEEP EXTRACTION DATA: {snippet}\n"
            total_articles += 1
            print("✅ Successfully extracted Hegemon Global intelligence.")
        else:
            print("⚠️ Hegemon Global returned no readable text.")
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch Hegemon Global - {e}")

    print(f"📰 Successfully grabbed {total_articles} raw headlines and deep-scraped data.")
    return aggregated_news, total_articles

# ==========================================
# 3. AI EXTRACTION PIPELINES
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
                sleep_time = 15 * (attempt + 1) 
                time.sleep(sleep_time)
            else:
                raise e 

def generate_flush_to_brief(news_text):
    print("🧠 Pushing data to Gemini for FLASH TO BRIEF generation...")
    prompt = f"""
    You are an elite Geopolitics-OSINT analyst. 
    Based on the provided raw intelligence from the last hour, generate a highly analytical "FLASH TO BRIEF" strategic intelligence report. 
    Your priority is rich data and deep analysis. Do not use generic filler words. Write with extreme precision.

    You MUST output ONLY a valid JSON object. Do not include markdown formatting like ```json. 
    
    It must have EXACTLY these keys and follow these guidelines:
    - "bluf": (Bottom Line Up Front - 3-4 sentences of immediate actionable intelligence summarizing the macro threat).
    - "tactical_indicators": (An Array of exactly 3 detailed string bullet points focusing on live anomalies).
    - "threat_narrative": (A rich analytical paragraph on state actor intent and macro shifts).
    - "risk_assessment": (A rich analytical paragraph evaluating supply chain vulnerabilities, maritime constraints, and market impacts).
    - "strategic_forecast": (A rich actionable forecast for the next 24 hours).

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
                time.sleep(sleep_time)
            else:
                raise e 

# ==========================================
# 4. EXECUTE & SAVE
# ==========================================
if __name__ == "__main__":
    try:
        news_data, article_count = fetch_daily_intelligence()
        
        if article_count == 0:
            print("❌ ABORTING: No articles scraped. Preventing AI hallucination.")
            exit(1)
            
        # 1. Generate the Tactical Grid Array
        tactical_events = extract_tactical_events(news_data)
        output_file_tactical = 'data/executive_home/tactical_events_24h.json'
        with open(output_file_tactical, 'w') as f:
            json.dump(tactical_events, f, indent=4)
        print(f"✅ Success! Wrote {len(tactical_events)} tactical events.")

        # 2. Generate the FLASH TO BRIEF Narrative
        flush_brief_data = generate_flush_to_brief(news_data)
        output_file_flush = 'data/executive_home/flush_brief_24h.json'
        with open(output_file_flush, 'w') as f:
            json.dump(flush_brief_data, f, indent=4)
        print("✅ Success! Wrote FLASH TO BRIEF data.")
        
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")