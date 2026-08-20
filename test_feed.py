import os
import ssl
import certifi
import requests
import time
import urllib.parse
import json

# 🛠️ Fix for Mac local SSL Certificate errors
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

# 🛡️ Bulletproof Secret Parser for .streamlit/secrets.toml
def get_secret(key_name):
    val = os.environ.get(key_name)
    if val: return val.strip()

    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            import tomllib  # Python 3.11+
            with open(secrets_path, "rb") as f:
                secrets = tomllib.load(f)
                if key_name in secrets:
                    return str(secrets[key_name]).strip()
        except Exception: pass

        try:
            with open(secrets_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or not line: continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        clean_k = k.replace("export", "").strip()
                        if clean_k == key_name:
                            return v.strip().strip('"').strip("'")
        except Exception: pass
    return ""

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'DNT': '1'
}

# =========================================================
# 🌐 GLOBAL AGGREGATORS (Agentic AI 3.5 Engine)
# =========================================================

def test_currents_api():
    print("📡 Targeting API: Currents API (120,000+ Global Sources)")
    api_key = get_secret("CURRENTS_API_KEY")
    if not api_key:
        print("⚠️ SKIPPED: CURRENTS_API_KEY not found in secrets.toml or environment.\n")
        return []

    url = "https://api.currentsapi.services/v1/search"
    params = {"apiKey": api_key, "language": "en", "keywords": "geopolitics OR semiconductor OR sanctions OR military"}

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            news = response.json().get("news", [])
            print(f"✅ SUCCESS: Extracted {len(news)} global news payload from Currents API.\n")
            return news
        else: print(f"❌ FAILED [Currents API]: HTTP {response.status_code}\n")
    except Exception as e: print(f"❌ CRITICAL FAILURE [Currents API]: {e}\n")
    return []

def test_gnews_api():
    print("📡 Targeting API: GNews API (Global Breaking News)")
    api_key = get_secret("GNEWS_API_KEY")
    if not api_key:
        print("⚠️ SKIPPED: GNEWS_API_KEY not found in secrets.toml or environment.\n")
        return []

    url = "https://gnews.io/api/v4/search"
    params = {"q": "geopolitics OR semiconductor OR sanctions", "lang": "en", "max": 10, "apikey": api_key}

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            print(f"✅ SUCCESS: Extracted {len(articles)} top global headlines from GNews API.\n")
            return articles
        else: print(f"❌ FAILED [GNews API]: HTTP {response.status_code}\n")
    except Exception as e: print(f"❌ CRITICAL FAILURE [GNews API]: {e}\n")
    return []

def test_guardian_api():
    print("📡 Targeting API: The Guardian Open Platform")
    api_key = get_secret("GUARDIAN_API_KEY")
    if not api_key:
        print("⚠️ SKIPPED: GUARDIAN_API_KEY not found.\n")
        return []

    url = "https://content.guardianapis.com/search"
    params = {"api-key": api_key, "q": "geopolitics OR defense OR technology", "page-size": 10, "show-fields": "headline,trailText,byline"}

    try:
        time.sleep(1) 
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            results = response.json().get("response", {}).get("results", [])
            print(f"✅ SUCCESS: Extracted {len(results)} verified reports from The Guardian.\n")
            return results
        else: print(f"❌ FAILED [The Guardian]: HTTP {response.status_code}\n")
    except Exception as e: print(f"❌ CRITICAL FAILURE [The Guardian]: {e}\n")
    return []

# =========================================================
# 🚀 NEW OSINT TARGET EXTRACTIONS (F12 Traces)
# =========================================================

