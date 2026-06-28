import streamlit as st
import pandas as pd
import json
import os
import re
from utils.data_helpers import get_brief_mappings, extract_tag, render_highlighted_text

def render_trend_timelines():
    st.title("Macro Trends & Timelines")
    st.markdown("Tracking the volume of Geopolitical Actions and Supply Chain Risks across historical briefs.")
    
    archive_mapping, _ = get_brief_mappings('data', archive_category="Weekly Archive")
    if archive_mapping:
        sorted_brief_paths = list(archive_mapping.values())
        sorted_brief_paths.reverse() 
        
        trend_data = []
        for f_path in sorted_brief_paths:
            try:
                with open(f_path, 'r', encoding='utf-8') as file:
                    d = json.load(file)
                    if isinstance(d, list): continue
                        
                    b_date = d.get('date', 'Unknown')
                    actions = d.get('recent_actions', [])
                    risks = d.get('supply_chain_risk', [])
                    
                    actions_count = len([a for a in actions if "System" not in str(a.values())])
                    risks_count = len([r for r in risks if "Data Unavailable" not in str(r.values())])
                    
                    trend_data.append({
                        "Date": b_date,
                        "Geopolitical Actions": actions_count,
                        "Supply Chain Risks": risks_count
                    })
            except: pass
        
        if trend_data:
            df_trends = pd.DataFrame(trend_data).set_index("Date")
            st.line_chart(df_trends)
        else:
            st.warning("Not enough valid data points to plot a trend.")
    else:
        st.warning("No archives available to generate trend timelines.")

def render_archived_intel_brief(dashboard_data):
    from features.tactical_features import render_verified_sources
    
    raw_text = dashboard_data.get('brief_raw', '')
    text_summary = extract_tag('SUMMARY', raw_text) or ""
    text_section_1 = extract_tag('EXEC', raw_text) or ""
    text_section_2 = extract_tag('LITHO', raw_text) or ""
    text_section_3 = extract_tag('REE', raw_text) or ""
    text_section_4 = extract_tag('GEO', raw_text) or ""
    text_military = extract_tag('MILITARY', raw_text) or ""
    text_section_5 = extract_tag('CONCLUSION', raw_text) or ""
    text_india = extract_tag('INDIA', raw_text) or ""
    text_wa = extract_tag('WEST_ASIA', raw_text) or ""
    text_final = extract_tag('FINAL_CONCLUSION', raw_text) or ""

    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Executive Summary</h3>", unsafe_allow_html=True)
    if text_summary: render_highlighted_text(text_summary, "All")

    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Global Foundry Market & Geopolitical Positioning</h3>", unsafe_allow_html=True)
    if text_section_1: render_highlighted_text(text_section_1, "All")

    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>AI Chip Demand, Manufacturing & Processing</h3>", unsafe_allow_html=True)
    if text_section_2: render_highlighted_text(text_section_2, "All")
    
    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Critical Minerals: Rare Earth Reserves & Supply Chains</h3>", unsafe_allow_html=True)
    if text_section_3: render_highlighted_text(text_section_3, "All")

    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Export Controls & Geopolitical Impact</h3>", unsafe_allow_html=True)
    if text_section_4: render_highlighted_text(text_section_4, "All")
    
    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>AI, Chips and Rare Earth in Military and Outer Space Domain</h3>", unsafe_allow_html=True)
    if text_military: render_highlighted_text(text_military, "All")
    
    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Lithography Chokepoints & State Actions</h3>", unsafe_allow_html=True)
    if text_section_5: render_highlighted_text(text_section_5, "All")

    if text_india and text_india.strip() != "": 
        st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>India: Domestic & Strategic Developments</h3>", unsafe_allow_html=True)
        render_highlighted_text(text_india, "All")
        
    if text_wa and text_wa.strip() != "": 
        st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>West Asia/Middle East: Domestic & Strategic Developments</h3>", unsafe_allow_html=True)
        render_highlighted_text(text_wa, "All")

    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Strategic Conclusion</h3>", unsafe_allow_html=True)
    if text_final: render_highlighted_text(text_final, "All")

    sources_list = dashboard_data.get('sources', [])
    if sources_list:
        clean_sources = []
        for src in sources_list:
            if isinstance(src, dict):
                if str(src.get('title', '')).strip().lower() == 'nan':
                    src['title'] = src.get('url', 'Verified Source')
                clean_sources.append(src)
            elif isinstance(src, str):
                if src.strip().lower() != 'nan':
                    clean_sources.append({"title": src[:50] + "...", "url": src})
        if clean_sources:
            render_verified_sources(clean_sources)

