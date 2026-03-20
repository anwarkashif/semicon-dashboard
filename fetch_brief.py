import os
import json
import requests
import glob
import time
import re
import urllib.parse
from google import genai
from datetime import datetime, timedelta, timezone
import feedparser
from email.utils import parsedate_to_datetime

SITREP_HISTORY_FILE = "data/sitrep_history.json"
MAX_SITREP_HISTORY = 12

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gather all potential News API keys from the environment
ALL_NEWS_KEYS = [
    os.environ.get("NEWS_API_KEY_1") or os.environ.get("NEWS_API_KEY"), # Fallback to original name if needed
    os.environ.get("NEWS_API_KEY_2"),
    os.environ.get("NEWS_API_KEY_3"),
    os.environ.get("NEWS_API_KEY_4")
]

# Filter out empty keys
VALID_NEWS_KEYS = [key for key in ALL_NEWS_KEYS if key]

if not VALID_NEWS_KEYS or not GEMINI_API_KEY:
    print("❌ ERROR: Missing API Keys. Please run with variables set.")
    exit()

client = genai.Client(api_key=GEMINI_API_KEY)
model_name = 'gemini-2.5-flash'

BANNED_SOURCES = ['variety.com', 'hollywoodlife.com', 'tmz.com', 'people.com', 'entertainment', 'amazon', 'searates', 'goodreads', 'researchgate', 'benzinga', 'yahoo']

def get_weekly_daterange():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    if start_date.month == end_date.month: return f"{start_date.strftime('%B')} {start_date.day}-{end_date.day}, {end_date.year}"
    elif start_date.year == end_date.year: return f"{start_date.strftime('%B')} {start_date.day} - {end_date.strftime('%B')} {end_date.day}, {end_date.year}"
    else: return f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"

def fetch_live_rss_feed():
    print("📡 Fetching LIVE Modular Boolean RSS Feeds (Advanced OSINT) for Think Tank Radar...")
    
    Q_A = '("semiconductor" OR "microchip" OR "AI") AND ("geopolitics" OR "supply chain" OR "export controls" OR "sanctions" OR "chokepoint")'
    Q_B = '("foundry" OR "fabs" OR "wafer" OR "packaging" OR "lithography") AND ("semiconductor" OR "chips")'
    Q_C = '("rare earth" OR "REE" OR "critical minerals" OR "lithium" OR "cobalt" OR "gallium") AND ("reserves" OR "mines" OR "refining" OR "supply chain" OR "export")'
    Q_D = '("military" OR "defense" OR "outer space" OR "arsenal") AND ("AI" OR "chips" OR "semiconductors" OR "autonomous") AND "geopolitics"'
    Q_E = '("oil price" OR "natural gas" OR "LNG" OR "energy") AND ("geopolitics" OR "OPEC" OR "supply" OR "chokepoint")'

    regional_queries = {
        "Asia": f'{Q_A} AND ("China" OR "Japan" OR "Taiwan" OR "South Korea" OR "India" OR site:.cn OR site:.jp OR site:.tw OR site:.in)',
        "West Asia/Middle East": '("UAE" OR "Saudi Arabia" OR "Israel" OR "Iran" OR "Middle East") AND ("geopolitics" OR "energy" OR "AI" OR "chips")',
        "Americas": f'{Q_B} AND ("US" OR "USA" OR "Canada" OR "Brazil" OR "Mexico")',
        "Africa": f'{Q_C} AND ("Africa" OR "South Africa" OR "Congo" OR "Nigeria" OR site:.za OR site:.ng)',
        "Europe": f'{Q_B} AND ("Europe" OR "EU" OR "UK" OR "Germany" OR "France" OR "Netherlands" OR site:.uk OR site:.de)',
        "Oceania": f'{Q_D} AND ("Australia" OR "New Zealand" OR site:.au OR site:.nz)'
    }
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    feed_data = {}
    
    rss_text_for_gemini = f"\n\n=== SUPPLEMENTARY REGIONAL OSINT RSS DATA ({datetime.now().strftime('%Y-%m-%d')}) ===\n"
    
    for region, query in regional_queries.items():
        feed_data[region] = []
        rss_text_for_gemini += f"\n--- {region} DOMAIN-FORCED NEWS ---\n"
        
        full_query = f'{query} when:3d'
        encoded_query = urllib.parse.quote(full_query)
        url = f'https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en&_={int(time.time())}'
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                feed = feedparser.parse(res.content)
                if feed.entries:
                    count = 0
                    for entry in feed.entries:
                        if count >= 5: break 
                        
                        if any(banned in entry.link.lower() for banned in BANNED_SOURCES):
                            continue
                            
                        pub_date_str = entry.get('published', 'Recent Update')
                        
                        # --- REPLACE THE OLD DATE EXTRACTION WITH THIS ---
                        if pub_date_str != 'Recent Update':
                            try:
                                pub_dt = parsedate_to_datetime(pub_date_str)
                                # Force it into a strict YYYY-MM-DD HH:MM format
                                display_date = pub_dt.strftime('%Y-%m-%d %H:%M') 
                                if datetime.now(timezone.utc) - pub_dt > timedelta(days=3):
                                    continue 
                            except:
                                display_date = pub_date_str[:19] # Fallback to capture time
                        else:
                            display_date = "Recent Update"
                            
                        feed_data[region].append({
                            "title": entry.title,
                            "link": entry.link,
                            "published": display_date
                        })
                        rss_text_for_gemini += f"- [{display_date}] {entry.title}\n"
                        count += 1
        except Exception as e:
            print(f"⚠️ RSS Fetch Failed for {region}: {e}")
            
        time.sleep(2)
            
    return feed_data, rss_text_for_gemini