def test_iran_monitor():
    print("📡 Targeting Backend: Iran Monitor (/api/daily-summary)")
    url = "https://www.iranmonitor.org/api/daily-summary?lang=en"
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://www.iranmonitor.org/'
    
    try:
        response = requests.get(url, headers=local_headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Extracted valid JSON payload from Iran Monitor.")
            print(f"    Preview: {str(data)[:200]}...\n")
            return data
        elif response.status_code == 403:
            print("❌ FAILED [Iran Monitor]: HTTP 403 Forbidden (Cloudflare Anti-Bot triggered).\n")
        else:
            print(f"❌ FAILED [Iran Monitor]: HTTP {response.status_code}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Iran Monitor]: {e}\n")
    return []

def test_conflict_radar_360():
    print("📡 Targeting Backend: Conflict Radar 360 (/api/v2/public/map/events)")
    url = "https://cr360-api.vercel.app/api/v2/public/map/events?lang=en&maxHours=72"
    local_headers = HEADERS.copy()
    local_headers['Origin'] = 'https://www.conflictradar360.com'
    local_headers['Referer'] = 'https://www.conflictradar360.com/'
    
    try:
        response = requests.get(url, headers=local_headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Extracted Map Events JSON from Conflict Radar 360.")
            print(f"    Preview: {str(data)[:200]}...\n")
            return data
        else:
            print(f"❌ FAILED [Conflict Radar 360]: HTTP {response.status_code}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Conflict Radar 360]: {e}\n")
    return []

def test_redroom_live():
    print("📡 Targeting Backend: Redroom TRPC Architecture")
    trpc_payload = '{"0":{"json":{"region":"Global","limit":20}}}'
    url = f"https://redroom.live/api/trpc/articles.breaking?batch=1&input={urllib.parse.quote(trpc_payload)}"
    
    local_headers = HEADERS.copy()
    local_headers['Origin'] = 'https://redroom.live'
    local_headers['Referer'] = 'https://redroom.live/'
    
    try:
        response = requests.get(url, headers=local_headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Extracted batched TRPC JSON from Redroom.")
            print(f"    Preview: {str(data)[:200]}...\n")
            return data
        else:
            print(f"❌ FAILED [Redroom]: HTTP {response.status_code}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Redroom]: {e}\n")
    return []

def test_track_wanted():
    print("📡 Targeting Backend: Track-Wanted Live (_serverFn Intercept)")
    # Decoded Next.js server function intercept from the F12 trace
    url = "https://track-wanted.live/_serverFn/e312619f033799b2df61c988154089f01bbe3def1e5bb7238b88b2d49c27d4e0"
    
    local_headers = HEADERS.copy()
    local_headers['Origin'] = 'https://track-wanted.live'
    local_headers['Referer'] = 'https://track-wanted.live/globe?m=wanted'
    local_headers['Content-Type'] = 'application/json'
    local_headers['x-tsr-serverfn'] = 'true'
    
    # Extracted SuperJSON payload tracking a specific target dossier
    payload = {"t":{"t":10,"i":0,"p":{"k":["data"],"v":[{"t":10,"i":1,"p":{"k":["query","size"],"v":[{"t":1,"s":"Klaus-Michael Kühne"},{"t":0,"s":320}]},"o":0}]},"o":0},"f":63,"m":[]}
    
    try:
        response = requests.post(url, headers=local_headers, json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Extracted ServerFn JSON payload from Track-Wanted.")
            print(f"    Preview: {str(data)[:200]}...\n")
            return data
        else:
            print(f"❌ FAILED [Track-Wanted]: HTTP {response.status_code}. (Note: Next.js hashes rotate on site updates)\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Track-Wanted]: {e}\n")
    return []

def extract_war_monitor():
    print("📡 Targeting Backend: War Monitor (Supabase Edge Functions)")
    url = "https://doibxberkxwpkwpmyvon.supabase.co/functions/v1/twitter-osint"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRvaWJ4YmVya3h3cGt3cG15dm9uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE2ODgzMTksImV4cCI6MjA4NzI2NDMxOX0.NIH12xDyXzAauMdgsJ9GN0NRw4kXFLQjaRVRZnQsfvo"
    
    local_headers = HEADERS.copy()
    local_headers['apikey'] = anon_key
    local_headers['authorization'] = f"Bearer {anon_key}"
    local_headers['Origin'] = 'https://warmonitor.app'
    local_headers['Referer'] = 'https://warmonitor.app/'
    local_headers['Content-Type'] = 'application/json'

    try:
        response = requests.post(url, headers=local_headers, json={"batch_index": 1}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Extracted direct Supabase JSON payload from War Monitor.")
            print(f"    Preview: {str(data)[:200]}...\n")
            return data
        else:
            print(f"❌ FAILED [War Monitor]: HTTP {response.status_code}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [War Monitor]: {e}\n")
    return []

def extract_monitor_the_situation():
    print("📡 Targeting Backend: Monitor The Situation")
    url = "https://monitor-the-situation.com/api/events"
    params = {"range": "24h", "feed": "live"}
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://monitor-the-situation.com/eastern-europe'

    try:
        response = requests.get(url, headers=local_headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: Extracted valid JSON payload from Monitor The Situation.")
            print(f"    Preview: {str(data)[:200]}...\n")
            return data
        else:
            print(f"❌ FAILED [MTS]: HTTP {response.status_code}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [MTS]: {e}\n")
    return []

# =========================================================
# 🛰️ EXISTING OSINT & KINETIC FEEDS
# =========================================================

def test_world_monitor():
    print("📡 Targeting Backend: World Monitor (api.worldmonitor.app)")
    url = "https://api.worldmonitor.app/api/news/v1/list-feed-digest?variant=full&lang=en&public=1"
    local_headers = HEADERS.copy()
    local_headers['Origin'] = 'https://www.worldmonitor.app'
    local_headers['Referer'] = 'https://www.worldmonitor.app/'
    try:
        response = requests.get(url, headers=local_headers, timeout=15)
        if response.status_code == 200:
            print("✅ SUCCESS: Extracted JSON payload from World Monitor.\n")
            return response.json()
    except Exception: pass
    return []

def test_pizzint_watch():
    print("📡 Targeting Backend: PizzINT Watch")
    url_breaking = "https://www.pizzint.watch/api/markets/breaking?window=6h"
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://www.pizzint.watch/'
    try:
        res = requests.get(url_breaking, headers=local_headers, timeout=15)
        if res.status_code == 200:
            print("✅ SUCCESS: Extracted [Breaking Markets] JSON from PizzINT.\n")
            return res.json()
    except Exception: pass
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
        res = requests.get(url, headers=local_headers, params=params, timeout=15)
        if res.status_code == 200:
            print("✅ SUCCESS: Extracted valid JSON payload from Psyopoly Supabase.\n")
            return res.json()
    except Exception: pass
    return []

def test_liveuamap():
    print("📡 Targeting Web Feed: Liveuamap (F12 HTML Scraper Intercept)")
    url = "https://liveuamap.com/"
    headers = HEADERS.copy()
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            events = [item.get_text(strip=True) for item in soup.select('.title') if item.get_text(strip=True)]
            print(f"✅ SUCCESS: Extracted {len(events)} live geopolitical events from Liveuamap.\n")
            return events
    except Exception: pass
    return []

# =========================================================
# 🚀 MAIN DIAGNOSTIC SUITE
# =========================================================
if __name__ == "__main__":
    print("==================================================")
    print("🔍 INITIATING AGENTIC 5.5 LIVE API DIAGNOSTICS")
    print("==================================================\n")
    
    # 1. Global Aggregators
    currents_data = test_currents_api()
    gnews_data = test_gnews_api()
    guardian_data = test_guardian_api()

    print("--- NEW OSINT TARGET EXTRACTIONS ---")
    iran_data = test_iran_monitor()
    cr360_data = test_conflict_radar_360()
    redroom_data = test_redroom_live()
    tw_data = test_track_wanted()
    war_monitor_data = extract_war_monitor()
    mts_data = extract_monitor_the_situation()

    print("--- EXISTING OSINT FEEDS ---")
    wm_data = test_world_monitor()
    pz_data = test_pizzint_watch()
    psy_data = test_psyopoly_supabase()
    liveuamap_data = test_liveuamap()

    print("==================================================")
    print("📊 DIAGNOSTIC COMPLETED")
    print("==================================================")