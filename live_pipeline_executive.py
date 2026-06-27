# -*- coding: utf-8 -*-
import os
import json
import time
import feedparser
import requests
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urlparse
from datetime import datetime, timezone
from google import genai
from huggingface_hub import HfApi
import re
import logging

os.makedirs('data/executive_home', exist_ok=True)

logging.basicConfig(
    filename='data/pipeline_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

def generate_with_rotation(prompt, temperature=0.1):
    if not VALID_KEYS:
        raise Exception("CRITICAL: No valid API keys found in environment.")
        
    current_idx = 0
    failures = 0
    
    while current_idx < len(VALID_KEYS):
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
            err_msg = str(e)
            log_msg = f"API Key {current_idx + 1} Attempt {failures} Failed: {type(e).__name__} - {err_msg[:100]}"
            print(f"⚠️ {log_msg}")
            logging.warning(log_msg)
            
            if failures >= 2:
                print(f"🔄 Rotating to API Key {current_idx + 2}...")
                logging.info(f"Rotating to API Key {current_idx + 2}")
                current_idx += 1
                failures = 0
                time.sleep(3)
            else:
                time.sleep(10)
                
    raise Exception("All API keys exhausted via rotation.")

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
    raw_txt = generate_with_rotation(prompt, temperature=0.1)
    match = re.search(r'\[.*\]', raw_txt, re.DOTALL)
    if match: return json.loads(match.group(0))
    return json.loads(raw_txt.replace("```json", "").replace("```", "").strip())

def generate_flush_to_brief(accumulated_events):
    trimmed = accumulated_events[:10]
    
    # 🛑 THE FIX: Explicitly instructing the LLM to format EVERY section as a professionally written paragraph.
    prompt = (
        "You are an elite Geopolitics-OSINT analyst. "
        f"Generate a FLASH TO BRIEF from this data: {json.dumps(trimmed)}. "
        "Output ONLY a valid JSON object with these exact keys: "
        "bluf, tactical_indicators, threat_narrative, risk_assessment, strategic_forecast. "
        "CRITICAL: ALL values must be comprehensive, professionally graded analytical paragraphs. Do NOT use bullet points or JSON arrays for any section."
    )
    
    try:
        raw_txt = generate_with_rotation(prompt, temperature=0.2)
        match = re.search(r'\{.*\}', raw_txt, re.DOTALL)
        if match: return json.loads(match.group(0))
        return json.loads(raw_txt)
    except Exception as e:
        logging.error(f"FLASH TO BRIEF Final Failure: {e}")
        return {
            "bluf": "API Generation Timeout. Scanning macro-strategic feeds. Awaiting next telemetry generation cycle...",
            "tactical_indicators": "System Awaiting Reset. Data Pipeline Intact.",
            "threat_narrative": "Generation pending next scheduled cron execution.",
            "risk_assessment": "PENDING",
            "strategic_forecast": "PENDING"
        }

if __name__ == "__main__":
    try:
        news_data, article_count, psy_events, source_map = fetch_daily_intelligence()
        if article_count == 0: exit(1)
            
        extracted_events = []
        try:
            extracted_events = extract_tactical_events(news_data)
        except Exception as e:
            error_txt = f"Gemini Extraction Failed due to API limits. Proceeding with Psyopoly Direct Injection. Error: {e}"
            print(f"⚠️ {error_txt}")
            logging.warning(error_txt)
        
        validated_tactical_events = []
        seen_urls = set()
        validated_count = 0
        
        for event in extracted_events:
            target_id = event.get("Article_ID")
            if target_id not in source_map: continue
                
            url = source_map[target_id]["url"]
            if not valid_url(url) or url in seen_urls: continue
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
            validated_tactical_events = psy_events[:3] + validated_tactical_events
            
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
        
        print("⏳ Pooling data before FLASH TO BRIEF generation...")
        brief_input = unique_master[:10]
        
        flush_brief_data = generate_flush_to_brief(brief_input)
        json.dump(flush_brief_data, open('data/executive_home/flush_brief_24h.json', 'w'), indent=4)
        
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # 🛑 THE FIX: Ensured tactical_indicators is successfully passed into the Archive payload
        bluf = flush_brief_data.get('bluf', '')
        tactical = flush_brief_data.get('tactical_indicators', '')
        narrative = flush_brief_data.get('threat_narrative', '')
        risk = flush_brief_data.get('risk_assessment', '')
        forecast = flush_brief_data.get('strategic_forecast', '')
        
        parts = []
        if bluf: parts.append(f"**🎯 BLUF:**\n{bluf}")
        if tactical: parts.append(f"**🚩 TACTICAL INDICATORS:**\n{tactical}")
        if narrative: parts.append(f"**🕸️ THREAT NARRATIVE:**\n{narrative}")
        if risk: parts.append(f"**⚖️ RISK ASSESSMENT:**\n{risk}")
        if forecast: parts.append(f"**🔭 STRATEGIC FORECAST:**\n{forecast}")
        compiled_raw = "\n\n---\n\n".join(parts)
        
        daily_sources = []
        for event in unique_master:
            if "Source" in event and "Title" in event:
                daily_sources.append({"title": event["Title"], "url": event["Source"]})
        
        archive_payload = {
            "date": date_str,
            "title": f"Flash to Brief - {date_str}",
            "brief_raw": compiled_raw,
            "recent_actions": unique_master,
            "sources": daily_sources
        }
        
        archive_filename = f"data/brief_flash_{date_str}.json"
        with open(archive_filename, 'w', encoding='utf-8') as f:
            json.dump(archive_payload, f, indent=4)
        
        HF_TOKEN = os.environ.get("HF_TOKEN"); REPO_ID = os.environ.get("SPACE_ID") or "anwarkashif/semicon-dashboard"
        if HF_TOKEN and REPO_ID:
            api = HfApi()
            api.upload_file(path_or_fileobj=output_file_tactical, path_in_repo=output_file_tactical, repo_id=REPO_ID, repo_type="space", token=HF_TOKEN, commit_message="Sync Executive Home Tactical")
            api.upload_file(path_or_fileobj='data/executive_home/flush_brief_24h.json', path_in_repo='data/executive_home/flush_brief_24h.json', repo_id=REPO_ID, repo_type="space", token=HF_TOKEN)
            api.upload_file(path_or_fileobj=archive_filename, path_in_repo=archive_filename, repo_id=REPO_ID, repo_type="space", token=HF_TOKEN)
            print("✅ Executive Flash Archive Synced securely with Source URLs!")
            
    except Exception as e: 
        print(f"❌ Pipeline Failed: {e}")
        logging.error(f"Pipeline Failed: {e}")