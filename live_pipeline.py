import os
import json
import feedparser
from datetime import datetime
from google import genai

# ==========================================
# 1. CONFIGURATION & SETUP
# ==========================================
# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# Define your strategic intelligence feeds
RSS_FEEDS = [
    "https://www.defenseone.com/rss/all/",
    "https://warontherocks.com/feed/",
    "https://www.ft.com/technology?format=rss",
    "https://asia.nikkei.com/rss/feed/txnid/8558"
]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# ==========================================
# 2. DATA SCRAPING (LAST 24 HOURS)
# ==========================================
def fetch_daily_intelligence():
    print("🌍 Scraping strategic RSS feeds...")
    aggregated_news = ""
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        # Grab the top 5 most recent articles from each feed
        for entry in feed.entries[:5]:
            aggregated_news += f"- {entry.title}\n"
            
    return aggregated_news

# ==========================================
# 3. AI EXTRACTION PIPELINE
# ==========================================
def extract_tactical_events(news_text):
    print("🧠 Pushing data to Gemini for tactical extraction...")
    
    prompt = f"""
    You are an elite OSINT geopolitical analyst. 
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
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    # Clean up the output to ensure it's pure JSON
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_text)

# ==========================================
# 4. EXECUTE & SAVE
# ==========================================
if __name__ == "__main__":
    try:
        news_data = fetch_daily_intelligence()
        tactical_events = extract_tactical_events(news_data)
        
        # Save to the specific file app.py is looking for
        output_file = 'data/tactical_events_24h.json'
        with open(output_file, 'w') as f:
            json.dump(tactical_events, f, indent=4)
            
        print(f"✅ Success! Wrote {len(tactical_events)} tactical events to {output_file}.")
        
    except Exception as e:
        print(f"❌ Pipeline Failed: {e}")