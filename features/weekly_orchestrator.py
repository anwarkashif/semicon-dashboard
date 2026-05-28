import streamlit as st
from datetime import datetime, timezone

# --- Import all the engines and features needed for the weekly brief ---
from features.daily_features import run_shockwave_engine
from features.weekly_features import (
    render_correlation_engine_weekly,
    render_signal_prioritization_weekly,
    render_intelligence_assessment_weekly,
    render_geopolitical_memory_layer,
    render_scv_concentric_wheel,
    render_ai_geopolitical_synthesis_weekly
)
# from features.tactical_features import render_decision_support_engine   <-- Commented out

from features.report_body_features import render_weekly_report_body
from features.export_features import render_document_controls

def render_full_weekly_brief(
    dashboard_data, latest_filepath, brief_date, text_summary, 
    text_section_1, text_section_2, text_section_3, text_section_4, 
    text_military, text_section_5, text_india, text_wa, text_final, text_ews,
    selected_actor, df_actions, MAPBOX_PUBLIC_TOKEN
):
    st.title(f"SemicoN Weekly Brief - {brief_date}") 
    st.markdown("---")

    # ===========================
    # 🧠 DECISION SUPPORT ENGINE (REMOVED/COMMENTED OUT)
    # ===========================
    # all_text = " ".join([
    #     text_section_1, text_section_2, text_section_3,
    #     text_section_4, text_military, text_india, text_wa
    # ]).lower()
    # 
    # render_decision_support_engine(all_text)

    # ==========================================
    # 🌐 GEOPOLITICAL SHOCKWAVE ENGINE
    # ==========================================
    # --- HIDING 24-HOUR FEATURES FOR NOW (Migrated to Today's Snippet) ---
    # run_shockwave_engine()
    # st.markdown("---")

    # ==========================================
    # 🧠 CORRELATION ENGINE (WEEKLY INTELLIGENCE)
    # ==========================================
    # --- HIDING WEEKLY FEATURES FOR NOW (Migrated to Friday's Snippet) ---
    # render_correlation_engine_weekly()
    # st.markdown("---")
    
    # ==========================================
    # 🧠 SIGNAL PRIORITIZATION ENGINE & ALERTS (WEEKLY)
    # ==========================================
    # render_signal_prioritization_weekly(dashboard_data)
    # st.markdown("---")

    # ==========================================
    # 🧠 INTELLIGENCE BRIEFING ENGINE (WEEKLY)
    # ==========================================
    # render_intelligence_assessment_weekly(dashboard_data, text_section_1, text_section_2, text_section_3, text_section_4, text_military, text_india, text_wa)

    # ==========================================
    # 🧠 GEOPOLITICAL MEMORY LAYER
    # ==========================================
    # render_geopolitical_memory_layer()

    # ==========================================
    # 🌀 SCV CONCENTRIC WHEEL
    # ==========================================
    render_scv_concentric_wheel(dashboard_data, text_section_1, text_section_2, text_section_3, text_section_4, text_military, text_india, text_wa)
    
    # ==========================================
    # AI GEOPOLITICAL SYNTHESIS
    # ==========================================
    render_ai_geopolitical_synthesis_weekly(text_summary, text_ews, selected_actor)

    # ==========================================
    # THE CORE REPORT BODY (TEXT, KPIS, MAPS, RSS)
    # ==========================================
    if latest_filepath:
        render_weekly_report_body(dashboard_data, selected_actor, df_actions, MAPBOX_PUBLIC_TOKEN)

    # --- CALL THE EXTRACTED DOCUMENT CONTROLS ---
    render_document_controls(
        dashboard_data, latest_filepath, brief_date, text_summary, 
        text_section_1, text_section_2, text_section_3, text_section_4, 
        text_military, text_section_5, text_india, text_wa, text_final, text_ews
    )