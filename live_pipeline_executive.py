# -*- coding: utf-8 -*-
import os
import json
import time
import feedparser
import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urlparse
from datetime import datetime
from google import genai
from huggingface_hub import HfApi
import re # 🛑 THE FIX: Guaranteeing JSON Extraction

os.makedirs('data/executive_home', exist_ok=True)

RSS_FEEDS = [
    "https://www.ft.com/technology?format=rss", "https://www.atlanticcouncil.org/feed/", "https://foreignpolicy.com/feed/",
    "https://moderndiplomacy.eu/feed/", "https://www.worldpoliticsreview.com/feed/", "https://www.defenseone.com/rss/all/",
    "https://warontherocks.com/feed/", "https://www.realcleardefense.com/index.xml", "https://www.c4isrnet.com/arc/outboundfeeds/rss/",
    "https://www.defensenews.com/arc/outboundfeeds/rss/", "https://spacepolicyonline.com/feed/", "https://www.space.com/feeds/all",
    "https://spacewatch.global/feed/", "https://spaceflightnow.com/feed/", "https://www.satellitetoday.com/feed/", 
    "https://semiwiki.com/feed/", "https://semiengineering.com/feed/", "https://www.mining.com/feed/",
    "https://www.eetimes.com/feed/", "https://www.supplychaindive.com/feeds/news/", "https://thediplomat.com/feed/",
    "https://technode.com/feed/", "https://asiatimes.com/feed/", "https://www.aspistrategist.org.au/feed/", 
    "https://fulcrum.sg/feed/", "https://gcaptain.com/feed/", "https://www.middleeasteye.net/rss",
    "https://www.aljazeera.com/xml/rss/all.xml", "https://www.al-monitor.com/rss.xml", "https://splash247.com/feed/", 
    "https://www.nextplatform.com/feed/", "https://thequantuminsider.com/feed/", "https://spectrum.ieee.org/feeds/feed.rss",
    "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "https://venturebeat.com/category/ai/feed/"
]

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# ==========================================
# 2. URL VALIDATION & REDIRECT UNPACKING
# ==========================================
def valid_url(url):
    if not url: return False
    try: return urlparse(url).scheme in ["http", "https"]
    except: return False

def resolve_final_url(url, headers):
    if not url or "news.google.com" not in url: return url
    try:
        r = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        final_url = r.url
        if any(d in urlparse(final_url).netloc.lower() for d in ["news.google.com", "google.com"]):
            return url
        return final_url
    except Exception: return url

def fetch_psyopoly_data():
    SUPABASE_URL = "https://lojirolzkshoqgccrwyh.supabase.co/rest/v1/breaking_news?select=id%2Cheadline%2Cposted_at%2Curl&order=posted_at.desc&limit=20"
    ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvamlyb2x6a3Nob3FnY2Nyd3loIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwODQyNjQsImV4cCI6MjA4OTY2MDI2NH0.DzdBr_d69SSlRxtnxH8DRqc0hLNQfb4wL5t1Qe96UMo"
    headers = {"apikey": ANON_KEY, "authorization": f"Bearer {ANON_KEY}", "accept": "application/json"}
    
    formatted_events = []; raw_psy_items = []
    try:
        for item in requests.get(SUPABASE_URL, headers=headers, timeout=10).json():
            headline = item.get("headline", "No Headline Provided")
            url = item.get("url", "https://www.psyopoly.pro/middle-east")
            if not valid_url(url): continue
            
            raw_psy_items.append({"headline": headline, "url": url})
            formatted_events.append({
                "Date": item.get("posted_at", "").split("T")[0],
                "Actor": "Psyopoly/West Asia", "Location": "Middle East",
                "Event": "Strategic Update", "Action": headline[:60] + "...",
                "Summary": headline, "Risk": "HIGH", "Source": url,
                "Title": headline, "Feed_Source": "Psyopoly Supabase",
                "Publisher": urlparse(url).netloc.replace("www.", "")
            })
        return formatted_events, raw_psy_items
    except Exception: return [], []

