import streamlit as st
import json
import os
import glob
from utils.snippet_docx_generator import generate_weekly_tactical_docx  # Utilizing the existing Docx generator for downloads

def render_west_asia_weekly_brief(archived_data=None, brief_title=None):
    
    st.markdown("""
    <style>
    .wa-gradient-box { padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); line-height: 1.6; font-size: 1.05em; }
    .wa-box-bluf { background: linear-gradient(135deg, #1e3a8a 0%, #1e1b4b 100%); border-left: 5px solid #3b82f6; color: #e0e7ff; }
    .wa-box-forecast { background: linear-gradient(135deg, #064e3b 0%, #022c22 100%); border-left: 5px solid #10b981; color: #d1fae5; }
    .wa-box-standard { background: linear-gradient(135deg, #18181b 0%, #0f172a 100%); border-left: 4px solid #a855f7; color: #cbd5e1; height: 100%; }
    .wa-header { color: #ffffff; margin-top: 0; font-size: 1.25em; font-family: 'Courier New', monospace; letter-spacing: 1px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 15px;}
    </style>
    """, unsafe_allow_html=True)

    # If accessed live, get the latest. If accessed from archives, use the passed data.
    data = archived_data
    if not data:
        files = glob.glob('data/west_asia/west_asia_brief_*.json')
        if files:
            files.sort(key=os.path.getmtime)
            try:
                with open(files[-1], 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except: data = {}
        else:
            st.warning("📡 Standby: Weekly West Asia Brief pipeline has not yet completed its first Sunday extraction cycle.")
            return

    date_range = data.get('date_range', 'Recent Cycle')
    title_str = brief_title if brief_title else f"West Asia In This Week - {date_range}"
    
    st.markdown(f"<h1 style='color: #00bfff; letter-spacing: 1px; text-transform: uppercase;'>{title_str}</h1>", unsafe_allow_html=True)
    st.caption(f"Synthesized from {data.get('event_volume', '150+')} Trafilatura-enhanced raw intelligence nodes gathered via Psyopoly.")
    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # ROW 1: BLUF & Strategic Forecast (Full Width / Split)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="wa-gradient-box wa-box-bluf"><div class="wa-header">🎯 BLUF</div>{data.get("bluf", "Data unavailable.")}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="wa-gradient-box wa-box-forecast"><div class="wa-header">🔭 STRATEGIC FORECAST</div>{data.get("strategic_forecast", "Data unavailable.")}</div>', unsafe_allow_html=True)

    # ROW 2: Exec & Escalation
    r2c1, r2c2 = st.columns(2)
    with r2c1: st.markdown(f'<div class="wa-gradient-box wa-box-standard"><div class="wa-header">📋 EXECUTIVE SUMMARY</div>{data.get("executive_summary", "Data unavailable.")}</div>', unsafe_allow_html=True)
    with r2c2: st.markdown(f'<div class="wa-gradient-box wa-box-standard"><div class="wa-header">📈 ESCALATION INDICATORS</div>{data.get("escalation_indicators", "Data unavailable.")}</div>', unsafe_allow_html=True)

    # ROW 3: Iran & Levant
    r3c1, r3c2 = st.columns(2)
    with r3c1: st.markdown(f'<div class="wa-gradient-box wa-box-standard"><div class="wa-header">🇮🇷 IRANO-CENTRIC NETWORK AXIS</div>{data.get("irano_centric_axis", "Data unavailable.")}</div>', unsafe_allow_html=True)
    with r3c2: st.markdown(f'<div class="wa-gradient-box wa-box-standard"><div class="wa-header">🇱🇧 LEVANTINE OPERATIONAL FRONT</div>{data.get("levantine_front", "Data unavailable.")}</div>', unsafe_allow_html=True)

    # ROW 4: Israel & GCC
    r4c1, r4c2 = st.columns(2)
    with r4c1: st.markdown(f'<div class="wa-gradient-box wa-box-standard"><div class="wa-header">🇮🇱 ISRAELI MULTI-THEATER STRATEGY</div>{data.get("israeli_strategy", "Data unavailable.")}</div>', unsafe_allow_html=True)
    with r4c2: st.markdown(f'<div class="wa-gradient-box wa-box-standard"><div class="wa-header">🛢️ GCC REGION AND DEVELOPMENT</div>{data.get("gcc_region", "Data unavailable.")}</div>', unsafe_allow_html=True)

    # ROW 5: Threat & Risk
    r5c1, r5c2 = st.columns(2)
    with r5c1: st.markdown(f'<div class="wa-gradient-box wa-box-standard"><div class="wa-header">🕸️ THREAT NARRATIVE</div>{data.get("threat_narrative", "Data unavailable.")}</div>', unsafe_allow_html=True)
    with r5c2: st.markdown(f'<div class="wa-gradient-box wa-box-standard"><div class="wa-header">⚖️ RISK ASSESSMENT</div>{data.get("risk_assessment", "Data unavailable.")}</div>', unsafe_allow_html=True)

    # ROW 6: Intel Log & Tactical
    r6c1, r6c2 = st.columns(2)
    with r6c1: st.markdown(f'<div class="wa-gradient-box wa-box-standard"><div class="wa-header">📂 STRATEGIC INTELLIGENCE LOG</div>{data.get("strategic_intel_log", "Data unavailable.")}</div>', unsafe_allow_html=True)
    with r6c2: st.markdown(f'<div class="wa-gradient-box wa-box-standard"><div class="wa-header">🚩 TACTICAL INDICATOR</div>{data.get("tactical_indicators", "Data unavailable.")}</div>', unsafe_allow_html=True)

    # Publisher URLs
    st.markdown("### 🔗 Themed Source Intelligence")
    urls = data.get("themed_urls", {})
    if urls:
        for theme, link_list in urls.items():
            if link_list:
                st.markdown(f"**{theme}**")
                for link in link_list:
                    if link.startswith('http'):
                        st.markdown(f"- [{link}]({link})")
    else:
        st.caption("No external reference links compiled for this cycle.")

    # Admin Download Button
    if st.session_state.get('role') == 'admin' and not archived_data:
        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
        colA, colB = st.columns([1, 4])
        with colA:
            # We map this into the existing DOCX generator structure 
            doc_data = {
                "date": data.get("generation_date", "Today"),
                "classification": "CONFIDENTIAL // WEEKLY WEST ASIA",
                "author": "Psyopoly Intelligence Desk",
                "title": title_str,
                "bluf": data.get("bluf", ""),
                "executive_summary": data.get("executive_summary", ""),
                "threat_narrative": data.get("threat_narrative", ""),
                "risk_assessment": data.get("risk_assessment", ""),
                "predictive_analysis": data.get("strategic_forecast", ""),
                "recommendations": data.get("strategic_forecast", ""),
                "tactical_indicators": [data.get("tactical_indicators", "")]
            }
            try:
                docx_buffer = generate_weekly_tactical_docx(doc_data)
                st.download_button(
                    label="📥 Download Brief (DOCX)", 
                    data=docx_buffer, 
                    file_name=f"Weekly_West_Asia_Brief_{data.get('generation_date', 'Export')}.docx", 
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                    type="primary", 
                    use_container_width=True
                )
            except Exception:
                st.button("📥 Download Unavailable", disabled=True, use_container_width=True)