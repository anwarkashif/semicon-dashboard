import streamlit as st
import os
import base64

def inject_early_css(role):
    """Handles CSS routing to prevent the login screen flash, actively formatting for mobile/desktop using fluid dimensions."""
    if role is None:
        st.markdown("""
        <style>
            [data-testid="stToolbar"], [data-testid="stHeader"], [data-testid="collapsedControl"], [data-testid="stSidebar"] { display: none !important; }
            footer { visibility: hidden; }
            html, body, .stApp { min-height: 100dvh; margin: 0; background-color: #000000; overflow-x: hidden; }
            
            /* DEFAULT DESKTOP */
            .fixed-left-panel {
                position: fixed; top: 0; left: 0; width: 50vw; height: 100vh;
                background: linear-gradient(135deg, #0f172a, #1e293b, #020617);
                padding: clamp(20px, 5vw, 60px); display: flex; flex-direction: column;
                justify-content: center; z-index: 100; box-sizing: border-box;
                border-right: 1px solid #222;
            }
            .fixed-left-panel h1 { font-size: clamp(2rem, 4vw, 3.2rem); font-weight: 300; line-height: 1.2; margin-bottom: 10px; color: white;}
            .fixed-left-panel span { font-weight: 700; color: #facc15; }
            .fixed-left-panel p { color: #94a3b8; font-size: clamp(1rem, 1.5vw, 1.2rem); margin-top: 10px; }

            .block-container {
                margin-left: 50vw !important; width: 50vw !important; max-width: 50vw !important;
                height: 100vh !important; padding: 0 15% !important;
                display: flex !important; flex-direction: column !important;
                justify-content: center !important;
            }

            .login-header { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 25px; text-align: center; }
            .login-logo { width: min(100%, 300px); margin-bottom: 5px; image-rendering: crisp-edges; }
            .login-header h2 { margin: 0; font-size: clamp(24px, 3vw, 32px); color: white; }
            .login-header p { margin-top: 5px; color: #aaa; font-size: clamp(12px, 1.5vw, 14px); }

            /* MOBILE OVERRIDES */
            @media (max-width: 900px) {
                html, body, .stApp { overflow-y: auto; }
                input[type="text"], input[type="password"] { font-size: 16px !important; }
                .fixed-left-panel { display: none !important; }
                .block-container {
                    margin-left: 0 !important; width: 100% !important; max-width: 100% !important;
                    padding: clamp(1rem, 5vw, 2rem) clamp(1rem, 5vw, 1.5rem) !important; position: relative !important;
                    height: auto !important; min-height: 100vh !important;
                }
                .login-logo { width: min(80vw, 250px); }
                .login-header h2 { font-size: clamp(20px, 6vw, 26px); }
            }

            /* BUTTONS */
            .stButton>button[kind="secondary"] { width: 100%; font-weight: bold; height: 45px; color: #ffffff !important; }
            .stButton>button[kind="secondary"] * { color: #ffffff !important; }
            button[kind="primaryFormSubmit"], button[kind="primary"], div[data-testid="stFormSubmitButton"] button {
                background-color: #facc15 !important; border: none !important; width: 100% !important; height: 45px !important; border-radius: 8px !important;
            }
            button[kind="primaryFormSubmit"] *, button[kind="primary"] *, div[data-testid="stFormSubmitButton"] button *, div[data-testid="stFormSubmitButton"] p {
                color: #000000 !important; font-weight: bold !important;
            }
            button[kind="primaryFormSubmit"]:hover, button[kind="primary"]:hover, div[data-testid="stFormSubmitButton"] button:hover {
                background-color: #eab308 !important;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .fixed-left-panel, .login-header { 
                display: none !important; visibility: hidden !important; opacity: 0 !important; z-index: -999 !important; height: 0px !important;
            } 
            .block-container {
                margin-left: auto !important; margin-right: auto !important;
                width: 100% !important; max-width: 100% !important; display: block !important; height: auto !important;   
            }
            [data-testid="stToolbar"], [data-testid="collapsedControl"] { display: flex !important; }
        </style>
        """, unsafe_allow_html=True)

