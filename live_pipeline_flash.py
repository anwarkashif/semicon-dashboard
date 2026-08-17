# -*- coding: utf-8 -*-
import os
import json
import time
import requests
import feedparser
from urllib.parse import urlparse
from google import genai
from huggingface_hub import HfApi
import trafilatura  # 🛑 THE FIX: Added Trafilatura for deep text extraction

GEMINI_API_KEY_SECONDARY = os.environ.get("RAG_GEMINI_API_KEY_5")
if not GEMINI_API_KEY_SECONDARY:
    print("Error: RAG_GEMINI_API_KEY_5 environment variable not set.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY_SECONDARY)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive'
}

def valid_url(url):
    if not url: return False
    try: return urlparse(url).scheme in ["http", "https"]
    except: return False

def robust_gemini_call(prompt, task_name="Generation"):
    models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
    for model_name in models:
        print(f"🤖 Attempting {task_name} with {model_name}...")
        for attempt in range(2):
            try:
                response = client.models.generate_content(model=model_name, contents=prompt)
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_text)
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ API Error on {model_name}: {error_msg}")
                if '429' in error_msg or 'Quota' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                    break 
                time.sleep(5)
    raise Exception(f"❌ FATAL: All Gemini models failed for {task_name}.")

def fetch_and_evaluate_flash_alerts():
    article_map = {}
    article_counter = 1
    raw_intel_payload = ""
    global_seen_titles = set() # 🛡️ NEW: TITLE DEDUPLICATION SHIELD

    # 🛑 THE FIX: Helper to deep-scrape article bodies using Trafilatura
    def extract_deep_text(url):
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
                if text:
                    # Return the first 1000 characters to give Gemini rich context without blowing up token limits
                    return text[:1000].replace('\n', ' ') + "..."
        except Exception: pass
        return ""

    # Helper function to process feeds and remove title duplicates instantly
    def add_to_payload(feed_data, source_name, max_items=15):
        nonlocal article_counter, raw_intel_payload
        added = 0
        raw_intel_payload += f"\n--- {source_name} ---\n"
        for e in feed_data:
            title = e.get('title')
            if not title: continue
            
            clean_title = str(title).strip().lower()
            if clean_title in global_seen_titles:
                continue # Skip exact title duplicates
                
            global_seen_titles.add(clean_title)
            
            url = e.get('url') or e.get('link') or f"https://{source_name.lower().replace(' ', '')}.com/"
            art_id = f"ART_{article_counter:03d}"
            article_map[art_id] = {"title": title, "url": url, "feed_source": source_name}
            
            # 🛑 THE FIX: Deep extract the article body
            body_text = extract_deep_text(url)
            
            if body_text:
                raw_intel_payload += f"ID: {art_id} | TITLE: {title}\n  DEEP DATA: {body_text}\n"
            else:
                raw_intel_payload += f"ID: {art_id} | TITLE: {title}\n"
            
            article_counter += 1
            added += 1
            if added >= max_items: break

    # --- 1. MONITOR THE SITUATION ---
    try:
        url = "https://monitor-the-situation.com/api/events"
        res = requests.get(url, headers={'Referer': 'https://monitor-the-situation.com/', **HEADERS}, params={"range": "12h", "feed": "live"}, timeout=10)
        if res.status_code == 200:
            add_to_payload(res.json(), "MONITOR THE SITUATION")
    except Exception as e: print(f"⚠️ Failed MTS: {e}")

    # --- 2. WAR MONITOR ---
    try:
        url = "https://doibxberkxwpkwpmyvon.supabase.co/functions/v1/twitter-osint"
        anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRvaWJ4YmVya3h3cGt3cG15dm9uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE2ODgzMTksImV4cCI6MjA4NzI2NDMxOX0.NIH12xDyXzAauMdgsJ9GN0NRw4kXFLQjaRVRZnQsfvo"
        
        wm_headers = HEADERS.copy()
        wm_headers.update({
            'apikey': anon_key,
            'authorization': f"Bearer {anon_key}",
            'Origin': 'https://warmonitor.app',
            'Referer': 'https://warmonitor.app/',
            'Content-Type': 'application/json'
        })

        res = requests.post(url, headers=wm_headers, json={"batch_index": 1}, timeout=15)
        if res.status_code == 200:
            posts = res.json().get('posts', [])
            
            # Map 'text' to 'title' so the add_to_payload helper function can read it
            mapped_events = []
            for post in posts:
                post_url = post.get('url', f"https://x.com/{post.get('author_username', '')}/status/{post.get('tweet_id', '')}")
                mapped_events.append({
                    "title": post.get('text', 'No Title Provided'),
                    "url": post_url
                })
                
            if mapped_events: 
                add_to_payload(mapped_events, "WAR MONITOR")
            else: 
                print("⚠️ War Monitor returned an empty posts array.")
        else:
            print(f"⚠️ War Monitor API returned status {res.status_code}")
    except Exception as e: 
        print(f"⚠️ Failed War Monitor Block: {e}")

    # --- 3. CISA ---
    try:
        url = "https://www.cisa.gov/cybersecurity-advisories/all.xml"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            feed = feedparser.parse(res.text)
            add_to_payload(feed.entries, "CISA")
    except Exception as e: print(f"⚠️ Failed CISA: {e}")

    # --- AI EXTRACTION (ID ONLY) ---
    prompt = f"""
    You are a Geopolitics-OSINT Intelligence Router. Review the following raw feeds and Deep Extraction Data.
    Select EXACTLY 10 distinct, critical geopolitical, cyber, or defense-related events.
    
    CRITICAL INSTRUCTIONS:
    1. Return exactly 10 objects.
    2. Do NOT invent IDs. You must use the EXACT "Article_ID" provided.
    3. DIVERSITY MANDATE: You MUST select items from ALL THREE sources (MONITOR THE SITUATION, WAR MONITOR, CISA). Do not pick all 10 from just one source.
    4. THREAT SCORING: You MUST assign a realistic `threat_level` based on severity: "CRITICAL" (Red-level), "HIGH" (Orange-level), or "WATCH" (Yellow-level). 
    
    Output a raw JSON array. Format exactly like this:
    [
      {{
        "Article_ID": "ART_001",
        "threat_level": "HIGH"
      }}
    ]
    
    Raw Data:
    {raw_intel_payload}
    """
    
    extracted_ids = robust_gemini_call(prompt, "Flash Alert Evaluation")
    
    # --- 🛡️ DETERMINISTIC REATTACHMENT & METADATA INJECTION ---
    final_flash_data = []
    seen_urls = set()
    validated_count = 0

    for item in extracted_ids:
        t_id = item.get("Article_ID")
        if t_id not in article_map:
            print(f"⚠️ Rejected invalid ID: {t_id}")
            continue
            
        url = article_map[t_id]["url"]
        if not valid_url(url) or url in seen_urls:
            continue
            
        seen_urls.add(url)
        final_flash_data.append({
            "Source": url,
            "Title": article_map[t_id]["title"],
            "Feed_Source": article_map[t_id]["feed_source"],
            "Publisher": urlparse(url).netloc.replace("www.", ""),
            "threat_level": item.get("threat_level", "WATCH")
        })
        validated_count += 1
        
        # Enforce strict 10-item limit if Gemini over-generates
        if len(final_flash_data) == 10: 
            break
            
    # --- 🚀 CRITICAL PADDING: GUARANTEE EXACTLY 10 DIVERSE ITEMS ---
    if len(final_flash_data) < 10:
        print(f"⚠️ Padding required. Gemini only validated {len(final_flash_data)} items. Adding {10 - len(final_flash_data)} more unique alerts.")
        for aid, adata in article_map.items():
            if len(final_flash_data) >= 10: 
                break
            url = adata["url"]
            if url not in seen_urls:
                seen_urls.add(url)
                final_flash_data.append({
                    "Source": url,
                    "Title": adata["title"],
                    "Feed_Source": adata["feed_source"],
                    "Publisher": urlparse(url).netloc.replace("www.", ""),
                    "threat_level": "WATCH"
                })

    print(f"✅ Validated exactly {len(final_flash_data)} unique Gemini/Fallback selections")
    return final_flash_data