def fetch_daily_intelligence():
    print("🌍 Scraping strategic feeds & resolving publisher URLs...")
    aggregated_news = ""; total_articles = 0; article_map = {}; article_counter = 1
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for url in RSS_FEEDS:
        try:
            for entry in feedparser.parse(requests.get(url, headers=headers, timeout=15).text).entries[:5]:
                art_id = f"ART_{article_counter:03d}"; final_url = resolve_final_url(entry.link, headers)
                article_map[art_id] = {"title": entry.title, "url": final_url, "feed_source": "Premium RSS"}
                aggregated_news += f"ID: {art_id} | [MACRO] {entry.title}\n"
                article_counter += 1; total_articles += 1
        except Exception: pass

    for query in ['("geopolitics" OR "sanctions" OR "foreign policy" OR "tariffs") when:1h', '("semiconductor" OR "lithography" OR "rare earth" OR "critical minerals") when:1h', '("artificial intelligence" OR "quantum computing" OR "data center" OR "Nvidia") when:1h']:
        try:
            gn_url = f'https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en&_={int(time.time())}'
            for entry in feedparser.parse(requests.get(gn_url, headers=headers, timeout=15).text).entries[:5]: 
                art_id = f"ART_{article_counter:03d}"; final_url = resolve_final_url(entry.link, headers)
                article_map[art_id] = {"title": entry.title, "url": final_url, "feed_source": "Google News Live 1H"}
                aggregated_news += f"ID: {art_id} | [LIVE 1H] {entry.title}\n"
                article_counter += 1; total_articles += 1
        except Exception: pass
            
    print("🚢 Executing Deep-Scrape on Live Maritime URLs...")
    try:
        gn_maritime_url = f'https://news.google.com/rss/search?q={urllib.parse.quote("UKMTO OR Ambrey OR Houthi attack")}...&_={int(time.time())}'
        m_feed = feedparser.parse(requests.get(gn_maritime_url, headers=headers, timeout=15).text)
        for entry in m_feed.entries[:6]: 
            final_url = resolve_final_url(entry.link, headers)
            art_id = f"ART_{article_counter:03d}"
            article_map[art_id] = {"title": entry.title, "url": final_url, "feed_source": "Maritime Deep Scrape"}
            try:
                text = " ".join([p.get_text(strip=True) for p in BeautifulSoup(requests.get(final_url, headers=headers, timeout=10).text, 'html.parser').find_all('p') if len(p.get_text()) > 30])
                aggregated_news += f"ID: {art_id} | [MARITIME] {entry.title}\n DATA: {text[:800]}...\n" if text else f"ID: {art_id} | [MARITIME] {entry.title}\n"
            except Exception: aggregated_news += f"ID: {art_id} | [MARITIME] {entry.title}\n"
            article_counter += 1; total_articles += 1
    except Exception: pass

    print("🌐 Executing Deep-Scrape on Hegemon Global...")
    try:
        hg_url = "https://hegemonglobal.com"
        text = " ".join([e.get_text(strip=True) for e in BeautifulSoup(requests.get(hg_url, headers=headers, timeout=15).text, 'html.parser').find_all(['h1', 'h2', 'h3', 'p']) if len(e.get_text()) > 20])
        if text:
            art_id = f"ART_{article_counter:03d}"
            article_map[art_id] = {"title": "Hegemon Global Intel", "url": hg_url, "feed_source": "Hegemon Global"}
            aggregated_news += f"ID: {art_id} | [HEGEMON GLOBAL]\n DATA: {text[:1500]}...\n"
            article_counter += 1; total_articles += 1
    except Exception: pass

    psy_events, psy_raw_items = fetch_psyopoly_data()
    for item in psy_raw_items:
        art_id = f"ART_{article_counter:03d}"
        article_map[art_id] = {"title": item["headline"], "url": item["url"], "feed_source": "Psyopoly Supabase"}
        aggregated_news += f"ID: {art_id} | [PSYOPOLY] {item['headline']}\n"
        article_counter += 1; total_articles += 1

    return aggregated_news, total_articles, psy_events, article_map

