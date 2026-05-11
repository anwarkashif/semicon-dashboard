import streamlit as st
import pandas as pd
import json
import time
from utils.data_helpers import clean_dataframe, extract_tag

def render_vetting_editor(dashboard_data, latest_filepath):
    st.warning("You are currently in Edit Mode. Changes made here will be permanently written to the intelligence database.")
    
    # 1. Re-extract current text to populate the form
    raw_text = dashboard_data.get('brief_raw', '')
    text_summary = extract_tag('SUMMARY', raw_text) or ""
    text_ews = extract_tag('EWS', raw_text) or ""
    text_section_1 = extract_tag('EXEC', raw_text) or ""
    text_section_2 = extract_tag('LITHO', raw_text) or ""
    text_section_3 = extract_tag('REE', raw_text) or ""
    text_section_4 = extract_tag('GEO', raw_text) or ""
    text_military = extract_tag('MILITARY', raw_text) or ""
    text_section_5 = extract_tag('CONCLUSION', raw_text) or ""
    text_india = extract_tag('INDIA', raw_text) or ""
    text_wa = extract_tag('WEST_ASIA', raw_text) or ""
    text_final = extract_tag('FINAL_CONCLUSION', raw_text) or ""

    # 2. Render the massive form
    with st.form("editor_form"):
        st.markdown("### Edit Intelligence Text")
        new_sum = st.text_area("Executive Summary", text_summary, height=150)
        new_ews = st.text_area("Early Warning & Red Flags", text_ews, height=100)
        new_s1 = st.text_area("Global Foundry Market", text_section_1, height=150)
        new_s2 = st.text_area("AI Chip Demand", text_section_2, height=100)
        new_s3 = st.text_area("Critical Minerals", text_section_3, height=100)
        new_s4 = st.text_area("Export Controls", text_section_4, height=100)
        new_mil = st.text_area("Military & Outer Space", text_military, height=100)
        new_s5 = st.text_area("Lithography Chokepoints", text_section_5, height=150)
        new_india = st.text_area("India: Domestic & Strategic Developments", text_india, height=150)
        new_wa = st.text_area("West Asia: Domestic & Strategic Developments", text_wa, height=150)
        new_fin = st.text_area("Strategic Conclusion", text_final, height=150)
        
        st.markdown("### Edit Data Tables & KPIs")
        edited_kpi_df = st.data_editor(clean_dataframe(pd.DataFrame(dashboard_data.get('kpi_metrics', []))), num_rows="dynamic", use_container_width=True)
        edited_funding_df = st.data_editor(clean_dataframe(pd.DataFrame(dashboard_data.get('funding_data', []))), num_rows="dynamic", use_container_width=True)
        edited_market_df = st.data_editor(clean_dataframe(pd.DataFrame(dashboard_data.get('market_impact', []))), num_rows="dynamic", use_container_width=True)
        edited_risk_df = st.data_editor(clean_dataframe(pd.DataFrame(dashboard_data.get('supply_chain_risk', []))), num_rows="dynamic", use_container_width=True)
        edited_actions_df = st.data_editor(clean_dataframe(pd.DataFrame(dashboard_data.get('recent_actions', []))), num_rows="dynamic", use_container_width=True)
        
        if st.form_submit_button("💾 Save Vetted Intelligence"):
            clean_kpi = edited_kpi_df.fillna("")
            clean_actions = edited_actions_df.fillna("")
            clean_fund = edited_funding_df.fillna("")
            clean_market = edited_market_df.fillna("")
            clean_risk = edited_risk_df.fillna("")
            
            new_raw = f"<SUMMARY>\n{new_sum}\n</SUMMARY>\n\n<EWS>\n{new_ews}\n</EWS>\n\n<EXEC>\n{new_s1}\n</EXEC>\n\n<LITHO>\n{new_s2}\n</LITHO>\n\n<REE>\n{new_s3}\n</REE>\n\n<GEO>\n{new_s4}\n</GEO>\n\n<MILITARY>\n{new_mil}\n</MILITARY>\n\n<CONCLUSION>\n{new_s5}\n</CONCLUSION>\n\n<INDIA>\n{new_india}\n</INDIA>\n\n<WEST_ASIA>\n{new_wa}\n</WEST_ASIA>\n\n<FINAL_CONCLUSION>\n{new_fin}\n</FINAL_CONCLUSION>\n\n<KPI_METRICS>{clean_kpi.to_json(orient='records')}</KPI_METRICS>\n<FUNDING_DATA>{clean_fund.to_json(orient='records')}</FUNDING_DATA>\n<MARKET_IMPACT>{clean_market.to_json(orient='records')}</MARKET_IMPACT>\n<RISK_INDEX>{clean_risk.to_json(orient='records')}</RISK_INDEX>\n<ACTION_MATRIX>{clean_actions.to_json(orient='records')}</ACTION_MATRIX>"
            
            dashboard_data['brief_raw'] = new_raw
            dashboard_data['kpi_metrics'] = clean_kpi.to_dict(orient='records')
            dashboard_data['recent_actions'] = clean_actions.to_dict(orient='records')
            dashboard_data['funding_data'] = clean_fund.to_dict(orient='records')
            dashboard_data['market_impact'] = clean_market.to_dict(orient='records')
            dashboard_data['supply_chain_risk'] = clean_risk.to_dict(orient='records')
            
            if latest_filepath:
                with open(latest_filepath, 'w') as f:
                    json.dump(dashboard_data, f)
                
            st.cache_data.clear() 
            st.success("Changes permanently saved! Refreshing system...")
            time.sleep(1)
            st.rerun() 
            
    st.markdown("<br>", unsafe_allow_html=True)
    st.toggle("✏️ Enable Human-AI Vetting Mode (Edit Text & Data)", key="vetting_toggle")