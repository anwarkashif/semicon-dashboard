import streamlit as st
import os
import base64

def inject_early_css(role):
    """Handles CSS routing to prevent the login screen flash."""
    if role is None:
        st.markdown("""
        <style>
            /* SAFE UI HIDING */
            [data-testid="stToolbar"], [data-testid="stHeader"], [data-testid="collapsedControl"], [data-testid="stSidebar"] { 
                display: none !important; 
            }
            footer { visibility: hidden; }

            /* FIX 1: Use 100dvh for virtual keyboards and allow safe overflow */
            html, body, .stApp { min-height: 100dvh; margin: 0; background-color: #000000; overflow-x: hidden; }

            /* FIX 1: Prevent Mobile Browser Auto-Zoom on inputs */
            input[type="text"], input[type="password"] {
                font-size: 16px !important; 
            }

            /* --- 1. THE PURE CSS LEFT PANEL --- */
            .fixed-left-panel {
                position: fixed; top: 0; left: 0; width: 50vw; height: 100vh;
                background: linear-gradient(135deg, #0f172a, #1e293b, #020617);
                padding: 60px; display: flex; flex-direction: column;
                justify-content: center; z-index: 100; box-sizing: border-box;
                border-right: 1px solid #222;
            }
            .fixed-left-panel h1 { font-size: 3.2rem; font-weight: 300; line-height: 1.2; margin-bottom: 10px; color: white;}
            .fixed-left-panel span { font-weight: 700; color: #facc15; }
            .fixed-left-panel p { color: #94a3b8; font-size: 1.2rem; margin-top: 10px; }

            /* --- 2. THE RIGHT PANEL (STREAMLIT NATIVE CONTAINER) --- */
            .block-container {
                margin-left: 50vw !important; width: 50vw !important; max-width: 50vw !important;
                height: 100vh !important; padding: 0 15% !important;
                display: flex !important; flex-direction: column !important;
                justify-content: center !important;
            }

            /* --- 3. LOGIN HEADER --- */
            .login-header { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 25px; text-align: center; }
            .login-logo { width: 300px; max-width: 100%; margin-bottom: 5px; image-rendering: crisp-edges; }
            .login-header h2 { margin: 0; font-size: 32px; color: white; }
            .login-header p { margin-top: 5px; color: #aaa; font-size: 14px; }

            /* --- SECONDARY BUTTON FIX (View As Guest) --- */
            .stButton>button[kind="secondary"] { 
                width: 100%; font-weight: bold; height: 45px; color: #ffffff !important; 
            }
            .stButton>button[kind="secondary"] * { color: #ffffff !important; }

            /* --- LOGIN BUTTON YELLOW OVERRIDE --- */
            button[kind="primaryFormSubmit"],
            button[kind="primary"],
            div[data-testid="stFormSubmitButton"] button {
                background-color: #facc15 !important;
                border: none !important;
                width: 100% !important;
                height: 45px !important;
                border-radius: 8px !important;
            }
            
            /* AGGRESSIVE FIX: Force all text/paragraphs inside the button to be black */
            button[kind="primaryFormSubmit"] *,
            button[kind="primary"] *,
            div[data-testid="stFormSubmitButton"] button *,
            div[data-testid="stFormSubmitButton"] p {
                color: #000000 !important;
                font-weight: bold !important;
            }

            button[kind="primaryFormSubmit"]:hover,
            button[kind="primary"]:hover,
            div[data-testid="stFormSubmitButton"] button:hover {
                background-color: #eab308 !important;
            }

            /* --- 5. MOBILE OVERRIDES --- */
            @media screen and (max-width: 900px) {
                html, body, .stApp { overflow: auto; }
                .fixed-left-panel { display: none !important; }
                .block-container {
                    margin-left: 0 !important; width: 100vw !important; max-width: 100vw !important;
                    padding: 2rem !important; position: relative !important;
                    height: auto !important; min-height: 100vh !important;
                }
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            /* AGGRESSIVELY HIDE ALL LOGIN ELEMENTS TO PREVENT 1-SECOND GHOSTING FLASH */
            .fixed-left-panel, .login-header { 
                display: none !important; 
                visibility: hidden !important; 
                opacity: 0 !important; 
                z-index: -999 !important; 
                height: 0px !important;
            } 
            
            .block-container {
                margin-left: auto !important; margin-right: auto !important;
                width: 100% !important; max-width: 100% !important;
                display: block !important; 
                height: auto !important;   
            }
            [data-testid="stToolbar"], [data-testid="collapsedControl"] { display: flex !important; }
        </style>
        """, unsafe_allow_html=True)