def fetch_gdelt_data():
    print("🌍 Querying GDELT Database for Macro State Actions & Supply Chain events...")
    
    query = '("semiconductor" OR "rare earth" OR "lithography" OR "foundry") AND ("export" OR "sanction" OR "subsidy" OR "military" OR "chokepoint")'
    encoded_query = urllib.parse.quote(query)
    url = f'https://api.gdeltproject.org/api/v2/doc/doc?query={encoded_query}&mode=artlist&maxrecords=25&timespan=7d&format=json'

    gdelt_compiled = ""
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            data = res.json()
            articles = data.get('articles', [])
            if articles:
                gdelt_compiled += "\n\n=== GDELT MACRO DATABASE: VERIFIED STATE ACTIONS ===\n"
                for a in articles:
                    title = a.get('title', '')
                    domain = a.get('domain', '').lower()
                    seendate = a.get('seendate', '')[:8] 
                    
                    if any(banned in domain for banned in BANNED_SOURCES):
                        continue
                        
                    if title:
                        formatted_date = f"{seendate[:4]}-{seendate[4:6]}-{seendate[6:]}" if len(seendate) == 8 else "Recent"
                        gdelt_compiled += f"- [{formatted_date} | Source: {domain}] {title}\n"
        return gdelt_compiled
    except Exception as e:
        print(f"⚠️ GDELT Fetch Failed: {e}")
        return ""

def evaluate_daily_threat(daily_text):
    print("🚨 Running 2-Hour Live Situational Report (SITREP)...")
    prompt = f"""
    You are a Tier-1 Geopolitical & Supply Chain Analyst. Review these recent news headlines collected over the last 2 hours.
    Your job is to identify the SINGLE most significant development that will directly or indirectly impact global geopolitics, rare earth markets, AI infrastructure, semiconductor fabs, or supply chain logistics.

    Unlike a strict emergency system, you should report MAJOR business moves, regulatory shifts, trade war escalations, or regional conflicts that affect tech.
    
    If there is a significant development, respond with ONLY a valid JSON object:
    {{"threat_level": "ELEVATED", "headline": "<A punchy 1-sentence headline>", "summary": "<A 2-sentence summary of the geopolitical or market impact>"}}
    
    If the news is completely mundane (e.g., standard product reviews, unrelated local news, pure fluff), respond with the exact word: NONE
    
    Headlines:
    {daily_text}
    """
    try:
        response = client.models.generate_content(model=model_name, contents=prompt)
        text = response.text.strip().replace('```json', '').replace('```', '')
        if text == "NONE":
            return None
        
        alert_data = json.loads(text)
        alert_data["timestamp"] = datetime.now(timezone.utc).isoformat()
        return alert_data
    except Exception as e:
        print(f"⚠️ SITREP Check failed: {e}")
        return None

