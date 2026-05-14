import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from utils.snippet_engine import get_fallback_snippet

def render_daily_snippet(df_actions, client=None, model_name=None, dashboard_data=None):
    st.markdown("""
    <div style='text-align: center; margin-top: 10px; margin-bottom: 20px;'>
        <h1 style='color: #00bfff; font-size: 2.2em; letter-spacing: 1px;'>📝 Today's Snippet</h1>
        <p style='color: #d1d5db; font-family: monospace;'>12-HOUR TACTICAL INTELLIGENCE SYNTHESIS</p>
    </div>
    <hr style='border: 1px solid #333;'>
    """, unsafe_allow_html=True)

    # In a live environment, you would call synthesize_12h_snippet here. 
    intel_data = get_fallback_snippet() 

    # 1. NEW BLUF STRUCTURE
    st.markdown("### 🎯 BLUF (Bottom Line Up Front)")
    st.warning(intel_data.get('bluf', 'Pending AI Generation...'))

    # 2. EVIDENCE (UPDATED WITH 12-HOUR FILTER)
    st.markdown("### 📊 Raw Tactical Feeds (12H)")
    if not df_actions.empty:
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

    # 3. ANALYSIS
    st.markdown("### 📋 Executive Summary")
    st.info(intel_data.get('executive_summary', 'Pending AI Generation...'))
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### ⚠️ Escalation Indicators")
        st.markdown(intel_data.get('escalation_indicators', '- No indicators detected.'))
        
    with col2:
        st.markdown("### 🔭 Strategic Outlook & Recommendations")
        st.success(intel_data.get('strategic_outlook', 'Pending AI Generation...'))