import requests
import json
import os
from datetime import datetime

# 1. PSYOPOLY SUPABASE CONFIGURATION
# We use the permanent Anon Key, NOT your personal expiring JWT session token.
SUPABASE_URL = "https://lojirolzkshoqgccrwyh.supabase.co/rest/v1/breaking_news?select=id%2Cheadline%2Cposted_at%2Curl&order=posted_at.desc&limit=40"
ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvamlyb2x6a3Nob3FnY2Nyd3loIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwODQyNjQsImV4cCI6MjA4OTY2MDI2NH0.DzdBr_d69SSlRxtnxH8DRqc0hLNQfb4wL5t1Qe96UMo"

headers = {
    "apikey": ANON_KEY,
    "authorization": f"Bearer {ANON_KEY}",  # Bypasses personal auth for permanent public read access
    "accept": "application/json",
    "origin": "https://www.psyopoly.pro",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extract_psyopoly_intel():
    print("🔍 Initiating Psyopoly Supabase Extraction...")
    try:
        response = requests.get(SUPABASE_URL, headers=headers)
        
        if response.status_code == 200:
            raw_data = response.json()
            print(f"✅ SUCCESS: Siphoned {len(raw_data)} intelligence events from Psyopoly.")
            
            # 2. STANDARDIZE TO SEMICON DASHBOARD FORMAT
            formatted_events = []
            for item in raw_data:
                formatted_events.append({
                    "Date": item.get("posted_at", "").split("T")[0],
                    "Actor": "Psyopoly/West Asia",
                    "Location": "Middle East",
                    "Event": "Strategic Update",
                    "Summary": item.get("headline", "No Headline Provided"),
                    "Source": item.get("url", "https://www.psyopoly.pro/middle-east")
                })
            return formatted_events
            
        else:
            print(f"⚠️ API REJECTED: Status {response.status_code}")
            return []
            
    except Exception as e:
        print(f"⚠️ CRITICAL FAILURE: Could not connect to Psyopoly backend. Error: {e}")
        return []

def merge_with_global_pool(new_events):
    if not new_events:
        return
        
    filepath = 'data/tactical_events_24h.json'
    existing_events = []
    
    # Load current pool
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_events = json.load(f)
        except Exception:
            pass

    # Prevent duplicates based on Summary headline
    existing_summaries = {event.get("Summary") for event in existing_events}
    
    added_count = 0
    for event in new_events:
        if event["Summary"] not in existing_summaries:
            existing_events.insert(0, event) # Add newest to the top
            added_count += 1
            
    # Save back to the global pool
    os.makedirs('data', exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(existing_events, f, indent=4)
        
    print(f"✅ INJECTION COMPLETE: {added_count} new events pushed to the global data pool.")

if __name__ == "__main__":
    extracted_data = extract_psyopoly_intel()
    merge_with_global_pool(extracted_data)