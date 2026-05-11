import streamlit as st
from utils.docx_generator import create_landscape_word

def render_document_controls(dashboard_data, latest_filepath, brief_date, text_summary, text_section_1, text_section_2, text_section_3, text_section_4, text_military, text_section_5, text_india, text_wa, text_final, text_ews):
    st.markdown("---")
    st.markdown("### Document Controls")
    
    if st.session_state['role'] == 'admin':
        bot_col1, bot_col2 = st.columns(2)
        with bot_col1:
            st.markdown("**🔗 Share Dashboard Link:**")
            st.code("https://www.semirare.in/", language="text")
        with bot_col2:
            st.markdown("**📄 Export Full Document:**")
            if latest_filepath:
                text_list = [text_summary, text_section_1, text_section_2, text_section_3, text_section_4, text_military, text_section_5, text_india, text_wa]
                word_file = create_landscape_word(
                    text_list, text_final, 
                    dashboard_data.get('recent_actions', []), 
                    brief_date, 
                    dashboard_data.get('funding_data', []), 
                    dashboard_data.get('market_impact', []), 
                    dashboard_data.get('supply_chain_risk', []),
                    dashboard_data.get('sources', []),
                    text_ews
                )
                
                st.download_button(
                    label="⬇️ Download Authentic Word Doc", data=word_file,
                    file_name=f"SemicoN Weekly Brief - {brief_date}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        if latest_filepath:
            st.markdown("---")
            st.markdown("### System Administration")
            st.toggle("✏️ Enable Human-AI Vetting Mode (Edit Text & Data)", key="vetting_toggle")
    
    else:
        st.markdown("**🔗 Share Dashboard Link:**")
        st.code("https://www.semirare.in/", language="text")