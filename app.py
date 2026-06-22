import streamlit as st
import os
import warnings

# 🔇 AGGRESSIVE SYSTEM-LEVEL WARNING SUPPRESSION
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["STREAMLIT_DATA_FRAME_SERIALIZATION"] = "legacy"
warnings.filterwarnings("ignore")

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

# ⬛ DEFAULT UI RESET CSS
st.markdown(
    """
    <div id="top-of-page"></div>
    <style>
    html, body, [data-testid="stAppViewContainer"], .stApp { background-color: #0e1117 !important; }
    [data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stStatusWidget"] { visibility: hidden !important; display: none !important; opacity: 0 !important; }
    [data-testid="stSkeleton"], [data-testid="stDecoration"] { display: none !important; opacity: 0 !important; visibility: hidden !important; }
    @keyframes pulse { 0% { opacity: 0.2; } 50% { opacity: 0.7; } 100% { opacity: 0.2; } }
    .loading-pulse {
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        color: #666666; font-family: 'Courier New', monospace; font-size: 13px;
        letter-spacing: 3px; animation: pulse 2.5s infinite; z-index: 99999; pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True
)

if 'role' not in st.session_state or st.session_state['role'] is None:
    st.markdown("<div class='loading-pulse'>ESTABLISHING SECURE CONNECTION...</div>", unsafe_allow_html=True)
    st.session_state['role'] = None

inject_early_css(st.session_state['role'])

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
    st.markdown("""<style>.loading-pulse { display: none !important; }</style>""", unsafe_allow_html=True)
    
    # 🌌 VERTICAL GEMINI LOGIN WAVE (DESKTOP LEFT-SIDE ONLY)
    st.markdown(
        """
        <div class="login-ambient-container">
            <div class="login-blob blob-a"></div>
            <div class="login-blob blob-b"></div>
            <div class="login-blob blob-c"></div>
            <div class="login-blob blob-4"></div>
            <div class="login-blob blob-5"></div>
        </div>
        <style>
        .login-ambient-container { position: fixed; top: 0; left: 0; width: 50vw; height: 100vh; z-index: 99999; pointer-events: none; overflow: hidden; mix-blend-mode: screen; mask-image: linear-gradient(to right, rgba(0,0,0,1) 30%, rgba(0,0,0,0) 100%); -webkit-mask-image: linear-gradient(to right, rgba(0,0,0,1) 30%, rgba(0,0,0,0) 100%); }
        @media (max-width: 992px) { .login-ambient-container { display: none !important; } }
        .login-blob { position: absolute; filter: blur(100px); opacity: 0.8; border-radius: 50%; mix-blend-mode: screen; }
        .blob-a { top: -10vh; left: -10vw; width: 50vw; height: 75vh; background: #1b60d4; animation: waveA 4s infinite alternate ease-in-out; }
        .blob-b { top: 30vh; right: -5vw; width: 45vw; height: 80vh; background: #7f3ab7; animation: waveB 4s infinite alternate ease-in-out; }
        .blob-c { top: 50vh; left: -5vw; width: 45vw; height: 60vh; background: #d44c5c; animation: waveC 4s infinite alternate ease-in-out; }
        .blob-4 { top: 30px; left: 5vw; width: 50vw; height: 220px; background: #FF272A; animation: waveA 5s infinite alternate ease-in-out; animation-delay: -1s; }
        .blob-5 { top: -10px; left: 15vw; width: 55vw; height: 250px; background: #0ADD08; animation: waveB 6s infinite alternate ease-in-out; animation-delay: -3.5s; }
        @keyframes waveA { 0% { transform: translate(0, 0) scale(1); } 50% { transform: translate(12vw, 15vh) scale(1.15); } 100% { transform: translate(-5vw, 20vh) scale(0.9); } }
        @keyframes waveB { 0% { transform: translate(0, 0) scale(1); } 50% { transform: translate(-10vw, -15vh) scale(0.85); } 100% { transform: translate(8vw, -20vh) scale(1.1); } }
        @keyframes waveC { 0% { transform: translate(0, 0) scale(1); } 50% { transform: translate(15vw, -10vh) scale(1.1); } 100% { transform: translate(-10vw, 10vh) scale(0.95); } }
        </style>
        """, unsafe_allow_html=True
    )
    
    render_login_screen()

else:
    # --- STAGE 2: LOGGED IN ---
    st.markdown("""<style>.loading-pulse { display: none !important; }</style>""", unsafe_allow_html=True)
    
    if 'dashboard_entered' not in st.session_state:
        st.session_state['dashboard_entered'] = False

    # ==========================================
    # ⚡ INSTANT TRANSITION SPLASH SCREEN
    # ==========================================
    # This prevents the Command Centre from graying/dimming out while the backend loads Executive Home.
    if st.session_state.get('just_entered', False):
        st.markdown("""
        <div id="instant-splash" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: #0e1117; z-index: 9999999; display: flex; align-items: center; justify-content: center; flex-direction: column;">
            <div style="color: #00bfff; font-family: 'Courier New', monospace; font-size: 26px; font-weight: bold; letter-spacing: 2px; margin-bottom: 25px;">
                Welcome to SemicoN Dashboard...
            </div>
            <div style="width: 250px; height: 3px; background: #333; position: relative; overflow: hidden; border-radius: 2px;">
                <div style="position: absolute; top: 0; left: 0; height: 100%; width: 40%; background: #00bfff; animation: loadingLine 1s infinite linear;"></div>
            </div>
        </div>
        <style>
        @keyframes loadingLine { 0% { left: -40%; } 100% { left: 100%; } }
        #instant-splash { animation: hideInstantSplash 0.5s ease-in-out forwards; animation-delay: 2.5s; }
        @keyframes hideInstantSplash { to { opacity: 0; visibility: hidden; } }
        /* PREVENT STREAMLIT FROM DIMMING THE PREVIOUS UI */
        [data-testid="stAppViewContainer"] { transition: none !important; opacity: 1 !important; filter: none !important; }
        </style>
        """, unsafe_allow_html=True)
        # Turn it off instantly so it doesn't replay during normal dashboard usage
        st.session_state['just_entered'] = False

    # ⬛ INJECT SYNCING MASK ONLY IF THEY HAVEN'T ENTERED COMMAND CENTER YET
    if not st.session_state['dashboard_entered']:
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
    from features.weekly_orchestrator import render_full_weekly_brief
    from features.home_features import render_executive_home
    from features.snippet_features import render_daily_snippet
    from features.snippet_orchestrator import handle_snippet_logic
    from features.shadowbroker_features import render_shadowbroker
    from features.psyopoly_features import render_psyopoly_viewer  

    MAPBOX_PUBLIC_TOKEN = os.environ.get("MAPBOX_PUBLIC_TOKEN")
    if not MAPBOX_PUBLIC_TOKEN:
        try: MAPBOX_PUBLIC_TOKEN = st.secrets.get("MAPBOX_PUBLIC_TOKEN")
        except Exception: MAPBOX_PUBLIC_TOKEN = None

    if MAPBOX_PUBLIC_TOKEN:
        MAPBOX_PUBLIC_TOKEN = str(MAPBOX_PUBLIC_TOKEN).strip(' "\'')
        os.environ["MAPBOX_API_KEY"] = MAPBOX_PUBLIC_TOKEN
    
    GEMINI_API_KEY = os.environ.get("RAG_GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        try: GEMINI_API_KEY = st.secrets.get("RAG_GEMINI_API_KEY")
        except Exception: GEMINI_API_KEY = None
            
    client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
    
    rag_api_keys = []
    for key_name in ["RAG_GEMINI_API_KEY", "RAG_GEMINI_API_KEY_2", "RAG_GEMINI_API_KEY_3", "RAG_GEMINI_API_KEY_4"]:
        val = os.environ.get(key_name)
        if not val:
            try: val = st.secrets.get(key_name)
            except Exception: val = None
        if val: rag_api_keys.append(val)
            
    model_name = 'gemini-2.5-flash'

    GITHUB_REPO = "anwarkashif/semicon-dashboard"
    GITHUB_PAT = os.environ.get("GITHUB_PAT") 
    if not GITHUB_PAT:
        try: GITHUB_PAT = st.secrets.get("GITHUB_PAT")
        except Exception: GITHUB_PAT = None
            
    auth_headers = {"Authorization": f"token {GITHUB_PAT}"} if GITHUB_PAT else {}

    @st.cache_data(ttl=60, show_spinner=False)
    def stream_pipeline_data_to_disk():
        files_to_sync = [
            'tactical_events_24h.json', 'rss_accumulator.txt', 'live_alert.json', 'sitrep_history.json',
            'weekly_tactical_live.json', 'executive_home/tactical_events_24h.json', 'executive_home/flush_brief_24h.json',
            'today_snippet/tactical_events_24h.json', 'today_snippet/shift_brief.json', 'friday_snippet/tactical_events_24h.json'
        ]
        
        for filename in files_to_sync:
            local_path = f"data/{filename}"
            
            # 🛡️ DATA PROTECTION SHIELD
            # Prevents GitHub's empty files from erasing the rich data pushed to Hugging Face
            if os.path.exists(local_path) and os.path.getsize(local_path) > 10:
                continue

            url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/data/{filename}"
            try:
                resp = requests.get(url, headers=auth_headers, timeout=5)
                if resp.status_code == 200:
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)
                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(resp.text)
            except Exception: pass

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
        except Exception: pass

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
        except Exception: return None

    @st.cache_data(ttl=60, show_spinner=False)
    def load_live_tactical_data():
        filepath = 'data/tactical_events_24h.json'
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f: 
                    return json.load(f)
            except Exception: return None
        return None

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
                    if current_reg not in rss_dict: rss_dict[current_reg] = []
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
                                "title": title_str, "published": date_str, "link": news_link, "is_24h": True
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
                    if score >= 9: prefix = "🔴 CRITICAL:"
                    elif score >= 7: prefix = "🟠 ELEVATED:"
                    else: prefix = "🟡 WATCH:"
                    
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
            /* Frosted glass so the ambient glow bleeds through */
            background-color: rgba(14, 17, 23, 0.35); 
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            border-top: 1px solid rgba(255, 255, 255, 0.03) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important; 
            box-shadow: none !important; 
            z-index: 990; 
            overflow: hidden; 
            display: flex; 
            align-items: center; 
        }}
        .block-container {{ padding-top: 110px !important; }}
        .ticker-move {{ display: flex; width: fit-content; animation: ticker {dynamic_duration}s linear infinite; }}
        .ticker-track {{ display: flex; white-space: nowrap; }}
        .ticker-move:hover {{ animation-play-state: paused; }}
        @keyframes ticker {{ 0% {{ transform: translate3d(0, 0, 0); }} 100% {{ transform: translate3d(-50%, 0, 0); }} }}
        .ticker-item {{ display: inline-block; margin-right: 60px; font-family: "Courier New", monospace; font-weight: bold; font-size: 14px; letter-spacing: 0.5px; }}
        .ticker-item a {{ text-decoration: none; color: #ffffff !important; text-shadow: 0 1px 4px rgba(0,0,0,0.8); }}
        .ticker-item a:hover {{ text-decoration: underline; opacity: 0.8; }}
        </style>
        <div class="ticker-wrap"><div class="ticker-move"><div class="ticker-track">{all_items_html}</div><div class="ticker-track">{all_items_html}</div></div></div>
        """
        st.markdown(ticker_code, unsafe_allow_html=True)

    try:
        df_actions_weekly = clean_dataframe(pd.DataFrame(dashboard_data.get('recent_actions', []) if dashboard_data else []))
        if live_tactical_data is not None:
            if isinstance(live_tactical_data, list):
                df_actions = clean_dataframe(pd.DataFrame(live_tactical_data))
            else:
                df_actions = clean_dataframe(pd.DataFrame(live_tactical_data.get('recent_actions', [])))
        else:
            df_actions = df_actions_weekly
    except Exception as e:
        df_actions = pd.DataFrame()

    # --- RENDER LOGIC ---
    if not st.session_state['dashboard_entered']:
        # 🟢 LIFT THE BLACKOUT MASK IMMEDIATELY BEFORE SHOWING COMMAND CENTER
        st.markdown("""<style>#blackout-mask { display: none !important; }</style>""", unsafe_allow_html=True)
        try:
            from features.landing_page import render_redroom_landing
            render_redroom_landing(df_actions)
            # 🛑 CRITICAL: HALT EXECUTION SO IT STAYS ON THE COMMAND CENTER
            st.stop() 
        except Exception as e:
            st.error(f"🚨 **Landing Page Error:** {e}")
            st.stop()
            
    else:
        # --- STAGE 3: DASHBOARD ENTERED ---
        
        if SNIPPET_TEST_MODE:
            st.sidebar.info("🛠️ **Snippet Test Mode Active**")

        selected_actor, view_selection = render_sidebar(
            dashboard_data, df_actions, raw_text, text_india, text_wa
        )

        # ==========================================
        # 🌌 GEMINI-STYLE AMBIENT GLOW HEADER
        # ==========================================
        target_glow_sections = [
            "Executive Home", "Today's Snippet", "Weekly Tactical Brief", 
            "Weekly Intelligence Brief", "West Asia Strategic Intel (Psyopoly)", 
            "Archives"
        ]
        
        if view_selection in target_glow_sections:
            st.markdown(
                """
                <div class="gemini-ambient-container">
                    <div class="gemini-blob blob-1"></div>
                    <div class="gemini-blob blob-2"></div>
                    <div class="gemini-blob blob-3"></div>
                    <div class="gemini-blob blob-4"></div>
                    <div class="gemini-blob blob-5"></div>
                </div>
                <style>
                .gemini-ambient-container { position: fixed; top: 0; left: 0; width: 100vw; height: 350px; z-index: 0; pointer-events: none; overflow: hidden; mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 15%, rgba(0,0,0,0) 100%); -webkit-mask-image: linear-gradient(to bottom, rgba(0,0,0,1) 15%, rgba(0,0,0,0) 100%); }
                .gemini-blob { position: absolute; filter: blur(75px); opacity: 0.7; border-radius: 50%; animation: floatWave 5.5s infinite alternate ease-in-out; mix-blend-mode: screen; }
                .blob-1 { top: -40px; left: -10vw; width: 60vw; height: 280px; background: #1b60d4; animation-delay: 0s; }
                .blob-2 { top: -20px; right: -10vw; width: 55vw; height: 260px; background: #7f3ab7; animation-delay: -2s; }
                .blob-3 { top: 10px; left: 20vw; width: 60vw; height: 240px; background: #d44c5c; animation-delay: -4s; }
                .blob-4 { top: 30px; right: 20vw; width: 50vw; height: 220px; background: #FF272A; animation-delay: -1s; }
                .blob-5 { top: -10px; left: 35vw; width: 55vw; height: 250px; background: #0ADD08; animation-delay: -3.5s; }
                @keyframes floatWave { 0% { transform: translate(0, 0) scale(1); } 33% { transform: translate(6vw, 40px) scale(1.15); } 66% { transform: translate(-4vw, -20px) scale(0.85); } 100% { transform: translate(4vw, 30px) scale(1.1); } }
                </style>
                """, unsafe_allow_html=True
            )

        if view_selection != "West Asia Strategic Intel (Psyopoly)":
            render_ticker_tape()

        if view_selection not in ["Trend Timelines", "Archives"]:
            st.markdown(
                """
                <style>
                .scroll-top-btn {
                    position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); background-color: rgba(255, 255, 255, 0.15); 
                    color: #ffffff !important; width: 45px; height: 45px; border-radius: 50%; display: flex; align-items: center;
                    justify-content: center; font-size: 22px; font-weight: bold; text-decoration: none; backdrop-filter: blur(5px); 
                    -webkit-backdrop-filter: blur(5px); box-shadow: 0 4px 10px rgba(0,0,0,0.3); z-index: 999990; 
                    border: 1px solid rgba(255, 255, 255, 0.3); transition: background-color 0.3s ease, transform 0.2s ease;
                }
                .scroll-top-btn:hover { background-color: rgba(255, 255, 255, 0.35); transform: translateX(-50%) translateY(-3px); }
                </style>
                <a href="#top-of-page" target="_self" class="scroll-top-btn" title="Scroll to Top">↑</a>
                """, unsafe_allow_html=True
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
                mode="weekly_tactical", dashboard_data=dashboard_data, text_summary=text_summary,
                text_section_1=text_section_1, text_section_2=text_section_2, text_section_3=text_section_3,
                text_section_4=text_section_4, text_military=text_military, text_india=text_india,
                text_wa=text_wa, text_ews=text_ews, selected_actor=selected_actor, df_actions=df_actions
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
                rag_api_keys, model_name, text_summary=text_summary, text_section_1=text_section_1, 
                text_section_2=text_section_2, text_section_3=text_section_3, text_section_4=text_section_4, 
                text_military=text_military, text_india=text_india, text_wa=text_wa, text_ews=text_ews
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
            rag_api_keys, model_name, text_summary=text_summary, text_section_1=text_section_1, 
            text_section_2=text_section_2, text_section_3=text_section_3, text_section_4=text_section_4, 
            text_military=text_military, text_india=text_india, text_wa=text_wa, text_ews=text_ews
        )