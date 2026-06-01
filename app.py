import streamlit as st
import os

# ⚡ We ONLY import the lightweight UI elements at the top for an instant login load
from features.ui_features import inject_early_css, inject_global_theme, render_login_screen

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="SemicoN Dashboard", 
    page_icon="🛡️",  
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ⬛ INSTANT SEAMLESS MASK (Color-matched to config.toml #0e1117)
st.markdown(
    """
    <style>
    /* Intercept the topmost browser layers immediately with your EXACT theme color */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0e1117 !important; 
    }
    
    /* Aggressively destroy Streamlit's native header, running man, and status widgets */
    header, [data-testid="stHeader"], [data-testid="stStatusWidget"], .st-emotion-cache-1avcm0n {
        visibility: hidden !important;
        display: none !important;
        opacity: 0 !important;
    }
    
    /* Elegant pulse text initialization */
    @keyframes pulse {
        0% { opacity: 0.2; }
        50% { opacity: 0.7; }
        100% { opacity: 0.2; }
    }
    .loading-pulse {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: #666666;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        letter-spacing: 3px;
        animation: pulse 2.5s infinite;
        z-index: 99999;
        pointer-events: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Only show the initial loading state text if authentication is unverified
if 'role' not in st.session_state or st.session_state['role'] is None:
    st.markdown("<div class='loading-pulse'>ESTABLISHING SECURE CONNECTION...</div>", unsafe_allow_html=True)

if 'role' not in st.session_state: 
    st.session_state['role'] = None

# ==========================================
# 2. EARLY CSS ROUTING & THEME
# ==========================================
inject_early_css(st.session_state['role'])

# ==========================================
# 3. APP CONFIGURATION & FOLDERS
# ==========================================
MAINTENANCE_MODE = False
if MAINTENANCE_MODE:
    st.markdown("""<style>[data-testid="stSidebar"] { display: none; }</style>""", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 15vh;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try: st.image("logo.jpg", width=300)
        except: pass
        st.warning("⚠️ **Warning: Work in Progress.** Please wait, the Dashboard will be live soon.")
    st.stop()

SNIPPET_TEST_MODE = False

os.makedirs('data', exist_ok=True)
os.makedirs('trash', exist_ok=True)

inject_global_theme()

# ==========================================
# 4. MAIN ROUTING & LAZY LOADING
# ==========================================
if st.session_state['role'] is None:
    # ⚡ FAST PATH: The user is not logged in. Render login instantly.
    
    # Dismiss the pre-loader text smoothly right before drawing elements
    st.markdown("""<style>.loading-pulse { display: none !important; }</style>""", unsafe_allow_html=True)
    render_login_screen()

else:
    # Dismiss the pre-loader text for authenticated users
    st.markdown("""<style>.loading-pulse { display: none !important; }</style>""", unsafe_allow_html=True)
    
    # 📦 HEAVY PATH: User is logged in. Now we load the heavy libraries and data.
    import pandas as pd
    import glob
    import json
    from google import genai
    
    from utils.data_helpers import clean_dataframe, extract_tag
    from features.daily_features import render_ticker_tape
    from features.advanced_features import render_threat_scoring, render_rag_interrogation, render_fab_chat
    from features.archive_features import render_trend_timelines, render_archives, render_clean_archives, render_trash
    from features.editor_features import render_vetting_editor
    from features.sidebar_features import render_sidebar
    from features.ui_features import render_splash_screen
    from features.weekly_orchestrator import render_full_weekly_brief
    from features.home_features import render_executive_home
    from features.snippet_features import render_daily_snippet
    from features.snippet_orchestrator import handle_snippet_logic

    MAPBOX_PUBLIC_TOKEN = "pk.eyJ1Ijoia2FzaGlmYW53YXIiLCJhIjoiY21td2loemd2Mm10MzJycXh4aTd1YjZtdCJ9.EN4o_kXPmA8ScOimJyf53A"
    
    # Safe Environment Look-up
    GEMINI_API_KEY = os.environ.get("RAG_GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        try:
            GEMINI_API_KEY = st.secrets.get("RAG_GEMINI_API_KEY")
        except Exception:
            GEMINI_API_KEY = None
            
    client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
    model_name = 'gemini-2.5-flash'

    # --- DATA LOADING ---
    def get_latest_file():
        if not os.path.exists('data'): return None
        files = glob.glob('data/brief_*.json')
        if not files: return None
        files.sort() 
        return files[-1]

    latest_filepath = get_latest_file()

    @st.cache_data(ttl=30) 
    def load_data(filepath):
        if not filepath: return None
        with open(filepath, 'r') as f: return json.load(f)

    @st.cache_data(ttl=60)
    def load_live_tactical_data():
        filepath = 'data/tactical_events_24h.json'
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                return None
        return None

    dashboard_data = load_data(latest_filepath)
    live_tactical_data = load_live_tactical_data()

    if dashboard_data:
        brief_date = dashboard_data.get('date', 'Unknown')
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
    else:
        brief_date = "Unknown"
        raw_text = ""
        text_summary = text_ews = text_section_1 = text_section_2 = text_section_3 = text_section_4 = text_military = text_section_5 = text_india = text_wa = text_final = ""

    # --- DASHBOARD RENDERING ---
    render_splash_screen()
    render_ticker_tape()
    
    if SNIPPET_TEST_MODE:
        st.sidebar.info("🛠️ **Snippet Test Mode Active**")

    df_actions_weekly = clean_dataframe(pd.DataFrame(dashboard_data.get('recent_actions', []) if dashboard_data else []))

    if live_tactical_data is not None:
        if isinstance(live_tactical_data, list):
            df_actions = clean_dataframe(pd.DataFrame(live_tactical_data))
        else:
            df_actions = clean_dataframe(pd.DataFrame(live_tactical_data.get('recent_actions', [])))
    else:
        df_actions = df_actions_weekly

    selected_actor, view_selection = render_sidebar(
        dashboard_data, df_actions, raw_text, text_india, text_wa
    )

    if view_selection == "Executive Home":
        render_executive_home(dashboard_data, df_actions, live_tactical_data, MAPBOX_PUBLIC_TOKEN)

    elif view_selection == "Today's Snippet":
        text_sections = [
            text_summary, text_section_1, text_section_2, text_section_3, 
            text_section_4, text_military, text_india, text_wa, text_final
        ]
        render_daily_snippet(df_actions, client=client, model_name=model_name, dashboard_data=dashboard_data, text_sections=text_sections)

    elif view_selection == "Weekly Tactical Brief":
        handle_snippet_logic(
            mode="weekly_tactical",
            dashboard_data=dashboard_data,
            text_summary=text_summary,
            text_section_1=text_section_1,
            text_section_2=text_section_2,
            text_section_3=text_section_3,
            text_section_4=text_section_4,
            text_military=text_military,
            text_india=text_india,
            text_wa=text_wa,
            text_ews=text_ews,
            selected_actor=selected_actor,
            df_actions=df_actions
        )
        
    elif view_selection == "Weekly Intelligence Brief":
        is_editing = st.session_state.get('vetting_toggle', False)
            
        if is_editing and st.session_state.get('role') == 'admin':
            render_vetting_editor(dashboard_data, latest_filepath)
        else:
            render_full_weekly_brief(
                dashboard_data, latest_filepath, brief_date, text_summary, 
                text_section_1, text_section_2, text_section_3, text_section_4, 
                text_military, text_section_5, text_india, text_wa, text_final, text_ews,
                selected_actor, df_actions, MAPBOX_PUBLIC_TOKEN
            )
            
    elif view_selection == "Quantitative Threat Scoring":
        render_threat_scoring()
        
    elif view_selection == "Intelligence Interrogation (RAG)":
        render_rag_interrogation(
            client, 
            model_name, 
            text_summary=text_summary, 
            text_section_1=text_section_1, 
            text_section_2=text_section_2, 
            text_section_3=text_section_3, 
            text_section_4=text_section_4, 
            text_military=text_military, 
            text_india=text_india, 
            text_wa=text_wa, 
            text_ews=text_ews
        )

    elif view_selection == "Trend Timelines":
        render_trend_timelines()

    elif view_selection == "Archives":
        render_archives()

    elif view_selection == "Clean Archives" and st.session_state['role'] == 'admin':
        render_clean_archives()
            
    elif view_selection == "Trash" and st.session_state['role'] == 'admin':
        render_trash()

    render_fab_chat(
        client, 
        model_name, 
        text_summary=text_summary, 
        text_section_1=text_section_1, 
        text_section_2=text_section_2, 
        text_section_3=text_section_3, 
        text_section_4=text_section_4, 
        text_military=text_military, 
        text_india=text_india, 
        text_wa=text_wa, 
        text_ews=text_ews
    )