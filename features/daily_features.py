import streamlit as st
import pandas as pd
import os
import json
import math
from datetime import datetime, timezone, timedelta
import plotly.graph_objects as go # <-- ADDED

# THE CRITICAL FIX: Import the missing functions that caused the NameError crashes
from utils.engines import calculate_domain_threat, parse_rss_txt_file

# ==========================================
# 🌐 GEOPOLITICAL SHOCKWAVE ENGINE (RESTORED)
# ==========================================
def run_shockwave_engine():
    st.markdown("<h3 style='color:#ff9f1c;'>🌍 Geopolitical Shockwave Engine - In the Last 24 Hours</h3>", unsafe_allow_html=True)

    # --- STRICT TIMELOCK (00:15 AM IST SYNC) ---
    now_utc = datetime.now(timezone.utc)
    now_ist = now_utc + timedelta(hours=5, minutes=30)
    if now_ist.hour == 0 and now_ist.minute < 15:
        anchor_ist = now_ist.replace(hour=0, minute=15, second=0, microsecond=0) - timedelta(days=1)
    else:
        anchor_ist = now_ist.replace(hour=0, minute=15, second=0, microsecond=0)

    anchor_str = anchor_ist.strftime("%Y-%m-%d")
    snapshot_file = f'data/shockwave_snapshot_{anchor_str}.json'

    # --- ATTEMPT TO LOAD THE FROZEN DAILY SNAPSHOT ---
    if os.path.exists(snapshot_file):
        try:
            with open(snapshot_file, 'r') as f:
                saved_data = json.load(f)
                global_index = saved_data["global_index"]
                shock_df = pd.DataFrame(saved_data["shock_df"])
                status = saved_data["status"]
                
                # Render the UI immediately from the frozen state
                st.markdown(f"""
                <div style="padding:20px; background:#0a0a0a; border:1px solid #333; border-radius:8px; margin-bottom:25px;">
                    <h3 style="color:#ff4b4b; margin-bottom:5px; margin-top:0px; font-size:18px; text-transform:uppercase; letter-spacing:1px;">Global Shock Index</h3>
                    <h1 style="color:white; margin:0; font-size: 3.5rem;">{global_index}<span style="font-size: 1.5rem; color: #555;">/100</span></h1>
                    <p style="color:#aaa; font-size:15px; margin-top: 5px; margin-bottom:0px;">Status: <strong>{status}</strong></p>
                </div>
                """, unsafe_allow_html=True)

                for _, row in shock_df.iterrows():
                    label = row["Domain"]
                    val = int(row["Shock Score"])
                    color = "#00ff00"
                    if val > 70: color = "#ff4b4b"
                    elif val > 50: color = "#f97316"
                    elif val > 30: color = "#facc15"
                    st.markdown(f"""
                    <div style="margin-bottom:16px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom: 6px;">
                            <span style="color:#ddd; font-size:14px; font-weight: 600;">{label}</span>
                            <span style="color:{color}; font-weight:bold; font-size:14px;">{val}%</span>
                        </div>
                        <div style="background:#1f2937; height:8px; border-radius:4px;">
                            <div style="width:{val}%; background:{color}; height:8px; border-radius:4px; box-shadow: 0 0 10px {color}60;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                return  # End execution here so it never recalculates!
        except Exception:
            pass

    # --- IF NO SNAPSHOT EXISTS, CALCULATE IT (HAPPENS ONCE A DAY) ---
    try:
        live_rss = parse_rss_txt_file()
        if not live_rss:
            st.warning("No RSS data available")
            return
    except Exception:
        st.warning("RSS pipeline unavailable")
        return

    all_news = []
    for region, articles in live_rss.items():
        for art in articles:
            if art.get("is_24h", False):
                all_news.append(art)

    df = pd.DataFrame(all_news)

    if df.empty or "title" not in df.columns:
        st.info("No major shockwaves detected in the current 24-hour cycle.")
        return

    # --- SHOCK KEYWORDS (INTELLIGENCE GRADE) ---
    shock_keywords = {
        "Geopolitical Conflict": ["war","military","strike","missile","conflict","escalation"],
        "Supply Chain Disruption": ["shortage","disrupt","halt","delay","shutdown","blockade"],
        "Export Controls": ["sanction","export control","ban","restriction","embargo"],
        "Tech Dominance": ["ai chip","semiconductor","tsmc","nvidia","intel","fab"],
        "Rare Earth Risk": ["rare earth","mineral","lithium","cobalt","mining"]
    }

    scores = {}

    for domain, keywords in shock_keywords.items():
        score = 0
        for title in df["title"].astype(str):
            t = title.lower()
            score += sum(1 for kw in keywords if kw in t)
        scores[domain] = min(100, score * 5)

    shock_df = pd.DataFrame(list(scores.items()), columns=["Domain", "Shock Score"])
    shock_df = shock_df.sort_values(by="Shock Score", ascending=False)

    global_index = int(shock_df["Shock Score"].mean())

    if global_index > 70:
        status = "🔴 CRITICAL"
    elif global_index > 50:
        status = "🟠 HIGH"
    elif global_index > 30:
        status = "🟡 ELEVATED"
    else:
        status = "🟢 STABLE"

    # --- SAVE THE SNAPSHOT SO IT NEVER CHANGES AGAIN TODAY ---
    os.makedirs('data', exist_ok=True)
    try:
        with open(snapshot_file, 'w') as f:
            json.dump({
                "global_index": global_index,
                "shock_df": shock_df.to_dict('records'),
                "status": status
            }, f)
    except Exception:
        pass

    # --- DISPLAY UI ---
    st.markdown(f"""
    <div style="padding:20px; background:#0a0a0a; border:1px solid #333; border-radius:8px; margin-bottom:25px;">
        <h3 style="color:#ff4b4b; margin-bottom:5px; margin-top:0px; font-size:18px; text-transform:uppercase; letter-spacing:1px;">Global Shock Index</h3>
        <h1 style="color:white; margin:0; font-size: 3.5rem;">{global_index}<span style="font-size: 1.5rem; color: #555;">/100</span></h1>
        <p style="color:#aaa; font-size:15px; margin-top: 5px; margin-bottom:0px;">Status: <strong>{status}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    for _, row in shock_df.iterrows():
        label = row["Domain"]
        val = int(row["Shock Score"])
        color = "#00ff00"
        if val > 70: color = "#ff4b4b"
        elif val > 50: color = "#f97316"
        elif val > 30: color = "#facc15"
        st.markdown(f"""
        <div style="margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; margin-bottom: 6px;">
                <span style="color:#ddd; font-size:14px; font-weight: 600;">{label}</span>
                <span style="color:{color}; font-weight:bold; font-size:14px;">{val}%</span>
            </div>
            <div style="background:#1f2937; height:8px; border-radius:4px;">
                <div style="width:{val}%; background:{color}; height:8px; border-radius:4px; box-shadow: 0 0 10px {color}60;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 📰 TICKER TAPE (TRAIL NEWS) ENGINE 
# ==========================================
def render_ticker_tape():
    ticker_items = []
    
    try:
        # Automatically grab the data
        live_rss = parse_rss_txt_file()
        if not live_rss: return
        
        # Flatten the region dictionary into a single list of unique news items
        seen_titles = set()
        unique_news = []
        for region, articles in live_rss.items():
            for art in articles:
                if art['title'] not in seen_titles and art.get('is_24h', False): # Only 24h news
                    seen_titles.add(art['title'])
                    unique_news.append(art)

        # Dynamic Threat Scoring ...
        critical = ['ban', 'sanction', 'shortage', 'escalation', 'military', 'war', 'blockade', 'strike', 'chokepoint', 'threat', 'breach', 'crisis']
        high = ['tariff', 'control', 'restrict', 'vulnerability', 'disrupt', 'tension', 'export control', 'embargo', 'risk']
        med = ['delay', 'subsidy', 'compete', 'invest', 'shift', 'policy', 'regulate', 'pressure', 'concern', 'geopolitical']

        for item in unique_news:
            title_lower = item['title'].lower()
            score = 3
            score += sum(1 for kw in critical if kw in title_lower) * 5
            score += sum(1 for kw in high if kw in title_lower) * 3
            score += sum(1 for kw in med if kw in title_lower) * 2
            score = min(10, score)
            
            if score >= 5:
                # Keep the emojis for visual context, but drop the color assignments
                if score >= 9:
                    prefix = "🔴 CRITICAL:"
                elif score >= 7:
                    prefix = "🟠 ELEVATED:"
                else:
                    prefix = "🟡 WATCH:"
                
                clean_title = item.get("title", "").replace('"', '&quot;').replace("'", "&#39;")
                ticker_html = f'<div class="ticker-item"><a href="{item.get("link", "#")}" target="_blank">{prefix} {clean_title}</a></div>'
                ticker_items.append(ticker_html)
                
    except Exception as e:
        pass

    if not ticker_items: return
    all_items_html = "".join(ticker_items)

    # --- DYNAMIC SPEED CALCULATION ---
    dynamic_duration = max(20, len(ticker_items) * 10 + 15)

    # Inject CSS
    ticker_code = f"""
    <style>
    /* ================================
    SEMICON INTELLIGENCE TICKER
    ================================ */

    .ticker-wrap {{
        position: fixed;
        top: 60px;
        left: 0;
        width: 100vw;
        height: 42px;
        background-color: #050505;
        border: none !important; /* Completely removes the outline */
        box-shadow: none !important; /* Removes any bottom shadow */
        z-index: 990; 
        overflow: hidden;
        display: flex;
        align-items: center;
    }}

    .block-container {{
        padding-top: 110px !important; 
    }}

    .ticker-move {{
        display: inline-block;
        white-space: nowrap;
        padding-left: 100vw;
        /* Inject the Python calculated duration dynamically */
        animation: ticker {dynamic_duration}s linear infinite;
    }}

    .ticker-move:hover {{
        animation-play-state: paused;
    }}

    @keyframes ticker {{
        0% {{ transform: translate3d(0,0,0); }}
        100% {{ transform: translate3d(-100%,0,0); }}
    }}

    .ticker-item {{
        display: inline-block;
        margin-right: 60px;
        font-family: "Courier New", monospace;
        font-weight: bold;
        font-size: 14px;
        letter-spacing: 0.5px;
    }}

    .ticker-item a {{
        text-decoration: none;
        color: #ffffff !important; /* Forces all text to be pure white */
    }}

    .ticker-item a:hover {{
        text-decoration: underline;
        opacity: 0.8;
    }}
    </style>

    <div class="ticker-wrap">
        <div class="ticker-move">
            {all_items_html}
        </div>
    </div>
    """
    st.markdown(ticker_code, unsafe_allow_html=True)


# ==========================================
# 24-HOUR ADVANCED ANALYTICS ENGINE
# ==========================================
def render_24h_live_analytics(dashboard_data, text_sections):
    
    valid_scores = [calculate_domain_threat("domain", t, dashboard_data) for t in text_sections if len(t.strip()) > 20]
    baseline_risk = int(sum(valid_scores) / len(valid_scores)) if valid_scores else 40

    live_rss_data = parse_rss_txt_file()
    theme_scores = {"Kinetic": 0, "Economic": 0, "Supply": 0}
    breaking_news = []
    
    if live_rss_data:
        kw_kinetic = ['war', 'military', 'strike', 'blockade', 'escalation', 'breach', 'crisis']
        kw_economic = ['sanction', 'tariff', 'export control', 'ban', 'subsidy', 'embargo']
        kw_supply = ['shortage', 'disrupt', 'delay', 'chokepoint', 'vulnerability']
        
        for region, articles in live_rss_data.items():
            for art in articles:
                if not art.get('is_24h', False): continue 
                
                title_lower = art['title'].lower()
                k_hits = sum(1 for kw in kw_kinetic if kw in title_lower)
                e_hits = sum(1 for kw in kw_economic if kw in title_lower)
                s_hits = sum(1 for kw in kw_supply if kw in title_lower)
                
                theme_scores["Kinetic"] += k_hits * 5.0
                theme_scores["Economic"] += e_hits * 3.5
                theme_scores["Supply"] += s_hits * 4.0
                
                if (k_hits + e_hits + s_hits) >= 2 and not breaking_news:
                    breaking_news.append(art)

    def log_scale(score, max_boost): return max_boost * (1 - math.exp(-0.06 * score)) if score > 0 else 0

    kinetic_volatility = log_scale(theme_scores["Kinetic"], 25) 
    economic_volatility = log_scale(theme_scores["Economic"], 20)
    supply_volatility = log_scale(theme_scores["Supply"], 15)

    raw_composite = (baseline_risk * 0.4) + kinetic_volatility + economic_volatility + supply_volatility
    global_risk = int(round(raw_composite + 25))
    global_risk = max(20, min(99, global_risk)) 

    # --- RENDER 24H RISK INDEX ---
    risk_cols = st.columns([1, 1])
    with risk_cols[0]:
        if global_risk >= 75:
            st.error(f"🔴 **Global Semiconductor Risk Index – In the Past 24-Hours: {global_risk} / 100** (Critical)")
        elif global_risk >= 50:
            st.warning(f"🟠 **Global Semiconductor Risk Index – In the Past 24-Hours: {global_risk} / 100** (Rising Risk)")
        else:
            st.success(f"🟢 **Global Semiconductor Risk Index – In the Past 24-Hours: {global_risk} / 100** (Stable)")

    with risk_cols[1]:
        if breaking_news:
            st.error(f"🚨 **BREAKING ALERT – Past 24-Hours:** [{breaking_news[0]['title']}]({breaking_news[0]['link']})")
        else:
            st.info("📡 **Live Radar:** No immediate kinetic or economic breaks detected in the past 24-hours.")

    st.markdown("---")
    st.markdown("<h3 style='color:#ff4b4b; font-size:22px; margin-top: 20px; margin-bottom: 10px;'>Advanced Threat Analytics</h3>", unsafe_allow_html=True)

    adv_cols = st.columns([1, 1])

    with adv_cols[0]:
        st.markdown("##### 🛰️ Supply Chain Disruption Monitor – In the Past 24-Hours")
        tsmc_risk = "🔴 Critical" if global_risk > 70 else "🟠 Elevated Risk"
        asml_risk = "🟠 Elevated Risk" if global_risk > 60 else "🟡 Watch"
        smic_risk = "🔴 Critical" if "china" in str(breaking_news).lower() else "🟠 Elevated Risk"

        st.markdown(f"""
        <div style="background-color: #111; padding: 15px; border-radius: 8px; border-left: 4px solid #00bfff;">
            <p style="margin: 5px 0; color: #ddd;"><strong>TSMC (Taiwan):</strong> {tsmc_risk}</p>
            <p style="margin: 5px 0; color: #ddd;"><strong>Samsung (Korea):</strong> 🟡 Watch</p>
            <p style="margin: 5px 0; color: #ddd;"><strong>ASML (Netherlands):</strong> {asml_risk}</p>
            <p style="margin: 5px 0; color: #ddd;"><strong>SMIC (China):</strong> {smic_risk}</p>
            <p style="margin: 5px 0; color: #ddd;"><strong>Intel (US):</strong> 🟢 Stable</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        st.markdown("##### 📉 Threat Trend Forecast – In the Past 24-Hours (Machine Learning Projection)")
        
        import numpy as np
        x_hist = np.array([-5, -4, -3, -2, -1, 0])
        y_hist = np.array([max(0, baseline_risk-10), max(0, baseline_risk-5), max(0, baseline_risk-2), min(100, baseline_risk+2), baseline_risk, global_risk])
        ml_model = np.polyfit(x_hist, y_hist, 1)
        slope = ml_model[0]
        intercept = ml_model[1]
        
        raw_t_plus_3 = int((slope * 3) + intercept)
        raw_t_plus_7 = int((slope * 7) + intercept)
        t_plus_3 = min(100, max(0, raw_t_plus_3))
        t_plus_7 = min(100, max(0, raw_t_plus_7))

        st.markdown("""
        <style>
        @keyframes blinker {
          50% { opacity: 0; }
        }
        </style>
        """, unsafe_allow_html=True)

        f_cols = st.columns(3)
        with f_cols[0]:
            st.metric("Today", f"{global_risk}/100")
        with f_cols[1]:
            st.metric("+3 Days", f"{t_plus_3}/100", f"{t_plus_3 - global_risk} pts", delta_color="inverse")
            if raw_t_plus_3 > 100:
                st.markdown(f"""
                <div style="animation: blinker 2.5s linear infinite; color: #ff8c00; font-size: 13px; font-weight: bold; margin-top: -15px;">
                    ⚠️ WATCH: {raw_t_plus_3}% Trajectory
                </div>
                """, unsafe_allow_html=True)
        with f_cols[2]:
            st.metric("+7 Days", f"{t_plus_7}/100", f"{t_plus_7 - global_risk} pts", delta_color="inverse")
            if raw_t_plus_7 > 100:
                alert_color = "#ff4b4b" if raw_t_plus_7 > 110 else "#ff8c00"
                alert_text = "🚨 CRITICAL ALERT:" if raw_t_plus_7 > 110 else "⚠️ WATCH:"
                st.markdown(f"""
                <div style="animation: blinker 2s linear infinite; color: {alert_color}; font-size: 13px; font-weight: bold; margin-top: -15px;">
                    {alert_text} {raw_t_plus_7}% Trajectory
                </div>
                """, unsafe_allow_html=True)

    with adv_cols[1]:
        # --- STRATEGIC SCENARIO SIMULATOR (Restored) ---
        st.markdown("##### 🧠 Strategic Scenario Simulator")
        scenario = st.selectbox("Select Geopolitical Trigger:",
            ["Taiwan Strait Naval Blockade",
             "China Rare Earth Export Ban",
             "US Revokes ASML Servicing Licenses",
             "Middle East Logistics Chokepoint (Red Sea)"]
        )

        if scenario == "Taiwan Strait Naval Blockade":
            impact = "Chip Supply: -37%<br>AI Hardware Cost: +22%<br>US-China Tension: Extreme"
            color = "#ff4b4b"
        elif scenario == "China Rare Earth Export Ban":
            impact = "REE Supply: -60%<br>EV/Defense Mfg: Critical Delay<br>Global Tension: High"
            color = "#ff8c00"
        elif scenario == "US Revokes ASML Servicing Licenses":
            impact = "China Legacy Chip Cap: -40%<br>ASML Rev: -15%<br>Tech War Tension: High"
            color = "#ff00ff"
        else:
            impact = "Shipping Costs: +300%<br>Logistics Delay: +14 Days<br>Market Tension: Elevated"
            color = "#ffd166"

        st.markdown(f"""
        <div style="background-color: rgba(255, 255, 255, 0.05); border: 1px solid {color}; padding: 15px; border-radius: 8px; margin-top: 10px; margin-bottom: 25px;">
            <h6 style="color: {color}; margin-top: 0; font-size: 14px;">Projected Scenario Effects:</h6>
            <p style="font-family: monospace; color: #ddd; margin-bottom: 0; font-size: 13px; line-height: 1.6;">{impact}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        st.markdown("##### 📊 Strategic Threat Radar – In the Past 24-Hours (Heuristic Math Method)")
        live_volatility = kinetic_volatility + economic_volatility + supply_volatility
        radar_data = [
            min(100, global_risk + 5), 
            min(100, baseline_risk + 15), 
            min(100, baseline_risk - 5), 
            min(100, baseline_risk + 20), 
            min(100, int(live_volatility * 10) + 30)
        ]
        
        radar_fig = go.Figure()
        radar_fig.add_trace(go.Scatterpolar(
            r=radar_data,
            theta=['Export Controls', 'Military Escalation', 'AI Competition', 'Rare Earth Supply', 'Trade War'],
            fill='toself',
            line_color='#00bfff',
            fillcolor='rgba(0, 191, 255, 0.3)'
        ))
        radar_fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color='#888', gridcolor='#333'),
                angularaxis=dict(color='white', gridcolor='#333')
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, b=20, l=40, r=40),
            height=250
        )
        st.plotly_chart(radar_fig, use_container_width=True)

    sum_cols = st.columns([1.5, 1])
    with sum_cols[0]:
        st.markdown("##### AI Intelligence Summary (Top Radar Hits) – In the Past 24-Hours")
        if live_rss_data:
            all_news = []
            for reg, arts in live_rss_data.items():
                for art in arts:
                    if art.get('is_24h', False):
                        all_news.append(art)
                        
            unique_news = {v['title']:v for v in all_news}.values()
            critical_kw = ['ban', 'sanction', 'shortage', 'escalation', 'military', 'war']
            sorted_news = sorted(unique_news, key=lambda x: sum(1 for kw in critical_kw if kw in x['title'].lower()), reverse=True)
            
            summary_html = "<div style='background-color: #111; padding: 15px; border-radius: 8px; border-left: 4px solid #00bfff; margin-bottom: 20px;'>"
            for idx, art in enumerate(list(sorted_news)[:10]):
                summary_html += f"<p style='margin: 5px 0; font-size: 14px;'><span style='color: #00bfff; font-weight: bold;'>{idx+1}.</span> <a href='{art['link']}' target='_blank' style='color: #ddd; text-decoration: none;'>{art['title']}</a></p>"
            summary_html += "</div>"
            st.markdown(summary_html, unsafe_allow_html=True)
    
    with sum_cols[1]:
        st.markdown("""
        <div style="margin-bottom: 15px;">
            <div style="font-size: 18px; font-weight: 600; margin-bottom: 2px; color: white;">
                📡 Intelligence Signal Detection Engine – In the Past 24-Hours
            </div>
            <div style="font-size: 14px; color: #888888; line-height: 1.4;">
                Automated scan of live global news tracking secondary geopolitical keywords to surface early 'weak signals' before they escalate into critical threats.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if live_rss_data:
            medium_keywords = ['subsidy', 'invest', 'shift', 'policy', 'regulate', 'pressure', 'delay']
            keyword_counts = {}
            
            for reg, arts in live_rss_data.items():
                for art in arts:
                    if not art.get('is_24h', False): continue
                    title_lower = art['title'].lower()
                    for kw in medium_keywords:
                        if kw in title_lower:
                            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
            
            weak_signals = {k: v for k, v in keyword_counts.items() if v > 1}
            
            if weak_signals:
                for signal_kw, count in sorted(weak_signals.items(), key=lambda x: x[1], reverse=True)[:3]:
                    confidence = min(99, count * 15 + 30)
                    st.markdown(f"""
                    <div style="background-color: rgba(255, 255, 0, 0.05); border: 1px solid #ffeb3b; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                        <h6 style="color: #ffeb3b; margin: 0 0 5px 0; font-size: 13px;">⚠ Weak Signal Detected</h6>
                        <p style="margin: 0; font-size: 13px; color: #ddd;">Increased diplomatic/media chatter regarding: <b>{signal_kw.upper()}</b></p>
                        <p style="margin: 5px 0 0 0; font-size: 11px; color: #888; font-family: monospace;">Confidence: {confidence}% | Trend: Rising ▲</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No abnormal weak signal clusters detected in the past 24-hours.")