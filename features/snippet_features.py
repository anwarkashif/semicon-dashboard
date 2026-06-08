import streamlit as st
import pandas as pd
import os
import json
import re  
from datetime import datetime, timedelta, timezone
from utils.snippet_engine import get_fallback_snippet

from features.daily_features import render_24h_live_analytics, run_shockwave_engine

def render_daily_snippet(df_actions, client=None, model_name=None, dashboard_data=None, text_sections=None):
    
    today_data_path = 'data/today_snippet/tactical_events_24h.json'
    if os.path.exists(today_data_path):
        try:
            with open(today_data_path, 'r') as f:
                today_events = json.load(f)
                df_today = pd.DataFrame(today_events)
                
                if 'Headline' not in df_today.columns and 'Action' in df_today.columns:
                    df_today['Headline'] = df_today['Action']
                    
                if not df_today.empty:
                    if df_actions is None or df_actions.empty:
                        df_actions = df_today
                    else:
                        df_actions = pd.concat([df_today, df_actions], ignore_index=True)
        except Exception as e:
            pass 

    st.markdown("""
    <div style='text-align: center; margin-top: 10px; margin-bottom: 20px;'>
        <h1 style='color: #00bfff; font-size: 2.2em; letter-spacing: 1px;'>📝 Today's Snippet</h1>
        <p style='color: #d1d5db; font-family: monospace;'>12-HOUR TACTICAL INTELLIGENCE SYNTHESIS</p>
    </div>
    <hr style='border: 1px solid #333;'>
    """, unsafe_allow_html=True)

    # --- NEW: LOAD THE DYNAMIC AI SHIFT BRIEF ---
    brief_data_path = 'data/today_snippet/shift_brief.json'
    intel_data = get_fallback_snippet() # Defaults to fallback if no live data exists yet
    
    if os.path.exists(brief_data_path):
        try:
            with open(brief_data_path, 'r') as f:
                intel_data = json.load(f)
        except Exception:
            pass

    def format_html_text(text):
        text = str(text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        return text.replace('\n', '<br>')

    # ==========================================
    # 1. ANALYSIS (BLUF AND EXECUTIVE SUMMARY)
    # ==========================================
    
    bluf_content = format_html_text(intel_data.get('bluf', 'Pending AI Generation...'))
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #141e30 0%, #243b55 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #00bfff; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h3 style="margin-top: 0; color: #ffffff;">🎯 BLUF (Bottom Line Up Front)</h3>
        <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{bluf_content}</p>
    </div>
    """, unsafe_allow_html=True)

    exec_content = format_html_text(intel_data.get('executive_summary', 'Pending AI Generation...'))
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #4facfe; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h3 style="margin-top: 0; color: #ffffff;">📋 Executive Summary</h3>
        <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{exec_content}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        esc_content = format_html_text(intel_data.get('escalation_indicators', '- No indicators detected.'))
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2b0f19 0%, #591b2c 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #ff4b2b; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #ffffff;">⚠️ Escalation Indicators</h3>
            <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{esc_content}</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        strat_content = format_html_text(intel_data.get('strategic_outlook', 'Pending AI Generation...'))
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #093028 0%, #1b4b36 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #00ff87; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #ffffff;">🔭 Strategic Outlook & Recommendations</h3>
            <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{strat_content}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # ==========================================
    # 2. EVIDENCE (RAW TACTICAL FEEDS)
    # ==========================================
    st.markdown("### 📊 Raw Tactical Feeds (12H)")
    if df_actions is not None and not df_actions.empty:
        temp_df = df_actions.copy()
        
        # Target exact columns to map directly to the backend
        target_cols = ['Date', 'Actor', 'Action', 'Location', 'Risk']
        
        # Ensure target columns exist safely
        for col in target_cols:
            if col not in temp_df.columns:
                if col == 'Action' and 'Headline' in temp_df.columns:
                    temp_df['Action'] = temp_df['Headline']
                elif col == 'Actor' and 'Source' in temp_df.columns:
                    temp_df['Actor'] = temp_df['Source']
                else:
                    temp_df[col] = "Pending Data"
                    
        # Clean, Sort, and Enforce Diversity via Deduplication
        display_df = temp_df[target_cols].copy()
        display_df = display_df.drop_duplicates(subset=['Action'], keep='first')
        
        if 'Date' in display_df.columns:
            display_df['Parsed_Date'] = pd.to_datetime(display_df['Date'], errors='coerce', utc=True)
            display_df = display_df.sort_values(by=['Parsed_Date'], ascending=[False])
            display_df['Date'] = display_df['Date'].astype(str)
            display_df = display_df.drop(columns=['Parsed_Date'])
            
        # Lock in exactly 10 diverse rows
        display_df = display_df.head(10)
        display_df = display_df.fillna("")
        
        # Intense Dynamic Styling for CRITICAL Risk Elements
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
        st.info("No tactical alerts logged.")

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # ==========================================
    # 3. ALL 24-HOUR FEATURES 
    # ==========================================
    
    run_shockwave_engine()
    st.markdown("<br>", unsafe_allow_html=True)
    
    if dashboard_data is not None and text_sections is not None:
        render_24h_live_analytics(dashboard_data, text_sections)
        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)