import streamlit as st
import pandas as pd
import json
import os
from utils.data_helpers import get_brief_mappings, extract_tag

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

def render_archives():
    st.title("Archives")
    archive_mapping = get_brief_mappings('data')
    
    if archive_mapping:
        selected_brief = st.selectbox("Select Past Brief:", list(archive_mapping.keys()))
        st.info(f"Displaying: {selected_brief}")
        
        with open(archive_mapping[selected_brief], 'r', encoding='utf-8') as f:
            archived_data = json.load(f)
        
        # 🛑 THE FIX: Auto-stitch the brief if 'brief_raw' isn't explicitly defined
        arch_raw = ""
        if isinstance(archived_data, dict):
            if 'brief_raw' in archived_data and archived_data['brief_raw']:
                arch_raw = archived_data['brief_raw']
            else:
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