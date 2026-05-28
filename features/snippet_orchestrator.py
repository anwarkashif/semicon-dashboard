import streamlit as st
import pandas as pd
import os
import json
import re  # <-- Added to properly parse markdown bolding in HTML

# --- UPDATED IMPORTS ---
from utils.snippet_templates import get_weekly_tactical_template
from utils.snippet_docx_generator import generate_weekly_tactical_docx

from features.weekly_features import (
    render_correlation_engine_weekly,
    render_signal_prioritization_weekly,
    render_intelligence_assessment_weekly,
    render_geopolitical_memory_layer,
    render_event_correlation_and_timeline_weekly
)

def handle_snippet_logic(mode="weekly_tactical", dashboard_data=None, text_summary="", text_section_1="", text_section_2="", text_section_3="", text_section_4="", text_military="", text_india="", text_wa="", text_ews="", selected_actor=None, df_actions=None):
    if mode == "weekly_tactical":
        render_weekly_tactical_brief(dashboard_data, text_summary, text_section_1, text_section_2, text_section_3, text_section_4, text_military, text_india, text_wa, text_ews, selected_actor, df_actions)
    else:
        st.error("Unknown Snippet Mode Requested.")

def render_weekly_tactical_brief(dashboard_data, text_summary, text_section_1, text_section_2, text_section_3, text_section_4, text_military, text_india, text_wa, text_ews, selected_actor, df_actions):
    
    # --- UPDATED PATH: Load isolated Weekly Tactical data and complement existing feed ---
    tactical_data_path = 'data/weekly_tactical/tactical_events_24h.json'
    if os.path.exists(tactical_data_path):
        try:
            with open(tactical_data_path, 'r') as f:
                tactical_events = json.load(f)
                df_tactical = pd.DataFrame(tactical_events)
                
                # Align columns to match the master dataframe expected format
                if 'Headline' not in df_tactical.columns and 'Action' in df_tactical.columns:
                    df_tactical['Headline'] = df_tactical['Action']
                    
                # Merge with existing df_actions to enrich the analysis
                if not df_tactical.empty:
                    if df_actions is None or df_actions.empty:
                        df_actions = df_tactical
                    else:
                        df_actions = pd.concat([df_tactical, df_actions], ignore_index=True)
        except Exception as e:
            pass # Fail silently and safely rely on the master df_actions if reading fails
    # -----------------------------------------------------------------------------------

    intel_data = get_weekly_tactical_template()
    
    st.markdown(f"""
    <div style='text-align: center; border-bottom: 3px solid #00bfff; padding-bottom: 10px; margin-bottom: 20px;'>
        <h1 style='color: #ffffff; font-size: 2.3em; margin-bottom: 0px;'>{intel_data.get('title', "Tactical Weekly Brief: Strategic Intelligence Synthesis")}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # Helper: Convert AI Markdown to HTML for the custom gradient boxes
    # ==========================================
    def format_html_text(text):
        text = str(text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text) # Markdown bold to HTML bold
        return text.replace('\n', '<br>')

    # ==========================================
    # --- ANALYSIS & STRATEGY SECTIONS ---
    # ==========================================
    
    bluf_content = format_html_text(intel_data.get('bluf', 'Pending generation...'))
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #141e30 0%, #243b55 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #00bfff; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h3 style="margin-top: 0; color: #ffffff;">🎯 BLUF (Bottom Line Up Front)</h3>
        <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{bluf_content}</p>
    </div>
    """, unsafe_allow_html=True)

    tactical_raw = intel_data.get('tactical_indicators', 'No indicators provided.')
    if isinstance(tactical_raw, list):
        tactical_content = "<br>".join([f"• {format_html_text(ind)}" for ind in tactical_raw])
    else:
        tactical_content = format_html_text(tactical_raw)
        
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2c1b3d 0%, #4a2b5e 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #a855f7; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h3 style="margin-top: 0; color: #ffffff;">🚩 Tactical Indicators</h3>
        <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{tactical_content}</p>
    </div>
    """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        exec_content = format_html_text(intel_data.get('executive_summary', 'Pending generation...'))
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #4facfe; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #ffffff;">📋 Executive Summary</h3>
            <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{exec_content}</p>
        </div>
        """, unsafe_allow_html=True)
        
        risk_content = format_html_text(intel_data.get('risk_assessment', 'Pending generation...'))
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #3f2b1a 0%, #613c20 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #f59e0b; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #ffffff;">⚖️ Risk Assessment</h3>
            <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{risk_content}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        threat_content = format_html_text(intel_data.get('threat_narrative', 'Pending generation...'))
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2b0f19 0%, #591b2c 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #ef4444; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #ffffff;">🕸️ Threat Narrative</h3>
            <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{threat_content}</p>
        </div>
        """, unsafe_allow_html=True)
        
        pred_content = format_html_text(intel_data.get('predictive_analysis', 'Pending generation...'))
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1c29 0%, #2a2d43 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #6366f1; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #ffffff;">🔭 Predictive Analysis</h3>
            <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{pred_content}</p>
        </div>
        """, unsafe_allow_html=True)
        
    strat_content = format_html_text(intel_data.get('recommendations', 'Pending generation...'))
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #093028 0%, #1b4b36 100%); padding: 20px; border-radius: 8px; border-left: 5px solid #10b981; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
        <h3 style="margin-top: 0; color: #ffffff;">🛡️ Strategic Recommendations</h3>
        <p style="color: #e2e8f0; font-size: 1.05em; margin-bottom: 0; line-height: 1.5;">{strat_content}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # ==========================================
    # --- WEEKLY FEATURES ---
    # ==========================================
    if dashboard_data is not None:
        render_correlation_engine_weekly()
        st.markdown("---")
        render_signal_prioritization_weekly(dashboard_data)
        st.markdown("---")
        render_intelligence_assessment_weekly(dashboard_data, text_section_1, text_section_2, text_section_3, text_section_4, text_military, text_india, text_wa)
        st.markdown("---")
        render_geopolitical_memory_layer()
        st.markdown("---")
        
    if df_actions is not None and not df_actions.empty:
        render_event_correlation_and_timeline_weekly(df_actions)
        # VISUAL FIX: Removed trailing st.markdown("---") from inside here to prevent duplicate line wrapping

    # ==========================================
    # --- CLEANED FOOTER & DOWNLOAD BLOCK ---
    # ==========================================
    st.markdown("<hr style='border: 1px solid #333; margin-top: 20px; margin-bottom: 25px;'>", unsafe_allow_html=True)
    
    if st.session_state.get('role') == 'admin':
        colA, colB = st.columns([3, 1])
        with colB:
            try:
                docx_buffer = generate_weekly_tactical_docx(intel_data)
                st.download_button(label="📥 Download Weekly Tactical Brief (DOCX)", data=docx_buffer, file_name=f"Weekly_Tactical_Brief.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
            except Exception as e:
                st.button("📥 Download Unavailable", disabled=True)