def inject_global_theme():
    """Injects the pure pitch black theme and mobile responsive fixes."""
    st.markdown("""
    <style>
        /* Force main app background to pure black */
        .stApp, .stAppViewContainer, .main .block-container { 
            background-color: #000000 !important; 
        }
        
        /* AGGRESSIVE FIX FOR ISSUE 2: Kill Streamlit's native crossfade/ghosting completely */
        [data-testid="stAppViewContainer"] > section > div > div,
        [data-testid="stHeader"],
        .element-container,
        .stMarkdown {
            transition: none !important;
            animation-duration: 0s !important;
        }

        /* --- GLOBAL BUTTON THEME --- */
        div[data-testid="stButton"] > button[kind="primary"],
        div[data-testid="stButton"] > button[data-testid="baseButton-primary"],
        div[data-testid="stFormSubmitButton"] button,
        button[kind="primaryFormSubmit"] { 
            width: 100%; background-color: #facc15 !important; color: black !important; 
            font-weight: bold; border: none !important; margin-top: 10px; height: 45px;
        }
        
        div[data-testid="stButton"] > button[kind="primary"] *,
        div[data-testid="stButton"] > button[data-testid="baseButton-primary"] *,
        div[data-testid="stFormSubmitButton"] button *,
        button[kind="primaryFormSubmit"] *,
        div[data-testid="stFormSubmitButton"] p,
        div[data-testid="stButton"] > button[kind="primary"] p {
            color: #000000 !important;
            font-weight: bold !important;
        }

        div[data-testid="stButton"] > button[kind="secondary"] *,
        div[data-testid="stButton"] > button[data-testid="baseButton-secondary"] *,
        div[data-testid="stButton"] > button[kind="secondary"] p {
            color: #ffffff !important;
        }
        
        div[data-testid="stButton"] > button[kind="primary"]:hover,
        div[data-testid="stButton"] > button[data-testid="baseButton-primary"]:hover,
        div[data-testid="stFormSubmitButton"] button:hover,
        button[kind="primaryFormSubmit"]:hover { 
            background-color: #eab308 !important; border: none !important;
        }
        
        header[data-testid="stHeader"] { background-color: transparent !important; }
        [data-testid="stStatusWidget"] { display: none !important; }

        .block-container {
            padding-top: max(1rem, env(safe-area-inset-top)) !important;
            padding-left: max(1rem, env(safe-area-inset-left)) !important;
            padding-right: max(1rem, env(safe-area-inset-right)) !important;
            margin-top: 0rem !important;
        }
        
        [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #222222 !important; } 
        footer { visibility: hidden; height: 0%; }
        
        h1, h2, h3, h4, h5 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; letter-spacing: 0.5px; }
        p, li { color: #d1d5db; line-height: 1.6; }

        @media (max-width: 768px) {
            .block-container { padding: 1rem !important; }
            .ticker-item { font-size: 11px !important; margin-right: 30px !important; }
            h1 { font-size: 24px !important; }
            h3 { font-size: 18px !important; }
            [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
            [data-testid="column"] { width: 100% !important; min-width: 100% !important; margin-bottom: 15px; }
        }
    </style>
    """, unsafe_allow_html=True)

def render_login_screen():
    """Renders the login UI and handles authentication."""
    login_placeholder = st.empty()
    
    with login_placeholder.container():
        st.markdown("""
        <div class="fixed-left-panel">
            <h1>Be a Part of<br>Something <span>Beautiful</span></h1>
            <p>Access high-fidelity insights at the intersection of global policy and the semiconductor industry.</p>
        </div>
        """, unsafe_allow_html=True)

        try:
            with open("logo.jpg", "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                img_html = f'<img src="data:image/jpeg;base64,{encoded_string}" class="login-logo" style="width: 300px; max-width: 100%;"/>'
        except FileNotFoundError:
            img_html = '' 

        st.markdown(f"""
        <div class="login-header">
            {img_html}
            <h2>Login</h2>
            <p>Enter your credentials</p>
        </div>
        <style>
            [data-testid="stForm"] {{ border: none !important; padding: 0 !important; }}
        </style>
        """, unsafe_allow_html=True)
        
        spacer_left, center_col, spacer_right = st.columns([1, 1.5, 1])
        
        with center_col:
            # 🛑 REVERT: Using st.form prevents rapid keystrokes from crashing the local WebSocket connection
            with st.form("login_form", border=False):
                email_input = st.text_input("Email", placeholder="analyst@agency.gov")
                password_input = st.text_input("Password", type="password", placeholder="Enter Secure Key")
                submit_login = st.form_submit_button("Login", type="primary", use_container_width=True)

            if submit_login:
                ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "anwarkashif@semirare.in")
                ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123") 
                
                if email_input == ADMIN_EMAIL and password_input == ADMIN_PASSWORD:
                    st.session_state['role'] = 'admin'
                    login_placeholder.empty() 
                    st.rerun()
                else:
                    st.toast("Invalid credentials. Please verify your secure key.", icon="🚫")

            if st.button("View as Guest", type="secondary", use_container_width=True):
                st.session_state['role'] = 'guest'
                login_placeholder.empty() 
                st.rerun()

def render_splash_screen():
    """Renders the initial loading overlay."""
    if 'splash_shown' not in st.session_state:
        st.session_state['splash_shown'] = True 
        st.markdown("""
        <style>
            .splash-overlay {
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background-color: #000000; display: flex; align-items: center;
                justify-content: center; z-index: 9999999;
                animation: fadeOutSplash 3.5s forwards; pointer-events: none;
            }
            .splash-text {
                color: #ffffff; font-size: 2.5rem; font-weight: 300;
                font-family: 'Times New Roman', Times, serif;
                letter-spacing: 2px; text-align: center;
            }
            @keyframes fadeOutSplash {
                0% { opacity: 1; visibility: visible; }
                75% { opacity: 1; visibility: visible; } 
                100% { opacity: 0; visibility: hidden; display: none; }
            }
            @keyframes blinkDots {
                0%, 100% { opacity: 0; }
                50% { opacity: 1; }
            }
            .loading-dots { animation: blinkDots 1.2s infinite ease-in-out; }
        </style>
        <div class="splash-overlay">
            <div class="splash-text">Welcome to my SemicoN Dashboard<span class="loading-dots">...</span></div>
        </div>
        """, unsafe_allow_html=True)