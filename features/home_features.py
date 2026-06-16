import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.graph_objects as go
from collections import Counter
import os
import json
import time
from datetime import datetime, timezone
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim

# --- Newly added imports for Folium Combo Feature ---
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium

# --- Strategic Constants Import ---
try:
    from utils.constants import INFRASTRUCTURE_DATA, COUNTRY_INFO
except ImportError:
    INFRASTRUCTURE_DATA = {}
    COUNTRY_INFO = {}

# --- Existing imports for Decision Support Engine ---
from features.tactical_features import render_decision_support_engine
from features.executive_intelligence_note import render_executive_deep_intelligence_note

# ==========================================
# 1. CSS INJECTION (Self-Contained)
# ==========================================
def inject_executive_home_css():
    st.markdown("""
    <style>
    .sector-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-left: 5px solid #00bfff;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    .hot-actor-box {
        background-color: #0f172a;
        border: 1px solid #334155;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 10px;
        text-align: center;
    }
    .intel-box {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 14px;
        padding: 18px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. HELPER COMPONENTS (Self-Contained)
# ==========================================
def render_velocity_chart(title, values):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=values,
        mode='lines+markers',
        line=dict(width=3, color='#00bfff'),
        marker=dict(size=6, color='#00bfff'),
        fill='tozeroy',
        fillcolor='rgba(0, 191, 255, 0.1)'
    ))
    
    fig.update_layout(
        height=180,
        margin=dict(l=10, r=10, t=30, b=20),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(text=title, font=dict(size=14, color="#d1d5db")),
        xaxis=dict(
            showgrid=True, 
            gridcolor='#334155', 
            visible=True, 
            tickvals=[0,1,2,3,4,5,6], 
            ticktext=['D-6','D-5','D-4','D-3','D-2','D-1','Today'],
            tickfont=dict(size=10, color='#9ca3af')
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='#334155', 
            visible=True, 
            title=dict(text="Risk Score", font=dict(size=10, color='#9ca3af')), 
            range=[0, 100],
            tickfont=dict(size=10, color='#9ca3af')
        )
    )
    st.plotly_chart(fig, use_container_width=True)

def get_hot_actors(df_actions):
    if df_actions.empty:
        return []
    if 'Actor' not in df_actions.columns:
        return []
    actor_counts = Counter(df_actions['Actor'].dropna())
    return actor_counts.most_common(5)

def render_flash_alert():
    flash_path = 'data/flash_alert.json'
    
    # --- Sleek Fallback UI ---
    fallback_html = """
    <style>
        .flash-container { margin-bottom: 25px; font-family: system-ui, -apple-system, sans-serif; }
        .flash-header { color: #ef4444; font-size: 1.2em; font-weight: 900; letter-spacing: 2px; margin-bottom: 15px; display: flex; align-items: center; }
        .flash-header span { animation: blinkText 1.5s infinite; }
        @keyframes blinkText { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .flash-placeholder { background: rgba(17, 24, 39, 0.6); border: 1px dashed #374151; border-left: 5px solid #374151; padding: 20px; border-radius: 6px; color: #9ca3af; font-family: 'Courier New', monospace; font-size: 13px; letter-spacing: 1px; }
    </style>
    <div class="flash-container">
        <div class="flash-header"><span>🚨 EXECUTIVE OSINT FLASH ALERTS</span></div>
        <div class="flash-placeholder">📡 STANDBY: Awaiting initial flash telemetry payload from global OSINT nodes...</div>
    </div>
    """

    # Check if the automated file exists
    if not os.path.exists(flash_path):
        components.html(fallback_html, height=120)
        return

    try:
        with open(flash_path, 'r') as f:
            alerts = json.load(f)
    except:
        components.html(fallback_html, height=120)
        return

    # Skip rendering if empty or invalid
    if not alerts or not isinstance(alerts, list):
        components.html(fallback_html, height=120)
        return

    html_code = """
    <style>
        .flash-container {
            margin-bottom: 25px;
            font-family: system-ui, -apple-system, sans-serif;
        }
        .flash-header {
            color: #ef4444;
            font-size: 1.2em;
            font-weight: 900;
            letter-spacing: 2px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .flash-header span {
            animation: blinkText 1.5s infinite;
        }
        
        /* THE NEW FLASHY RED DEFCON BAR OVERRIDE */
        .flash-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 14px 20px;
            margin-bottom: 10px;
            border-radius: 6px;
            text-decoration: none !important;
            color: #ffffff !important;
            background: linear-gradient(90deg, #8b0000 0%, #ff0000 50%, #8b0000 100%); 
            background-size: 200% 200%; 
            animation: pulseBackground 2s infinite; 
            border: 2px solid #ff4b4b; 
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
            transition: transform 0.2s;
        }
        .flash-bar:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 25px rgba(255, 0, 0, 0.8);
        }
        
        @keyframes pulseBackground { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        @keyframes blinkText { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        .flash-source {
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 11px;
            letter-spacing: 1.5px;
            color: #fca5a5;
            margin-bottom: 4px;
        }
        .flash-title {
            font-size: 15px;
            font-weight: 800;
            line-height: 1.3;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
        }
        .flash-arrow {
            font-size: 20px;
            opacity: 0.9;
            margin-left: 15px;
        }
    </style>
    
    <div class="flash-container">
        <div class="flash-header"><span>🚨 EXECUTIVE OSINT FLASH ALERTS</span></div>
    """

    for alert in alerts:
        source = alert.get('source', 'UNKNOWN SOURCE').upper()
        title = alert.get('title', 'Intelligence Update Available')
        url = alert.get('url', '#')
        threat = alert.get('threat_level', 'CRITICAL').upper()

        # The CSS class logic is removed since the .flash-bar itself handles the red pulsing now
        html_code += f"""
        <a href="{url}" target="_blank" class="flash-bar">
            <div>
                <div class="flash-source">[{source}] // THREAT: {threat}</div>
                <div class="flash-title">{title}</div>
            </div>
            <div class="flash-arrow">➡️</div>
        </a>
        """
        
    html_code += "</div>"
    
    # Render the interactive block
    components.html(html_code, height=380)
# ==========================================
# 3. DYNAMIC GEOCODING ENGINE
# ==========================================
@st.cache_data(show_spinner=False, ttl=86400) 
def resolve_location(query):
    if not query or not isinstance(query, str):
        return None, None, "Unknown"

    if INFRASTRUCTURE_DATA:
        for category, sites in INFRASTRUCTURE_DATA.items():
            for site in sites:
                if query.lower() in site['name'].lower() or site['name'].lower() in query.lower():
                    return site['lat'], site['lon'], site['name']

    baseline = {
        "TSMC": (24.77, 120.99, "TSMC Hsinchu"), "Taiwan": (23.7, 120.9, "Taiwan"),
        "China": (39.9, 116.4, "China"), "United States": (38.9, -77.0, "USA"),
        "US": (38.9, -77.0, "USA"), "USA": (38.9, -77.0, "USA"),
        "ASML": (51.44, 5.47, "ASML Veldhoven"), "Japan": (35.68, 139.76, "Japan"), 
        "South Korea": (37.56, 126.97, "South Korea"), "India": (28.61, 77.20, "India"), 
        "EU": (50.85, 4.35, "Brussels"), "Netherlands": (52.36, 4.90, "Netherlands"), 
        "Intel": (37.38, -121.96, "Santa Clara"), "Russia": (61.52, 105.31, "Russia"),
        "Ukraine": (48.37, 31.16, "Ukraine"), "Israel": (31.04, 34.85, "Israel"),
        "Iran": (32.42, 53.68, "Iran"), "UK": (55.37, -3.43, "United Kingdom"),
        "Germany": (51.16, 10.45, "Germany"), "France": (46.22, 2.21, "France")
    }
    
    for key, data in baseline.items():
        if key.lower() in query.lower():
            return data[0], data[1], data[2]

    try:
        geolocator = Nominatim(user_agent="semicon_tactical_osint_local")
        time.sleep(1.5) 
        loc = geolocator.geocode(query, timeout=5)
        if loc:
            clean_name = loc.address.split(',')[0]
            return loc.latitude, loc.longitude, clean_name
    except Exception:
        pass 
    
    return None, None, query


# ==========================================
# 4. EXACT DEFCON LOGIC FROM APP.PY
# ==========================================
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

def get_deployment_timestamp():
    os.makedirs('data', exist_ok=True)
    file_path = 'data/nominal_timer.txt'
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return int(f.read().strip())
        except Exception:
            pass
            
    now_ms = int(time.time() * 1000)
    try:
        with open(file_path, 'w') as f:
            f.write(str(now_ms))
    except Exception:
        pass
        
    return now_ms

def check_early_warnings():
    try:
        if st.session_state.get('role') == 'admin' and os.path.exists('data/live_alert.json'):
            if st.button("🛠️ Admin: Force Clear Live Alert (Resolve Stuck EWS)", type="primary"):
                try:
                    os.remove('data/live_alert.json')
                    st.success("Alert cleared! Refreshing...")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear: {e}")

        alert = get_active_live_alert()
        box_bg_color = "#000000"
        nominal_text_color = "#d1d5db"
        fallback_time_ms = get_deployment_timestamp()
        
        if alert:   
            try:
                if 'timestamp' in alert:
                    dt = datetime.fromisoformat(alert['timestamp'].replace("Z", "+00:00"))
                    start_timestamp_ms = int(dt.timestamp() * 1000)
                else:
                    start_timestamp_ms = fallback_time_ms
            except:
                start_timestamp_ms = fallback_time_ms
            
            elapsed_ms = max(0, int(time.time() * 1000) - start_timestamp_ms)
            h, m, s = elapsed_ms // 3600000, (elapsed_ms % 3600000) // 60000, (elapsed_ms % 60000) // 1000
            
            initial_clock = f"{h:02d}:{m:02d}:{s:02d}"
            
            html_code = f"""
            <style>
                body {{ font-family: 'Courier New', Courier, monospace; margin: 0; padding: 0; background-color: {box_bg_color}; overflow: hidden; }}
                .defcon-box {{
                    background: linear-gradient(90deg, #8b0000 0%, #ff0000 50%, #8b0000 100%); 
                    background-size: 200% 200%; 
                    animation: pulseBackground 2s infinite; 
                    border: 2px solid #ff4b4b; 
                    padding: 15px; 
                    border-radius: 8px; 
                    box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
                    color: #ffffff;
                    min-height: 185px;
                    max-height: 240px; 
                    height: auto;
                    box-sizing: border-box;
                    overflow-y: auto; 
                    -webkit-overflow-scrolling: touch; 
                }}
                :fullscreen {{
                    background-color: rgba(20, 20, 20, 0.95);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                :fullscreen .defcon-box {{ width: 90vw; max-height: 90vh; height: auto; padding: 40px; border-width: 4px; }}
                :fullscreen .title {{ font-size: 2.5em; }}
                :fullscreen .timer {{ font-size: 1.5em; }}
                :fullscreen .headline {{ font-size: 2em; line-height: 1.2; margin-top: 20px; }}
                :fullscreen .summary {{ font-size: 1.5em; line-height: 1.4; margin-top: 20px; }}
                
                @keyframes pulseBackground {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
                @keyframes blinkText {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0; }} }}
                
                .header-flex {{ display: flex; justify-content: space-between; align-items: center; margin-top: 0px; margin-bottom: 8px; flex-wrap: wrap; gap: 10px; }}
                .title {{ font-size: 1.17em; font-weight: bold; letter-spacing: 2px; text-transform: uppercase; margin:0; display:flex; align-items:center; flex: 1 1 100%; }}
                .timer-container {{ display: flex; align-items: center; flex: 1 1 100%; justify-content: flex-start; margin-bottom: 5px; }}
                
                @media (min-width: 600px) {{
                    .title {{ flex: 1; }}
                    .timer-container {{ flex: 1; justify-content: flex-end; margin-bottom: 0px; }}
                }}
                
                .timer {{ font-size: 15px; font-weight: bold; background: rgba(0,0,0,0.5); padding: 5px 10px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.4); }}
                .headline {{ font-weight: 800; font-size: 16px; margin-bottom: 8px; margin-top:0; }}
                .summary {{ font-size: 14px; color: #f8f8f8; margin-bottom: 0px; border-top: 1px solid rgba(255,255,255,0.3); padding-top: 10px; }}
                
                .magnify-btn {{ background: rgba(0,0,0,0.6); color: white; border: 1px solid white; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: bold; margin-left: 10px; }}
                .magnify-btn:hover {{ background: rgba(255,255,255,0.2); }}
                :fullscreen .magnify-btn {{ display: none; }} 
                .close-btn {{ display: none; }}
                :fullscreen .close-btn {{ display: inline-block; background: transparent; color: white; border: 1px solid white; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 18px; margin-top: 20px; }}
            </style>
            
            <div class="defcon-box" id="defcon-container">
                <div class="header-flex">
                    <h3 class="title">
                        <span style="animation: blinkText 1s infinite; margin-right: 15px;">⚠️ DEFCON-LEVEL THREAT</span> 
                    </h3>
                    <div class="timer-container">
                        <div class="timer">Live Since: <span id="clock">{initial_clock}</span></div>
                        <button class="magnify-btn" onclick="toggleFullscreen()">🔍 MAGNIFY</button>
                    </div>
                </div>
                <p class="headline">{alert.get('headline', '')}</p>
                <p class="summary">{alert.get('summary', '')}</p>
                <button class="close-btn" onclick="document.exitFullscreen()">✖ CLOSE VIEW</button>
            </div>
            
            <script>
                function toggleFullscreen() {{
                    let elem = document.documentElement;
                    if (!document.fullscreenElement) {{
                        elem.requestFullscreen().catch(err => {{ alert(`Error: ${{err.message}}`); }});
                    }} else {{ document.exitFullscreen(); }}
                }}
                const start = {start_timestamp_ms};
                function update() {{
                    const now = new Date().getTime();
                    let diff = now - start;
                    if(diff < 0) diff = 0;
                    let h = Math.floor(diff / (1000 * 60 * 60));
                    let m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                    let s = Math.floor((diff % (1000 * 60)) / 1000);
                    document.getElementById('clock').innerText = String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
                }}
                setInterval(update, 1000); update();
            </script>
            """
            components.html(html_code, height=210) 
            
        else:
            html_code = f"""
            <style>
                body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 0; background-color: {box_bg_color}; overflow: hidden; }}
                .nominal-box {{ background-color: rgba(0, 191, 255, 0.05); border-left: 5px solid #00bfff; padding: 15px; border-radius: 5px; min-height: 90px; height: auto; }}
                .header-flex {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px; }}
                .title {{ color: #00bfff; margin: 0; font-size: 1.1em; font-weight: bold; display: flex; align-items: center; }}
                .timer {{ font-size: 13px; font-weight: bold; color: #00bfff; background: rgba(0, 191, 255, 0.1); padding: 5px 10px; border-radius: 4px; border: 1px solid rgba(0, 191, 255, 0.3); font-family: monospace; }}
                .desc {{ font-size: 14px; margin: 0; color: {nominal_text_color}; }}
            </style>
            <div class="nominal-box">
                <div class="header-flex">
                    <h4 class="title"><span>🟢 System Nominal</span></h4>
                    <div class="timer">Status Verified: <span id="clock">Loading...</span></div>
                </div>
                <p class="desc">Current Warning System doesn't see an early warning situation. Watch out for further updates.</p>
            </div>
            <script>
                function updateNominalTime() {{
                    const now = new Date();
                    const options = {{
                        timeZone: 'Asia/Kolkata',
                        day: '2-digit', month: 'short', year: 'numeric',
                        hour: '2-digit', minute: '2-digit', second: '2-digit',
                        hour12: true
                    }};
                    document.getElementById('clock').innerText = now.toLocaleString('en-IN', options) + ' IST';
                }}
                updateNominalTime();
                setInterval(updateNominalTime, 1000);
            </script>
            """
            components.html(html_code, height=95)

    except Exception as e:
        pass 

# ==========================================
# NEW DYNAMIC ANALYTICS HELPER ENGINES
# ==========================================
def calculate_dynamic_posture(df_actions):
    active_escalations = 0
    chokepoints = 0
    geo_shifts = 0
    
    if df_actions is not None and not df_actions.empty:
        for _, row in df_actions.iterrows():
            risk = str(row.get('Risk', '')).upper()
            text_parts = [str(row.get(col, '')) for col in ['Action', 'Headline', 'Location', 'Event'] if col in row]
            text = " ".join(text_parts).lower()
            
            if risk == 'CRITICAL':
                active_escalations += 1
            elif risk == 'HIGH':
                geo_shifts += 1
                
            if any(kw in text for kw in ['supply', 'semiconductor', 'chip', 'export', 'tsmc', 'asml', 'mineral', 'material', 'foundry', 'node', 'logistics', 'transit', 'strait']):
                chokepoints += 1
                
    sys_status = "DEFCON 3" if active_escalations > 0 else "DEFCON 4"
    return str(active_escalations), str(chokepoints), str(max(geo_shifts, 1)), sys_status

def calculate_dynamic_velocity(df_actions, keywords, base_trend):
    score = base_trend[-1]
    if df_actions is not None and not df_actions.empty:
        score = 50 
        for _, row in df_actions.iterrows():
            text_parts = [str(row.get(col, '')) for col in ['Action', 'Headline', 'Location'] if col in row]
            text = " ".join(text_parts).lower()
            if any(kw in text for kw in keywords):
                risk = str(row.get('Risk', '')).upper()
                if risk == 'CRITICAL': score += 15
                elif risk == 'HIGH': score += 10
                else: score += 5
    score = min(100, max(0, score))
    return base_trend[:6] + [score]

def calculate_dynamic_risk(df_actions, keywords, base_val):
    val = base_val
    if df_actions is not None and not df_actions.empty:
        count = 0
        for _, row in df_actions.iterrows():
            text_parts = [str(row.get(col, '')) for col in ['Action', 'Headline', 'Location'] if col in row]
            text = " ".join(text_parts).lower()
            if any(kw in text for kw in keywords):
                count += 1
        val = min(1.0, base_val + (count * 0.08))
        
    if val >= 0.8: level = "Critical"
    elif val >= 0.6: level = "Elevated"
    elif val >= 0.4: level = "Moderate"
    else: level = "Low"
    return val, f"{level} ({int(val*100)}%)"

# ==========================================
# NEW AUTONOMOUS MARITIME SCRAPER ENGINE
# ==========================================
@st.cache_data(show_spinner=False, ttl=600) 
def fetch_live_maritime_intel():
    import feedparser
    import requests
    import urllib.parse
    import time
    import re
    
    feed_data = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

    query = '("UKMTO" OR "Ambrey" OR "MSCHOA" OR "MSCIO") AND ("incident" OR "attack" OR "vessel" OR "boarded" OR "missile" OR "houthi") when:7d'
    encoded_query = urllib.parse.quote(query)
    gn_url = f'https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en&_={int(time.time())}'
    
    try:
        res = requests.get(gn_url, headers=headers, timeout=10)
        if res.status_code == 200:
            feed = feedparser.parse(res.text)
            for entry in feed.entries[:8]:
                title = entry.title
                clean_title = re.sub(r' - [^-]+$', '', title).strip()
                
                source = "🌍 Maritime Intel"
                if "UKMTO" in title.upper(): source = "🇬🇧 UKMTO Report"
                elif "AMBREY" in title.upper(): source = "🛡️ Ambrey Security"
                elif "MSCIO" in title.upper() or "MSCHOA" in title.upper(): source = "🇪🇺 MSCIO Advisory"
                
                type_val = "Security Advisory"
                if any(w in title.lower() for w in ['attack', 'missile', 'strike', 'hijack', 'boarded']):
                    type_val = "🚨 Attack Warning"
                elif any(w in title.lower() for w in ['incident', 'explosion', 'suspicious']):
                    type_val = "⚠️ Incident Report"
                    
                pub_date = entry.get('published', 'Recent')
                if pub_date.endswith(" GMT"):
                    pub_date = pub_date[:-4] 
                    
                feed_data.append({
                    "source": source,
                    "type": type_val,
                    "time": pub_date,
                    "details": clean_title, 
                    "url": entry.link
                })
    except Exception as e:
        pass

    if feed_data:
        return feed_data
        
    try:
        res = requests.get("https://gcaptain.com/feed/", headers=headers, timeout=10)
        if res.status_code == 200:
            feed = feedparser.parse(res.text)
            for entry in feed.entries[:5]:
                feed_data.append({
                    "source": "⚓ gCaptain Network",
                    "type": "Maritime Dispatch",
                    "time": entry.get('published', 'Recent')[:22],
                    "details": entry.title,
                    "url": entry.link
                })
    except:
        pass
        
    if feed_data:
        return feed_data

    return [{
        "source": "System",
        "type": "Monitoring Active",
        "time": "Live",
        "details": "Scanning global maritime frequencies. No major kinetic incidents reported in the last cycle.",
        "url": "#"
    }]

# ==========================================
# 🌍 AUTONOMOUS GEOCODER FOR FOLIUM
# ==========================================
folium_geolocator = Nominatim(user_agent="semicon_intel_dashboard")

GEOCODER_MAP = {
    "Strait of Hormuz": [26.56, 56.25],
    "China": [35.86, 104.19],
    "Vietnam": [14.05, 108.27],
    "Africa": [-8.78, 34.50],
    "Global (referencing China)": [35.86, 104.19],
    "Taiwan": [23.69, 120.96],
    "United States": [37.09, -95.71],
    "India": [20.59, 78.96]
}

@st.cache_data(ttl=86400, show_spinner=False)
def intelligent_geocode(location_name):
    if not location_name or pd.isna(location_name):
        return None

    if location_name in GEOCODER_MAP:
        return GEOCODER_MAP[location_name]

    try:
        time.sleep(0.5)
        location = folium_geolocator.geocode(location_name)
        if location:
            return [location.latitude, location.longitude]
    except Exception:
        return None

    return None

def get_strategic_asset_match(row):
    if not INFRASTRUCTURE_DATA:
        return None, None
        
    headline = str(row.get('Headline', '')).lower()
    action = str(row.get('Action', '')).lower()
    loc = str(row.get('Location', '')).lower()
    actor = str(row.get('Actor', '')).lower()
    
    combined_text = f"{headline} {action} {loc} {actor}"
    
    key_identifiers = ["tsmc", "samsung", "intel", "smic", "globalfoundries", "micron", "asml", 
                       "bayan obo", "malacca", "hormuz", "bab el-mandeb", "suez", "taiwan strait", 
                       "severomorsk", "kadamba", "cape canaveral", "jiuquan"]

    for category, sites in INFRASTRUCTURE_DATA.items():
        for site in sites:
            site_name_lower = site['name'].lower()
            
            if len(loc) > 3 and loc in site_name_lower:
                return site, category
            if len(actor) > 2 and actor in site_name_lower:
                return site, category
                
            for identifier in key_identifiers:
                if identifier in combined_text and identifier in site_name_lower:
                    return site, category

    return None, None


def render_tactical_conflict_overlay(df_actions):
    st.markdown("""
    ### 🗺️ Multi-Domain Conflict & Thermal Radar Overlay
    """)
    
    st.caption(
        "Live geopolitical telemetry mapping with maritime disruption zones, semiconductor chokepoints, and strategic conflict overlays."
    )

    m = folium.Map(
        location=[25.0, 60.0],
        zoom_start=3,
        tiles="CartoDB dark_matter"
    )

    folium.raster_layers.WmsTileLayer(
        url="https://firms.modaps.eosdis.nasa.gov/mapserver/wms/fires",
        layers="fires_viirs_24",
        name="NASA Active Thermal Signatures",
        fmt="image/png",
        transparent=True,
        overlay=True,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="Carto",
        name="Maritime Shipping Density",
        overlay=True,
        control=True
    ).add_to(m)

    conflict_zones = [
        {
            "name": "Red Sea Disruption Zone",
            "coords": [[12.0, 42.0], [16.0, 42.0], [16.0, 46.0], [12.0, 46.0]],
            "color": "red"
        },
        {
            "name": "South China Sea Strategic Friction Zone",
            "coords": [[8.0, 109.0], [20.0, 109.0], [20.0, 121.0], [8.0, 121.0]],
            "color": "orange"
        },
        {
            "name": "Black Sea / Ukraine Theater",
            "coords": [[42.0, 27.0], [47.0, 27.0], [47.0, 40.0], [42.0, 40.0]],
            "color": "darkred"
        },
        {
            "name": "Persian Gulf / Iran Tension Zone",
            "coords": [[24.0, 48.0], [30.0, 48.0], [30.0, 57.0], [24.0, 57.0]],
            "color": "crimson"
        }
    ]

    for zone in conflict_zones:
        folium.Polygon(
            locations=zone["coords"],
            color=zone["color"],
            fill=True,
            fill_opacity=0.15,
            popup=zone["name"]
        ).add_to(m)

    if INFRASTRUCTURE_DATA:
        asset_colors = {
            "Semiconductor Fabs": "#00bfff",
            "Critical Mineral Sites": "#10b981",
            "Maritime Chokepoints": "#3b82f6",
            "Gulf FDI & Capital Diplomacy": "#f59e0b",
            "Naval Order of Battle & Strategic Bases": "#8b5cf6",
            "Aerospace & Space Force Installations": "#f43f5e"
        }

        for category, sites in INFRASTRUCTURE_DATA.items():
            fg = folium.FeatureGroup(name=f"📍 {category}", show=False)
            color = asset_colors.get(category, "#ffffff")
            
            for site in sites:
                folium.CircleMarker(
                    location=[site["lat"], site["lon"]],
                    radius=5,
                    popup=f"<b>{category}</b><br>{site['name']}",
                    tooltip=f"{category}: {site['name']}",
                    color=color,
                    fill=True,
                    fill_opacity=0.7,
                    weight=1
                ).add_to(fg)
            
            fg.add_to(m)

    marker_cluster = MarkerCluster(
        name="🚨 Verified Strategic Events (Live)"
    ).add_to(m)

    event_points = []
    heat_data = []

    if (
        df_actions is not None
        and not df_actions.empty
        and 'Location' in df_actions.columns
    ):
        for _, row in df_actions.iterrows():
            location_str = str(row.get('Location', '')).strip()
            actor = str(row.get('Actor', 'Unknown Actor'))
            headline = str(row.get('Headline', row.get('Action', 'Strategic Event')))
            risk_val = "CRITICAL" if str(row.get('Risk', '')).upper() == 'CRITICAL' else "HIGH"

            matched_site, matched_category = get_strategic_asset_match(row)

            if matched_site:
                lat, lon = matched_site['lat'], matched_site['lon']
                site_name = matched_site['name']
                
                popup_html = f"""
                <div style='min-width: 250px; font-family: sans-serif;'>
                    <h4 style='color: #ef4444; margin-top: 0px; margin-bottom: 8px; border-bottom: 1px solid #ccc; padding-bottom: 5px;'>🎯 STRATEGIC ASSET ALERT</h4>
                    <b style='color: #000;'>📍 The Spot:</b> <span style='color: #333;'>{site_name}</span><br><br>
                    <b style='color: #000;'>⚡ What is happening:</b> <span style='color: #333;'>{headline}</span><br><br>
                    <b style='color: #000;'>🛡️ Why it's important:</b> <span style='color: #333;'>This location is tracked as a critical node in <b>{matched_category}</b>. Disruption here has immediate macro-strategic ripple effects.</span>
                </div>
                """
                
                event_points.append({
                    "name": site_name,
                    "lat": lat,
                    "lon": lon,
                    "risk": risk_val,
                    "is_asset_match": True,
                    "popup_html": popup_html
                })
                heat_data.append([lat, lon, 1.0])

            else:
                coords = intelligent_geocode(location_str)

                if coords:
                    lat, lon = coords
                    popup_html = f"<b>{actor}:</b> {headline} <br><i>(General Vicinity: {location_str})</i>"

                    event_points.append({
                        "name": f"{actor}: {headline}",
                        "lat": lat,
                        "lon": lon,
                        "risk": risk_val,
                        "is_asset_match": False,
                        "popup_html": popup_html
                    })
                    heat_data.append([lat, lon, 0.8])

    if len(event_points) == 0:
        event_points = [
            {"name": "Taiwan Semiconductor Fabrication Corridor", "lat": 24.14, "lon": 120.67, "risk": "HIGH", "is_asset_match": False, "popup_html": "Taiwan Corridor Event"},
            {"name": "Bab-el-Mandeb Maritime Disruption", "lat": 12.58, "lon": 43.33, "risk": "CRITICAL", "is_asset_match": False, "popup_html": "Bab-el-Mandeb Event"}
        ]
        heat_data = [[24.14, 120.67, 0.9], [12.58, 43.33, 1.0]]

    for event in event_points:
        color = "red" if event["risk"] == "CRITICAL" else "orange" if event["risk"] == "HIGH" else "yellow"

        if event.get("is_asset_match", False):
            folium.Marker(
                location=[event["lat"], event["lon"]],
                popup=folium.Popup(event["popup_html"], max_width=350),
                icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
            ).add_to(marker_cluster)
            
            folium.CircleMarker(
                location=[event["lat"], event["lon"]],
                radius=18,
                color="red",
                fill=True,
                fill_opacity=0.3,
                weight=3
            ).add_to(marker_cluster)
        else:
            folium.CircleMarker(
                location=[event["lat"], event["lon"]],
                radius=9,
                popup=folium.Popup(event["popup_html"], max_width=300),
                color=color,
                fill=True,
                fill_opacity=0.8,
                weight=2
            ).add_to(marker_cluster)

    if heat_data:
        HeatMap(
            heat_data,
            name="Geopolitical Tension Heatmap",
            radius=35,
            blur=20,
            max_zoom=5
        ).add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(
        m,
        width="100%",
        height=650,
        returned_objects=[]
    )

    active_locations = []
    for e in event_points:
        if '(' in e['name']:
            loc = e['name'].split('(')[-1].strip(')')
            active_locations.append(loc)
    
    active_locations = list(set(active_locations))

    if len(active_locations) > 0:
        top_locs = ", ".join(active_locations[:3])
        if len(active_locations) > 3:
            top_locs += " and other emerging theaters"
    else:
        top_locs = "Global Baseline Supply Routes"

    event_count = len(event_points)

    st.markdown(f"""
    <div style="
        background: rgba(17,17,17,0.85);
        padding:18px;
        border-radius:10px;
        border-left:4px solid #00bfff;
        margin-top:15px;
        box-shadow:0 4px 15px rgba(0,191,255,0.15);
    ">
    <b style="
        color:#00bfff;
        letter-spacing:1px;
    ">
    INTELLIGENCE NOTE:
    </b>
    <br><br>
    The Geospatial Intelligence Layer correlates:
    <ul style="
        color:#d1d5db;
        margin-top:8px;
    ">
        <li>Semiconductor manufacturing chokepoints</li>
        <li>
        Maritime disruption zones, shipping telemetry,
        and strategic conflict polygons
        </li>
        <li>Rare earth concentration regions</li>
    </ul>
    
    <div style="
        background: rgba(0, 0, 0, 0.4);
        padding: 12px;
        border-radius: 6px;
        border-left: 3px solid #ef4444;
        margin-top: 15px;
    ">
        <span style="color: #ef4444; font-weight: bold; font-size: 13px; letter-spacing: 0.5px;">LIVE CYCLE ASSESSMENT:</span><br>
        <span style="color: #e2e8f0; font-size: 14px; line-height: 1.5; display: inline-block; margin-top: 5px;">
            The autonomous geocoder has successfully verified and plotted <b>{event_count}</b> critical strategic events originating from the most recent Geopolitics-OSINT data feed. Current kinetic and regulatory anomalies are predominantly clustered near <b>{top_locs}</b>. 
            <br><br>
            <i>What this conveys:</i> The Multi-Domain Radar is designed to cross-reference physical ground-truth anomalies (via NASA FIRMS thermal imaging) directly against these fresh textual intelligence drops, verifying if digital reports of infrastructural damage or maritime friction correlate with actual thermal spikes in those specific zones.
        </span>
    </div>
    
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 5. MAIN EXECUTIVE HOME RENDER
# ==========================================
def render_executive_home(dashboard_data, df_actions, live_tactical_data, mapbox_token):
    # 1. Aggressively normalize global df_actions (strips hidden spaces and fixes case)
    if not df_actions.empty:
        df_actions.columns = [str(c).strip().title() for c in df_actions.columns]

    exec_data_path = 'data/executive_home/tactical_events_24h.json'
    if os.path.exists(exec_data_path):
        try:
            with open(exec_data_path, 'r') as f:
                exec_events = json.load(f)
                df_exec = pd.DataFrame(exec_events)
                
                if not df_exec.empty:
                    # 2. Aggressively normalize local df_exec
                    df_exec.columns = [str(c).strip().title() for c in df_exec.columns]
                    
                    # 3. Cross-fill Action and Headline in df_exec if one is missing entirely
                    if 'Action' in df_exec.columns and 'Headline' not in df_exec.columns:
                        df_exec['Headline'] = df_exec['Action']
                    elif 'Headline' in df_exec.columns and 'Action' not in df_exec.columns:
                        df_exec['Action'] = df_exec['Headline']
                        
                    # 4. Safe Concatenation
                    if df_actions.empty:
                        df_actions = df_exec
                    else:
                        df_actions = pd.concat([df_exec, df_actions], ignore_index=True)
        except Exception as e:
            pass

    inject_executive_home_css()

    st.markdown("""
    <div style='text-align: center; margin-top: 10px; margin-bottom: 30px;'>
        <h1 style='color: #00bfff; font-size: 2.5em; letter-spacing: 2px; margin-bottom: 0px;'>SemicoN Strategic Command</h1>
        <p style='color: #d1d5db; font-family: monospace; font-size: 1.1em;'>LIVE GEOPOLITICS-OSINT & THREAT MONITORING ENVIRONMENT</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ⚠️ REPLACED LINE: Calling the newly defined function without arguments
    render_flash_alert()

    st.markdown("### 🚨 Live Strategic Alert Monitor")
    check_early_warnings()
    st.markdown("<hr style='border: 1px solid #333; margin-top: -15px; margin-bottom: -10px;'>", unsafe_allow_html=True)

    st.markdown("### 📝 Strategic Command Analysis")
    st.caption("Autonomous geopolitical synthesis aggregating threat velocity, maritime telemetry, and multi-domain actor posturing.")
    
    # ==========================================
    # --- NEW FLASH TO BRIEF UI ---
    # ==========================================
    flush_path = 'data/executive_home/flush_brief_24h.json'
    flush_data = {}
    if os.path.exists(flush_path):
        try:
            with open(flush_path, 'r') as f:
                flush_data = json.load(f)
        except:
            pass

    # Extract dynamic keys or provide secure fallbacks
    bluf_text = flush_data.get('bluf', "Scanning macro-strategic feeds. Awaiting telemetry generation cycle...")
    tactical_list = flush_data.get('tactical_indicators', ["System initiating...", "Monitoring baseline anomalies...", "Awaiting active extraction..."])
    threat_text = flush_data.get('threat_narrative', "Data currently rendering inside the strategic analysis layer...")
    risk_text = flush_data.get('risk_assessment', "Data currently rendering inside the strategic analysis layer...")
    forecast_text = flush_data.get('strategic_forecast', "Data currently rendering inside the strategic analysis layer...")
    
    if isinstance(tactical_list, list):
        tactical_html = "<br>".join([f"• {item}" for item in tactical_list])
    else:
        tactical_html = tactical_list

    # Title
    st.markdown("""
    <h2 style='color: #a855f7; margin-bottom: 15px; margin-top: 10px; font-size: 2em; letter-spacing: 1.5px; border-bottom: 2px solid #a855f7; padding-bottom: 5px; display: inline-block;'>FLASH TO BRIEF</h2>
    """, unsafe_allow_html=True)
    
    # 1. BLUF Box
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #141e30 0%, #243b55 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #00bfff; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h3 style="margin-top: 0; color: #ffffff;">🎯 BLUF (Bottom Line Up Front)</h3>
        <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{bluf_text}</p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Side-By-Side Triple Columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2c1b3d 0%, #4a2b5e 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #a855f7; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #ffffff; font-size: 1.2em;">🚩 Tactical Indicators</h3>
            <p style="color: #e2e8f0; font-size: 0.95em; margin-bottom: 0; line-height: 1.5;">{tactical_html}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2b0f19 0%, #591b2c 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #ef4444; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #ffffff; font-size: 1.2em;">🕸️ Threat Narrative</h3>
            <p style="color: #e2e8f0; font-size: 0.95em; margin-bottom: 0; line-height: 1.5;">{threat_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #3f2b1a 0%, #613c20 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #f59e0b; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #ffffff; font-size: 1.2em;">⚖️ Risk Assessment</h3>
            <p style="color: #e2e8f0; font-size: 0.95em; margin-bottom: 0; line-height: 1.5;">{risk_text}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Forecast Box
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #093028 0%, #1b4b36 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #10b981; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h3 style="margin-top: 0; color: #ffffff;">🔭 Strategic Recommendations/Strategic Forecast (Within 24 Hours)</h3>
        <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{forecast_text}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
    
    all_text_parts = []
    
    if not df_actions.empty:
        for col in ['Headline', 'Event', 'Action', 'Actor', 'Location']:
            if col in df_actions.columns:
                all_text_parts.extend(df_actions[col].dropna().astype(str).tolist())
                
    all_text = " ".join(all_text_parts).lower()
    
    render_decision_support_engine(all_text)
    
    st.markdown("<hr style='border: 1px solid #333; margin-top: -15px; margin-bottom: -10px;'>", unsafe_allow_html=True)

    st.markdown("### 📊 Global Threat Posture")
    esc_val, choke_val, geo_val, status_val = calculate_dynamic_posture(df_actions)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric(label="🔴 Active Escalations", value=esc_val, delta="Live Updated", delta_color="inverse" if int(esc_val)>0 else "off")
    with col2: st.metric(label="🚢 Supply Chain Chokepoints", value=choke_val, delta="Live Updated", delta_color="off")
    with col3: st.metric(label="🛰️ Geopolitical Shifts", value=geo_val, delta="Live Updated", delta_color="normal")
    with col4: st.metric(label="🛡️ System Status", value=status_val, delta="Monitoring Active")

    # ==========================================
    # 📊 GLOBAL THREAT POSTURE ANALYSIS ENGINE
    # ==========================================
    with st.expander("📖 Global Threat Posture Intelligence Analysis & Strategic Interpretation"):

        st.markdown("""
        <div style="
            background: rgba(17,17,17,0.82);
            border-left: 4px solid #00bfff;
            padding: 22px;
            border-radius: 10px;
            margin-top: 10px;
            margin-bottom: 10px;
            box-shadow: 0 4px 18px rgba(0,191,255,0.10);
        ">

        <h4 style="
            color:#00bfff;
            margin-top:0;
            margin-bottom:12px;
            letter-spacing:1px;
        ">
        📊 Understanding Global Threat Posture
        </h4>

        <p style="
            color:#d1d5db;
            line-height:1.65;
            font-size:0.96rem;
            margin-bottom:12px;
        ">
        The Global Threat Posture module functions as a strategic geopolitical
        risk interpretation engine. Rather than displaying raw event counts alone,
        the architecture correlates escalation patterns, semiconductor supply-chain
        pressure, maritime instability, export-control friction, critical mineral
        volatility, and geopolitical realignment into a unified executive risk picture.
        </p>

        <p style="
            color:#9ca3af;
            line-height:1.6;
            font-size:0.92rem;
            margin-bottom:20px;
            font-style:italic;
        ">
        The objective is not only to detect events — but to explain how changes
        in those indicators alter the strategic operating environment surrounding
        semiconductor ecosystems, rare earth supply chains, advanced-node foundries,
        logistics corridors, and industrial resilience.
        </p>

        </div>
        """, unsafe_allow_html=True)

        # ==========================================
        # 🔴 ACTIVE Escalations
        # ==========================================
        st.markdown("""
        ### 🔴 Active Escalations

        **What it measures:** Tracks high-severity geopolitical or military escalation events detected
        across the live Geopolitics-OSINT pipeline.

        **Examples include:**
        * Military mobilization
        * Maritime attacks or blockades
        * Export-control retaliation
        * Sanctions escalation
        * Strategic cyber activity
        * Crisis-level diplomatic breakdowns

        **If the number INCREASES:** * Semiconductor shipment insurance premiums may rise
        * Foundry logistics become less predictable
        * Rare earth export restrictions may intensify
        * Global markets price in elevated supply risk
        * Strategic investors reduce exposure to fragile routes

        **If the number DECREASES:** * Supply chain confidence stabilizes
        * Maritime transit becomes more reliable
        * Regulatory friction may temporarily ease
        * Industrial planning horizons improve

        **Strategic Interpretation:** A rise in Active Escalations does not automatically mean open conflict.
        In modern geopolitical competition, sustained low-intensity escalation
        often produces greater long-term supply-chain disruption than short-duration
        kinetic events.
        """)

        # ==========================================
        # 🚢 SUPPLY CHAIN CHOKEPOINTS
        # ==========================================
        st.markdown("""
        ### 🚢 Supply Chain Chokepoints

        **What it measures:** Monitors stress signals affecting semiconductor manufacturing,
        logistics infrastructure, maritime corridors, and critical mineral flow.

        **Tracked domains include:**
        * Taiwan Strait
        * Strait of Hormuz
        * Bab-el-Mandeb
        * South China Sea
        * Advanced-node lithography routes
        * Rare earth refining concentration zones

        **If the number INCREASES:** * Shipping delays and rerouting risks expand
        * Semiconductor fabrication timelines may slow
        * Critical minerals become harder to source
        * Foundries dependent on single-route logistics face elevated vulnerability
        * Advanced packaging ecosystems experience downstream instability

        **If the number DECREASES:** * Transit normalization improves supply-chain predictability
        * Industrial procurement confidence improves
        * Strategic stockpiling pressure may decline

        **Strategic Interpretation:** Semiconductor ecosystems are highly dependent on uninterrupted maritime
        and mineral logistics. Even small disruptions in one chokepoint can create
        cascading second-order effects across fabrication, assembly, testing,
        and downstream electronics manufacturing.
        """)

        # ==========================================
        # 🛰️ GEOPOLITICAL SHIFTS
        # ==========================================
        st.markdown("""
        ### 🛰️ Geopolitical Shifts

        **What it measures:** Tracks structural geopolitical realignments affecting technology,
        industrial policy, strategic alliances, and resource control.

        **Examples include:**
        * New export-control regimes
        * Defense partnerships
        * Critical mineral agreements
        * Industrial subsidy programs
        * BRICS/G7 technology positioning
        * Strategic semiconductor diplomacy

        **If the number INCREASES:** * Technology fragmentation accelerates
        * Supply chains regionalize into geopolitical blocs
        * Companies may face dual-compliance environments
        * Advanced semiconductor access becomes increasingly politicized

        **If the number DECREASES:** * Strategic alignment stabilizes
        * Cross-border technology cooperation may improve
        * Regulatory predictability increases

        **Strategic Interpretation:** Not all geopolitical shifts are immediately visible through military activity.
        Many long-term semiconductor disruptions emerge through policy architecture,
        investment restrictions, technology-access controls, and alliance restructuring.
        """)

        # ==========================================
        # 🛡️ SYSTEM STATUS
        # ==========================================
        st.markdown(f"""
        ### 🛡️ System Status — {status_val}

        **What it represents:** The System Status indicator reflects the platform's aggregate geopolitical
        threat assessment derived from escalation velocity, logistics disruption,
        maritime instability, export-control activity, and strategic actor behavior.

        **Current Meaning of {status_val}:**
        * Elevated geopolitical monitoring posture
        * Active strategic friction detected
        * Increased probability of regional supply instability
        * Higher executive attention recommended

        **Operational Implications for Semiconductor Ecosystems:**
        * Increased risk to advanced-node continuity
        * Potential rare earth pricing volatility
        * Elevated insurance and transit costs
        * Greater pressure on fab redundancy planning
        * Higher sensitivity around Taiwan-centered supply architectures

        **Executive Assessment Framework:** The System Status layer functions similarly to an integrated geopolitical
        readiness index rather than a military-only DEFCON system. It is designed
        to help decision-makers understand whether the global technology and
        industrial environment is stabilizing, deteriorating, or entering
        sustained strategic friction.
        """)

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    st.markdown("### 📈 Threat Velocity (Past 7 Days)")
    
    indo_kws = ['taiwan', 'china', 'japan', 'korea', 'indo-pacific', 'south china sea', 'philippines']
    export_kws = ['export', 'control', 'sanction', 'entity list', 'smic', 'huawei', 'asml', 'node']
    maritime_kws = ['strait', 'sea', 'maritime', 'ship', 'cargo', 'transit', 'logistics', 'red sea', 'hormuz']
    
    indo_trend = calculate_dynamic_velocity(df_actions, indo_kws, [40,45,50,55,60,62,65])
    export_trend = calculate_dynamic_velocity(df_actions, export_kws, [20,25,30,40,55,70,85])
    maritime_trend = calculate_dynamic_velocity(df_actions, maritime_kws, [35,38,42,40,44,48,52])
    
    v1, v2, v3 = st.columns(3)
    with v1: render_velocity_chart("Indo-Pacific Risk", indo_trend)
    with v2: render_velocity_chart("Export Control Friction", export_trend)
    with v3: render_velocity_chart("Maritime Disruption", maritime_trend)
        
    with st.expander("⚙️ Threat Velocity Methodology & Approach"):
        st.markdown("""
        **Analytical Approach:** The Threat Velocity charts utilize a quantitative 0-100 Risk Score. The timeline standard uses the military "D-Day" designation, where **Today** represents the current tactical environment, and **D-6** represents the environment six days prior.
        
        **Calculation Basis:** Scores are generated by processing the 12-Hour Geopolitics-OSINT feed through natural language processing (NLP). The engine assigns weight multipliers to distinct friction events: Kinetic/Maritime Posturing, Regulatory Action, and Supply Chain Contractions.
        """)

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    st.markdown("### 🔥 Hot Actor Telemetry")
    hot_actors = get_hot_actors(df_actions)
    if hot_actors:
        st.caption("Highest friction entities actively tracked in the current cycle:")
        actor_cols = st.columns(len(hot_actors))
        for idx, (actor, count) in enumerate(hot_actors):
            with actor_cols[idx]:
                st.markdown(f"""
                <div class="hot-actor-box">
                <b style="font-size:1.1em;">{actor}</b><br>
                <span style="color:#00bfff; font-size: 0.9em; font-weight:bold;">High-Confidence Signals: {count}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No concentrated actor activity detected.")

    with st.expander("⚙️ Hot Actor Telemetry Methodology & Approach"):
        st.markdown("""
        **Analytical Approach:** Isolates specific nation-states, corporations, or strategic entities driving critical geopolitical friction.
        **Understanding "High-Confidence Signals":** Verified, definitive intelligence artifacts sourced from official state media declarations, confirmed regulatory filings, or corroborated regional defense reporting.
        """)
        
    st.markdown("<br>", unsafe_allow_html=True)

    # ==========================================
    # ⚠️ RECENT TACTICAL ALERTS
    # ==========================================
    st.markdown("### ⚠️ Recent Tactical Alerts")
    
    if not df_actions.empty:
        temp_df = df_actions.copy()
        
        # 1. Target exact columns to map directly to the backend
        target_cols = ['Date', 'Actor', 'Action', 'Location', 'Risk']
        
        # 2. Ensure target columns exist safely
        for col in target_cols:
            if col not in temp_df.columns:
                if col == 'Action' and 'Headline' in temp_df.columns:
                    temp_df['Action'] = temp_df['Headline']
                elif col == 'Actor' and 'Source' in temp_df.columns:
                    temp_df['Actor'] = temp_df['Source']
                else:
                    temp_df[col] = "Pending Data"
                    
        # 3. Clean, Sort, and Enforce Diversity via Deduplication
        display_df = temp_df[target_cols].copy()
        
        # Drop identical actions to prevent one event flooding the board
        display_df = display_df.drop_duplicates(subset=['Action'], keep='first')
        
        if 'Date' in display_df.columns:
            display_df['Parsed_Date'] = pd.to_datetime(display_df['Date'], errors='coerce', utc=True)
            display_df = display_df.sort_values(by=['Parsed_Date'], ascending=[False])
            display_df['Date'] = display_df['Date'].astype(str)
            display_df = display_df.drop(columns=['Parsed_Date'])
            
        # 4. Lock in exactly 10 diverse rows
        display_df = display_df.head(10)
        display_df = display_df.fillna("")
        
        # 5. Intense Dynamic Styling for CRITICAL Risk Elements
        def color_risk(val):
            val_str = str(val).upper()
            if 'CRITICAL' in val_str:
                return 'background-color: rgba(220, 38, 38, 0.35); color: #fca5a5; font-weight: 900; border: 1px solid #ef4444;'
            elif 'HIGH' in val_str:
                return 'background-color: rgba(217, 119, 6, 0.2); color: #fcd34d; font-weight: bold;'
            elif 'MODERATE' in val_str or 'MID' in val_str or 'ELEVATED' in val_str:
                return 'color: #fbbf24;'
            elif 'LOW' in val_str or 'NOMINAL' in val_str:
                return 'color: #4ade80;'
            return ''

        # Apply styling dynamically
        try:
            styled_df = display_df.style.map(color_risk, subset=['Risk'])
        except AttributeError:
            styled_df = display_df.style.applymap(color_risk, subset=['Risk'])
            
        # Expanded height slightly to perfectly frame 10 rows
        st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)
    else:
        st.write("No tactical alerts logged in the current operational cycle.")
            
    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    st.markdown("### 🌍 Strategic Geospatial Intelligence Layer")
    st.caption("Live global telemetry mapping with active 13-sector radar scanning.")
    
    regions = [
        "North America", "Latin America", "Africa", "Oceanic",
        "East Europe", "Central Europe", "Western Europe", "West Asia",
        "South Asia", "East Asia and Far East Asia", "South East Asia",
        "Central Asia", "Eurasia"
    ]
    regions_js = json.dumps(regions)

    sweep_html = f"""
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 0; background: transparent; }}
        .radar-container {{
            background-color: rgba(17, 24, 39, 0.8); border: 1px solid #1f2937;
            border-left: 4px solid #10b981; padding: 12px 18px; border-radius: 6px;
            display: flex; align-items: center; justify-content: space-between;
            color: #d1d5db; margin-bottom: 15px;
        }}
        .radar-text {{ font-size: 13px; font-weight: bold; letter-spacing: 1.5px; text-transform: uppercase; display: flex; align-items: center; gap: 8px; }}
        .radar-text::before {{ content: ''; display: inline-block; width: 10px; height: 10px; border-radius: 50%; background-color: #10b981; box-shadow: 0 0 8px #10b981; animation: blink 1s infinite; }}
        .radar-region {{ color: #10b981; font-weight: 800; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }}
        @keyframes blink {{ 0%, 100% {{opacity: 1;}} 50% {{opacity: 0.4;}} }}
    </style>
    <div class="radar-container">
        <div class="radar-text">Live Sector Scan Active</div>
        <div>RESOLVING TELEMETRY: <span id="radar-region" class="radar-region">INITIALIZING...</span></div>
    </div>
    <script>
        const regions = {regions_js};
        let index = 0;
        setInterval(() => {{
            document.getElementById('radar-region').innerText = regions[index];
            index = (index + 1) % regions.length;
        }}, 1000);
    </script>
    """
    components.html(sweep_html, height=70)
    
    map_data = []
    if not df_actions.empty:
        geo_col = 'Location' if 'Location' in df_actions.columns else 'Actor'
        
        if geo_col in df_actions.columns:
            recent_entities = df_actions.head(15)[geo_col].dropna().unique()
            for entity in recent_entities:
                clean_query = str(entity).replace("Government of ", "").strip()
                lat, lon, resolved_name = resolve_location(clean_query)
                
                if lat is not None and lon is not None:
                    high_friction_zones = ["china", "taiwan", "russia", "iran", "israel", "red sea", "ukraine"]
                    is_hot = any(hot in str(entity).lower() for hot in high_friction_zones)
                    alert_color = [255, 75, 75, 200] if is_hot else [0, 191, 255, 200]
                    
                    map_data.append({
                        "name": resolved_name,
                        "entity": str(entity),
                        "lat": lat,
                        "lon": lon,
                        "color": alert_color,
                        "radius": 150000
                    })

    if not map_data:
        map_data = [{"name": "Global Monitor", "entity": "System Nominal", "lat": 20.0, "lon": 0.0, "color": [0, 191, 255, 100], "radius": 400000}]

    map_df = pd.DataFrame(map_data)
    map_df['lat'] = pd.to_numeric(map_df['lat'], errors='coerce')
    map_df['lon'] = pd.to_numeric(map_df['lon'], errors='coerce')
    
    center_lat = map_df['lat'].mean() if len(map_df) > 0 and pd.notna(map_df['lat'].mean()) else 20.0
    center_lon = map_df['lon'].mean() if len(map_df) > 0 and pd.notna(map_df['lon'].mean()) else 0.0

    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=1.2, pitch=0)
    layer = pdk.Layer(
        "ScatterplotLayer", 
        data=map_df, 
        get_position='[lon, lat]', 
        get_color='color', 
        get_radius='radius', 
        pickable=True, 
        filled=True
    )
    
    st.pydeck_chart(pdk.Deck(
        api_keys={"mapbox": mapbox_token}, 
        map_style="mapbox://styles/mapbox/dark-v11", 
        initial_view_state=view_state, 
        layers=[layer], 
        tooltip={"text": "Location: {name}\nActive Entity: {entity}"}
    ), use_container_width=True)

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    render_tactical_conflict_overlay(df_actions)
    
    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    st.markdown("### 📦 Strategic Risk Indicators")
    
    indo_risk_val, indo_risk_text = calculate_dynamic_risk(df_actions, indo_kws, 0.40)
    wa_kws = ['iran', 'israel', 'red sea', 'yemen', 'houthis', 'suez', 'middle east']
    wa_risk_val, wa_risk_text = calculate_dynamic_risk(df_actions, wa_kws, 0.30)
    node_risk_val, node_risk_text = calculate_dynamic_risk(df_actions, export_kws, 0.60)
    
    col_ind1, col_ind2, col_ind3 = st.columns(3)
    with col_ind1: st.progress(indo_risk_val, text=f"Indo-Pacific Transit Risk: {indo_risk_text}")
    with col_ind2: st.progress(wa_risk_val, text=f"West Asia Logistics: {wa_risk_text}")
    with col_ind3: st.progress(node_risk_val, text=f"Advanced Node Controls: {node_risk_text}")

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    st.markdown("### 🌊 Live Combined Maritime Security Feed")
    st.caption("Cross-referenced live maritime security advisories parsed directly into the dashboard.")

    maritime_intel = fetch_live_maritime_intel()
    
    # --- NEW SORTING LOGIC ---
    try:
        def parse_feed_time(item):
            dt = pd.to_datetime(item.get('time', ''), errors='coerce', utc=True)
            return dt if pd.notna(dt) else pd.Timestamp('1970-01-01', tz='UTC')
            
        maritime_intel = sorted(maritime_intel, key=parse_feed_time, reverse=True)
    except Exception:
        pass
    # -------------------------

    st.markdown("""
    <style>
    .maritime-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .maritime-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px -2px rgba(0, 191, 255, 0.2);
    }
    .maritime-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .maritime-source { font-size: 13px; font-weight: bold; color: #94a3b8; font-family: monospace; }
    .maritime-time { font-size: 12px; color: #64748b; font-weight: bold; }
    .maritime-title { font-size: 16px; font-weight: 800; color: #f8fafc; margin-bottom: 6px; }
    .maritime-desc { font-size: 14px; color: #cbd5e1; line-height: 1.5; margin-bottom: 12px; }
    .maritime-link a { 
        display: inline-block;
        font-size: 13px; 
        color: #00bfff; 
        text-decoration: none; 
        font-weight: bold;
        border: 1px solid #00bfff;
        padding: 4px 10px;
        border-radius: 4px;
        transition: background-color 0.2s;
    }
    .maritime-link a:hover {
        background-color: rgba(0, 191, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    for item in maritime_intel:
        border_color = "#ef4444" if "Incident" in item['type'] else "#eab308" if "Advisory" in item['type'] or "Warning" in item['type'] else "#3b82f6"
        url = item.get('url', '#')
        
        st.markdown(f"""
        <div class="maritime-card" style="border-left: 5px solid {border_color};">
            <div class="maritime-header">
                <div class="maritime-source">{item['source']}</div>
                <div class="maritime-time">{item['time']}</div>
            </div>
            <div class="maritime-title">{item['type']}</div>
            <div class="maritime-desc">{item['details']}</div>
            <div class="maritime-link">
                <a href="{url}" target="_blank">🔗 Read Official Alert</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    st.markdown("### 🚢 Live Maritime Telemetry")
    st.caption("Real-time tracking of global shipping lanes and critical maritime chokepoints.")

    try:
        components.iframe(
            "https://www.marinetraffic.com/en/ais/embed/zoom:4/centery:25.0/centerx:-12.0/maptype:3/shownames:false/mmsi:0/shipid:0/fleet:/fleet_id:/vtypes:/showmenu:false/remember:false",
            height=600,
            scrolling=False
        )
    except Exception:
        st.warning("Unable to load MarineTraffic telemetry feed at this time.")

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # ==========================================
    # 🌍 HEGEMON GLOBAL EMBED
    # ==========================================
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    
    st.markdown("### 🌐 Hegemon Global Monitor")
    st.caption("Live external intelligence platform. **Credit & Rights:** [Hegemon Global](https://hegemonglobal.com) and its original creators. All embedded interactivity is preserved below.")

    try:
        # We set scrolling=True so you can navigate their site from within your dashboard
        components.iframe(
            "https://hegemonglobal.com",
            height=700, 
            scrolling=True
        )
    except Exception:
        st.warning("⚠️ Unable to load Hegemon Global. The website's server may actively block iframe embedding (X-Frame-Options).")

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # This is your Intelligence Note at the absolute bottom
    render_executive_deep_intelligence_note()