# -*- coding: utf-8 -*-
import os
import json
import time
import requests
import feedparser
from urllib.parse import urlparse
from google import genai
from huggingface_hub import HfApi

GEMINI_API_KEY = os.environ.get("RAG_GEMINI_API_KEY_5")
if not GEMINI_API_KEY:
    print("Error: RAG_GEMINI_API_KEY_5 environment variable not set.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

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

    # --- 1. MONITOR THE SITUATION ---
    try:
        url = "https://monitor-the-situation.com/api/events"
        res = requests.get(url, headers={'Referer': 'https://monitor-the-situation.com/', **HEADERS}, params={"range": "12h", "feed": "live"}, timeout=10)
        if res.status_code == 200:
            raw_intel_payload += "\n--- MONITOR THE SITUATION ---\n"
            for e in res.json()[:15]:
                art_id = f"ART_{article_counter:03d}"
                article_url = e.get('url') or e.get('link') or "https://monitor-the-situation.com/"
                article_map[art_id] = {"title": e.get('title'), "url": article_url, "feed_source": "MONITOR THE SITUATION"}
                raw_intel_payload += f"ID: {art_id} | TITLE: {e.get('title')}\n"
                article_counter += 1
    except Exception as e: print(f"⚠️ Failed MTS: {e}")

    # --- 2. WAR MONITOR ---
    try:
        url = "https://api.war-monitor.com/api/events"
        res = requests.get(url, headers={'Origin': 'https://war-monitor.com', 'Referer': 'https://war-monitor.com/', **HEADERS}, params={"page": "1", "limit": "15", "fresh_hours": "168"}, timeout=10)
        if res.status_code == 200:
            raw_intel_payload += "\n--- WAR MONITOR ---\n"
            for e in res.json().get('data', [])[:15]:
                art_id = f"ART_{article_counter:03d}"
                article_url = e.get('url') or e.get('link') or "https://war-monitor.com/events"
                article_map[art_id] = {"title": e.get('title'), "url": article_url, "feed_source": "WAR MONITOR"}
                raw_intel_payload += f"ID: {art_id} | TITLE: {e.get('title')}\n"
                article_counter += 1
    except Exception as e: print(f"⚠️ Failed War Monitor: {e}")

    # --- 3. CISA ---
    try:
        url = "https://www.cisa.gov/cybersecurity-advisories/all.xml"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            feed = feedparser.parse(res.text)
            raw_intel_payload += "\n--- CISA (GLOBAL CYBER THREATS) ---\n"
            for entry in feed.entries[:15]:
                art_id = f"ART_{article_counter:03d}"
                article_map[art_id] = {"title": entry.title, "url": entry.link, "feed_source": "CISA"}
                raw_intel_payload += f"ID: {art_id} | TITLE: {entry.title}\n"
                article_counter += 1
    except Exception as e: print(f"⚠️ Failed CISA: {e}")

    # --- AI EXTRACTION (ID ONLY) ---
    prompt = f"""
    You are a Geopolitics-OSINT Intelligence Router. Review the following raw feeds.
    Select EXACTLY 10 distinct, critical geopolitical, cyber, or defense-related headlines.
    
    CRITICAL INSTRUCTIONS:
    1. Return exactly 10 objects.
    2. Do NOT invent IDs. You must use the EXACT "Article_ID" provided.
    
    Output a raw JSON array. Format exactly like this:
    [
      {{
        "Article_ID": "ART_001",
        "threat_level": "CRITICAL"
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
        if not valid_url(url):
            print(f"⚠️ Rejected invalid URL: {url}")
            continue
            
        if url in seen_urls:
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
        
    print(f"✅ Validated {validated_count} of {len(extracted_ids)} Gemini selections")
    return final_flash_data

if __name__ == "__main__":
    try:
        flash_data = fetch_and_evaluate_flash_alerts()
        os.makedirs('data', exist_ok=True)
        output_file = 'data/flash_alert.json'
        
        with open(output_file, 'w') as f:
            json.dump(flash_data, f, indent=4)
            
        print(f"✅ Success! Generated {len(flash_data)} 100% authenticated Flash Alerts.")
        
        HF_TOKEN = os.environ.get("HF_TOKEN")
        REPO_ID = os.environ.get("SPACE_ID") or "anwarkashif/semicon-dashboard" 
        
        if HF_TOKEN and REPO_ID:
            api = HfApi()
            api.upload_file(path_or_fileobj=output_file, path_in_repo=output_file, repo_id=REPO_ID, repo_type="space", token=HF_TOKEN, commit_message="Auto-sync Live Flash Alerts with Provenance")
            print("✅ Locked Flash Alerts into permanent Hugging Face storage!")
                
    except Exception as e:
        print(f"❌ Flash Alert Pipeline Failed: {e}")