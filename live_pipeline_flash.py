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

# Exact headers needed to bypass standard firewall blocks
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive'
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

def extract_monitor_the_situation():
    print("🌍 Siphoning from Monitor The Situation API...")
    url = "https://monitor-the-situation.com/api/events"
    params = {"range": "6h", "feed": "live"}
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://monitor-the-situation.com/'
    
    try:
        res = requests.get(url, headers=local_headers, params=params, timeout=10)
        if res.status_code == 200:
            events = res.json()
            extracted = ""
            for e in events[:5]:
                extracted += f"TITLE: {e.get('title')}\nURL: https://monitor-the-situation.com/\n\n"
            return "\n--- MONITOR THE SITUATION ---\n" + extracted
    except Exception as e:
        print(f"⚠️ Failed MTS: {e}")
    return ""

def extract_war_monitor():
    print("🌍 Siphoning from War Monitor API...")
    url = "https://api.war-monitor.com/api/events"
    params = {"page": "1", "limit": "5", "fresh_hours": "168"}
    local_headers = HEADERS.copy()
    local_headers['Origin'] = 'https://war-monitor.com'
    local_headers['Referer'] = 'https://war-monitor.com/'
    
    try:
        res = requests.get(url, headers=local_headers, params=params, timeout=10)
        if res.status_code == 200:
            events = res.json().get('data', [])
            extracted = ""
            for e in events[:5]:
                extracted += f"TITLE: {e.get('title')}\nURL: https://war-monitor.com/events\n\n"
            return "\n--- WAR MONITOR ---\n" + extracted
    except Exception as e:
        print(f"⚠️ Failed War Monitor: {e}")
    return ""

def extract_cisa():
    print("🌍 Siphoning from CISA RSS Feed...")
    url = "https://www.cisa.gov/cybersecurity-advisories/all.xml"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            feed = feedparser.parse(res.text)
            extracted = ""
            for entry in feed.entries[:5]:
                extracted += f"TITLE: {entry.title}\nURL: {entry.link}\n\n"
            return "\n--- CISA (GLOBAL CYBER THREATS) ---\n" + extracted
    except Exception as e:
        print(f"⚠️ Failed CISA: {e}")
    return ""

def fetch_and_evaluate_flash_alerts():
    raw_intel_payload = ""
    raw_intel_payload += extract_monitor_the_situation()
    raw_intel_payload += extract_war_monitor()
    raw_intel_payload += extract_cisa()

    prompt = f"""
    You are an OSINT Intelligence Router. Review the following raw feeds from 3 intelligence providers.
    For EACH of the 3 providers, select the SINGLE MOST CRITICAL geopolitical, cyber, or defense-related headline.
    
    CRITICAL RULE: You MUST use the EXACT title and EXACT URL provided in the text. Do not invent links.
    
    Assign a Threat Level to each selected article based on its severity:
    - CRITICAL (Red alert)
    - HIGH (Orange alert)
    - ELEVATED (Yellow alert)
    
    Output a raw JSON array of 3 objects (one for each source). Do not use markdown.
    Format exactly like this:
    [
      {{
        "source": "MONITOR THE SITUATION",
        "title": "Exact Article Title",
        "url": "Exact Article URL",
        "threat_level": "CRITICAL"
      }},
      {{
        "source": "WAR MONITOR",
        "title": "Exact Article Title",
        "url": "Exact Article URL",
        "threat_level": "CRITICAL"
      }},
      {{
        "source": "CISA",
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
        
        os.makedirs('data', exist_ok=True)
        with open('data/flash_alert.json', 'w') as f:
            json.dump(flash_data, f, indent=4)
            
        print(f"✅ Success! Generated {len(flash_data)} authenticated Flash Alerts.")
    except Exception as e:
        print(f"❌ Flash Alert Pipeline Failed: {e}")