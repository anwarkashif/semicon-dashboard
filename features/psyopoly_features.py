import streamlit as st
import streamlit.components.v1 as components

def render_psyopoly_viewer():
    st.markdown(
    """
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        width: 100%;
        font-size: 20px;
        font-weight: 600;
        margin: 20px 0;
    ">
        Live operational overlay from the Psyopoly Middle East intelligence desk.
    </div>
    """,
    unsafe_allow_html=True
)
    st.markdown("---")
    
    # Renders the live website securely inside your dashboard
    components.iframe("https://www.psyopoly.pro/middle-east", height=850, scrolling=True)