def fetch_latest_news():
    print(f"📡 Fetching Friday sweep using {len(VALID_NEWS_KEYS)} active NewsAPI keys...")
    url = "https://newsapi.org/v2/everything"
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    from_date = start_date.strftime('%Y-%m-%d')
    to_date = end_date.strftime('%Y-%m-%d')
    
    core = '("semiconductor" OR "microchip" OR "foundry" OR "lithography" OR "rare earth" OR "critical minerals" OR "export control" OR "military AI" OR "data center" OR "AI chip" OR "OSAT" OR "packaging")'
    
    regional_queries = [
        (f'{core} AND ("Asia" OR "China" OR "Taiwan" OR "Japan" OR "South Korea" OR "TSMC")', 15, 'ASIA'),
        (f'{core} AND ("USA" OR "United States" OR "Americas" OR "Brazil" OR "Canada" OR "Anthropic" OR "Nvidia")', 15, 'AMERICAS'),
        (f'("rare earth" OR "cobalt" OR "lithium" OR "gallium" OR "minerals") AND ("Africa" OR "South Africa" OR "Sudan" OR "Congo" OR "Egypt" OR "mining")', 10, 'AFRICA'),
        (f'{core} AND ("Europe" OR "EU" OR "UK" OR "Germany" OR "France" OR "ASML")', 15, 'EUROPE'),
        (f'{core} AND ("Oceania" OR "Australia" OR "New Zealand")', 10, 'OCEANIA'),
        (f'{core} AND ("Middle East" OR "West Asia" OR "Gulf" OR "OPEC" OR "LNG")', 15, 'WEST ASIA / MIDDLE EAST (GLOBAL)'),
        (f'{core} AND ("India" OR "Modi" OR "Pax Silica" OR "New Delhi")', 10, 'INDIA (DEDICATED)'),
        (f'("AI" OR "data center" OR "chips" OR "military" OR "energy") AND ("UAE" OR "Saudi Arabia" OR "Israel" OR "Iran" OR "G42" OR "Humain")', 10, 'WEST ASIA (DEDICATED)')
    ]
    
    news_compiled = ""
    seen_urls = set()
    regional_sources = {reg[2]: [] for reg in regional_queries}
    
    for i, (query, limit, region_name) in enumerate(regional_queries):
        # ROTATION LOGIC: Cycles through whichever keys are valid
        current_api_key = VALID_NEWS_KEYS[i % len(VALID_NEWS_KEYS)]
        
        params = {
            "q": query, "language": "en", "sortBy": "publishedAt", 
            "pageSize": limit, "from": from_date, "to": to_date, "apiKey": current_api_key
        }
        try:
            res = requests.get(url, params=params)
            if res.status_code == 200:
                articles = res.json().get('articles', [])
                if articles:
                    news_compiled += f"\n\n--- {region_name} REGION NEWS ---\n"
                    for a in articles:
                        title = a.get('title')
                        desc = a.get('description')
                        article_url = a.get('url')
                        
                        source_obj = a.get('source', {})
                        source_name = source_obj.get('name', 'News Source') if isinstance(source_obj, dict) else 'News Source'
                        
                        if any(banned in str(article_url).lower() or banned in str(source_name).lower() for banned in BANNED_SOURCES):
                            continue
                            
                        if desc and title and article_url and article_url not in seen_urls:
                            news_compiled += f"- [{a.get('publishedAt', '')[:10]}] {title}: {desc}\n"
                            regional_sources[region_name].append({
                                "title": f"[{source_name}] {title}", 
                                "url": article_url
                            })
                            seen_urls.add(article_url)
            else:
                print(f"⚠️ NewsAPI returned {res.status_code} for {region_name}. Key might be invalid or rate-limited.")
            time.sleep(1) 
        except Exception as e:
            print(f"⚠️ Error fetching quota for {region_name}: {e}")
            
    if not news_compiled.strip():
        print("❌ NewsAPI failed to return any articles across all keys.")
        return "", []
        
    diverse_sources = []
    for reg in regional_queries:
        reg_name = reg[2]
        diverse_sources.extend(regional_sources[reg_name])
            
    return news_compiled, diverse_sources

