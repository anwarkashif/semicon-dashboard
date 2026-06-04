import streamlit as st

def render_sidebar(dashboard_data, df_actions, raw_text, text_india, text_wa):
    st.sidebar.image("logo.jpg", use_container_width=True)
    st.sidebar.markdown("""
    <div style='text-align: center; margin-top: -10px;'>
        <p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>A Semicon News Dashboard.</p>
        <p style='font-size: 14px; margin-bottom: 5px;'>Prepared by: Kashif Anwar</p>
        <p style='font-size: 13px; color: #00bfff; font-weight: bold; font-style: italic; margin-bottom: 0px;'>A Human-AI Vetted Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    st.sidebar.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>Global Filter</p>", unsafe_allow_html=True)
    
    actor_list = []
    if not df_actions.empty and 'Actor' in df_actions.columns:
        actor_list = [a for a in df_actions['Actor'].dropna().unique().tolist() if str(a).strip()]
    
    selected_actor = st.sidebar.selectbox("🔍 Highlight & Filter by Actor:", ["All"] + sorted(actor_list))
    st.sidebar.markdown("---")

    st.sidebar.title("SemicoN Access")

    # Define the base strategic sequence for EVERYONE (ShadowBroker removed)
    base_options = [
        "Executive Home",
        "Today's Snippet",
        "Weekly Tactical Brief",
        "Weekly Intelligence Brief",
        "Trend Timelines",
        "Archives"
    ]

    if st.session_state.get('role') == 'admin':
        st.sidebar.info("Access Level: **Administrator**")
        if st.sidebar.button("Logout"):
            st.session_state['role'] = None
            st.rerun()
        # Admin gets everything: Base + ShadowBroker + Clean Archives + Trash
        view_options = base_options + ["Global Threat Intercept (ShadowBroker)", "Clean Archives", "Trash"]
    else:
        st.sidebar.info("Access Level: **Guest Viewer**")
        st.sidebar.caption("*(System Access Restricted)*")
        view_options = base_options

    st.sidebar.markdown("---")
    view_selection = st.sidebar.radio("Strategic Navigation", view_options)
    st.sidebar.markdown("---")

    st.sidebar.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>Regions Covered</p>", unsafe_allow_html=True)
    
    region_checks = {
        "Asia": ["**Asia:**", text_india], 
        "Middle East/West Asia": ["**Middle East/West Asia:**", text_wa],
        "Africa": ["**Africa:**"],
        "Europe": ["**Europe:**"],
        "Americas": ["**Americas:**"],
        "Oceania": ["**Oceania:**"]
    }
    
    for r, indicators in region_checks.items():
        is_covered = False
        for ind in indicators:
            if ind and len(ind.strip()) > 5: 
                is_covered = True
            elif ind in raw_text: 
                is_covered = True
                
        if is_covered:
            st.sidebar.markdown(f"✅ {r}")
        else:
            st.sidebar.markdown(f"➖ <span style='color:grey'>{r}</span>", unsafe_allow_html=True)
            
    st.sidebar.markdown("---")
    with st.sidebar.expander("🧠 Key Concepts Explained"):
        st.markdown("""
        **EUV Lithography:** Extreme Ultraviolet Lithography. The cutting-edge tech used to print the most advanced microchips.  
        **Tape-out:** The final design phase for integrated circuits before manufacturing begins.  
        **Foundry:** A specialized factory where semiconductor chips are manufactured (e.g., TSMC).  
        **Rare Earth Elements (REEs):** 17 metallic elements crucial for high-tech, defense, and green energy products.  
        **Fabless:** Companies that design chips but outsource manufacturing (e.g., Nvidia, Apple, AMD).
        """)

    return selected_actor, view_selection