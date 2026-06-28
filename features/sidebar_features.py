import streamlit as st
import os
import json

def render_sidebar(dashboard_data, df_actions, raw_text, text_india, text_wa):
    
    # ==========================================
    # 🎨 DYNAMIC HOVER BAR & SIDEBAR STYLING
    # ==========================================
    st.sidebar.markdown("""
    <style>
    /* 1. Ensure the sidebar background is pitch black */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }

    /* 2. Base styling for the navigation menu items */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label {
        position: relative;
        background-color: transparent !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        margin-bottom: 6px !important;
        border-radius: 6px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        overflow: hidden;
    }

    /* 3. Ensure Text remains purely white and bold */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        margin: 0 !important;
        z-index: 2;
        position: relative;
    }

    /* 4. THE FIX: Hide ONLY the inner radio circle securely without hiding the text */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-of-type > div:first-child:not([data-testid="stMarkdownContainer"]) {
        display: none !important;
    }
    
    /* Reset margins so the text correctly aligns to the left edge */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label > div:first-of-type > div[data-testid="stMarkdownContainer"] {
        margin-left: 0 !important;
    }

    /* 5. Create the Colorful Bar (Hidden by default) */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 5px;
        background: linear-gradient(180deg, #00bfff, #a855f7); /* Cyan to Purple Gradient */
        opacity: 0;
        transition: all 0.3s ease;
        border-radius: 4px;
    }

    /* 6. HOVER EFFECT: Soft reveal of the colorful bar + slight shift */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: linear-gradient(90deg, rgba(255, 255, 255, 0.05) 0%, transparent 100%) !important;
        transform: translateX(4px);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:hover::before {
        opacity: 0.6;
    }

    /* 7. SELECTED/ACTIVE EFFECT: Full vibrant bar + subtle background glow */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(90deg, rgba(0, 191, 255, 0.15) 0%, rgba(0,0,0,0) 100%) !important;
        transform: translateX(4px);
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked)::before {
        opacity: 1;
        width: 6px;
        box-shadow: 0 0 12px rgba(0, 191, 255, 0.8); /* Glowing neon effect */
    }

    /* 8. Force active/selected text to glow slightly */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) [data-testid="stMarkdownContainer"] p {
        text-shadow: 0 0 8px rgba(0, 191, 255, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.sidebar.image("logo.jpg", use_container_width=True)
    st.sidebar.markdown("""
    <div style='text-align: center; margin-top: -10px;'>
        <p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>A Semicon News Dashboard.</p>
        <p style='font-size: 14px; margin-bottom: 5px;'>Prepared by: Kashif Anwar</p>
        <p style='font-size: 13px; color: #00bfff; font-weight: bold; font-style: italic; margin-bottom: 0px;'>A Human-AI Vetted Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")

    st.sidebar.title("SemicoN Access")

    base_options = [
        "Executive Home",
        "Today's Snippet",
        "Weekly Tactical Brief",
        "Weekly Intelligence Brief",
        "West Asia Strategic Intel (Psyopoly)"
    ]

    # 🛑 THE FIX: "Weekly Archive" properly integrated into the trio
    archive_options = ["Daily Archive", "Weekly Archive", "Monthly Archive"]

    if st.session_state.get('role') == 'admin':
        st.sidebar.info("Access Level: **Administrator**")
        if st.sidebar.button("Logout"):
            st.session_state['role'] = None
            st.rerun()
        view_options = base_options + ["Trend Timelines"] + archive_options + ["Global Threat Intercept (ShadowBroker)", "Clean Archives", "Trash"]
    else:
        st.sidebar.info("Access Level: **Guest Viewer**")
        st.sidebar.caption("*(System Access Restricted)*")
        view_options = base_options + archive_options

    st.sidebar.markdown("---")
    view_selection = st.sidebar.radio("Strategic Navigation", view_options)
    st.sidebar.markdown("---")

    selected_actor = "All" 
    
    if view_selection in ["Weekly Tactical Brief", "Weekly Intelligence Brief"]:
        st.sidebar.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>Global Filter</p>", unsafe_allow_html=True)
        
        actor_set = set()
        
        strategic_taxonomy = [
            "United States", "US", "China", "Taiwan", "India", "Iran", "Russia", "Ukraine", "Israel", "Lebanon", "Germany", "Djibouti", "Thailand", "Eritrea", "Ethiopia",
            "Indo-Pacific", "West Asia", "Middle East", "MENA", "Africa", "Europe", "Americas", "Gaza", "Horn of Africa",
            "CISA", "DoD", "MoD", "State Department", "Ministry", "Government",
            "Trade deal", "Tariff", "Export controls", "Agreement", "Embargo", "Sanctions", "Summit", "Bilateral", "Multilateral", "Visit",
            "Semiconductor", "Rare Earth", "Lithography", "Tape-out", "Foundry", "Fabless", "TSMC", "ASML", "Nvidia", "SMIC", "Intel", "Samsung", "Lithium", "Indium", "Cobalt", "Aluminium", "Supply Chain", "Vulnerabilities", "Disruption", "Shortage",
            "AI", "Artificial Intelligence", "Anthropic", "OpenAI", "AI Chip",
            "Loan", "Subsidy", "Financial Assistance", "MoU", "MoC", "Funding", "Investment",
            "NATO", "UN", "BRICS", "SCO", "ASEAN", "BRI", "Hormuz mission",
            "Humanitarian", "Rights groups", "Peace deal", "War", "Conflict", "Incursion", "Attack", "Drone strike", "Confrontation", "Kinetic action", "Troop movements", "Clashes", "Tensions", "Flashpoints", "Brink-of-war", "Standoff", "Threat", "Volatility",
            "Shipping strait", "Maritime", "Port", "Naval", "Strait of Hormuz", "Malacca Strait", "Suez Canal", "Chokepoint"
        ]
        
        text_to_scan = ""
        
        if view_selection == "Weekly Intelligence Brief":
            text_to_scan = str(raw_text)
            
        elif view_selection == "Weekly Tactical Brief":
            from utils.snippet_templates import get_weekly_tactical_template
            tac_brief = get_weekly_tactical_template()
            text_to_scan = " ".join([str(tac_brief.get(k, '')) for k in ['bluf', 'executive_summary', 'risk_assessment', 'threat_narrative', 'predictive_analysis', 'recommendations', 'tactical_indicators']])

        lower_scan_pool = text_to_scan.lower()
        for keyword in strategic_taxonomy:
            if keyword.lower() in lower_scan_pool:
                actor_set.add(keyword)
        
        if view_selection == "Weekly Intelligence Brief" and dashboard_data and 'recent_actions' in dashboard_data:
            for row in dashboard_data['recent_actions']:
                for key in ['Actor', 'actor', 'Location', 'location']:
                    val = str(row.get(key, '')).strip()
                    if val and val.lower() not in ['unknown', 'none', 'system', 'global']:
                        for item in val.split(','):
                            clean_item = item.strip()
                            if len(clean_item) > 2 and clean_item.lower() in lower_scan_pool:
                                actor_set.add(clean_item)
                                
        actor_list = sorted(list(actor_set))
        
        selected_actor = st.sidebar.selectbox("🔍 Highlight & Filter by Keyword:", ["All"] + actor_list)
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