def safe_extract_json(raw_text, tag_name, fallback_data):
    try:
        match = re.search(rf'<{tag_name}>(.*?)</{tag_name}>', raw_text, re.DOTALL | re.IGNORECASE)
        if not match: return fallback_data
        
        content = match.group(1).strip()
        start_idx = content.find('[')
        end_idx = content.rfind(']')
        
        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx:end_idx+1]
            parsed = json.loads(json_str)
            if isinstance(parsed, list) and len(parsed) > 0:
                if not isinstance(parsed[0], dict):
                    return [{"Extracted Information": str(x)} for x in parsed]
                return parsed
        return fallback_data
    except Exception as e:
        print(f"Failed to parse {tag_name}: {e}")
        return fallback_data

def generate_geopolitical_brief(news_text, timeframe_str):
    print(f"🧠 Handing data to Gemini for timeframe: {timeframe_str}...")
    
    prompt = f"""
    You are a Tier-1 geopolitical intelligence analyst. Read the following recent news snippets and supplementary RSS headlines.
    Write a highly detailed, DATA-RICH Weekly Intelligence Brief. Timeframe: {timeframe_str}.
    
    <SYSTEM_ANCHOR_COMMANDS>
    1. CURRENT REALITY: The current year is 2026. Donald Trump is the CURRENT President of the United States. NEVER refer to him as "former".
    2. ANTI-HALLUCINATION: Use ONLY the facts provided below. DO NOT invent military operations or duplicate exact news points. DO NOT force a region into a section if there is no relevant news for it.
    3. NO HEADINGS: DO NOT write titles like "Executive Summary" or "Strategic Conclusion" inside the text blocks. Just write the analytical paragraphs. 
    4. STRUCTURED DATA: Provide structured comparative tables in place of descriptive figure captions whenever you are summarizing multiple actors, capabilities, or resource metrics.
    </SYSTEM_ANCHOR_COMMANDS>
    
    <ANTI-FLUFF PROTOCOL> (CRITICAL)
    1. ZERO GENERALIZATIONS: Do NOT write filler sentences like "The region remains central to competition" or "Despite economic headwinds...". 
    2. HARD FACTS ONLY: Every single sentence must report a SPECIFIC event, company name, investment, or state action found in the text.
    3. IF NO SPECIFIC DATA EXISTS FOR A REGION IN A SECTION, OMIT THE REGION ENTIRELY. Do not force it in with vague commentary.
    </ANTI-FLUFF PROTOCOL>

    STRUCTURAL MANDATES (STRICT):
    1. VITAL INTELLIGENCE ONLY: Only include high-impact, critical developments that directly affect the specific heading (Foundry, AI Chips, Minerals, Export Controls, Military/Space, Lithography). Discard low-level fluff.
    2. GEOGRAPHICAL ACCURACY: Do NOT misplace countries. (e.g., Canada is Americas, India is Asia. Their relations belong in Americas or Asia, NEVER Oceania). Only place news in a region if the actor or impact is physically located there.
    3. REGIONAL JUSTIFICATION (CRITICAL): If you place an event under a region (e.g., **Africa:**) that occurred geographically elsewhere (e.g., an arrest in Indiana, US), you MUST explicitly write the connection to that region (e.g., "linked to the Test Flying Academy of South Africa").
    4. EXCLUSIVITY RULE: ALL news relating to India MUST go exclusively into the <INDIA> section. ALL news relating to the Middle East, UAE, Saudi Arabia, Israel, or Iran MUST go exclusively into the <WEST_ASIA> section. Do NOT mention them in sections <EXEC> through <CONCLUSION>.
    5. REGIONAL SUBHEADINGS: In sections <EXEC> through <CONCLUSION>, use these exact bolded tags: **Asia:** (excluding India), **Africa:**, **Europe:**, **Americas:**, **Oceania:**. 
    6. OMIT IF EMPTY (ABSOLUTE RULE): If you do not have vital, verified news for a region under a specific heading, YOU MUST COMPLETELY OMIT THAT REGION from that section. DO NOT write the bold tag (e.g., do not write "**Africa:**"). NEVER write filler text just to include a region. It is perfectly fine for a section to only have 1 or 2 regions.
    7. SEPARATE PARAGRAPHS: You MUST place a double line break (\\n\\n) before every single regional subheading. DO NOT mash them together on one line.
    
    Wrap your analysis exactly within the 16 XML tags provided below:
    
    <SUMMARY>(Write the executive summary paragraph here. Do not write the title.)</SUMMARY>
    <EWS>(Synthesize the week's most critical early warnings and red flags here based on the collected data. Omit if none. Do not write the title.)</EWS>
    <EXEC>(Write analysis here. ONLY use bold regional tags if there is relevant news. Omit empty regions. Do not write the title.)</EXEC>
    <LITHO>(Write analysis here. ONLY use bold regional tags if there is relevant news. Omit empty regions. Do not write the title.)</LITHO>
    <REE>(Write analysis here. ONLY use bold regional tags if there is relevant news. Omit empty regions. Do not write the title.)</REE>
    <GEO>(Write analysis here. ONLY use bold regional tags if there is relevant news. Omit empty regions. Do not write the title.)</GEO>
    <MILITARY>(Write analysis here. ONLY use bold regional tags if there is relevant news. Omit empty regions. Do not write the title.)</MILITARY>
    <CONCLUSION>(Write analysis here. ONLY use bold regional tags if there is relevant news. Omit empty regions. Do not write the title.)</CONCLUSION>
    
    <INDIA>(Synthesize ALL developments relevant to India here. Do not write the title.)</INDIA>
    <WEST_ASIA>(Synthesize ALL developments from West Asia/Middle East here. Do not write the title.)</WEST_ASIA>
    
    <FINAL_CONCLUSION>(Write the forward-looking conclusion here. Do not write the title.)</FINAL_CONCLUSION>
    
    <KPI_METRICS>
    (Extract exactly 6 metrics focusing strictly on GEOPOLITICS AND SECURITY. Output strictly as a JSON array of dictionaries. Example: [{{"Metric": "Threat Level", "Value": "High"}}])
    </KPI_METRICS>

    <FUNDING_DATA>
    (Extract 2 to 4 instances of financial investments. Output strictly as a JSON array of dictionaries.)
    </FUNDING_DATA>

    <MARKET_IMPACT>
    (Extract 2 to 4 distinct entities/regions and their market impact. Output strictly as a JSON array of dictionaries.)
    </MARKET_IMPACT>

    <RISK_INDEX>
    (Identify ALL specific supply chain vulnerabilities. Output strictly as a JSON array of dictionaries.)
    </RISK_INDEX>
    
    <ACTION_MATRIX>
    (Extract ALL concrete geopolitical state actions. Output strictly as a JSON array of dictionaries. Example: [{{"Date": "2026-02-27", "Actor": "China", "Action": "Restricted exports", "Location": "China"}}])
    </ACTION_MATRIX>
    
    Raw Data:
    {news_text}
    """
    try:
        response = client.models.generate_content(model=model_name, contents=prompt)
        if not response.text: return ""
        return response.text.replace('`', '') 
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return ""

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    current_weekly_range = get_weekly_daterange()
    
    ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    
    # 1. DAILY RSS FETCH
    live_rss_feed, daily_rss_text = fetch_live_rss_feed() 
    
    # 1.5 RUN EARLY WARNING SYSTEM (EWS) MICRO-SWEEP
    alert_data = evaluate_daily_threat(daily_rss_text)
    
    # --- NEW: Aggregated 24h SITREP Logging ---
    sitrep_history = []
    if os.path.exists(SITREP_HISTORY_FILE):
        try:
            with open(SITREP_HISTORY_FILE, 'r', encoding="utf-8") as f:
                sitrep_history = json.load(f)
        except: pass

    history_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "threat_level": alert_data['threat_level'] if alert_data else "STANDARD",
        "headline": alert_data['headline'] if alert_data else "Nominal 2h Sync",
        "summary": alert_data['summary'] if alert_data else ""
    }
    sitrep_history.insert(0, history_entry)
    sitrep_history = sitrep_history[:MAX_SITREP_HISTORY] # Maintain last 12 checks
    
    with open(SITREP_HISTORY_FILE, 'w', encoding="utf-8") as f:
        json.dump(sitrep_history, f)
    # --- End Log Logic ---

    if alert_data:
        with open("data/live_alert.json", "w", encoding="utf-8") as f:
            json.dump(alert_data, f)
        print(f"🔴 ELEVATED SITREP DETECTED AND SAVED: {alert_data['headline']}")
    else:
        if os.path.exists("data/live_alert.json"):
            os.remove("data/live_alert.json")
        print("🟢 No major SITREP developments detected in the last 2 hours. Cleared.")
    
    # 2. CACHE APPEND
    cache_file = "data/rss_accumulator.txt"
    with open(cache_file, "a", encoding="utf-8") as f:
        f.write(daily_rss_text)
    print("✅ Daily RSS Accumulator Updated.")

    # 3. UI LIVE UPDATE
    files = glob.glob('data/brief_*.json')
    if files:
        files.sort()
        latest_file = files[-1]
        try:
            with open(latest_file, 'r', encoding="utf-8") as f:
                current_dash_data = json.load(f)
            
            current_dash_data['live_rss'] = live_rss_feed 
            
            with open(latest_file, 'w', encoding="utf-8") as f:
                json.dump(current_dash_data, f)
            print(f"✅ Dashboard UI updated with today's Live Telemetry ({latest_file}).")
        except Exception as e:
            print(f"⚠️ Could not update UI feed: {e}")

    # 4. FRIDAY ONLY AI GENERATION 
    filename = f"data/brief_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
    
    if ist_time.weekday() == 4 and ist_time.hour < 12:
        if os.path.exists(filename):
            print(f"✅ Brief {filename} already exists. Skipping duplicate AI generation for this fallback window.")
        else:
            print("🚀 FRIDAY MORNING DETECTED: Initiating full Gemini AI Intelligence Sweep...")
            
            raw_news, extracted_sources = fetch_latest_news()
            gdelt_text = fetch_gdelt_data()
            
            accumulated_rss_text = ""
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    accumulated_rss_text = f.read()
                    
            combined_news_for_gemini = raw_news + accumulated_rss_text + gdelt_text
            
            if combined_news_for_gemini.strip():
                raw_brief = generate_geopolitical_brief(combined_news_for_gemini, current_weekly_range)
                
                dynamic_kpi = safe_extract_json(raw_brief, 'KPI_METRICS', [{"Metric": "Data Sync Error", "Value": "N/A"}])
                dynamic_risk = safe_extract_json(raw_brief, 'RISK_INDEX', [{"Risk Factor": "Data Unavailable", "Threat Level": "Unknown"}])
                dynamic_actions = safe_extract_json(raw_brief, 'ACTION_MATRIX', [{"Date": current_weekly_range, "Actor": "System", "Action": "Insufficient news data.", "Location": "Global"}])
                dynamic_funding = safe_extract_json(raw_brief, 'FUNDING_DATA', [{"Entity": "No specific funding reported", "Amount": "0"}])
                dynamic_market = safe_extract_json(raw_brief, 'MARKET_IMPACT', [{"Entity": "Data Unavailable", "Market Share (%)": "N/A"}])
                
                data_package = {
                    "date": current_weekly_range,
                    "brief_raw": raw_brief,
                    "kpi_metrics": dynamic_kpi,
                    "supply_chain_risk": dynamic_risk, 
                    "recent_actions": dynamic_actions,
                    "funding_data": dynamic_funding,
                    "market_impact": dynamic_market,
                    "sources": extracted_sources,
                    "live_rss": live_rss_feed 
                }
                
                with open(filename, 'w') as f:
                    json.dump(data_package, f)
                    
                open(cache_file, 'w').close()
                print("🗑️ RSS Accumulator cleared for the new week.")
                    
                cutoff_date = datetime.now() - timedelta(days=180)
                for file_path in glob.glob("data/brief_*.json"):
                    try:
                        date_str = file_path.split('_')[1].split('.json')[0]
                        if datetime.strptime(date_str, '%Y-%m-%d') < cutoff_date: os.remove(file_path)
                    except: pass
                print(f"✅ Success! Saved authentic data to {filename}")
            else:
                print("❌ Script Stopped: No news data was pulled. Gemini was not triggered.")
    else:
        print(f"⏳ Normal 2-Hour Cycle (IST Weekday: {ist_time.weekday()}, Hour: {ist_time.hour}). Deep AI generation skipped.")
        print("Dashboard is running smoothly on cached AI data with dynamically updated 2-hour RSS/SITREP.")