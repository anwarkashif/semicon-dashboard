import requests

# Set up the exact headers required to bypass basic anti-bot systems
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive'
}

def extract_war_monitor():
    print("📡 Targeting Backend: War Monitor (api.war-monitor.com)")
    url = "https://api.war-monitor.com/api/events"
    
    # Passing the exact query parameters from your network log
    params = {
        "page": "1",
        "limit": "20",
        "fresh_hours": "168"
    }
    
    # Adding the specific Origin and Referer headers required by their server
    local_headers = HEADERS.copy()
    local_headers['Origin'] = 'https://war-monitor.com'
    local_headers['Referer'] = 'https://war-monitor.com/'

    try:
        response = requests.get(url, headers=local_headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            events = data.get('data', []) # Assuming 'data' or similar key holds the array
            print(f"✅ SUCCESS: Extracted a valid JSON payload from War Monitor.")
            print(f"   Preview: {str(data)[:200]}...\n")
            return events
        elif response.status_code == 403:
            print("❌ FAILED: 403 Forbidden. Cloudflare block triggered.\n")
        else:
            print(f"⚠️ UNEXPECTED RESULT: {response.status_code}\n")
            
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
            print(f"   Preview: {str(data)[:200]}...\n")
            return data
        else:
            print(f"⚠️ UNEXPECTED RESULT: {response.status_code}\n")
            
    except Exception as e:
        print(f"❌ CRITICAL FAILURE: {e}\n")
    return []

if __name__ == "__main__":
    print("🔍 INITIATING DIRECT API EXTRACTION...\n")
    
    war_monitor_data = extract_war_monitor()
    mts_data = extract_monitor_the_situation()