def inject_global_theme():
    """Injects the pure pitch black theme and dynamically sets structural padding based on device."""
    st.markdown("""
    <style>
        .stApp, .stAppViewContainer, .main .block-container { background-color: #000000 !important; }
        [data-testid="stAppViewContainer"] > section > div > div, [data-testid="stHeader"], .element-container, .stMarkdown {
            transition: none !important; animation-duration: 0s !important;
        }

        div[data-testid="stButton"] > button[kind="secondary"] { margin-top: 10px !important; }
        div[data-testid="stButton"] > button[kind="primary"], div[data-testid="stButton"] > button[data-testid="baseButton-primary"], div[data-testid="stFormSubmitButton"] button, button[kind="primaryFormSubmit"] { 
            width: 100%; background-color: #facc15 !important; color: black !important; font-weight: bold; border: none !important; margin-top: 10px; height: 45px;
        }
        div[data-testid="stButton"] > button[kind="primary"] *, div[data-testid="stButton"] > button[data-testid="baseButton-primary"] *, div[data-testid="stFormSubmitButton"] button *, button[kind="primaryFormSubmit"] *, div[data-testid="stFormSubmitButton"] p, div[data-testid="stButton"] > button[kind="primary"] p {
            color: #000000 !important; font-weight: bold !important;
        }
        div[data-testid="stButton"] > button[kind="secondary"] *, div[data-testid="stButton"] > button[data-testid="baseButton-secondary"] *, div[data-testid="stButton"] > button[kind="secondary"] p {
            color: #ffffff !important;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover, div[data-testid="stButton"] > button[data-testid="baseButton-primary"]:hover, div[data-testid="stFormSubmitButton"] button:hover, button[kind="primaryFormSubmit"]:hover { 
            background-color: #eab308 !important; border: none !important;
        }
        
        header[data-testid="stHeader"] { background-color: transparent !important; }
        [data-testid="stStatusWidget"] { display: none !important; }
        [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #222222 !important; } 
        footer { visibility: hidden; height: 0%; }
        h1, h2, h3, h4, h5 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important; letter-spacing: 0.5px; }
        p, li { color: #d1d5db; line-height: 1.6; }

        /* DESKTOP DEFAULTS */
        .block-container {
            padding-top: max(1rem, env(safe-area-inset-top)) !important;
            padding-left: max(1rem, env(safe-area-inset-left)) !important;
            padding-right: max(1rem, env(safe-area-inset-right)) !important;
            margin-top: 0rem !important;
        }

        /* MOBILE OVERRIDES */
        @media (max-width: 900px) {
            .block-container {
                padding-top: max(1rem, env(safe-area-inset-top)) !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                width: 100% !important;
                max-width: 100% !important;
                overflow-x: hidden;
            }
            .ticker-item { font-size: clamp(10px, 3vw, 12px) !important; margin-right: 30px !important; }
            h1 { font-size: clamp(20px, 6vw, 24px) !important; }
            h3 { font-size: clamp(16px, 5vw, 18px) !important; }
            [data-testid="stMetricValue"] { font-size: clamp(1.2rem, 5vw, 1.4rem) !important; }
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
                img_html = f'<img src="data:image/jpeg;base64,{encoded_string}" class="login-logo"/>'
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
            with st.container():
                email_input = st.text_input("Email", placeholder="Enter your Email ID")
                password_input = st.text_input("Password", type="password", placeholder="Enter Your Password")
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    submit_login = st.button("Login", type="primary", use_container_width=True)
                with btn_col2:
                    guest_login = st.button("View as Guest", type="secondary", use_container_width=True)

            if submit_login:
                ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "anwarkashif@semirare.in")
                ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123") 
                
                if email_input == ADMIN_EMAIL and password_input == ADMIN_PASSWORD:
                    st.session_state['role'] = 'admin'
                    login_placeholder.empty() 
                    st.rerun()
                else:
                    st.toast("Invalid credentials. Please verify your secure key.", icon="🚫")

            if guest_login:
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
                position: fixed; top: 0; left: 0; width: 100%; height: 100vh;
                background-color: #000000; display: flex; align-items: center;
                justify-content: center; z-index: 9999999;
                animation: fadeOutSplash 3.5s forwards; pointer-events: none;
            }
            .splash-text {
                color: #ffffff; font-size: clamp(20px, 5vw, 2.5rem); font-weight: 300;
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

import streamlit.components.v1 as components

def render_sd_bot():
    """Renders a dynamic, draggable, voice-enabled SD Bot on the login screen."""
    if 'sdbot_chat_history' not in st.session_state:
        st.session_state['sdbot_chat_history'] = [
            {"role": "bot", "content": "Hi! I'm SD Bot. Ask me about the dashboard or global intelligence or click the 🎤 to speak!"}
        ]

    # Hidden input to act as a secure bridge between injected JS and Python
    st.text_input("Hidden SD Bot Input", key="sdbot_query_input", label_visibility="hidden")
    st.markdown("""
    <style>
    div[data-testid="stTextInput"]:has(input[aria-label="Hidden SD Bot Input"]) {
        display: none !important;
        height: 0px !important;
        overflow: hidden !important;
        position: absolute;
    }
    </style>
    """, unsafe_allow_html=True)

    # Compile Chat History
    chat_html = ""
    for msg in st.session_state['sdbot_chat_history']:
        css_class = "bot" if msg["role"] == "bot" else "user"
        content_safe = msg["content"].replace('\n', '<br>').replace('`', '&#96;')
        chat_html += f'<div class="msg {css_class}">{content_safe}</div>'

    is_open = "true" if len(st.session_state['sdbot_chat_history']) > 1 else "false"
    box_display = "flex" if is_open == "true" else "none"
    icon_display = "none" if is_open == "true" else "flex"

    bot_html = f"""
    <div id="SD_BOT_IDENTIFIER"></div>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ margin: 0; overflow: hidden; background: transparent; color: white; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; height: 100vh; width: 100vw; }}
        #bot-container {{ display: flex; justify-content: center; align-items: center; height: 100%; width: 100%; }}
        
        /* Floating Icon State - Updated Size and Color */
        #bot-icon {{
            display: {icon_display};
            width: 75px; height: 75px; background: #ffffff;
            border-radius: 50%; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            align-items: center; justify-content: center;
            font-size: 40px; cursor: pointer; transition: transform 0.2s; pointer-events: auto; color: black;
        }}
        #bot-icon:hover {{ transform: scale(1.1); }}
        
        /* Expanded Chat State */
        #bot-box {{ 
            display: {box_display}; flex-direction: column; width: 100%; height: 100%; max-height: 100vh;
            background: rgba(15, 23, 42, 0.95); border: 1px solid #333; border-radius: 12px; 
            box-shadow: 0px 10px 40px rgba(0,0,0,0.9); backdrop-filter: blur(10px); pointer-events: auto;
        }}
        #header {{ flex: 0 0 auto; background: #facc15; color: black; padding: 12px; font-weight: bold; cursor: grab; display: flex; justify-content: space-between; align-items: center; border-radius: 12px 12px 0 0; font-size: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 10; user-select: none; }}
        #chat-history {{ flex: 1 1 auto; padding: 15px; overflow-y: auto; font-size: 13.5px; line-height: 1.6; display: flex; flex-direction: column; gap: 12px; min-height: 0; }}
        .msg {{ padding: 10px 14px; border-radius: 8px; max-width: 85%; word-wrap: break-word; }}
        .msg.bot {{ background: #1e293b; align-self: flex-start; border-left: 3px solid #facc15; color: #f8fafc; }}
        .msg.user {{ background: #2563eb; align-self: flex-end; color: white; border-bottom-right-radius: 2px; }}
        #input-bar {{ flex: 0 0 auto; display: flex; padding: 12px; background: #020617; border-top: 1px solid #333; border-radius: 0 0 12px 12px; align-items: center; }}
        input {{ flex: 1; padding: 10px 12px; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; outline: none; font-size: 13px; transition: border 0.3s; }}
        input:focus {{ border-color: #facc15; }}
        button {{ border: none; padding: 10px; margin-left: 8px; border-radius: 6px; cursor: pointer; font-weight: bold; transition: all 0.2s; display: flex; align-items: center; justify-content: center; width: 38px; height: 38px; }}
        #mic-btn {{ background: #ef4444; color: white; }}
        #mic-btn.recording {{ background: #22c55e; animation: pulse 1s infinite; }}
        #send-btn {{ background: #facc15; color: black; }}
        #send-btn:hover {{ background: #eab308; transform: scale(1.05); }}
        @keyframes pulse {{ 0% {{ opacity: 1; transform: scale(1); }} 50% {{ opacity: 0.6; transform: scale(1.1); }} 100% {{ opacity: 1; transform: scale(1); }} }}
        
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 10px; }}
        
        /* MOBILE RESPONSIVENESS */
        @media (max-width: 900px) {{
            .msg {{ font-size: 14.5px; max-width: 95%; }}
            input {{ font-size: 16px; }} /* Prevents iOS auto-zoom */
        }}
    </style>
    
    <div id="bot-container">
        <div id="bot-icon">📟</div>
        <div id="bot-box">
            <div id="header">
                <span style="display: flex; align-items: center; gap: 8px;">📟 SD Bot</span>
                <span id="close-btn" style="cursor:pointer; font-size:16px; padding: 0 5px;" title="Minimize">✖</span>
            </div>
            <div id="chat-history">
                {chat_html}
            </div>
            <div id="input-bar">
                <button id="mic-btn" title="Voice Input">🎤</button>
                <input type="text" id="user-input" placeholder="Type or speak a prompt..." autocomplete="off"/>
                <button id="send-btn" title="Send">➤</button>
            </div>
        </div>
    </div>

    <script>
        const iframes = window.parent.document.querySelectorAll('iframe');
        let myIframe = null;
        iframes.forEach(f => {{
            try {{ if(f.contentDocument && f.contentDocument.getElementById('SD_BOT_IDENTIFIER')) {{ myIframe = f; }} }} catch(e) {{}}
        }});

        if (myIframe) {{
            const parentDiv = myIframe.parentNode;
            parentDiv.style.position = 'fixed';
            parentDiv.style.zIndex = '9999999';
            
            // Fix iframe internals
            myIframe.style.width = '100%';
            myIframe.style.height = '100%';
            
            const isMobile = window.parent.innerWidth <= 900;
            const expandedWidth = isMobile ? '90vw' : '360px';
            const expandedHeight = isMobile ? '70vh' : '520px';
            
            const botIcon = document.getElementById('bot-icon');
            const botBox = document.getElementById('bot-box');
            const header = document.getElementById('header');
            const chatHistory = document.getElementById('chat-history');
            
            // Set dimensions immediately before transition to stop flickering
            const shouldBeOpen = {is_open};
            if (shouldBeOpen) {{
                parentDiv.style.width = expandedWidth;
                parentDiv.style.height = expandedHeight;
                parentDiv.style.borderRadius = '12px';
            }} else {{
                parentDiv.style.width = '60px';
                parentDiv.style.height = '60px';
                parentDiv.style.borderRadius = '30px';
            }}

            // Initial positioning ONLY if not already dragged
            if (!parentDiv.style.left && !parentDiv.style.top) {{
                parentDiv.style.bottom = isMobile ? '10px' : '20px';
                parentDiv.style.right = isMobile ? '5vw' : '20px';
            }}

            // Add transition AFTER setting the initial static size to stop load flash
            setTimeout(() => {{ parentDiv.style.transition = 'width 0.3s, height 0.3s'; }}, 50);

            const setOpenState = () => {{
                parentDiv.style.width = expandedWidth;
                parentDiv.style.height = expandedHeight;
                parentDiv.style.borderRadius = '12px';
                botIcon.style.display = 'none';
                botBox.style.display = 'flex';
                setTimeout(() => {{ chatHistory.scrollTop = chatHistory.scrollHeight; }}, 100);
            }};

            const setClosedState = () => {{
                parentDiv.style.width = '75px';
                parentDiv.style.height = '75px';
                parentDiv.style.borderRadius = '50%';
                botIcon.style.display = 'flex';
                botBox.style.display = 'none';
            }};

            const shouldBeOpen = {is_open};
            if (shouldBeOpen) {{
                parentDiv.style.width = expandedWidth;
                parentDiv.style.height = expandedHeight;
                parentDiv.style.borderRadius = '12px';
            }} else {{
                parentDiv.style.width = '75px';
                parentDiv.style.height = '75px';
                parentDiv.style.borderRadius = '50%';
            }}

            // Auto scroll on load
            setTimeout(() => {{ chatHistory.scrollTop = chatHistory.scrollHeight; }}, 50);

            let dragged = false;
            botIcon.addEventListener('click', (e) => {{
                if(dragged) {{ e.preventDefault(); dragged = false; return; }}
                setOpenState();
            }});
            
            document.getElementById('close-btn').addEventListener('click', (e) => {{
                e.stopPropagation();
                setClosedState();
            }});

            // Reliable Dragging Logic
            let isDragging = false;
            let dragOffsetX = 0;
            let dragOffsetY = 0;

            const dragStart = (e) => {{
                if (e.target.id === 'close-btn' || e.target.tagName.toLowerCase() === 'button') return;
                isDragging = true;
                dragged = false;
                
                // Capture mouse offset relative to the interior of the widget
                const innerX = e.clientX || (e.touches ? e.touches[0].clientX : 0);
                const innerY = e.clientY || (e.touches ? e.touches[0].clientY : 0);
                
                dragOffsetX = innerX;
                dragOffsetY = innerY;
                
                const rect = parentDiv.getBoundingClientRect();
                
                // Lock current absolute position before switching anchoring
                parentDiv.style.left = rect.left + 'px';
                parentDiv.style.top = rect.top + 'px';
                parentDiv.style.right = 'auto'; 
                parentDiv.style.bottom = 'auto';
                parentDiv.style.transition = 'none'; 
                
                myIframe.style.pointerEvents = 'none'; 
            }};

            const dragMove = (e) => {{
                if(!isDragging) return;
                e.preventDefault();
                dragged = true;
                
                // Track mouse movement relative to the parent window
                const parentX = e.clientX || (e.touches ? e.touches[0].clientX : 0);
                const parentY = e.clientY || (e.touches ? e.touches[0].clientY : 0);
                
                requestAnimationFrame(() => {{
                    let newLeft = parentX - dragOffsetX;
                    let newTop = parentY - dragOffsetY;
                    
                    // Prevent dragging completely off the top or left of screen
                    if (newTop < 0) newTop = 0;
                    if (newLeft < -300) newLeft = -300;
                    
                    parentDiv.style.left = `${{newLeft}}px`;
                    parentDiv.style.top = `${{newTop}}px`;
                }});
            }};

            const dragEnd = () => {{
                if(!isDragging) return;
                isDragging = false;
                parentDiv.style.transition = 'width 0.3s, height 0.3s';
                myIframe.style.pointerEvents = 'auto';
            }};

            header.addEventListener('mousedown', dragStart);
            header.addEventListener('touchstart', dragStart, {{passive: false}});
            botIcon.addEventListener('mousedown', dragStart);
            botIcon.addEventListener('touchstart', dragStart, {{passive: false}});
            
            window.parent.addEventListener('mousemove', dragMove);
            window.parent.addEventListener('touchmove', dragMove, {{passive: false}});
            window.parent.addEventListener('mouseup', dragEnd);
            window.parent.addEventListener('touchend', dragEnd);
        }}

        // Voice & Input Handlers
        const chatHistory = document.getElementById('chat-history');
        const micBtn = document.getElementById('mic-btn');
        const inputField = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {{
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            let isRecording = false;

            micBtn.addEventListener('click', () => {{
                if (isRecording) {{ recognition.stop(); }} else {{ recognition.start(); }}
            }});

            recognition.onstart = () => {{
                isRecording = true;
                micBtn.classList.add('recording');
                inputField.placeholder = "Listening...";
            }};

            recognition.onresult = (event) => {{
                inputField.value = event.results[0][0].transcript;
            }};

            recognition.onend = () => {{
                isRecording = false;
                micBtn.classList.remove('recording');
                inputField.placeholder = "Type or speak a prompt...";
            }};
        }} else {{
            micBtn.style.display = 'none'; 
        }}

        function sendMessage() {{
            const text = inputField.value.trim();
            if (!text) return;

            chatHistory.innerHTML += `<div class="msg user">${{text}}</div>`;
            chatHistory.innerHTML += `<div class="msg bot">Thinking...💬</div>`;
            chatHistory.scrollTop = chatHistory.scrollHeight;
            inputField.value = '';

            const stInputs = window.parent.document.querySelectorAll('input[aria-label="Hidden SD Bot Input"]');
            if (stInputs.length > 0) {{
                const stInput = stInputs[0];
                let lastValue = stInput.value;
                stInput.value = text;
                let event = new Event('input', {{ bubbles: true }});
                event.simulated = true;
                let tracker = stInput._valueTracker;
                if (tracker) {{ tracker.setValue(lastValue); }}
                stInput.dispatchEvent(event);

                setTimeout(() => {{
                    stInput.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }}));
                }}, 100);
            }}
        }}

        sendBtn.addEventListener('click', sendMessage);
        inputField.addEventListener('keypress', (e) => {{
            if (e.key === 'Enter') sendMessage();
        }});
    </script>
    """
    
    # 🛑 FIX: Setting height=0 kills the Streamlit DOM allocation flicker permanently!
    components.html(bot_html, height=0)