# =========================================================================
# START EXECUTIVE HOME PIPELINE LOGIC
# =========================================================================

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
    os.environ.get("GEMINI_API_KEY_SECONDARY"),
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
            err_msg = str(e)
            log_msg = f"API Key {current_idx + 1} Attempt {failures} Failed: {type(e).__name__} - {err_msg[:100]}"
            print(f"⚠️ {log_msg}")
            logging.warning(log_msg)
            
            # 🛑 CRITICAL FIX: Instantly pause for 65 seconds if a 429 Quota limit is hit to prevent burning keys
            if "429" in err_msg or "quota" in err_msg.lower():
                print("🛑 429 Quota Limit Hit! Forcing strict 65-second API cooldown...")
                time.sleep(65)
            else:
                time.sleep(10)
            
            if failures >= 2:
                current_idx += 1
                failures = 0
                
                if current_idx >= len(VALID_KEYS):
                    print("⏳ All keys exhausted in this cycle. Sleeping an additional 60 seconds...")
                    logging.info("All keys exhausted. Sleeping additional 60s.")
                    time.sleep(60)
                    current_idx = 0
                    global_cycles += 1
                else:
                    print(f"🔄 Rotating to API Key {current_idx + 1}...")
                    logging.info(f"Rotating to API Key {current_idx + 1}")
                    time.sleep(5)
                
    raise Exception("CRITICAL: All API keys exhausted across multiple recovery cycles. Manual intervention required.")

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
    print("🌍 Scraping strategic feeds, resolving URLs, & Executing Deep Text Extraction...")
    aggregated_news = ""; total_articles = 0; article_map = {}; article_counter = 1
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 🛑 Trafilatura is completely untouched here.
    def extract_deep_text(url):
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
                if text:
                    return text[:1000].replace('\n', ' ') + "..."
        except Exception: pass
        return ""

    for url in RSS_FEEDS:
        try:
            for entry in feedparser.parse(requests.get(url, headers=headers, timeout=15).text).entries[:5]:
                art_id = f"ART_{article_counter:03d}"
                final_url = resolve_final_url(entry.link, headers)
                
                body_text = extract_deep_text(final_url)
                
                article_map[art_id] = {"title": entry.title, "url": final_url, "feed_source": "Premium RSS"}
                
                if body_text:
                    aggregated_news += f"ID: {art_id} | [MACRO] {entry.title}\n  DEEP DATA: {body_text}\n"
                else:
                    aggregated_news += f"ID: {art_id} | [MACRO] {entry.title}\n"
                    
                article_counter += 1; total_articles += 1
        except Exception: pass

    current_utc_hour = datetime.now(timezone.utc).hour
    is_super_brief_run = current_utc_hour >= 18 
    time_modifier = "when:1d" if is_super_brief_run else "when:1h"

    for query in [f'("geopolitics" OR "sanctions" OR "foreign policy" OR "tariffs") {time_modifier}', f'("semiconductor" OR "lithography" OR "rare earth" OR "critical minerals") {time_modifier}', f'("artificial intelligence" OR "quantum computing" OR "data center" OR "Nvidia") {time_modifier}']:
        try:
            gn_url = f'https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en&_={int(time.time())}'
            for entry in feedparser.parse(requests.get(gn_url, headers=headers, timeout=15).text).entries[:5]: 
                art_id = f"ART_{article_counter:03d}"
                final_url = resolve_final_url(entry.link, headers)
                
                body_text = extract_deep_text(final_url)
                
                article_map[art_id] = {"title": entry.title, "url": final_url, "feed_source": f"Google News {time_modifier}"}
                
                if body_text:
                    aggregated_news += f"ID: {art_id} | [LIVE NEWS] {entry.title}\n  DEEP DATA: {body_text}\n"
                else:
                    aggregated_news += f"ID: {art_id} | [LIVE NEWS] {entry.title}\n"
                    
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
            
            body_text = extract_deep_text(final_url)
            if body_text:
                aggregated_news += f"ID: {art_id} | [MARITIME] {entry.title}\n  DEEP DATA: {body_text}\n"
            else:
                aggregated_news += f"ID: {art_id} | [MARITIME] {entry.title}\n"
            article_counter += 1; total_articles += 1
    except Exception: pass

    print("🌐 Executing Deep-Scrape on Hegemon Global...")
    try:
        hg_url = "https://hegemonglobal.com"
        body_text = extract_deep_text(hg_url)
        if body_text:
            art_id = f"ART_{article_counter:03d}"
            article_map[art_id] = {"title": "Hegemon Global Intel", "url": hg_url, "feed_source": "Hegemon Global"}
            aggregated_news += f"ID: {art_id} | [HEGEMON GLOBAL]\n  DEEP DATA: {body_text}\n"
            article_counter += 1; total_articles += 1
    except Exception: pass

    psy_events, psy_raw_items = fetch_psyopoly_data()
    for item in psy_raw_items:
        art_id = f"ART_{article_counter:03d}"
        article_map[art_id] = {"title": item["headline"], "url": item["url"], "feed_source": "Psyopoly Supabase"}
        
        body_text = extract_deep_text(item["url"])
        if body_text:
            aggregated_news += f"ID: {art_id} | [PSYOPOLY] {item['headline']}\n  DEEP DATA: {body_text}\n"
        else:
            aggregated_news += f"ID: {art_id} | [PSYOPOLY] {item['headline']}\n"
            
        article_counter += 1; total_articles += 1

    return aggregated_news, total_articles, psy_events, article_map

