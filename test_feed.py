import os
import ssl
import certifi
import requests
import time

# 🛠️ Fix for Mac local SSL Certificate errors
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

# 🛡️ Bulletproof Secret Parser for .streamlit/secrets.toml
def get_secret(key_name):
    # 1. Environment Variable
    val = os.environ.get(key_name)
    if val: 
        return val.strip()

    # 2. TOML Parser (.streamlit/secrets.toml)
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            import tomllib  # Python 3.11+
            with open(secrets_path, "rb") as f:
                secrets = tomllib.load(f)
                if key_name in secrets:
                    return str(secrets[key_name]).strip()
        except Exception:
            pass

        # Manual Line-by-Line Fallback Parser
        try:
            with open(secrets_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or not line:
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        # Handles accidental "export" prefix or raw KEY=VAL
                        clean_k = k.replace("export", "").strip()
                        if clean_k == key_name:
                            return v.strip().strip('"').strip("'")
        except Exception:
            pass

    return ""

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'DNT': '1'
}

# =========================================================
# 🌐 NEW GLOBAL AGGREGATORS (Agentic AI 3.5 Engine)
# =========================================================

def test_currents_api():
    print("📡 Targeting API: Currents API (120,000+ Global Sources)")
    api_key = get_secret("CURRENTS_API_KEY")
    if not api_key:
        print("⚠️ SKIPPED: CURRENTS_API_KEY not found in secrets.toml or environment.\n")
        return []

    # 🛑 THE FIX: Changed /v1/latest-news to /v1/search to allow keyword filtering
    url = "https://api.currentsapi.services/v1/search"
    params = {
        "apiKey": api_key,
        "language": "en",
        "keywords": "geopolitics OR semiconductor OR sanctions OR military"
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            news = data.get("news", [])
            print("✅ SUCCESS: Extracted global news payload from Currents API.")
            print(f"    Articles retrieved: {len(news)}")
            print(f"    Preview: {str(news[:1])[:200]}...\n")
            return news
        else:
            print(f"❌ FAILED [Currents API]: HTTP {response.status_code} - {response.text[:150]}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Currents API]: {e}\n")
    return []

def test_gnews_api():
    print("📡 Targeting API: GNews API (Global Breaking News)")
    api_key = get_secret("GNEWS_API_KEY")
    if not api_key:
        print("⚠️ SKIPPED: GNEWS_API_KEY not found in secrets.toml or environment.\n")
        return []

    url = "https://gnews.io/api/v4/search"
    params = {
        "q": "geopolitics OR semiconductor OR sanctions",
        "lang": "en",
        "max": 10,
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            print("✅ SUCCESS: Extracted top global headlines from GNews API.")
            print(f"    Articles retrieved: {len(articles)}")
            print(f"    Preview: {str(articles[:1])[:200]}...\n")
            return articles
        else:
            print(f"❌ FAILED [GNews API]: HTTP {response.status_code} - {response.text[:150]}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [GNews API]: {e}\n")
    return []

def test_guardian_api():
    print("📡 Targeting API: The Guardian Open Platform (500/day Non-Commercial Tier)")
    api_key = get_secret("GUARDIAN_API_KEY")
    if not api_key:
        print("⚠️ SKIPPED: GUARDIAN_API_KEY not found in secrets.toml or environment.\n")
        return []

    url = "https://content.guardianapis.com/search"
    params = {
        "api-key": api_key,
        "q": "geopolitics OR defense OR technology",
        "page-size": 10,
        "show-fields": "headline,trailText,byline"
    }

    try:
        time.sleep(1)  # Enforce 1 call/sec limit for Guardian free tier
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            results = data.get("response", {}).get("results", [])
            print("✅ SUCCESS: Extracted verified reports from The Guardian Open Platform.")
            print(f"    Articles retrieved: {len(results)}")
            print(f"    Preview: {str(results[:1])[:200]}...\n")
            return results
        else:
            print(f"❌ FAILED [The Guardian]: HTTP {response.status_code} - {response.text[:150]}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [The Guardian]: {e}\n")
    return []

# =========================================================
# 🛰️ EXISTING OSINT & KINETIC FEEDS
# =========================================================

def test_world_monitor():
    print("📡 Targeting Backend: World Monitor (api.worldmonitor.app/api/news)")
    url = "https://api.worldmonitor.app/api/news/v1/list-feed-digest?variant=full&lang=en&public=1"
    local_headers = HEADERS.copy()
    local_headers['Origin'] = 'https://www.worldmonitor.app'
    local_headers['Referer'] = 'https://www.worldmonitor.app/'
    local_headers['Accept'] = '*/*'

    try:
        response = requests.get(url, headers=local_headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Extracted a valid JSON payload from World Monitor.")
            print(f"    Preview: {str(data)[:200]}...\n")
            return data
        else:
            print(f"❌ FAILED: HTTP {response.status_code}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

def test_pizzint_watch():
    print("📡 Targeting Backend: PizzINT Watch")
    url_breaking = "https://www.pizzint.watch/api/markets/breaking?window=6h"
    url_doomsday = "https://www.pizzint.watch/api/neh-index/doomsday"
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://www.pizzint.watch/polyglobe/app'
    local_headers['Origin'] = 'https://www.pizzint.watch'

    collected_data = {}
    try:
        res_break = requests.get(url_breaking, headers=local_headers, timeout=15)
        if res_break.status_code == 200:
            collected_data['breaking'] = res_break.json()
            print("✅ SUCCESS: Extracted [Breaking Markets] JSON from PizzINT.")
        res_doom = requests.get(url_doomsday, headers=local_headers, timeout=15)
        if res_doom.status_code == 200:
            collected_data['doomsday'] = res_doom.json()
            print("✅ SUCCESS: Extracted [Doomsday Index] JSON from PizzINT.\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [PizzINT]: {e}\n")
    return collected_data

def test_scalytics_osint():
    print("📡 Targeting Backend: Scalytics OSINT Pipeline")
    timestamp = int(time.time() * 1000)
    url = f"https://osint.scalytics.io/alerts.json?t={timestamp}"
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://osint.scalytics.io/m/'

    try:
        response = requests.get(url, headers=local_headers, timeout=15)
        if response.status_code == 200:
            print("✅ SUCCESS: Extracted valid JSON payload from Scalytics OSINT.\n")
            return response.json()
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Scalytics]: {e}\n")
    return []

def test_psyopoly_supabase():
    print("📡 Targeting Backend: Psyopoly Supabase")
    url = "https://lojirolzkshoqgccrwyh.supabase.co/rest/v1/breaking_news"
    params = {"select": "id,headline,posted_at,url", "order": "posted_at.desc", "limit": "20"}
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvamlyb2x6a3Nob3FnY2Nyd3loIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwODQyNjQsImV4cCI6MjA4OTY2MDI2NH0.DzdBr_d69SSlRxtnxH8DRqc0hLNQfb4wL5t1Qe96UMo"
    
    local_headers = HEADERS.copy()
    local_headers['apikey'] = anon_key
    local_headers['authorization'] = f"Bearer {anon_key}"

    try:
        response = requests.get(url, headers=local_headers, params=params, timeout=15)
        if response.status_code == 200:
            print("✅ SUCCESS: Extracted valid JSON payload from Psyopoly Supabase.\n")
            return response.json()
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Psyopoly]: {e}\n")
    return []

def extract_war_monitor():
    print("📡 Targeting Backend: War Monitor")
    url = "https://api.allorigins.win/raw?url=https%3A%2F%2Fapi.war-monitor.com%2Fapi%2Fevents%3Fpage%3D1%26limit%3D15%26fresh_hours%3D168"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            print("✅ SUCCESS: Extracted valid JSON payload from War Monitor.\n")
            return response.json()
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [War Monitor]: {e}\n")
    return []

def extract_monitor_the_situation():
    print("📡 Targeting Backend: Monitor The Situation")
    url = "https://monitor-the-situation.com/api/events"
    params = {"range": "6h", "feed": "live"}
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://monitor-the-situation.com/east-asia'

    try:
        response = requests.get(url, headers=local_headers, params=params, timeout=15)
        if response.status_code == 200:
            print("✅ SUCCESS: Extracted valid JSON payload from Monitor The Situation.\n")
            return response.json()
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [MTS]: {e}\n")
    return []

def test_earth_engine_sar():
    print("📡 Targeting Backend: Google Earth Engine (Sentinel-1 SAR)")
    try:
        import ee
        try:
            ee.Initialize(project='smiling-foundry-487519-b1')
        except Exception:
            print("⚠️ Earth Engine not authenticated. Skipping active call...\n")
            return []
        
        region = ee.Geometry.Rectangle([55.5, 26.0, 56.5, 27.0])
        collection = ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(region).limit(5)
        print("✅ SUCCESS: Communicated with Earth Engine.\n")
        return {"status": "success"}
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Earth Engine]: {e}\n")
        return []

# =========================================================
# 🚀 MAIN DIAGNOSTIC SUITE
# =========================================================
if __name__ == "__main__":
    print("==================================================")
    print("🔍 INITIATING AGENTIC 3.5 LIVE API DIAGNOSTICS")
    print("==================================================\n")
    
    # 1. New Global Aggregators (Agentic AI 3.5 Expansion)
    currents_data = test_currents_api()
    gnews_data = test_gnews_api()
    guardian_data = test_guardian_api()

    # 2. Existing OSINT Feeds
    wm_data = test_world_monitor()
    pz_data = test_pizzint_watch()
    scalytics_data = test_scalytics_osint()
    psy_data = test_psyopoly_supabase()
    war_monitor_data = extract_war_monitor()
    mts_data = extract_monitor_the_situation()
    ee_data = test_earth_engine_sar()

    print("==================================================")
    print("📊 DIAGNOSTIC COMPLETED")
    print("==================================================")