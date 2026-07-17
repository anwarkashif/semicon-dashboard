import requests
import time

# Exact headers required to spoof standard browser environments
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive'
}

def test_scalytics_osint():
    print("📡 Targeting Backend: Scalytics OSINT Pipeline (osint.scalytics.io)")
    # Generate millisecond timestamp dynamically to match real browser telemetry requests
    timestamp = int(time.time() * 1000)
    url = f"https://osint.scalytics.io/alerts.json?t={timestamp}"
    
    local_headers = HEADERS.copy()
    local_headers['Accept'] = '*/*'
    local_headers['Referer'] = 'https://osint.scalytics.io/m/'
    local_headers['DNT'] = '1'

    try:
        response = requests.get(url, headers=local_headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Extracted a valid JSON payload from Scalytics OSINT.")
            print(f"    Records found: {len(data) if isinstance(data, list) else 1}")
            print(f"    Preview: {str(data)[:200]}...\n")
            return data
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"    Response text: {response.text}\n")
            
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

def test_psyopoly_supabase():
    print("📡 Targeting Backend: Psyopoly Supabase (api.psyopoly.pro / supabase)")
    url = "https://lojirolzkshoqgccrwyh.supabase.co/rest/v1/breaking_news"
    
    params = {
        "select": "id,headline,posted_at,url",
        "order": "posted_at.desc",
        "limit": "20"
    }
    
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
            print(f"    Records found: {len(data)}")
            if len(data) > 0:
                print(f"    Preview: {str(data[0])[:200]}...\n")
            return data
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"    Response text: {response.text}\n")
            
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

def extract_war_monitor():
    print("📡 Targeting Backend: War Monitor (api.war-monitor.com)")
    # Uses the upgraded proxy array pattern to avoid direct-connect firewalls
    url = "https://api.allorigins.win/raw?url=https%3A%2F%2Fapi.war-monitor.com%2Fapi%2Fevents%3Fpage%3D1%26limit%3D15%26fresh_hours%3D168"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            events = data.get('data', data.get('events', [])) 
            print(f"✅ SUCCESS: Extracted a valid JSON payload from War Monitor via Proxy Tunnel.")
            print(f"    Records found: {len(events)}")
            print(f"    Preview: {str(events)[:200]}...\n")
            return events
        else:
            print(f"❌ FAILED: HTTP {response.status_code} via proxy tunnel\n")
            
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

def extract_monitor_the_situation():
    print("📡 Targeting Backend: Monitor The Situation (monitor-the-situation.com/api)")
    url = "https://monitor-the-situation.com/api/events"
    
    params = {
        "range": "6h",
        "feed": "live"
    }
    
    local_headers = HEADERS.copy()
    local_headers['Referer'] = 'https://monitor-the-situation.com/east-asia'

    try:
        response = requests.get(url, headers=local_headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Extracted a valid JSON payload from Monitor The Situation.")
            print(f"    Records found: {len(data)}")
            print(f"    Preview: {str(data)[:200]}...\n")
            return data
        else:
            print(f"⚠️ UNEXPECTED RESULT: {response.status_code}\n")
            
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

if __name__ == "__main__":
    print("==================================================")
    print("🔍 INITIATING LIVE DATA STREAM API TARGET DIAGNOSTICS")
    print("==================================================\n")
    
    scalytics_data = test_scalytics_osint()
    psy_data = test_psyopoly_supabase()
    war_monitor_data = extract_war_monitor()
    mts_data = extract_monitor_the_situation()