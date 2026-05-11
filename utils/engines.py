import os
import json
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
import streamlit as st

# ==========================================
# TEXT PARSER FOR RSS ACCUMULATOR FIX
# ==========================================
@st.cache_data(ttl=900) # Caches data for 15 minutes to vastly improve render speed
def parse_rss_txt_file():
    rss_dict = {}
    filepath = 'data/rss_accumulator.txt'
    if not os.path.exists(filepath): return rss_dict

    # --- CRITICAL FIX: FREEZE 24-HOUR WINDOW TO 00:15 AM IST ROLLOVER ---
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc + timedelta(hours=5, minutes=30)

    # The new target anchor is 18:45 UTC (00:15 AM IST).
    # We freeze the dashboard to ONLY evaluate news from the 24 hours PRECEDING this exact time.
    if now_ist.hour == 0 and now_ist.minute < 15:
        # If visited before 00:15 AM IST, lock onto yesterday's rollover snapshot
        anchor_ist = now_ist.replace(hour=0, minute=15, second=0, microsecond=0) - timedelta(days=1)
    else:
        # If visited after 00:15 AM IST, lock onto today's rollover snapshot
        anchor_ist = now_ist.replace(hour=0, minute=15, second=0, microsecond=0)

    # Convert strict window back to UTC for safe comparison with published timestamps
    window_end_utc = anchor_ist - timedelta(hours=5, minutes=30)
    window_start_utc = window_end_utc - timedelta(hours=24)
    # ----------------------------------------------------------------------

    current_reg = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("---") and "DOMAIN-FORCED NEWS" in line:
                reg = line.replace("---", "").replace("DOMAIN-FORCED NEWS", "").strip()
                if "Middle East" in reg: reg = "West Asia/Middle East"
                current_reg = reg
                if current_reg not in rss_dict:
                    rss_dict[current_reg] = []
            elif line.startswith("- [") and current_reg:
                try:
                    d_end = line.find("]")
                    date_str = line[3:d_end]
                    title_str = line[d_end+1:].strip()

                    # --- NEW STATIC WINDOW EVALUATION ---
                    is_recent = False
                    if date_str != "Recent Update":
                        try:
                            pub_dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                            # ONLY mark as 24h if it falls perfectly inside the locked daily window
                            if window_start_utc <= pub_dt <= window_end_utc:
                                is_recent = True
                        except Exception:
                            is_recent = False
                    else:
                        is_recent = False

                    clean_search = title_str.replace("🔴", "").replace("🟠", "").replace("🟡", "").replace("CRITICAL:", "").replace("ELEVATED:", "").replace("WATCH:", "").replace("LIVE WARNING:", "").strip()
                    search_query = urllib.parse.quote_plus(clean_search)
                    news_link = f"https://news.google.com/search?q={search_query}"

                    if not any(x['title'] == title_str for x in rss_dict[current_reg]):
                        # Inject the "is_24h" flag into the dictionary
                        rss_dict[current_reg].append({"title": title_str, "published": date_str, "link": news_link, "is_24h": is_recent})
                except Exception: pass
    return rss_dict

# ==========================================
# NEW ALGORITHMIC THREAT SCORING FUNCTION
# ==========================================
def calculate_domain_threat(domain_name, text_content, dash_data):
    """
    Dynamically calculates a threat score (0-100) based on textual severity 
    and cross-referencing json data (risks & actions) without hardcoding values.
    """
    if not text_content or len(text_content.strip()) < 20:
        return 0
    
    score = 35 

    text_lower = text_content.lower()
    critical_keywords = ['ban', 'sanction', 'shortage', 'escalation', 'military', 'war', 'blockade', 'strike', 'chokepoint', 'threat', 'breach', 'crisis']
    high_keywords = ['tariff', 'control', 'restrict', 'vulnerability', 'disrupt', 'tension', 'export control', 'embargo', 'risk']
    medium_keywords = ['delay', 'subsidy', 'compete', 'invest', 'shift', 'policy', 'regulate', 'pressure', 'concern', 'geopolitical']

    score += sum(text_lower.count(kw) for kw in critical_keywords) * 8
    score += sum(text_lower.count(kw) for kw in high_keywords) * 5
    score += sum(text_lower.count(kw) for kw in medium_keywords) * 2

    domain_parts = [p.lower() for p in domain_name.replace(" / ", " ").split() if len(p) > 3]

    risks = dash_data.get('supply_chain_risk', [])
    for risk in risks:
        risk_text = str(risk).lower()
        if any(part in risk_text for part in domain_parts):
            score += 10 
    
    actions = dash_data.get('recent_actions', [])
    for action in actions:
        action_text = str(action).lower()
        if any(part in action_text for part in domain_parts):
            score += 5 

    return min(100, max(20, score))

# --- NEW CENTRALIZED LIVE ALERT FETCH FUNCTION ---
def get_active_live_alert():
    if not os.path.exists('data/live_alert.json'): 
        return None
    try:
        with open('data/live_alert.json', 'r') as f:
            alert = json.load(f)
        alert_time = datetime.fromisoformat(alert['timestamp'].replace("Z", "+00:00"))
        time_diff = datetime.now(timezone.utc) - alert_time
        
        if time_diff.total_seconds() < 7200: 
            return alert
    except Exception:
        pass 
    return None

# --- NEW ROCK-SOLID CLOCK CACHE (FIX FOR ISSUE 2) ---
def get_deployment_timestamp():
    """Anchors the clock to a persistent file so it survives all refreshes and log-ins."""
    os.makedirs('data', exist_ok=True)
    file_path = 'data/nominal_timer.txt'
    
    # Read the saved timestamp if it exists
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return int(f.read().strip())
        except Exception:
            pass
            
    # If no file exists (first run), generate the time and save it
    now_ms = int(time.time() * 1000)
    try:
        with open(file_path, 'w') as f:
            f.write(str(now_ms))
    except Exception:
        pass
        
    return now_ms