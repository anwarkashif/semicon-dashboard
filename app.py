import streamlit as st
import os
import warnings

# 🔇 AGGRESSIVE SYSTEM-LEVEL WARNING SUPPRESSION
# Kills PyArrow and GenAI deprecation warnings before Streamlit even boots
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["STREAMLIT_DATA_FRAME_SERIALIZATION"] = "legacy"
warnings.filterwarnings("ignore")

# ⚡ We ONLY import the lightweight UI elements at the top for an instant login load
from features.ui_features import inject_early_css, inject_global_theme, render_login_screen

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="SemicoN Dashboard", 
    page_icon="logo.jpg",  
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# ⬛ INSTANT SEAMLESS MASK
st.markdown(
    """
    <div id="top-of-page"></div>
    
    <style>
    /* Intercept the topmost browser layers immediately with your EXACT theme color */
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background-color: #0e1117 !important; 
    }
    
    /* Make the header transparent to keep the Sidebar Button, but hide the background */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Aggressively destroy ONLY the status widget (running man/stop button) */
    [data-testid="stStatusWidget"] {
        visibility: hidden !important;
        display: none !important;
        opacity: 0 !important;
    }

    /* 🚫 NUKE SKELETONS & DECORATIONS GLOBALLY FROM THE START */
    [data-testid="stSkeleton"], [data-testid="stDecoration"] {
        display: none !important;
        opacity: 0 !important;
        visibility: hidden !important;
    }
    
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
    st.markdown("""<style>.loading-pulse { display: none !important; }</style>""", unsafe_allow_html=True)
    render_login_screen()

else:
    # Dismiss the pre-loader text for authenticated users
    st.markdown("""<style>.loading-pulse { display: none !important; }</style>""", unsafe_allow_html=True)
    
    # ==========================================
    # ⬛ THE ABSOLUTE BLACKOUT MASK
    # ==========================================
    # Instantly throws a pure #0e1117 background over the entire screen the millisecond login occurs.
    # This completely hides any native Streamlit loading glitches or layout shifting underneath.
    st.markdown("""
        <div id="blackout-mask" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #0e1117; z-index: 9999999; display: flex; align-items: center; justify-content: center;">
            <div style="color: #444; font-family: 'Courier New', monospace; letter-spacing: 3px; font-size: 14px; animation: pulse 2.5s infinite;">
                SYNCING SECURE DATA STREAMS...
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 📦 HEAVY PATH: User is logged in. Now we load the heavy libraries and data.
    import pandas as pd
    import json
    import requests 
    import glob
    from google import genai
    
    from utils.data_helpers import clean_dataframe, extract_tag
    from features.advanced_features import render_threat_scoring, render_rag_interrogation, render_fab_chat
    from features.archive_features import render_trend_timelines, render_archives, render_clean_archives, render_trash
    from features.editor_features import render_vetting_editor
    from features.sidebar_features import render_sidebar
    from features.ui_features import render_splash_screen
    from features.weekly_orchestrator import render_full_weekly_brief
    from features.home_features import render_executive_home
    from features.snippet_features import render_daily_snippet
    from features.snippet_orchestrator import handle_snippet_logic
    from features.shadowbroker_features import render_shadowbroker
    from features.psyopoly_features import render_psyopoly_viewer  

    MAPBOX_PUBLIC_TOKEN = os.environ.get("MAPBOX_PUBLIC_TOKEN")
    if not MAPBOX_PUBLIC_TOKEN:
        try:
            MAPBOX_PUBLIC_TOKEN = st.secrets.get("MAPBOX_PUBLIC_TOKEN")
        except Exception:
            MAPBOX_PUBLIC_TOKEN = None

    # ==========================================
    # 🛠️ THE MAPBOX FAILSAFE INJECTION
    # ==========================================
    if MAPBOX_PUBLIC_TOKEN:
        # 1. Aggressively strip any accidental literal quotes or spaces from cloud environments
        MAPBOX_PUBLIC_TOKEN = str(MAPBOX_PUBLIC_TOKEN).strip(' "\'')
        
        # 2. Force inject it into the global OS environment. 
        # PyDeck natively hunts for 'MAPBOX_API_KEY' behind the scenes.
        os.environ["MAPBOX_API_KEY"] = MAPBOX_PUBLIC_TOKEN
    
    # Safe Environment Look-up (Primary Key for Snippet Feature)
    GEMINI_API_KEY = os.environ.get("RAG_GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        try:
            GEMINI_API_KEY = st.secrets.get("RAG_GEMINI_API_KEY")
        except Exception:
            GEMINI_API_KEY = None
            
    client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
    
    # ==========================================
    # 🛡️ 4-NODE API KEY CASCADING ARRAY
    # ==========================================
    rag_api_keys = []
    for key_name in ["RAG_GEMINI_API_KEY", "RAG_GEMINI_API_KEY_2", "RAG_GEMINI_API_KEY_3", "RAG_GEMINI_API_KEY_4"]:
        val = os.environ.get(key_name)
        if not val:
            try:
                val = st.secrets.get(key_name)
            except Exception:
                val = None
        if val:
            rag_api_keys.append(val)
            
    model_name = 'gemini-2.5-flash'

    # ==========================================
    # --- DYNAMIC CLOUD DATA ENGINE (GitHub Real-Time Stream) ---
    # ==========================================
    # To prevent Hugging Face from freezing or getting out of sync with your automated cron-jobs,
    # this engine streams data directly from GitHub into the container space with a 60-second window.
    
    GITHUB_REPO = "anwarkashif/semicon-dashboard"
    
    GITHUB_PAT = os.environ.get("GITHUB_PAT") 
    if not GITHUB_PAT:
        try:
            GITHUB_PAT = st.secrets.get("GITHUB_PAT")
        except Exception:
            GITHUB_PAT = None
            
    auth_headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}

    @st.cache_data(ttl=60, show_spinner=False)
    def stream_pipeline_data_to_disk():
        """Downloads the latest telemetry across all subfolders directly from GitHub."""
        files_to_sync = [
            'tactical_events_24h.json',
            'rss_accumulator.txt',
            'live_alert.json',
            'sitrep_history.json',
            'weekly_tactical_live.json',
            'executive_home/tactical_events_24h.json',
            'executive_home/flush_brief_24h.json',
            'today_snippet/tactical_events_24h.json',
            'today_snippet/shift_brief.json',
            'friday_snippet/tactical_events_24h.json'
        ]
        
        for filename in files_to_sync:
            url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/data/{filename}"
            try:
                resp = requests.get(url, headers=auth_headers, timeout=5)
                if resp.status_code == 200:
                    local_path = f"data/{filename}"
                    # Ensure the subfolder path exists inside the container before writing
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(resp.text)
            except Exception:
                pass

        # Dynamically discover and pull the newest weekly brief file name from GitHub contents API
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/data"
        try:
            resp = requests.get(api_url, headers=auth_headers, timeout=5)
            if resp.status_code == 200:
                files = resp.json()
                brief_files = [f for f in files if f['name'].startswith('brief_') and f['name'].endswith('.json')]
                if brief_files:
                    brief_files.sort(key=lambda x: x['name'])
                    latest_brief = brief_files[-1]
                    b_resp = requests.get(latest_brief['download_url'], headers=auth_headers, timeout=5)
                    if b_resp.status_code == 200:
                        with open(f"data/{latest_brief['name']}", 'w', encoding='utf-8') as f:
                            f.write(b_resp.text)
                        return f"data/{latest_brief['name']}"
        except Exception:
            pass

        # Local fallback if network check fails
        local_files = glob.glob('data/brief_*.json')
        if local_files:
            local_files.sort()
            return local_files[-1]
        return None

    @st.cache_data(ttl=60, show_spinner=False) 
    def load_data(filepath):
        if not filepath: return None
        try:
            with open(filepath, 'r', encoding='utf-8') as f: 
                return json.load(f)
        except Exception:
            return None

    @st.cache_data(ttl=60, show_spinner=False)
    def load_live_tactical_data():
        filepath = 'data/tactical_events_24h.json'
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f: 
                    return json.load(f)
            except Exception:
                return None
        return None

    # Execute the streaming synchronization pass silently (No Spinner to prevent layout flashes)
    latest_filepath = stream_pipeline_data_to_disk()
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

    # ==========================================
    # --- NATIVE TRAIL NEWS / TICKER TAPE ENGINE ---
    # ==========================================
    def parse_rss_txt_file():
        import urllib.parse
        rss_dict = {}
        filepath = 'data/rss_accumulator.txt'
        if not os.path.exists(filepath): return rss_dict

        current_reg = None
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith("---") and "DOMAIN-FORCED NEWS" in line:
                    reg = line.replace("---", "").replace("DOMAIN-FORCED NEWS", "").strip()
                    if "Middle East" in reg: reg = "West Asia/Middle East"
                    current_reg = reg
                    if current_reg not in rss_dict:
                        rss_dict[current_reg] = []
                elif line.startswith("- [") and current_reg:
                    try:
                        d_end = line.find("]")
                        date_str = line[3:d_end]
                        title_str = line[d_end+1:].strip()
                        
                        clean_search = title_str.replace("🔴", "").replace("🟠", "").replace("🟡", "").replace("CRITICAL:", "").replace("ELEVATED:", "").replace("WATCH:", "").replace("LIVE WARNING:", "").strip()
                        search_query = urllib.parse.quote_plus(clean_search)
                        news_link = f"https://news.google.com/search?q={search_query}"

                        if not any(x['title'] == title_str for x in rss_dict[current_reg]):
                            rss_dict[current_reg].append({
                                "title": title_str, 
                                "published": date_str, 
                                "link": news_link, 
                                "is_24h": True
                            })
                    except Exception: pass
        return rss_dict

    def render_ticker_tape():
        ticker_items = []
        try:
            live_rss = parse_rss_txt_file()
            if not live_rss: return
            
            seen_titles = set()
            unique_news = []
            for region, articles in live_rss.items():
                for art in articles:
                    if art['title'] not in seen_titles and art.get('is_24h', False):
                        seen_titles.add(art['title'])
                        unique_news.append(art)

            unique_news = unique_news[-30:]

            critical = ['ban', 'sanction', 'shortage', 'escalation', 'military', 'war', 'blockade', 'strike', 'chokepoint', 'threat', 'breach', 'crisis']
            high = ['tariff', 'control', 'restrict', 'vulnerability', 'disrupt', 'tension', 'export control', 'embargo', 'risk']
            med = ['delay', 'subsidy', 'compete', 'invest', 'shift', 'policy', 'regulate', 'pressure', 'concern', 'geopolitical']

            for item in unique_news:
                title_lower = item['title'].lower()
                score = 3
                score += sum(1 for kw in critical if kw in title_lower) * 5
                score += sum(1 for kw in high if kw in title_lower) * 3
                score += sum(1 for kw in med if kw in title_lower) * 2
                score = min(10, score)
                
                if score >= 5:
                    if score >= 9:
                        prefix = "🔴 CRITICAL:"
                    elif score >= 7:
                        prefix = "🟠 ELEVATED:"
                    else:
                        prefix = "🟡 WATCH:"
                    
                    clean_title = item.get("title", "").replace('"', '&quot;').replace("'", "&#39;")
                    ticker_html = f'<div class="ticker-item"><a href="{item.get("link", "#")}" target="_blank">{prefix} {clean_title}</a></div>'
                    ticker_items.append(ticker_html)
                    
        except Exception: pass

        if not ticker_items: return
        all_items_html = "".join(ticker_items)

        dynamic_duration = max(20, len(ticker_items) * 10 + 15)

        ticker_code = f"""
        <style>
        .ticker-wrap {{
            position: fixed;
            top: 60px;
            left: 0;
            width: 100vw;
            height: 42px;
            background-color: #050505;
            border: none !important;
            box-shadow: none !important;
            z-index: 990; 
            overflow: hidden;
            display: flex;
            align-items: center;
        }}
        .block-container {{
            padding-top: 110px !important; 
        }}
        .ticker-move {{
            display: flex;
            width: fit-content;
            animation: ticker {dynamic_duration}s linear infinite;
        }}
        .ticker-track {{
            display: flex;
            white-space: nowrap;
        }}
        .ticker-move:hover {{
            animation-play-state: paused;
        }}
        @keyframes ticker {{
            0% {{ transform: translate3d(0, 0, 0); }}
            100% {{ transform: translate3d(-50%, 0, 0); }}
        }}
        .ticker-item {{
            display: inline-block;
            margin-right: 60px;
            font-family: "Courier New", monospace;
            font-weight: bold;
            font-size: 14px;
            letter-spacing: 0.5px;
        }}
        .ticker-item a {{
            text-decoration: none;
            color: #ffffff !important;
        }}
        .ticker-item a:hover {{
            text-decoration: underline;
            opacity: 0.8;
        }}
        </style>
        <div class="ticker-wrap">
            <div class="ticker-move">
                <div class="ticker-track">{all_items_html}</div>
                <div class="ticker-track">{all_items_html}</div>
            </div>
        </div>
        """
        st.markdown(ticker_code, unsafe_allow_html=True)

    # ==========================================
    # 🟢 LIFT THE BLACKOUT MASK
    # ==========================================
    # Destroys the pure black mask cleanly just before the dashboard renders
    st.markdown("""
        <style>
        #blackout-mask { 
            display: none !important; 
            opacity: 0 !important; 
            visibility: hidden !important; 
        }
        </style>
    """, unsafe_allow_html=True)

    # --- DASHBOARD RENDERING ---
    render_splash_screen()
    
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

    # 🟢 RENDER TICKER TAPE PLACE EXACTLY HERE 🟢
    # 🚀 EXCLUDE TICKER FROM PSYOPOLY TO PREVENT LAG/OVERLAP
    if view_selection != "West Asia Strategic Intel (Psyopoly)":
        render_ticker_tape()

    # 🚀 INJECT SCROLL-TO-TOP BUTTON (EXCLUDING SPECIFIC SECTIONS)
    if view_selection not in ["Trend Timelines", "Archives"]:
        st.markdown(
            """
            <style>
            .scroll-top-btn {
                position: fixed;
                bottom: 25px;
                left: 50%;
                transform: translateX(-50%);
                background-color: rgba(255, 255, 255, 0.15); 
                color: #ffffff !important; 
                width: 45px;
                height: 45px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 22px;
                font-weight: bold;
                text-decoration: none;
                backdrop-filter: blur(5px); 
                -webkit-backdrop-filter: blur(5px);
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                z-index: 999990; 
                border: 1px solid rgba(255, 255, 255, 0.3);
                transition: background-color 0.3s ease, transform 0.2s ease;
            }
            .scroll-top-btn:hover {
                background-color: rgba(255, 255, 255, 0.35);
                transform: translateX(-50%) translateY(-3px);
            }
            </style>
            <a href="#top-of-page" target="_self" class="scroll-top-btn" title="Scroll to Top">↑</a>
            """,
            unsafe_allow_html=True
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
            
    elif view_selection == "West Asia Strategic Intel (Psyopoly)":
        render_psyopoly_viewer(df_actions)

    elif view_selection == "Global Threat Intercept (ShadowBroker)":
        render_shadowbroker()
            
    elif view_selection == "Quantitative Threat Scoring":
        render_threat_scoring()
        
    elif view_selection == "Intelligence Interrogation (RAG)":
        render_rag_interrogation(
            rag_api_keys, 
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
        rag_api_keys, 
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