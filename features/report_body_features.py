import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from utils.data_helpers import clean_dataframe, render_highlighted_text, extract_tag

# Import the sub-features required specifically for the report body
from features.tactical_features import render_tactical_maps, render_live_telemetry, render_verified_sources
from features.weekly_features import render_event_correlation_and_timeline_weekly
from features.daily_features import render_24h_live_analytics

def render_weekly_report_body(dashboard_data, selected_actor, df_actions, MAPBOX_PUBLIC_TOKEN):
    # 1. Extract texts locally
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

    # 2. Extract dataframes locally
    df_kpi = clean_dataframe(pd.DataFrame(dashboard_data.get('kpi_metrics', [])))
    df_fund = clean_dataframe(pd.DataFrame(dashboard_data.get('funding_data', [])))
    df_market = clean_dataframe(pd.DataFrame(dashboard_data.get('market_impact', [])))
    df_risk = clean_dataframe(pd.DataFrame(dashboard_data.get('supply_chain_risk', [])))
    
    # --- RENDER KPIS ---
    if not df_kpi.empty and 'Metric' in df_kpi.columns:
        st.markdown("##### Executive Snapshot")
        cols_per_row = 3
        for i in range(0, len(df_kpi), cols_per_row):
            kpi_cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(df_kpi):
                    with kpi_cols[j]:
                        row = df_kpi.iloc[i + j]
                        label_val = str(row.get('Metric', ''))
                        metric_val = str(row.get('Value', ''))
                        st.markdown(f"""
                            <div style="
                                padding: 18px;
                                border-radius: 10px;
                                background: rgba(17, 17, 17, 0.85);
                                border-left: 4px solid #00bfff;
                                margin-bottom: 15px;
                                box-shadow: 0 4px 15px rgba(0, 191, 255, 0.15);
                                backdrop-filter: blur(10px);
                                border-top: 1px solid #333;
                                border-right: 1px solid #333;
                                border-bottom: 1px solid #333;
                            ">
                                <div style="font-size: 12px; font-weight: 700; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;">{label_val}</div>
                                <div style="font-size: 28px; font-weight: bold; color: #ffffff; line-height: 1.1;">{metric_val}</div>
                            </div>
                        """, unsafe_allow_html=True)
        st.markdown("---")
    
    # --- RENDER TEXT SECTIONS & TABLES ---
    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Executive Summary</h3>", unsafe_allow_html=True)
    if text_summary: render_highlighted_text(text_summary, selected_actor)

    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Global Foundry Market & Geopolitical Positioning</h3>", unsafe_allow_html=True)
    if text_section_1: render_highlighted_text(text_section_1, selected_actor)
    
    if not df_fund.empty and not (len(df_fund) == 1 and "No " in str(df_fund.iloc[0].values[0])):
        st.markdown("##### Strategic Investments & Funding")
        st.table(df_fund.set_index(df_fund.columns[0]))

    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>AI Chip Demand, Manufacturing & Processing</h3>", unsafe_allow_html=True)
    if text_section_2: render_highlighted_text(text_section_2, selected_actor)
    
    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Critical Minerals: Rare Earth Reserves & Supply Chains</h3>", unsafe_allow_html=True)
    if text_section_3: render_highlighted_text(text_section_3, selected_actor)
    
    if not df_market.empty and not (len(df_market) == 1 and "Data Unavailable" in str(df_market.iloc[0].values[0])):
        st.markdown("##### Market & Geopolitical Impact")
        st.table(df_market.set_index(df_market.columns[0]))

    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Export Controls & Geopolitical Impact</h3>", unsafe_allow_html=True)
    if text_section_4: render_highlighted_text(text_section_4, selected_actor)
    
    if not df_risk.empty and not (len(df_risk) == 1 and "Data Unavailable" in str(df_risk.iloc[0].values[0])):
        st.markdown("##### Supply Chain Risk Analysis")
        st.table(df_risk.set_index(df_risk.columns[0]))
        
    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>AI, Chips and Rare Earth in Military and Outer Space Domain</h3>", unsafe_allow_html=True)
    if text_military: render_highlighted_text(text_military, selected_actor)
    
    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Lithography Chokepoints & State Actions</h3>", unsafe_allow_html=True)
    if text_section_5: render_highlighted_text(text_section_5, selected_actor)

    if text_india and text_india.strip() != "": 
        st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>India: Domestic & Strategic Developments</h3>", unsafe_allow_html=True)
        render_highlighted_text(text_india, selected_actor)
        
    if text_wa and text_wa.strip() != "": 
        st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>West Asia/Middle East: Domestic & Strategic Developments</h3>", unsafe_allow_html=True)
        render_highlighted_text(text_wa, selected_actor)

    # ==========================================
    # TACTICAL MAPS & TIMELINE LAYER
    # ==========================================
    render_tactical_maps(df_actions, selected_actor, MAPBOX_PUBLIC_TOKEN)

    # ==========================================
    # 📡 RECENT STATE ACTIONS (PURE CALENDAR SNAPSHOT)
    # ==========================================
    # Directly projects exactly what is written in the loaded calendar JSON file.
    curated_actions = dashboard_data.get("recent_actions", [])

    if curated_actions:
        df_curated = clean_dataframe(pd.DataFrame(curated_actions))

        if not df_curated.empty:
            # Apply UI actor filter from the sidebar
            if selected_actor != "All" and "Actor" in df_curated.columns:
                display_actions = df_curated[df_curated["Actor"] == selected_actor]
            else:
                display_actions = df_curated
                
            if not display_actions.empty:
                # Strictly title only, no date strings attached
                st.markdown("##### Recent State Actions")
                
                # Format datetimes safely for display without mutating or dropping rows
                display_table = display_actions.copy()
                if "Date" in display_table.columns:
                    display_table["Date"] = pd.to_datetime(display_table["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
                
                st.table(display_table.set_index(display_table.columns[0]))
            else:
                st.info("No curated state actions matched the selected actor.")
        else:
            st.info("No curated state actions were supplied for this report.")
    else:
        st.info("No curated state actions were supplied for this report.")

    st.markdown("<h3 style='color:#00bfff; font-size:22px; margin-top: 20px; margin-bottom: 0px;'>Strategic Conclusion</h3>", unsafe_allow_html=True)
    if text_final: render_highlighted_text(text_final, selected_actor)

    sources_list = dashboard_data.get('sources', [])
    render_verified_sources(sources_list)