def render_archived_flash_brief(dashboard_data, brief_title="ARCHIVE"):
    from features.tactical_features import render_verified_sources
    
    st.markdown(f"<h2 style='color: #a855f7; margin-bottom: 15px; margin-top: 10px; font-size: 2em; letter-spacing: 1.5px; border-bottom: 2px solid #a855f7; padding-bottom: 5px; text-transform: uppercase;'>{brief_title}</h2>", unsafe_allow_html=True)
    
    raw_text = dashboard_data.get('brief_raw', '')
    
    if "[Not Extracted]" in raw_text:
        raw_text = raw_text.replace("[Not Extracted]", "*(Not part of the Brief due to presence of BLUF)*")
        
    raw_text = raw_text.replace("**🎯 BLUF:**", "<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>🎯 BLUF (Bottom Line Up Front)</h3>")
    raw_text = raw_text.replace("**📋 EXECUTIVE SUMMARY:**", "<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>📋 Executive Summary</h3>")
    raw_text = raw_text.replace("**🚩 TACTICAL INDICATORS:**", "<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>🚩 Tactical Indicators</h3>")
    raw_text = raw_text.replace("**🕸️ THREAT NARRATIVE:**", "<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>🕸️ Threat Narrative</h3>")
    raw_text = raw_text.replace("**⚖️ RISK ASSESSMENT:**", "<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>⚖️ Risk Assessment</h3>")
    raw_text = raw_text.replace("**🔭 PREDICTIVE ANALYSIS:**", "<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>🔭 Predictive Analysis</h3>")
    raw_text = raw_text.replace("**🔭 STRATEGIC FORECAST:**", "<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>🔭 Strategic Forecast</h3>")
    raw_text = raw_text.replace("**🛡️ STRATEGIC RECOMMENDATIONS:**", "<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>🛡️ Strategic Recommendations</h3>")
    
    def format_markdown_to_html(text):
        text = str(text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return text.replace('\n', '<br>')
        
    st.markdown(f"""
    <div style="background: rgba(17, 17, 17, 0.4); padding: 20px; border-radius: 8px; border: 1px solid #333; line-height: 1.6; color: #e2e8f0;">
        {format_markdown_to_html(raw_text)}
    </div>
    """, unsafe_allow_html=True)
    
    sources_list = dashboard_data.get('sources', [])
    if sources_list:
        st.markdown("<br>", unsafe_allow_html=True)
        clean_sources = []
        for src in sources_list:
            if isinstance(src, dict):
                if str(src.get('title', '')).strip().lower() == 'nan':
                    src['title'] = src.get('url', 'Verified Source')
                clean_sources.append(src)
            elif isinstance(src, str):
                if src.strip().lower() != 'nan':
                    clean_sources.append({"title": src[:60] + "...", "url": src})
                
        if clean_sources:
            render_verified_sources(clean_sources)

# ==========================================
# 🛑 TRI-ARCHIVE RENDERING SYSTEM
# ==========================================

def render_daily_archives():
    st.title("Daily Archive")
    st.caption("Access historical Executive Flash Briefs, Today's Snippets, and West Asia Intelligence.")
    
    archive_mapping, ordered_keys = get_brief_mappings('data', archive_category="Daily Archive")
    
    if archive_mapping and ordered_keys:
        selected_brief = st.selectbox("Select Daily Brief:", ordered_keys)
        st.info(f"Displaying: {selected_brief}")
        
        with open(archive_mapping[selected_brief], 'r', encoding='utf-8') as f:
            archived_data = json.load(f)
            
        render_archived_flash_brief(archived_data, brief_title=selected_brief)
    else:
        st.warning("No Daily Archives found.")

def render_weekly_archives():
    st.title("Weekly Archive")
    st.caption("Access historical Weekly Intelligence Briefs and Weekly Tactical Briefs.")
    
    archive_mapping, ordered_keys = get_brief_mappings('data', archive_category="Weekly Archive")
    
    if archive_mapping and ordered_keys:
        selected_brief = st.selectbox("Select Weekly Brief:", ordered_keys)
        st.info(f"Displaying: {selected_brief}")
        
        with open(archive_mapping[selected_brief], 'r', encoding='utf-8') as f:
            archived_data = json.load(f)
        
        if "Weekly Intelligence Brief" in selected_brief:
            render_archived_intel_brief(archived_data)
        elif "Weekly Tactical Brief" in selected_brief:
            # 🛑 THE FIX: Dynamically auto-stitch the text and URLs without needing the sync button
            from utils.snippet_templates import get_weekly_tactical_template
            
            reconstructed_data = {"brief_raw": "", "sources": []}
            
            # 1. Fetch text natively from the template engine
            live_intel = get_weekly_tactical_template()
            bluf = live_intel.get('bluf', '')
            exec_sum = live_intel.get('executive_summary', '')
            tactical = live_intel.get('tactical_indicators', '')
            narrative = live_intel.get('threat_narrative', '')
            risk = live_intel.get('risk_assessment', '')
            pred = live_intel.get('predictive_analysis', '')
            rec = live_intel.get('recommendations', '')
            
            if isinstance(tactical, list):
                tactical = "\n".join([f"• {item}" for item in tactical])

            parts = []
            if bluf: parts.append(f"**🎯 BLUF:**\n{bluf}")
            if exec_sum: parts.append(f"**📋 EXECUTIVE SUMMARY:**\n{exec_sum}")
            if tactical: parts.append(f"**🚩 TACTICAL INDICATORS:**\n{tactical}")
            if narrative: parts.append(f"**🕸️ THREAT NARRATIVE:**\n{narrative}")
            if risk: parts.append(f"**⚖️ RISK ASSESSMENT:**\n{risk}")
            if pred: parts.append(f"**🔭 PREDICTIVE ANALYSIS:**\n{pred}")
            if rec: parts.append(f"**🛡️ STRATEGIC RECOMMENDATIONS:**\n{rec}")
            
            reconstructed_data['brief_raw'] = "\n\n---\n\n".join(parts)
            
            # 2. Automatically grab the URLs directly from the active live list
            events_list = archived_data if isinstance(archived_data, list) else archived_data.get('recent_actions', [])
            
            derived_sources = []
            for ev in events_list:
                if isinstance(ev, dict):
                    title = ev.get('Title') or ev.get('Headline') or ev.get('Action') or 'Verified Source'
                    url = ev.get('Source') or ev.get('Url') or '#'
                    if url != '#':
                        derived_sources.append({"title": title, "url": url})
                        
            reconstructed_data['sources'] = derived_sources

            # 3. Render it beautifully
            render_archived_flash_brief(reconstructed_data, brief_title=selected_brief)
    else:
        st.warning("No Weekly Archives found.")

def render_monthly_archives():
    st.title("Monthly Archive")
    st.caption("Access historical Monthly SemicoN Reports.")
    
    archive_mapping, ordered_keys = get_brief_mappings('data', archive_category="Monthly Archive")
    
    if archive_mapping and ordered_keys:
        selected_brief = st.selectbox("Select Monthly Report:", ordered_keys)
        st.info(f"Displaying: {selected_brief}")
        
        with open(archive_mapping[selected_brief], 'r', encoding='utf-8') as f:
            archived_data = json.load(f)
            
        render_archived_intel_brief(archived_data)
    else:
        st.info("The Monthly Archive is currently empty. Reports will appear here upon completion of a monthly cycle.")

def render_clean_archives():
    st.title("Clean Archives")
    st.info("Move outdated or incorrect briefs to the Trash. Guests cannot see this tool.")
    
    st.markdown("""
    <style>
        div[data-testid="stButton"] > button[kind="primary"] * {
            color: #000000 !important;
            font-weight: bold !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    archive_mapping, ordered_keys = get_brief_mappings('data', "All")
    
    if archive_mapping and ordered_keys:
        archive_to_clean = st.selectbox("Select Brief to Clean:", ordered_keys)
        if st.button("🗑️ Move to Trash", type="primary"):
            old_path = archive_mapping[archive_to_clean]
            filename = os.path.basename(old_path)
            new_path = os.path.join('trash', filename)
            os.rename(old_path, new_path)
            st.success(f"Successfully moved to Trash: {archive_to_clean}")
            st.rerun()
    else:
        st.warning("No active archives found to clean.")

def render_trash():
    st.title("Trash Bin")
    st.warning("Items here are completely hidden from the public dashboard.")
    
    st.markdown("""
    <style>
        div[data-testid="stButton"] > button[kind="primary"] * {
            color: #000000 !important;
            font-weight: bold !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    trash_mapping, trash_keys = get_brief_mappings('trash', "All")
    
    if not trash_mapping:
        files = glob.glob('trash/*.json')
        trash_mapping = {os.path.basename(f): f for f in files}
        trash_keys = list(trash_mapping.keys())
    
    if trash_mapping:
        archive_to_manage = st.selectbox("Select Brief in Trash:", trash_keys)
        old_path = trash_mapping[archive_to_manage]
        filename = os.path.basename(old_path)
        
        col_rev, col_del = st.columns(2)
        with col_rev:
            if st.button("♻️ Revert to Archives"):
                new_path = os.path.join('data', filename)
                os.rename(old_path, new_path)
                st.success(f"Completely restored: {archive_to_manage}")
                st.rerun()
        with col_del:
            if st.button("⚠️ Permanently Delete", type="primary"):
                os.remove(old_path)
                st.success(f"Permanently destroyed: {archive_to_manage}")
                st.rerun()
    else:
        st.info("Trash is currently empty.")