# 🛑 THE FIX: Enforced strict UI formatting schemas for Gemini
def extract_tactical_events(news_text):
    from datetime import datetime, timezone
    current_utc_hour = datetime.now(timezone.utc).hour
    is_super_brief = current_utc_hour >= 18 
    
    # 🛑 SCALED EXTRACTION: 40-45 for super brief, 20-30 for normal brief
    extraction_volume = "40-45" if is_super_brief else "20-30"
    
    prompt = f"""
    You are an elite Geopolitics-OSINT analyst. Review entries preceded by IDs. Extract {extraction_volume} critical events.
    Output raw JSON array. Keys exactly: "Article_ID", "Date", "Actor", "Action", "Location", "Risk".
    
    CRITICAL DATA FORMATTING RULES:
    1. "Date": MUST be strictly formatted as "YYYY-MM-DD". Do not use words like "July" or "2026" alone.
    2. "Risk": MUST be exactly one of these words: "CRITICAL", "HIGH", "MODERATE", or "LOW". Do NOT write sentences or explanations in the Risk column.
    
    Data: {news_text}
    """
    raw_txt = generate_with_rotation(prompt, temperature=0.1)
    import re
    match = re.search(r'\[.*\]', raw_txt, re.DOTALL)
    if match: return json.loads(match.group(0))
    return json.loads(raw_txt.replace("```json", "").replace("```", "").strip())

