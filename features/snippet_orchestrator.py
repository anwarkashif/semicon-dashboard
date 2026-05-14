import streamlit as st
from utils.snippet_templates import get_friday_2_0_template
from utils.snippet_docx_generator import generate_snippet_2_0_docx

def handle_snippet_logic(mode="friday"):
    if mode == "friday":
        render_friday_snippet_2_0()
    else:
        st.error("Unknown Snippet Mode Requested.")

def render_friday_snippet_2_0():
    intel_data = get_friday_2_0_template()
    
    st.markdown(f"""
    <div style='text-align: center; border-bottom: 3px solid #00bfff; padding-bottom: 10px; margin-bottom: 20px;'>
        <h1 style='color: #ffffff; font-size: 2.5em; margin-bottom: 0px;'>{intel_data.get('title', "Friday's Snippet 2.0")}</h1>
        <p style='color: #00bfff; font-family: monospace; font-size: 1.1em; letter-spacing: 1px; margin-top: 5px;'>
            DATE: {intel_data.get('date', '')} | {intel_data.get('classification', 'UNCLASSIFIED')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. NEW BLUF STRUCTURE
    st.markdown("### 🎯 BLUF (Bottom Line Up Front)")
    st.warning(intel_data.get('bluf', 'Pending generation...'))

    # 2. INDICATORS
    st.markdown("### 🚩 Tactical Indicators")
    if isinstance(intel_data.get('tactical_indicators'), list):
        for ind in intel_data['tactical_indicators']:
            st.markdown(f"{ind.replace('**', '**')}") # Allow native markdown bolding
    else:
        st.markdown(intel_data.get('tactical_indicators', 'No indicators provided.'))
        
    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    # 3. DEEP ANALYSIS
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Executive Summary")
        st.info(intel_data.get('executive_summary', ''))
        
        st.markdown("### ⚖️ Risk Assessment")
        st.markdown(intel_data.get('risk_assessment', ''))

    with col2:
        st.markdown("### 🕸️ Threat Narrative")
        st.markdown(intel_data.get('threat_narrative', ''))
        
        st.markdown("### 🔭 Predictive Analysis")
        st.error(intel_data.get('predictive_analysis', ''))
        
    st.markdown("### 🛡️ Strategic Recommendations")
    st.success(intel_data.get('recommendations', ''))

    # --- FOOTER & DOWNLOAD ---
    st.markdown("<hr style='border: 1px solid #333; margin-top: 30px;'>", unsafe_allow_html=True)
    colA, colB = st.columns([3, 1])
    with colA:
        st.caption("This intelligence product integrates OSINT feeds, weekly geopolitical briefs, and autonomous risk assessments.")
    with colB:
        try:
            docx_buffer = generate_snippet_2_0_docx(intel_data)
            st.download_button(label="📥 Download Friday's Snippet (DOCX)", data=docx_buffer, file_name=f"Fridays_Snippet.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", type="primary", use_container_width=True)
        except Exception as e:
            st.button("📥 Download Unavailable", disabled=True)