def extract_tactical_events(news_text):
    prompt = f"""
    You are an elite Geopolitics-OSINT analyst. Review entries preceded by IDs. Extract 4-6 critical events.
    Output raw JSON array. Keys exactly: "Article_ID", "Date", "Actor", "Action", "Location", "Risk".
    Data: {news_text}
    """
    for attempt in range(3):
        try: 
            raw_txt = client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text.strip()
            # 🛑 THE FIX: STRICT REGEX ARRAY EXTRACTION
            match = re.search(r'\[.*\]', raw_txt, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(raw_txt.replace("```json", "").replace("```", "").strip())
        except Exception: time.sleep(15 * (attempt + 1))
    raise Exception("Max retries reached.")

def generate_flush_to_brief(accumulated_events):
    prompt = f"You are an elite Geopolitics-OSINT analyst. Generate a FLASH TO BRIEF based on this data: {json.dumps(accumulated_events)}. Output ONLY a valid JSON object matching exactly: bluf, tactical_indicators, threat_narrative, risk_assessment, strategic_forecast."
    
    for attempt in range(3):
        try: 
            # 🛠️ FORCE GEMINI TO OUTPUT STRICT JSON
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config={"response_mime_type": "application/json", "temperature": 0.2}
            )
            
            raw_text = response.text.strip()
            
            # 🛑 THE FIX: STRICT REGEX OBJECT EXTRACTION
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
                
            return json.loads(raw_text)
        except Exception as e: 
            print(f"🚨 Executive API Attempt {attempt + 1} Failed: {e}")
            time.sleep(10)
        
    # 🛡️ DETERMINISTIC FALLBACK
    return {
        "bluf": "API Generation Timeout. Scanning macro-strategic feeds. Awaiting next telemetry generation cycle...",
        "tactical_indicators": ["API Rate Limit Hit", "System Awaiting Reset", "Data Pipeline Intact"],
        "threat_narrative": "Generation pending next scheduled cron execution.",
        "risk_assessment": "PENDING",
        "strategic_forecast": "PENDING"
    }

if __name__ == "__main__":
    try:
        news_data, article_count, psy_events, source_map = fetch_daily_intelligence()
        if article_count == 0: exit(1)
            
        extracted_events = extract_tactical_events(news_data)
        
        # 🛡️ DETERMINISTIC INJECTION & METADATA HYDRATION
        validated_tactical_events = []
        seen_urls = set()
        validated_count = 0
        
        for event in extracted_events:
            target_id = event.get("Article_ID")
            if target_id not in source_map:
                print(f"⚠️ Rejected invalid ID: {target_id}")
                continue
                
            url = source_map[target_id]["url"]
            if not valid_url(url):
                print(f"⚠️ Rejected invalid URL: {url}")
                continue
                
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            event["Source"] = url
            event["Title"] = source_map[target_id]["title"]
            event["Feed_Source"] = source_map[target_id]["feed_source"]
            event["Publisher"] = urlparse(url).netloc.replace("www.", "")
            del event["Article_ID"]
            
            validated_tactical_events.append(event)
            validated_count += 1
            
        print(f"✅ Validated {validated_count} of {len(extracted_events)} Gemini selections")
        
        if psy_events:
            validated_tactical_events = psy_events[:2] + validated_tactical_events
            
        output_file_tactical = 'data/executive_home/tactical_events_24h.json'
        master_events = []
        if os.path.exists(output_file_tactical):
            try: master_events = json.load(open(output_file_tactical, 'r'))
            except Exception: pass
                
        master_events = validated_tactical_events + master_events
        
        seen = set(); unique_master = []
        for e in master_events:
            iden = e.get('Action', e.get('Headline', '')).strip().lower()
            if iden and iden not in seen:
                seen.add(iden); unique_master.append(e)
                
        unique_master = unique_master[:25]
        json.dump(unique_master, open(output_file_tactical, 'w'), indent=4)
        json.dump(generate_flush_to_brief(unique_master), open('data/executive_home/flush_brief_24h.json', 'w'), indent=4)
        
        HF_TOKEN = os.environ.get("HF_TOKEN"); REPO_ID = os.environ.get("SPACE_ID") or "anwarkashif/semicon-dashboard"
        if HF_TOKEN and REPO_ID:
            api = HfApi()
            api.upload_file(path_or_fileobj=output_file_tactical, path_in_repo=output_file_tactical, repo_id=REPO_ID, repo_type="space", token=HF_TOKEN, commit_message="Sync Executive Home Tactical (100% Provenance)")
            api.upload_file(path_or_fileobj='data/executive_home/flush_brief_24h.json', path_in_repo='data/executive_home/flush_brief_24h.json', repo_id=REPO_ID, repo_type="space", token=HF_TOKEN)
            
    except Exception as e: print(f"❌ Pipeline Failed: {e}")