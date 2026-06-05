import streamlit as st
import streamlit.components.v1 as components

def render_psyopoly_viewer():
    st.markdown("## 🌍 West Asia Strategic Intel (Psyopoly)")
    st.markdown("Live operational overlay from the Psyopoly Middle East intelligence desk.")
    st.markdown("---")
    
    # Renders the live website securely inside your dashboard
    components.iframe("https://www.psyopoly.pro/middle-east", height=850, scrolling=True)