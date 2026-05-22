import streamlit as st
import pandas as pd
import os
import json
import re  # <-- Added regex to handle Markdown parsing
from datetime import datetime, timedelta, timezone
from utils.snippet_engine import get_fallback_snippet

# --- ADDED: Import ALL 24H Engines ---
from features.daily_features import render_24h_live_analytics, run_shockwave_engine

def render_daily_snippet(df_actions, client=None, model_name=None, dashboard_data=None, text_sections=None):
    
    # --- NEW INTEGRATION: Load isolated Today's Snippet data and complement existing feed ---
    today_data_path = 'data/today_snippet/tactical_events_24h.json'
    if os.path.exists(today_data_path):
        try:
            with open(today_data_path, 'r') as f:
                today_events = json.load(f)
                df_today = pd.DataFrame(today_events)
                
                # Align columns to match the master dataframe expected format
                if 'Headline' not in df_today.columns and 'Action' in df_today.columns:
                    df_today['Headline'] = df_today['Action']
                    
                # Merge with existing df_actions to enrich the analysis
                if not df_today.empty:
                    if df_actions is None or df_actions.empty:
                        df_actions = df_today
                    else:
                        df_actions = pd.concat([df_today, df_actions], ignore_index=True)
        except Exception as e:
            pass # Fail silently and safely rely on the master df_actions if reading fails
    # -----------------------------------------------------------------------------------

    st.markdown("""
    <div style='text-align: center; margin-top: 10px; margin-bottom: 20px;'>
        <h1 style='color: #00bfff; font-size: 2.2em; letter-spacing: 1px;'>📝 Today's Snippet</h1>
        <p style='color: #d1d5db; font-family: monospace;'>12-HOUR TACTICAL INTELLIGENCE SYNTHESIS</p>
    </div>
    <hr style='border: 1px solid #333;'>
    """, unsafe_allow_html=True)

    # In a live environment, you would call synthesize_12h_snippet here. 
    intel_data = get_fallback_snippet() 

    # ==========================================
    # Helper: Convert AI Markdown to HTML for the custom gradient boxes
    # ==========================================
    def format_html_text(text):
        text = str(text)
        # Converts **bold** text to HTML <b>bold</b>
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Converts newlines to HTML breaks
        return text.replace('\n', '<br>')

    # ==========================================
    # 1. ANALYSIS (BLUF AND EXECUTIVE SUMMARY MOVED TO TOP)
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
    # 2. EVIDENCE (RAW TACTICAL FEEDS MOVED DOWN)
    # ==========================================
    st.markdown("### 📊 Raw Tactical Feeds (12H)")
    if df_actions is not None and not df_actions.empty:
        # 1. Ensure Date column is standard timezone-aware datetime
        if 'Date' in df_actions.columns:
            df_actions['Date'] = pd.to_datetime(df_actions['Date'], format='mixed', errors='coerce', utc=True)
            
            # 2. Calculate the 12-hour rolling window
            twelve_hours_ago = datetime.now(timezone.utc) - timedelta(hours=12)
            
            # 3. Filter the dataframe to ONLY include the last 12 hours
            df_12h = df_actions[df_actions['Date'] >= twelve_hours_ago]
        else:
            df_12h = df_actions # Fallback if no Date column exists
        
        available_cols = df_12h.columns.tolist()
        target_cols = ['Date', 'Action', 'Event', 'Headline', 'Actor']
        cols_to_show = [col for col in target_cols if col in available_cols]
        
        # Display the filtered data (or fallback to empty state if nothing happened in 12h)
        if not df_12h.empty:
            display_df = df_12h[cols_to_show].head(8) if cols_to_show else df_12h.head(8)
            
            # Format date for clean UI display
            if 'Date' in display_df.columns:
                display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d %H:%M')
                
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No tactical alerts logged in the current 12-hour window. System Nominal.")
    else:
        st.info("No tactical alerts logged.")

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # ==========================================
    # 3. ALL 24-HOUR FEATURES 
    # ==========================================
    
    # Geopolitical Shockwave Engine
    run_shockwave_engine()
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Advanced Threat Analytics (Includes the 24H Risk Index & Breaking Alert)
    if dashboard_data is not None and text_sections is not None:
        render_24h_live_analytics(dashboard_data, text_sections)
        st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)