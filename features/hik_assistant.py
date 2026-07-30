import streamlit as st
import os
from google import genai

def render_hik_voice_assistant():
    """
    Core engine for the 'Hey Hik' voice assistant.
    Features: Strict CSS hiding, direct API key routing, and Safari-compliant Mic initiation.
    """
    
    # 1. HARD-ROUTE THE SPECIFIC API KEY
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        try: gemini_key = st.secrets.get("GEMINI_API_KEY")
        except Exception: gemini_key = None
        
    client = genai.Client(api_key=gemini_key) if gemini_key else None

    # 2. HIK'S IDENTITY & SYSTEM PROMPT
    hik_system_prompt = """
    You are Hik, the exclusive voice assistant for the SemicoN Dashboard. 
    Your creator and the owner of this platform is Kashif Anwar. 
    You are designed to assist geopolitical researchers and strategic intelligence analysts.
    
    RULES FOR VOCAL RESPONSES:
    1. Keep responses conversational, concise, and easy to listen to.
    2. DO NOT use markdown formatting, bolding, asterisks, or bullet points. Speak in plain text sentences.
    3. If the user asks a simple question, answer it directly.
    4. If the user asks a complex research question, give a brief 1-2 sentence overview, and then explicitly guide them by saying: "For a deeper analysis of this topic, I recommend using the Intelligence Interrogation RAG or the Agentic AI module located in your sidebar."
    """

    # 3. BULLETPROOF CSS HIDING & GLOW ANIMATION
    st.markdown("""
    <style>
        /* 🛑 STRICT HIDE: Completely obliterate the bridge input box so it cannot be typed into */
        div[data-testid="stTextInput"]:has(input[aria-label="hik_bridge_input"]) {
            display: none !important;
            visibility: hidden !important;
            height: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        
        body.hik-awake::before {
            content: ''; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            pointer-events: none; z-index: 999999;
            box-shadow: inset 0 0 60px 20px rgba(0, 191, 255, 0.7), inset 0 0 20px 5px rgba(168, 85, 247, 0.8);
            animation: pulse-glow 2s infinite alternate ease-in-out;
            transition: opacity 0.3s ease;
        }
        @keyframes pulse-glow {
            0% { box-shadow: inset 0 0 40px 10px rgba(0, 191, 255, 0.5), inset 0 0 15px 5px rgba(168, 85, 247, 0.5); }
            100% { box-shadow: inset 0 0 80px 25px rgba(0, 191, 255, 0.9), inset 0 0 30px 10px rgba(168, 85, 247, 0.9); }
        }
    </style>
    """, unsafe_allow_html=True)

    # 4. EXPLICIT BROWSER PERMISSION TOGGLE (Required for Safari/Mac)
    # We place a tiny, unobtrusive toggle so the browser registers a physical click to unlock the mic.
    st.sidebar.markdown("<hr style='border: 1px solid #333; margin-top: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
    activate_mic = st.sidebar.toggle("🎙️ Initialize 'Hey Hik' Voice Engine", value=False, help="Click to grant browser microphone permissions for continuous listening.")

    if activate_mic:
        # 5. JAVASCRIPT SPEECH RECOGNITION (Only runs when toggle is ON)
        st.html("""
        <script>
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                const recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                
                let isAwake = false;
                
                // Keep background listening alive
                recognition.onend = function() {
                    setTimeout(() => { try { recognition.start(); } catch(e){} }, 1000);
                };

                recognition.onresult = function(event) {
                    const last = event.results.length - 1;
                    const transcript = event.results[last][0].transcript.trim().toLowerCase();
                    
                    if (!isAwake && (transcript.includes("hey hik") || transcript.includes("hey hick") || transcript.includes("hey heek") || transcript.includes("hey hake"))) {
                        isAwake = true;
                        document.body.classList.add("hik-awake");
                        
                        // Audio blip acknowledgment
                        const beep = new Audio('data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU'); 
                        try { beep.play(); } catch(e) {}
                    } 
                    else if (isAwake && transcript.length > 2) {
                        isAwake = false;
                        
                        // Find the hidden Streamlit input and inject the query
                        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
                        let targetInput = null;
                        inputs.forEach(input => {
                            if (input.getAttribute('aria-label') === 'hik_bridge_input') {
                                targetInput = input;
                            }
                        });
                        
                        if (targetInput) {
                            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            nativeInputValueSetter.call(targetInput, transcript);
                            targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                            
                            setTimeout(() => {
                                targetInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                            }, 100);
                        }
                    }
                };
                
                // Start recognition immediately now that the user clicked the toggle
                try { recognition.start(); } catch(e){}
            } else {
                alert("Your browser does not support the Web Speech API. Please try Chrome or Edge.");
            }
        </script>
        """)

    # 6. INVISIBLE PYTHON RECEIVER
    vocal_query = st.text_input("hik_bridge_input", key="hik_vocal_query", label_visibility="hidden")

    if vocal_query:
        if not client:
            st.html("""<script>document.body.classList.remove("hik-awake"); window.speechSynthesis.speak(new SpeechSynthesisUtterance("I am offline. No Gemini API Key was detected in the environment variables."));</script>""")
            st.session_state['hik_vocal_query'] = ""
            return
            
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"SYSTEM INSTRUCTION: {hik_system_prompt}\n\nUSER VOCAL QUERY: {vocal_query}"
            )
            answer = response.text.replace('"', "'").replace('\n', ' ')
            
            st.html(f"""
            <script>
                document.body.classList.remove("hik-awake");
                const utterance = new SpeechSynthesisUtterance("{answer}");
                utterance.voice = speechSynthesis.getVoices().find(voice => voice.name.includes("Google UK English Male") || voice.name.includes("Male")) || null;
                utterance.rate = 1.05;
                utterance.pitch = 1.0;
                window.speechSynthesis.speak(utterance);
            </script>
            """)
            st.session_state['hik_vocal_query'] = ""
            
        except Exception as e:
            st.html("""<script>document.body.classList.remove("hik-awake"); window.speechSynthesis.speak(new SpeechSynthesisUtterance("I encountered a network error while connecting to the Agentic engine."));</script>""")
            st.session_state['hik_vocal_query'] = ""