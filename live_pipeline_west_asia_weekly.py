# -*- coding: utf-8 -*-
import os
import json
import time
import re
import trafilatura  # 🛑 THE FIX: Added Trafilatura at top level
from datetime import datetime, timedelta, timezone
from google import genai
from huggingface_hub import HfApi
import logging

os.makedirs('data/west_asia', exist_ok=True)

logging.basicConfig(
    filename='data/pipeline_wa_weekly_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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

def generate_with_rotation(prompt, temperature=0.2):
    if not VALID_KEYS: raise Exception("CRITICAL: No valid API keys found in environment.")
        
    current_idx = 0; failures = 0; global_cycles = 0; MAX_GLOBAL_CYCLES = 4
    
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
            if not raw_txt: raise ValueError("Empty response")
            return raw_txt
        except Exception as e:
            failures += 1
            print(f"⚠️ API Key {current_idx + 1} Attempt {failures} Failed: {str(e)[:100]}")
            if failures >= 2:
                current_idx += 1; failures = 0
                if current_idx >= len(VALID_KEYS):
                    print("⏳ All keys exhausted. Sleeping 65 seconds for RPM quotas to reset...")
                    time.sleep(65)
                    current_idx = 0; global_cycles += 1
                else: time.sleep(5)
            else: time.sleep(15)
    raise Exception("CRITICAL: All API keys exhausted across multiple recovery cycles.")

def get_sunday_to_sunday_range():
    today = datetime.now(timezone.utc)
    # Roll back to the most recent Sunday
    days_since_sunday = today.weekday() + 1 if today.weekday() != 6 else 0
    recent_sunday = today - timedelta(days=days_since_sunday)
    previous_sunday = recent_sunday - timedelta(days=7)
    
    if recent_sunday.month == previous_sunday.month:
        return f"{recent_sunday.strftime('%B')} {previous_sunday.day}-{recent_sunday.day}, {recent_sunday.year}"
    else:
        return f"{previous_sunday.strftime('%B %d')} - {recent_sunday.strftime('%B %d')}, {recent_sunday.year}"

def fetch_weekly_psyopoly_pool():
    standalone_path = 'data/psyopoly_alerts.json'
    if not os.path.exists(standalone_path): return []
    
    try:
        with open(standalone_path, 'r', encoding='utf-8') as f:
            all_events = json.load(f)
            
        today = datetime.now(timezone.utc)
        seven_days_ago = today - timedelta(days=7)
        
        # Filter for West Asia/Middle East and recent dates
        filtered_events = []
        for e in all_events:
            try:
                e_date = datetime.strptime(e.get('Date', ''), "%Y-%m-%d").replace(tzinfo=timezone.utc)
                # Keep only West Asia/Middle East entries
                if e_date >= seven_days_ago and ("Middle East" in e.get('Location', '') or "West Asia" in e.get('Actor', '')):
                    filtered_events.append(e)
            except: pass
            
        # Limit to 250 for depth
        return filtered_events[:250]
    except Exception as e:
        print(f"❌ Error loading Psyopoly pool: {e}")
        return []

def generate_west_asia_brief(events, date_range):
    print(f"🧠 Synthesizing {len(events)} events for Weekly West Asia Brief...")
    
    prompt = f"""
    You are an elite West Asia geopolitical, risk, and threat OSINT analyst expert with extensive experience in the Middle East.
    Synthesize the following {len(events)} events (gathered over the last 7 days) into a highly authoritative "Weekly West Asia Brief".
    
    CRITICAL INSTRUCTIONS:
    1. Focus STRICTLY on West Asia / Middle East. Exclude sports, entertainment, commercial fluff, film, and music entirely.
    2. Rely heavily on the deep-text provided in the 'Summary' fields for rich analytical context to meet the strict word count requirements.
    3. Output MUST be a valid JSON object. Do not use markdown wrappers.
    4. Provide comprehensive, professionally written analytical paragraphs for each section. YOU MUST STRICTLY ADHERE TO THE WORD COUNTS.
    
    REQUIRED JSON KEYS:
    "bluf": "Bottom Line Up Front paragraph. Strict length: 250-300 words.",
    "executive_summary": "Micro and Macro-level summary paragraph. Strict length: 300-450 words.",
    "escalation_indicators": "Paragraph detailing specific escalation signals. Strict length: 300-450 words.",
    "irano_centric_axis": "Paragraph on Iranian, IRGC, or allied proxy operations. Strict length: 350-400 words.",
    "levantine_front": "Paragraph on Lebanon, Syria, Hezbollah dynamics. Strict length: 350-400 words.",
    "israeli_strategy": "Paragraph on Israeli multi-theater operations. Strict length: 350-400 words.",
    "gcc_region": "Paragraph on Gulf Cooperation Council, energy, or economic and military shifts. Strict length: 300-450 words.",
    "strategic_intel_log": "Paragraph logging major intelligence and military moves. Strict length: 300-450 words.",
    "tactical_indicators": "Paragraph summarizing on-the-ground tactical shifts. Strict length: 250-300 words.",
    "threat_narrative": "Paragraph outlining the overarching threat landscape. Strict length: 250-300 words.",
    "risk_assessment": "Paragraph quantifying near-term operational risks. Strict length: 300-350 words.",
    "strategic_forecast": "Paragraph forecasting the next 7-14 days. Strict length: 300-350 words.",
    "themed_urls": {{
        "Military & Escalation": ["url1", "url2"],
        "Diplomacy & Economy": ["url3", "url4"],
        "Intelligence": ["url5"]
    }}
    
    Group the provided URLs into the 'themed_urls' object based on the context of the articles.
    
    RAW DATA POOL:
    {json.dumps(events)}
    """
    
    raw_txt = generate_with_rotation(prompt)
    match = re.search(r'\{.*\}', raw_txt, re.DOTALL)
    if match: return json.loads(match.group(0))
    return json.loads(raw_txt.replace("```json", "").replace("```", "").strip())

if __name__ == "__main__":
    try:
        events_pool = fetch_weekly_psyopoly_pool()
        if len(events_pool) < 10:
            print("⚠️ Insufficient data for a weekly brief.")
            exit(1)
            
        date_range_str = get_sunday_to_sunday_range()
        date_stamp = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
        brief_data = generate_west_asia_brief(events_pool, date_range_str)
        brief_data.update({'date_range': date_range_str, 'generation_date': date_stamp, 'event_volume': len(events_pool)})
        
        output_file = f'data/west_asia/west_asia_brief_{date_stamp}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(brief_data, f, indent=4)
            
        HF_TOKEN = os.environ.get("HF_TOKEN")
        REPO_ID = os.environ.get("SPACE_ID") or "anwarkashif/semicon-dashboard" 
        
        if HF_TOKEN and REPO_ID:
            HfApi().upload_file(path_or_fileobj=output_file, path_in_repo=output_file, repo_id=REPO_ID, repo_type="space", token=HF_TOKEN, commit_message=f"Auto-sync West Asia Brief: {date_range_str}")
            print("✅ Upload complete.")
            
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")