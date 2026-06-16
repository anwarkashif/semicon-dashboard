# -*- coding: utf-8 -*-
import os
import json
import time
import requests
import feedparser
from google import genai

# Use the specific new key for Flash Alerts
GEMINI_API_KEY = os.environ.get("RAG_GEMINI_API_KEY_5")
if not GEMINI_API_KEY:
    print("Error: RAG_GEMINI_API_KEY_5 environment variable not set.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

FEEDS = {
    "RECORDED FUTURE": "https://therecord.media/feed/",
    "FLASHPOINT": "https://flashpoint.io/blog/feed/",
    "SINTELIX (GLOBAL EYE)": "https://sintelix.com/feed/",
    "CISA (GLOBAL CYBER THREATS)": "https://www.cisa.gov/uscert/ncas/alerts.xml"
}

def robust_gemini_call(prompt, task_name="Generation"):
    models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
    for model_name in models:
        print(f"🤖 Attempting {task_name} with {model_name}...")
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                clean_text = response.text.replace("```json", "").replace("```", "").strip()
                return json.loads(clean_text)
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ API Error on {model_name} (Attempt {attempt + 1}/2): {error_msg}")
                if '429' in error_msg or 'Quota' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                    print(f"🚫 Hard Quota Limit hit for {model_name}. Cascading to fallback model...")
                    break 
                time.sleep(5)
    raise Exception(f"❌ FATAL: All Gemini models failed for {task_name}.")

def fetch_and_evaluate_flash_alerts():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    raw_intel_payload = ""

    print("🌍 Scraping Authentic OSINT Platforms...")
    for source_name, url in FEEDS.items():
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                feed = feedparser.parse(res.text)
                raw_intel_payload += f"\n--- {source_name} ---\n"
                # Grab top 5 articles per source for AI to evaluate
                for entry in feed.entries[:5]:
                    raw_intel_payload += f"TITLE: {entry.title}\nURL: {entry.link}\n\n"
        except Exception as e:
            print(f"⚠️ Failed to fetch {source_name}: {e}")

    prompt = f"""
    You are an OSINT Intelligence Router. Review the following raw RSS feeds from 4 premium intelligence providers.
    For EACH of the 4 providers, select the SINGLE MOST CRITICAL geopolitical, cyber, or defense-related headline.
    
    CRITICAL RULE: You MUST use the EXACT title and EXACT URL provided in the text. Do not invent links.
    
    Assign a Threat Level to each selected article based on its severity:
    - CRITICAL (Red alert)
    - HIGH (Orange alert)
    - ELEVATED (Yellow alert)
    
    Output a raw JSON array of 4 objects (one for each source). Do not use markdown.
    Format exactly like this:
    [
      {{
        "source": "RECORDED FUTURE",
        "title": "Exact Article Title",
        "url": "Exact Article URL",
        "threat_level": "CRITICAL"
      }}
    ]
    
    Raw Data:
    {raw_intel_payload}
    """
    
    return robust_gemini_call(prompt, "Flash Alert Evaluation")

if __name__ == "__main__":
    try:
        flash_data = fetch_and_evaluate_flash_alerts()
        
        # Save to data directory
        os.makedirs('data', exist_ok=True)
        with open('data/flash_alert.json', 'w') as f:
            json.dump(flash_data, f, indent=4)
            
        print(f"✅ Success! Generated {len(flash_data)} authenticated Flash Alerts.")
    except Exception as e:
        print(f"❌ Flash Alert Pipeline Failed: {e}")