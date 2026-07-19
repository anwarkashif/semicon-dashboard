import os
import ssl
import certifi

# 🛠️ Fix for Mac local SSL Certificate errors
os.environ['SSL_CERT_FILE'] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

import requests
import time

# Exact headers required to spoof standard browser environments
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'DNT': '1'
}

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
            print(f"✅ SUCCESS: Extracted a valid JSON payload from World Monitor.")
            print(f"    Records found: {len(data) if isinstance(data, list) else 'Dict Object'}")
            print(f"    Preview: {str(data)[:250]}...\n")
            return data
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"    Response text: {response.text[:200]}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

def test_pizzint_watch():
    print("📡 Targeting Backend: PizzINT Watch (pizzint.watch/api/markets/breaking)")
    url_breaking = "https://www.pizzint.watch/api/markets/breaking?window=6h"
    url_doomsday = "https://www.pizzint.watch/api/neh-index/doomsday"
    
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://www.pizzint.watch/polyglobe/app'
    local_headers['Origin'] = 'https://www.pizzint.watch'

    collected_data = {}
    
    # Test Breaking Markets API
    try:
        res_break = requests.get(url_breaking, headers=local_headers, timeout=15)
        if res_break.status_code == 200:
            data_break = res_break.json()
            collected_data['breaking'] = data_break
            print(f"✅ SUCCESS: Extracted [Breaking Markets] JSON from PizzINT.")
            print(f"    Preview: {str(data_break)[:150]}...\n")
        else:
            print(f"❌ FAILED [Breaking Markets]: HTTP {res_break.status_code}")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Breaking Markets]: {e}\n")

    # Test Doomsday Index API
    try:
        res_doom = requests.get(url_doomsday, headers=local_headers, timeout=15)
        if res_doom.status_code == 200:
            data_doom = res_doom.json()
            collected_data['doomsday'] = data_doom
            print(f"✅ SUCCESS: Extracted [Doomsday Index] JSON from PizzINT.")
            print(f"    Preview: {str(data_doom)[:150]}...\n")
        else:
            print(f"❌ FAILED [Doomsday Index]: HTTP {res_doom.status_code}")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Doomsday Index]: {e}\n")

    return collected_data

def test_scalytics_osint():
    print("📡 Targeting Backend: Scalytics OSINT Pipeline (osint.scalytics.io)")
    timestamp = int(time.time() * 1000)
    url = f"https://osint.scalytics.io/alerts.json?t={timestamp}"
    
    local_headers = HEADERS.copy()
    local_headers['Accept'] = '*/*'
    local_headers['Referer'] = 'https://osint.scalytics.io/m/'

    try:
        response = requests.get(url, headers=local_headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Extracted a valid JSON payload from Scalytics OSINT.")
            print(f"    Preview: {str(data)[:150]}...\n")
            return data
        else:
            print(f"❌ FAILED: HTTP {response.status_code}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

def test_psyopoly_supabase():
    print("📡 Targeting Backend: Psyopoly Supabase (api.psyopoly.pro / supabase)")
    url = "https://lojirolzkshoqgccrwyh.supabase.co/rest/v1/breaking_news"
    params = {"select": "id,headline,posted_at,url", "order": "posted_at.desc", "limit": "20"}
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxvamlyb2x6a3Nob3FnY2Nyd3loIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwODQyNjQsImV4cCI6MjA4OTY2MDI2NH0.DzdBr_d69SSlRxtnxH8DRqc0hLNQfb4wL5t1Qe96UMo"
    
    local_headers = HEADERS.copy()
    local_headers['apikey'] = anon_key
    local_headers['authorization'] = f"Bearer {anon_key}"
    local_headers['origin'] = "https://www.psyopoly.pro"
    local_headers['referer'] = "https://www.psyopoly.pro/"

    try:
        response = requests.get(url, headers=local_headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Extracted a valid JSON payload from Psyopoly Supabase.")
            print(f"    Preview: {str(data[0])[:150]}...\n" if data else "    Preview: []\n")
            return data
        else:
            print(f"❌ FAILED: HTTP {response.status_code}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

def extract_war_monitor():
    print("📡 Targeting Backend: War Monitor (api.war-monitor.com)")
    url = "https://api.allorigins.win/raw?url=https%3A%2F%2Fapi.war-monitor.com%2Fapi%2Fevents%3Fpage%3D1%26limit%3D15%26fresh_hours%3D168"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            events = data.get('data', data.get('events', [])) 
            print(f"✅ SUCCESS: Extracted a valid JSON payload from War Monitor via Proxy Tunnel.")
            print(f"    Preview: {str(events)[:150]}...\n")
            return events
        else:
            print(f"❌ FAILED: HTTP {response.status_code} via proxy tunnel\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

def extract_monitor_the_situation():
    print("📡 Targeting Backend: Monitor The Situation (monitor-the-situation.com/api)")
    url = "https://monitor-the-situation.com/api/events"
    params = {"range": "6h", "feed": "live"}
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://monitor-the-situation.com/east-asia'

    try:
        response = requests.get(url, headers=local_headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Extracted a valid JSON payload from Monitor The Situation.")
            print(f"    Preview: {str(data)[:150]}...\n")
            return data
        else:
            print(f"⚠️ UNEXPECTED RESULT: {response.status_code}\n")
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

def test_earth_engine_sar():
    print("📡 Targeting Backend: Google Earth Engine (Sentinel-1 SAR Maritime Radar)")
    try:
        import ee
        try:
            # Attempt to connect to Google's servers using saved credentials
            ee.Initialize(project='PASTE-YOUR-PROJECT-ID-HERE')
        except Exception:
            # If no credentials exist on this Mac, trigger the browser login flow
            print("⚠️ Earth Engine not authenticated on this machine. Triggering auth flow...")
            ee.Authenticate()
            ee.Initialize(project='smiling-foundry-487519-b1')
            
        # Define a spatial bounding box for the Strait of Hormuz
        region = ee.Geometry.Rectangle([55.5, 26.0, 56.5, 27.0])
        
        # Pull Sentinel-1 SAR imagery collection for the last week (July 2026)
        collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
            .filterBounds(region) \
            .filterDate('2026-07-11', '2026-07-18') \
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            
        image_count = collection.size().getInfo()
        
        print(f"✅ SUCCESS: Authenticated and communicated with Earth Engine.")
        print(f"    SAR Images retrieved for Hormuz geometry: {image_count}\n")
        return {"status": "success", "images_found": image_count}
        
    except Exception as e:
        print(f"❌ CRITICAL FAILURE [Earth Engine]: {e}\n")
        return []

if __name__ == "__main__":
    print("==================================================")
    print("🔍 INITIATING AGENTIC 2.5 LIVE API DIAGNOSTICS")
    print("==================================================\n")
    
    wm_data = test_world_monitor()
    pz_data = test_pizzint_watch()
    scalytics_data = test_scalytics_osint()
    psy_data = test_psyopoly_supabase()
    war_monitor_data = extract_war_monitor()
    mts_data = extract_monitor_the_situation()
    ee_data = test_earth_engine_sar() # <--- ADD THIS LINE