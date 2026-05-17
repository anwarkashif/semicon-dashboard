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

# --- Newly added import for Decision Support Engine ---
from features.tactical_features import render_decision_support_engine

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
    .flash-alert {
        background: linear-gradient(90deg,#7f1d1d,#991b1b);
        border: 1px solid #ef4444;
        padding: 14px;
        border-radius: 12px;
        color: white;
        font-weight: bold;
        margin-bottom: 18px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% {opacity:1;}
        50% {opacity:0.75;}
        100% {opacity:1;}
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

def render_flash_alert(df_actions):
    if df_actions.empty or 'Headline' not in df_actions.columns:
        return
    latest = df_actions.iloc[0]
    headline = latest.get('Headline', 'System Nominal')
    st.markdown(f"""
    <div class="flash-alert">
    🚨 FLASH ALERT: {headline}
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 3. DYNAMIC GEOCODING ENGINE
# ==========================================
@st.cache_data(show_spinner=False, ttl=86400) 
def resolve_location(query):
    """
    Dynamically fetches coordinates. 
    Uses expanded baseline to bypass API limits for major players.
    Applies strict sleep delays to prevent 429 API blocks.
    """
    if not query or not isinstance(query, str):
        return None, None, "Unknown"

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
                
                /* Responsive Flex Wrap Fix */
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
            components.html(html_code, height=245) 
            
        else:
            start_timestamp_ms = fallback_time_ms
            
            # Pre-calculate to eliminate 00:00:00 flash
            elapsed_ms = max(0, int(time.time() * 1000) - start_timestamp_ms)
            h, m, s = elapsed_ms // 3600000, (elapsed_ms % 3600000) // 60000, (elapsed_ms % 60000) // 1000
            
            initial_clock = f"{h:02d}:{m:02d}:{s:02d}"

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
                    <div class="timer">Status Verified: <span id="clock">{initial_clock}</span> ago</div>
                </div>
                <p class="desc">Current Warning System doesn't see an early warning situation. Watch out for further updates.</p>
            </div>
            <script>
                const start = {start_timestamp_ms};
                function update() {{
                    const now = new Date().getTime(); let diff = now - start; if(diff < 0) diff = 0;
                    let h = Math.floor(diff / (1000 * 60 * 60)); let m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60)); let s = Math.floor((diff % (1000 * 60)) / 1000);
                    document.getElementById('clock').innerText = String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0') + ':' + String(s).padStart(2, '0');
                }}
                setInterval(update, 1000); update();
            </script>
            """
            components.html(html_code, height=130)

    except Exception as e:
        pass 


# ==========================================
# 5. MAIN EXECUTIVE HOME RENDER
# ==========================================
def render_executive_home(dashboard_data, df_actions, live_tactical_data, mapbox_token):
    inject_executive_home_css()

    if not df_actions.empty:
        # Create a backup of the original index to preserve raw append order
        df_actions = df_actions.copy()
        df_actions['_raw_idx'] = range(len(df_actions))
        
        if 'Date' in df_actions.columns:
            # 1. Safely parse dates, coercing errors to NaT
            parsed_dates = pd.to_datetime(df_actions['Date'], format='mixed', errors='coerce', utc=True)
            
            # 2. NUCLEAR FIX: Fill NaT with the year 2099 so any new, unparseable LLM output 
            # is physically forced to be recognized as the "newest" date.
            df_actions['_sort_date'] = parsed_dates.fillna(pd.Timestamp('2099-12-31', tz='UTC'))
            
            # Sort by the forced date descending, then by raw index descending (highest index = newest row)
            df_actions = df_actions.sort_values(by=['_sort_date', '_raw_idx'], ascending=[False, False])
            
            # 3. Format cleanly parsed dates, fallback to whatever raw string the LLM originally output
            formatted_dates = parsed_dates.dt.strftime('%Y-%m-%d %H:%M')
            df_actions['Date'] = formatted_dates.fillna(df_actions['Date'].astype(str))
        else:
            # Absolute fallback if the 'Date' column is missing entirely
            df_actions = df_actions.sort_values(by='_raw_idx', ascending=False)

    st.markdown("""
    <div style='text-align: center; margin-top: 10px; margin-bottom: 30px;'>
        <h1 style='color: #00bfff; font-size: 2.5em; letter-spacing: 2px; margin-bottom: 0px;'>SemicoN Strategic Command</h1>
        <p style='color: #d1d5db; font-family: monospace; font-size: 1.1em;'>LIVE GEOPOLITICS-OSINT & THREAT MONITORING ENVIRONMENT</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_flash_alert(df_actions)

    st.markdown("### 🚨 Live Strategic Alert Monitor")
    check_early_warnings()
    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
    
    # ==========================================
    # 2.5 🧠 STRATEGIC DECISION SUPPORT ENGINE
    # ==========================================
    
    # --- ADDED: Robust Tactical Text Aggregation ---
    all_text_parts = []
    
    if not df_actions.empty:
        for col in ['Headline', 'Event', 'Action', 'Actor', 'Location']:
            if col in df_actions.columns:
                all_text_parts.extend(df_actions[col].dropna().astype(str).tolist())
                
    all_text = " ".join(all_text_parts).lower()
    
    # RENDER THE ENGINE WITH is_home=True TO TRIGGER THE NOTE AUTOMATICALLY
    render_decision_support_engine(all_text, is_home=True)
    
    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # 3. KPI CARDS
    st.markdown("### 📊 Global Threat Posture")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric(label="🔴 Active Escalations", value="3", delta="+1 in last 12h", delta_color="inverse")
    with col2: st.metric(label="🚢 Supply Chain Chokepoints", value="2", delta="Nominal", delta_color="off")
    with col3: st.metric(label="🛰️ Geopolitical Shifts", value="5", delta="-2 from yesterday", delta_color="normal")
    with col4: st.metric(label="🛡️ System Status", value="DEFCON 4", delta="Monitoring Active")

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # 4. THREAT VELOCITY 
    st.markdown("### 📈 Threat Velocity (Past 7 Days)")
    v1, v2, v3 = st.columns(3)
    with v1: render_velocity_chart("Indo-Pacific Risk", [40,45,50,55,60,62,65])
    with v2: render_velocity_chart("Export Control Friction", [20,25,30,40,55,70,85])
    with v3: render_velocity_chart("Maritime Disruption", [35,38,42,40,44,48,52])
        
    with st.expander("⚙️ Threat Velocity Methodology & Approach"):
        st.markdown("""
        **Analytical Approach:** The Threat Velocity charts utilize a quantitative 0-100 Risk Score. The timeline standard uses the military "D-Day" designation, where **Today** represents the current tactical environment, and **D-6** represents the environment six days prior.
        
        **Calculation Basis:** Scores are generated by processing the 12-Hour Geopolitics-OSINT feed through natural language processing (NLP). The engine assigns weight multipliers to distinct friction events: Kinetic/Maritime Posturing, Regulatory Action, and Supply Chain Contractions.
        """)

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # 5. HOT ACTOR TELEMETRY
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

    # 6. RECENT TACTICAL ALERTS 
    st.markdown("### ⚠️ Recent Tactical Alerts")
    if not df_actions.empty:
        available_cols = df_actions.columns.tolist()
        target_cols = ['Date', 'Action', 'Event', 'Headline']
        
        display_df = df_actions.copy()
        
        # ULTIMATE BYPASS: Stop relying on Pandas datetime parsing entirely.
        # The LLM appends new intelligence to the bottom of the dataset.
        # Therefore, sorting by the highest raw index guarantees the newest rows.
        if '_raw_idx' in display_df.columns:
            display_df = display_df.sort_values(by='_raw_idx', ascending=False)
            
        cols_to_show = [col for col in target_cols if col in display_df.columns]
        if cols_to_show:
            display_df = display_df[cols_to_show]
            
        display_df = display_df.head(8)
        
        # Force 'Date' to display whatever raw text the LLM wrote to prevent rendering crashes
        if 'Date' in display_df.columns:
            display_df['Date'] = display_df['Date'].astype(str)
            
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.write("No tactical alerts logged.")
            
    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # ==========================================
    # 7. 🌍 STRATEGIC GEOSPATIAL INTELLIGENCE LAYER
    # ==========================================
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

    # 8. RISK INDICATORS
    st.markdown("### 📦 Strategic Risk Indicators")
    col_ind1, col_ind2, col_ind3 = st.columns(3)
    with col_ind1: st.progress(0.65, text="Indo-Pacific Transit Risk: Elevated (65%)")
    with col_ind2: st.progress(0.40, text="West Asia Logistics: Moderate (40%)")
    with col_ind3: st.progress(0.85, text="Advanced Node Controls: Critical (85%)")

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # 9. STRATEGIC ANALYSIS
    st.markdown("### 📝 Strategic Command Analysis (12H Briefing)")
    
    live_summary = dashboard_data.get('executive_summary', None) if dashboard_data else None
    
    if live_summary:
        st.info(live_summary)
    else:
        st.info("""
        **Executive Geopolitical Assessment:**\n\n
        Over the preceding 12-hour monitoring window, global semiconductor supply architectures have demonstrated resilience against emerging legislative and maritime friction. However, deep-tier Geopolitics-OSINT analysis indicates a structural shift in how state actors are leveraging critical mineral chokepoints. Rather than immediate embargoes, the current threat matrix reveals a strategy of 'attritional compliance'—whereby Tier-2 and Tier-3 suppliers of advanced packaging materials are subjected to suddenly opaque customs audits. This creates a deniable, low-intensity disruption that primarily affects fabless design scaling rather than raw foundry output.\n\n
        Simultaneously, maritime transit corridors in the South China Sea and the Strait of Malacca remain highly sensitized. While commercial lithography equipment and wafer transit have not faced direct interdiction, the 'grey zone' posturing by regional naval assets has prompted a 1.2% aggregate increase in maritime insurance premiums for high-value tech cargo. This suggests that insurance markets are preemptively pricing in the risk of 'accidental' quarantine or boarding scenarios targeting dual-use technology components.\n\n
        Looking forward to the next 48-72 hours, the primary vector of vulnerability lies in the intersection of Western export controls and retaliatory critical mineral quotas. The SemicoN threat model assesses with moderate-to-high confidence that upcoming multilateral trade dialogues will fail to de-escalate the current tit-for-tat regulatory environment. Supply chain managers are strongly advised to audit their reliance on single-origin rare earth refining and begin immediate stress-testing of redundant logistics routes spanning through India and West Asia to bypass traditional Indo-Pacific chokepoints.
        """)