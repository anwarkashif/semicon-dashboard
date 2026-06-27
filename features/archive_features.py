import streamlit as st
import pandas as pd
import json
import os
import re
from utils.data_helpers import get_brief_mappings, extract_tag, render_highlighted_text

def render_trend_timelines():
    st.title("Macro Trends & Timelines")
    st.markdown("Tracking the volume of Geopolitical Actions and Supply Chain Risks across historical briefs.")
    
    archive_mapping = get_brief_mappings('data')
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

# --- NEW: Dedicated Renderer for Archived Weekly Intelligence Briefs ---
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

    # Render the Verified Intelligence Sources table with working URLs
    sources_list = dashboard_data.get('sources', [])
    if sources_list:
        render_verified_sources(sources_list)

def render_archives():
    st.title("Archives")
    archive_mapping = get_brief_mappings('data')
    
    if archive_mapping:
        selected_brief = st.selectbox("Select Past Brief:", list(archive_mapping.keys()))
        st.info(f"Displaying: {selected_brief}")
        
        with open(archive_mapping[selected_brief], 'r', encoding='utf-8') as f:
            archived_data = json.load(f)
        
        # 🛑 ROUTING LOGIC: Determine how to display based on the file type
        if "Weekly Intelligence Brief" in selected_brief:
            render_archived_intel_brief(archived_data)
            
        elif "Weekly Tactical Brief" in selected_brief:
            # Tactical Briefs use standard text rendering
            arch_raw = ""
            if isinstance(archived_data, dict):
                if 'brief_raw' in archived_data and archived_data['brief_raw']:
                    arch_raw = archived_data['brief_raw']
                    
            def format_html_text(text):
                text = str(text)
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                return text.replace('\n', '<br>')
            
            # Format cleanly without throwing errors if data is slightly malformed
            st.markdown(format_html_text(arch_raw), unsafe_allow_html=True)
            
        else:
            # Executive Flash & Today's Snippet
            arch_raw = ""
            if isinstance(archived_data, dict):
                bluf = archived_data.get('bluf', archived_data.get('bottom_line_up_front', ''))
                exec_sum = archived_data.get('executive_summary', '')
                narrative = archived_data.get('threat_narrative', '')
                risk = archived_data.get('risk_assessment', '')
                forecast = archived_data.get('strategic_forecast', archived_data.get('strategic_outlook', ''))
                
                parts = []
                if bluf: parts.append(f"**🎯 BLUF:**\n{bluf}")
                if exec_sum: parts.append(f"**📋 EXECUTIVE SUMMARY:**\n{exec_sum}")
                if narrative: parts.append(f"**🕸️ THREAT NARRATIVE:**\n{narrative}")
                if risk: parts.append(f"**⚖️ RISK ASSESSMENT:**\n{risk}")
                if forecast: parts.append(f"**🔭 STRATEGIC FORECAST:**\n{forecast}")
                
                arch_raw = "\n\n---\n\n".join(parts)
                
                if not arch_raw:
                    arch_raw = "*(No synthesized text keys found in this payload)*"
                    
            t1 = extract_tag('EXEC', arch_raw) or arch_raw
            st.markdown(t1.replace('$', r'\$'))
    else:
        st.warning("No active archives found.")

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
    
    archive_mapping = get_brief_mappings('data')
    
    if archive_mapping:
        archive_to_clean = st.selectbox("Select Brief to Clean:", list(archive_mapping.keys()))
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
    
    trash_mapping = get_brief_mappings('trash')
    
    if trash_mapping:
        archive_to_manage = st.selectbox("Select Brief in Trash:", list(trash_mapping.keys()))
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