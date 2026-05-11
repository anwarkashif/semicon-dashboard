import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go
from utils.data_helpers import get_brief_mappings, render_highlighted_text
from utils.engines import calculate_domain_threat, parse_rss_txt_file

def render_correlation_engine_weekly():
    st.markdown("### 🧠 Correlation Intelligence Layer (Weekly)")
    try:
        archive_mapping = get_brief_mappings('data')
        if archive_mapping and len(archive_mapping) >= 2:
            files = list(archive_mapping.values())
            with open(files[0], 'r') as f: latest = json.load(f)
            with open(files[1], 'r') as f: prev = json.load(f)

            def extract_domains(data):
                txt = data.get('brief_raw', '').lower()
                return {
                    "AI": txt.count("ai"), "Export": txt.count("export"),
                    "Military": txt.count("military"), "RareEarth": txt.count("rare earth"),
                    "Taiwan": txt.count("taiwan"), "China": txt.count("china"),
                    "US": txt.count("united states") + txt.count("u.s")
                }

            latest_d = extract_domains(latest)
            prev_d = extract_domains(prev)
            weights = {"US": 1.4, "China": 1.4, "Taiwan": 1.3, "Military": 1.5, "Export": 1.3}
            shock_words = ["sanction", "ban", "war", "strike", "export ban", "embargo"]
            shock_flag = any(word in latest.get('brief_raw', '').lower() for word in shock_words)

            correlations = []
            domains = ["AI", "Export", "Military", "RareEarth"]
            
            # FIX: Use index-based loop to prevent duplicate mirrored pairs (e.g., A<->B and B<->A)
            for i in range(len(domains)):
                for j in range(i + 1, len(domains)):
                    d1 = domains[i]
                    d2 = domains[j]
                    delta1 = latest_d[d1] - prev_d[d1]
                    delta2 = latest_d[d2] - prev_d[d2]
                    base_score = abs(delta1 * delta2)
                    weight = weights.get(d1, 1) * weights.get(d2, 1)
                    score = int(base_score * weight)
                    if shock_flag: score = int(score * 1.5)
                    if score > 5: correlations.append((d1, d2, score))

            correlations = sorted(correlations, key=lambda x: x[2], reverse=True)[:6]
            if correlations:
                for c in correlations:
                    d1, d2, score = c
                    
                    # --- NEW COLOR CODING LOGIC ---
                    if score > 750: 
                        color, label = "#ef4444", "CRITICAL LINK"   # Red
                    elif score > 500: 
                        color, label = "#f97316", "STRONG LINK"     # Orange
                    elif score > 200: 
                        color, label = "#facc15", "MODERATE LINK"   # Yellow
                    else: 
                        color, label = "#22c55e", "NOTABLE LINK"    # Green
                    # ------------------------------

                    # Scale properly out of 1000
                    visual_width = min((score / 1000) * 100, 100)

                    st.markdown(f"""
                    <div style="margin-bottom:12px;">
                        <span style="color:{color}; font-weight:bold;">{label} (Score: {score}) → {d1} ↔ {d2}</span>
                        <div style="width:100%; background:#1f2937; height:6px; border-radius:4px;">
                            <div style="width:{visual_width}%; background:{color}; height:6px; border-radius:4px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                if shock_flag:
                    st.warning("⚠️ Shock-trigger detected: correlations amplified due to sanctions / conflict signals.")
            else: st.info("No strong correlations detected this week.")
        else: st.info("Not enough historical data for correlation engine.")
    except Exception as e:
        st.warning("Correlation engine error.")

def render_signal_prioritization_weekly(dashboard_data):
    st.markdown("<h3 style='color:#00ffaa;'>🧠 Strategic Signal Prioritization (Weekly)</h3>", unsafe_allow_html=True)
    signal_scores = {}
    actor_weight = {"us": 1.5, "china": 1.5, "taiwan": 1.4, "eu": 1.2, "india": 1.2, "russia": 1.3}
    shock_keywords = ['sanction', 'ban', 'war', 'military', 'export control', 'embargo']
    
    actions = dashboard_data.get('recent_actions', [])
    if actions:
        for act in actions:
            text = str(act).lower()
            score = 1
    
            if any(k in text for k in ['war','military','conflict','strike']): score += 5
            if any(k in text for k in ['sanction','export','ban','restriction']): score += 4
            if any(k in text for k in ['investment','policy','deal']): score += 2
    
            for actor, weight in actor_weight.items():
                if actor in text: score *= weight
    
            if any(k in text for k in shock_keywords): score *= 1.5
    
            # --- FIX FOR "UNKNOWN EVENT" MEGA-GROUPING ---
            if isinstance(act, dict):
                # Tries to find ANY valid key, falls back to a snippet of the raw dict if missing
                label = act.get("Event") or act.get("Action") or act.get("Description") or act.get("Title")
                if not label:
                    label = f"Strategic Action recorded in {act.get('Location', 'Global Domain')}"
            else:
                label = str(act)[:80] + "..."
    
            signal_scores[label] = signal_scores.get(label, 0) + score
    
        ranked_signals = sorted(signal_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    
        for sig, val in ranked_signals:
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <span style="color:#00ffaa; font-weight:bold;">{sig}</span><br>
                <span style="color:#aaa;">Signal Strength: {int(val)}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # --- TOP 3 GEOPOLITICAL RISKS ---
        st.markdown("<h3 style='color:#ff4b4b; margin-top:25px;'>🚨 Top 3 Geopolitical Risks This Week</h3>", unsafe_allow_html=True)
        top3 = ranked_signals[:3]
        for i, (sig, val) in enumerate(top3, 1):
            risk_level = "Elevated"
            if val > 15: risk_level = "Critical"
            elif val > 10: risk_level = "High"
    
            st.markdown(f"""
            <div style="border-left:4px solid #ff4b4b; padding:10px; margin-bottom:12px; background:rgba(255,75,75,0.05);">
            <b>Risk #{i}: {sig}</b><br>
            Severity: <span style="color:#ff4b4b;">{risk_level}</span><br>
            Intelligence Score: {int(val)}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Not enough data for signal prioritization yet.")

def render_intelligence_assessment_weekly(dashboard_data, text_section_1, text_section_2, text_section_3, text_section_4, text_military, text_india, text_wa):
    st.markdown("<h3 style='color:#ff4b4b; margin-top: 30px;'>🧠 Weekly Intelligence Assessment</h3>", unsafe_allow_html=True)

    # Move scv_categories up here so the engine can calculate the scores
    scv_categories = [
        ("Global Foundry Market", text_section_1, "#00bfff"),
        ("AI Chip Demand", text_section_2, "#ff00ff"),
        ("Critical Minerals (REE)", text_section_3, "#00ff00"),
        ("Export Controls", text_section_4, "#ff4b4b"),
        ("Military & Outer Space", text_military, "#ffd166"),
        ("India Developments", text_india, "#ff8c00"),
        ("West Asia / Middle East", text_wa, "#9400d3")
    ]

    try:
        # --- 1. SCV SCORE ---
        scv_scores = []
        for name, txt, _ in scv_categories:
            if len(txt.strip()) > 20:
                scv_scores.append(calculate_domain_threat(name, txt, dashboard_data))

        avg_scv = int(sum(scv_scores)/len(scv_scores)) if scv_scores else 0

        # --- 2. RSS SIGNAL INTENSITY (last 7 days proxy) ---
        rss = parse_rss_txt_file()
        signal_score = 0

        for region in rss.values():
            for item in region:
                title = item.get("title", "").lower()

                if any(k in title for k in ["war","strike","military","crisis","blockade"]):
                    signal_score += 3
                elif any(k in title for k in ["sanction","export","ban","restriction"]):
                    signal_score += 2
                else:
                    signal_score += 1

        signal_score = min(100, signal_score)

        # --- 3. COMPOSITE RISK ---
        global_risk = int((avg_scv * 0.6) + (signal_score * 0.4))

        if global_risk >= 75:
            status = "🔴 HIGH RISK"
        elif global_risk >= 60:
            status = "🟠 ELEVATED"
        else:
            status = "🟡 MODERATE"

        # --- 4. TOP RISKS EXTRACTION ---
        risks = []

        if "taiwan" in text_section_2.lower():
            risks.append("Taiwan semiconductor dependency risk rising")
        if "rare earth" in text_section_3.lower():
            risks.append("Rare earth supply chain instability")
        if "export" in text_section_4.lower():
            risks.append("Export control fragmentation increasing")
        if "military" in text_military.lower():
            risks.append("Military-linked supply chain risks emerging")

        # fallback
        if not risks:
            risks = ["No dominant single-point risk detected (distributed instability)"]

        # --- OUTPUT ---
        st.markdown(f"""
        <div style="
            background: rgba(15, 15, 15, 0.85);
            padding: 24px;
            border-radius: 12px;
            border: 1px solid #333;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(8px);
        ">

        <h4 style="color:#00bfff; margin-top:0px; letter-spacing: 1px; border-bottom: 1px solid #333; padding-bottom: 10px;">GLOBAL SEMICONDUCTOR RISK ASSESSMENT</h4>

        <p style="margin-top: 15px;"><b>Overall Risk Level:</b> <span style="font-size: 16px; font-weight: bold;">{status} ({global_risk}/100)</span></p>

        <p style="margin-top: 15px;"><b>Top Strategic Risks:</b></p>
        <ul style="color:#d1d5db; line-height: 1.8;">
        {''.join(f"<li>{r}</li>" for r in risks[:3])}
        </ul>

        <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-top: 20px;">
        <p style="margin-top: 0;"><b>Key Insight:</b><br>
        <span style="color:#aaa;">Supply chain vulnerabilities are increasingly interconnected across geopolitical domains.</span></p>

        <p style="margin-bottom: 0;"><b>Recommended Monitoring:</b><br>
        <span style="color:#aaa;">&bull; Taiwan Strait developments<br>
        &bull; Rare earth export policies<br>
        &bull; US&ndash;China technology controls</span>
        </p>
        </div>

        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.warning("Intelligence briefing engine could not generate this week.")


def render_geopolitical_memory_layer():
    memory_file = "data/geopolitical_memory.json"
    
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            memory = json.load(f)
    
        st.markdown(
            "<h3 style='color:#ffd166; margin-bottom: 5px;'>🧠 Geopolitical Memory Layer</h3>",
            unsafe_allow_html=True
        )
        
        # NEW: Display the dynamic timeframe
        timeframe_text = memory.get("timeframe", "Bi-Weekly Strategic Assessment")
        st.markdown(f"<p style='color: #888; font-size: 13px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-top: 0px; margin-bottom: 15px;'>{timeframe_text}</p>", unsafe_allow_html=True)
    
        patterns_html = "".join(
            [f"<li>{p}</li>" for p in memory.get("persistent_patterns", [])]
        )
    
        st.markdown(f"""
        <div style="
            background:#0b0b0b;
            border:1px solid #333;
            padding:20px;
            border-radius:10px;
            margin-bottom:25px;
        ">
    
        <h4 style="color:#00bfff;">
        Persistent Strategic Patterns
        </h4>
    
        <ul>
        {patterns_html}
        </ul>
    
        <p style="margin-top:15px;">
        <b>Strategic Observation:</b><br>
        {memory["strategic_observation"]}
        </p>
    
        <p style="color:#888; font-size:12px;">
        Last Updated: {memory["date"]}
        </p>
    
        </div>
        """, unsafe_allow_html=True)

def render_scv_concentric_wheel(dashboard_data, text_section_1, text_section_2, text_section_3, text_section_4, text_military, text_india, text_wa):
    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 10px; margin-bottom: 10px;'>Semicon, Rare Earth and AI Geopolitical Outlook</h3>", unsafe_allow_html=True)
    scv_categories = [
        ("Global Foundry Market", text_section_1, "#00bfff"),
        ("AI Chip Demand", text_section_2, "#ff00ff"),
        ("Critical Minerals (REE)", text_section_3, "#00ff00"),
        ("Export Controls", text_section_4, "#ff4b4b"),
        ("Military & Outer Space", text_military, "#ffd166"),
        ("India Developments", text_india, "#ff8c00"),
        ("West Asia / Middle East", text_wa, "#9400d3")
    ]

    active_cats = []
    for name, txt, col in scv_categories:
        if len(txt.strip()) > 20:
            dynamic_score = calculate_domain_threat(name, txt, dashboard_data)
            active_cats.append({"name": name, "score": dynamic_score, "color": col})

    active_cats = sorted(active_cats, key=lambda x: x["score"], reverse=True)

    scv_cols = st.columns([1.2, 1])
    with scv_cols[0]:
        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("<p style='color: #888; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0px; text-align: center;'>Supply Chain Vulnerability (SCV) Wheel (weekly)</p>", unsafe_allow_html=True)

        if active_cats:
            fig = go.Figure()
            base_hole, ring_width, gap = 0.35, 0.015, 0.075         

            for i, cat in enumerate(active_cats):
                val, color = cat["score"], cat["color"]
                data_hole = base_hole + i * (ring_width + gap)
                
                fig.add_trace(go.Pie(values=[val, 100 - val], hole=data_hole, domain=dict(x=[0, 1], y=[0, 1]), marker=dict(colors=[color, "#000000"], line=dict(width=0)), textinfo='none', sort=False, direction='clockwise', hoverinfo='text', hovertext=[f"{cat['name']}: {val}%", ""], showlegend=False))
                fig.add_trace(go.Pie(values=[100], hole=data_hole + ring_width, domain=dict(x=[0, 1], y=[0, 1]), marker=dict(colors=["#000000"], line=dict(width=2, color="#000000")), textinfo='none', sort=False, hoverinfo='none', showlegend=False))
            
            fig.add_trace(go.Pie(values=[100], hole=0.98, domain=dict(x=[0, 1], y=[0, 1]), marker=dict(colors=["#000000"], line=dict(width=4, color="#000000")), textinfo='none', hoverinfo='none', showlegend=False))

            overall_score = int(sum(c["score"] for c in active_cats) / len(active_cats)) if active_cats else 0

            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20), height=400, annotations=[dict(text=f"<b style='font-size:42px; color:white;'>{overall_score}</b><br><span style='color:#aaaaaa; font-size:12px; font-weight:bold;'>AVG SCV SCORE</span>", x=0.5, y=0.5, showarrow=False)])
            st.plotly_chart(fig, use_container_width=True)
            
            legend_html = "<div style='display:flex; flex-wrap:wrap; justify-content:center; gap:12px; margin-top:-30px; margin-bottom:20px;'>"
            for cat in active_cats: legend_html += f"<div style='font-size:10px; font-weight:bold; color:#a3a3a3;'><span style='color:{cat['color']};'>●</span> {cat['name'].upper()}</div>"
            st.markdown(legend_html + "</div>", unsafe_allow_html=True)
        else: st.warning("Not enough data to render the wheel.")

    with scv_cols[1]:
        st.markdown("<div style='margin-top: 20px;'></div><p style='color: #888; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 20px;'>SCV Threat Matrix (Active Domains) (Weekly)</p>", unsafe_allow_html=True)
        if active_cats:
            for cat in active_cats:
                label, value, color = cat["name"].upper(), cat["score"], cat["color"]
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span style="font-size: 12px; font-weight: 600; color: #d1d5db; letter-spacing: 0.5px;">{label}</span>
                        <span style="font-size: 13px; font-weight: bold; color: {color};">{value}%</span>
                    </div>
                    <div style="width: 100%; background-color: #1f2937; border-radius: 4px; height: 6px;">
                        <div style="width: {value}%; background-color: {color}; height: 6px; border-radius: 4px; box-shadow: 0 0 8px {color}80;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else: st.info("No domain data available to calculate threat matrix.")

def render_ai_geopolitical_synthesis_weekly(text_summary, text_ews, selected_actor):
    st.markdown("<p style='color: #888; font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-top: 20px; margin-bottom: 10px;'>AI Geopolitical Synthesis (Weekly) - The Big Picture</p>", unsafe_allow_html=True)
    if text_summary and text_summary.strip() != "":
        with st.container(height=160):
            render_highlighted_text(text_summary, selected_actor)
    else:
        st.info("No synthesis data available.")
        
    st.markdown("---")

    if text_ews and text_ews.strip() != "":
        st.markdown("<h5 style='color:#ff4b4b; margin-top: 0px; margin-bottom: 5px;'>🚨 Weekly EWS Synthesis - The Tactical Alarm</h5>", unsafe_allow_html=True)
        render_highlighted_text(text_ews, selected_actor)
        st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("---")

def render_event_correlation_and_timeline_weekly(display_actions):
    col_tc1, col_tc2 = st.columns(2)
    
    with col_tc1:
        st.markdown("##### 🔗 Event Correlation Engine - Weekly")
        st.caption("Detects geographic hotspots where multiple distinct entities are operating simultaneously.")
        try:
            loc_group = display_actions.groupby('Location')['Actor'].apply(lambda x: list(set(x))).reset_index()
            # Strip out vague locations so we only get real strategic convergences
            loc_group = loc_group[~loc_group['Location'].isin(['Global', 'Multiple', 'Various', 'None', '', 'N/A'])]
            correlated = loc_group[loc_group['Actor'].apply(len) > 1]
            
            if not correlated.empty:
                for _, row in correlated.head(4).iterrows():
                    actors_str = ", ".join(row['Actor'])
                    loc = row['Location']
                    
                    # Updated 4WH Explanatory Format (Natural Language)
                    html_box = f'''
                    <div style="background-color: rgba(255,140,0, 0.1); border-left: 3px solid #ff8c00; padding: 12px; margin-bottom: 12px; border-radius: 4px;">
                        <p style="margin: 0 0 6px 0; font-size: 14px; color: #ff8c00;"><b>⚠️ Strategic Convergence Detected</b></p>
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #d1d5db; line-height: 1.5;">
                            Currently, multiple distinct entities—specifically <b>{actors_str}</b>—are actively concentrating their operational and policy vectors within <b>{loc}</b>, indicating a high-priority strategic hotspot.
                        </p>
                        <p style="margin: 0 0 2px 0; font-size: 12px; color: #aaaaaa;"><b>Location:</b> <span style="color: #ddd;">{loc}</span></p>
                        <p style="margin: 0; font-size: 12px; color: #aaaaaa;"><b>Actors Involved:</b> <span style="color: #ddd;">{actors_str}</span></p>
                    </div>
                    '''
                    st.markdown(html_box, unsafe_allow_html=True)
            else:
                st.info("No localized strategic convergences detected this week.")
        except Exception:
            pass
            
    with col_tc2:
        st.markdown("##### ⏳ Strategic Timeline Reconstruction - Weekly")
        try:
            if len(display_actions) > 0:
                timeline_html = '<div style="border-left: 2px solid #333; padding-left: 15px; margin-left: 10px;">'
                for _, row in display_actions.head(5).iterrows():
                    actor = row.get('Actor', 'Unknown')
                    # FIX: Removed the [:100] + "..." cutoff. Now the full sentence will render naturally.
                    action = str(row.get('Action', ''))
                    
                    timeline_html += f'<div style="position: relative; margin-bottom: 15px;"><span style="position: absolute; left: -21px; top: 0px; height: 10px; width: 10px; border-radius: 50%; background-color: #00bfff;"></span><div style="font-size: 12px; font-weight: bold; color: #00bfff;">{actor}</div><div style="font-size: 14px; color: #eee; line-height: 1.3; padding-top: 2px;">{action}</div></div>'
                timeline_html += '</div>'
                st.markdown(timeline_html, unsafe_allow_html=True)
        except Exception:
            pass