import requests
import json
import os
from datetime import datetime
from huggingface_hub import HfApi
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UNIVERSAL_POOL_PATH = os.path.join(BASE_DIR, 'data', 'tactical_events_24h.json')
STANDALONE_PSYOPOLY_PATH = os.path.join(BASE_DIR, 'data', 'psyopoly_alerts.json')

SUPABASE_URL = "https://lojirolzkshoqgccrwyh.supabase.co/rest/v1/breaking_news"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvamlyb2x6a3Nob3FnY2Nyd3loIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwODQyNjQsImV4cCI6MjA4OTY2MDI2NH0.DzdBr_d69SSlRxtnxH8DRqc0hLNQfb4wL5t1Qe96UMo"

headers = {
    "apikey": ANON_KEY,
    "authorization": f"Bearer {ANON_KEY}",
    "accept": "application/json",
    "origin": "https://www.psyopoly.pro",
    "referer": "https://www.psyopoly.pro/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

params = {
    "select": "id,headline,posted_at,url",
    "order": "posted_at.desc",
    "limit": "40"
}

def valid_url(url):
    if not url: return False
    try: return urlparse(url).scheme in ["http", "https"]
    except: return False

def extract_psyopoly_intel():
    print("🔍 Initiating Psyopoly Supabase Extraction...")
    try:
        response = requests.get(SUPABASE_URL, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            raw_data = response.json()
            formatted_events = []
            seen_urls = set()
            
            for item in raw_data:
                url = item.get("url", "https://www.psyopoly.pro/middle-east")
                if not valid_url(url) or url in seen_urls:
                    continue
                seen_urls.add(url)
                
                headline = item.get("headline", "No Headline Provided").strip()
                
                # 🚨 THE FIX: Appended exact keys required by live_pipeline_executive 
                # (Action, Headline, Risk) to ensure the deduplication engine doesn't strip them.
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
            print(f"✅ SUCCESS: Siphoned {len(formatted_events)} verified intelligence events.")
            return formatted_events
        else:
            print(f"❌ API Request Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ CRITICAL FAILURE: {e}")
    return []

def merge_and_sync(new_events):
    if not new_events: 
        print("⚠️ No events extracted. Sync aborted.")
        return
        
    os.makedirs(os.path.dirname(STANDALONE_PSYOPOLY_PATH), exist_ok=True)
    with open(STANDALONE_PSYOPOLY_PATH, 'w', encoding='utf-8') as f:
        json.dump(new_events, f, indent=4)

    existing_events = []
    if os.path.exists(UNIVERSAL_POOL_PATH):
        try: existing_events = json.load(open(UNIVERSAL_POOL_PATH, 'r', encoding='utf-8'))
        except Exception: pass

    # Refined deduplication logic to align with new data structures
    existing_signatures = {str(e.get("Summary", e.get("Action", ""))).strip().lower() for e in existing_events}
    
    added_count = 0
    for event in new_events:
        signature = str(event.get("Headline", "")).strip().lower()
        if signature and signature not in existing_signatures:
            existing_events.insert(0, event)
            existing_signatures.add(signature)
            added_count += 1
            
    # Cap file size to prevent token limit breach in downstream LLM processing
    existing_events = existing_events[:80]
            
    with open(UNIVERSAL_POOL_PATH, 'w', encoding='utf-8') as f:
        json.dump(existing_events, f, indent=4)
        
    print(f"✅ Merged {added_count} new unique Psyopoly events into Universal Pool.")

    HF_TOKEN = os.environ.get("HF_TOKEN")
    REPO_ID = os.environ.get("SPACE_ID") or "anwarkashif/semicon-dashboard"
    if HF_TOKEN and REPO_ID:
        try:
            api = HfApi()
            api.upload_file(path_or_fileobj=UNIVERSAL_POOL_PATH, path_in_repo='data/tactical_events_24h.json', repo_id=REPO_ID, repo_type="space", token=HF_TOKEN, commit_message="Auto-sync Universal Pool with Psyopoly metadata")
            api.upload_file(path_or_fileobj=STANDALONE_PSYOPOLY_PATH, path_in_repo='data/psyopoly_alerts.json', repo_id=REPO_ID, repo_type="space", token=HF_TOKEN)
            print("✅ Successfully locked Psyopoly payloads into permanent Hugging Face storage!")
        except Exception as e: print(f"❌ Failed to sync to Hub: {e}")

if __name__ == "__main__":
    merge_and_sync(extract_psyopoly_intel())