def generate_flush_to_brief(accumulated_events):
    is_super_brief = len(accumulated_events) > 30
    
    if is_super_brief:
        trimmed = accumulated_events[:45]
        word_req = "Strict length: 400-450 words."
    else:
        trimmed = accumulated_events[:30]
        word_req = "Strict length: 300-450 words."

    prompt = (
        "You are an elite Geopolitics-OSINT analyst. "
        f"Generate a FLASH TO BRIEF from this data: {json.dumps(trimmed)}. "
        "Output ONLY a valid JSON object with these exactly 5 keys: "
        f'"bluf": "Bottom Line Up Front. {word_req}", '
        f'"tactical_indicators": "Summary of on-the-ground tactical shifts. {word_req}", '
        f'"threat_narrative": "Outline of the overarching threat landscape. {word_req}", '
        f'"risk_assessment": "Quantified near-term operational risks. {word_req}", '
        f'"strategic_forecast": "Forecast for the next 24-72 hours. {word_req}" '
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
                
        # 🛑 STORE UP TO 45 EVENTS to support the 24-hour Super Brief depth
        unique_master = unique_master[:45]
        json.dump(unique_master, open(output_file_tactical, 'w'), indent=4)
        
        print("⏳ Pooling data before FLASH TO BRIEF generation...")
        
        current_utc_hour = datetime.now(timezone.utc).hour
        if current_utc_hour >= 18:
            print("🌟 Executing 24-Hour Super Brief Synthesis...")
            brief_input = unique_master[:45]
        else:
            brief_input = unique_master[:30]
        
        flush_brief_data = generate_flush_to_brief(brief_input)
        json.dump(flush_brief_data, open('data/executive_home/flush_brief_24h.json', 'w'), indent=4)
        
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
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
        
        # Saves safely using the correct naming convention so it doesn't crash the Weekly view
        archive_filename = f"data/flash_archive_{date_str}.json"
        with open(archive_filename, 'w', encoding='utf-8') as f:
            json.dump(archive_payload, f, indent=4)
        
        # HF_TOKEN = os.environ.get("HF_TOKEN"); REPO_ID = os.environ.get("SPACE_ID") or "anwarkashif/semicon-dashboard"
        # if HF_TOKEN and REPO_ID:
        #     api = HfApi()
        #     api.upload_file(path_or_fileobj=output_file_tactical, path_in_repo=output_file_tactical, repo_id=REPO_ID, repo_type="space", token=HF_TOKEN, commit_message="Sync Executive Home Tactical")
        #     api.upload_file(path_or_fileobj='data/executive_home/flush_brief_24h.json', path_in_repo='data/executive_home/flush_brief_24h.json', repo_id=REPO_ID, repo_type="space", token=HF_TOKEN)
        #     api.upload_file(path_or_fileobj=archive_filename, path_in_repo=archive_filename, repo_id=REPO_ID, repo_type="space", token=HF_TOKEN)
        #     print("✅ Executive Flash Archive Synced securely with Source URLs!")
            
    except Exception as e: 
        print(f"❌ Pipeline Failed: {e}")
        logging.error(f"Pipeline Failed: {e}")