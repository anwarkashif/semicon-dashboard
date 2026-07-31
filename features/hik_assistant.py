import streamlit as st
import os
from google import genai

def render_hik_voice_assistant():
    """
    Core engine for the 'Hey Hik' voice assistant.
    Features: Floating AI Orb UI, native browser mic bypass, and Safari TTS Unlocking.
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
    4. If the user asks a complex research question, give a brief 1-2 sentence overview, and then explicitly guide them by saying: "For a deeper analysis of this topic, I recommend using the Intelligence Interrogation RAG or the Agentic AI module located in your left sidebar."
    """

    # 3. HTML & CSS FOR THE FLOATING AI ORB AND GLOW
    # (Rendered via markdown to ensure global styling applies to the main app body)
    st.markdown("""
    <style>
        /* 🛑 STRICT HIDE: Completely obliterate the bridge input box */
        div[data-testid="stTextInput"]:has(input[aria-label="hik_bridge_input"]) {
            display: none !important; visibility: hidden !important; height: 0px !important;
            margin: 0px !important; padding: 0px !important; opacity: 0 !important; pointer-events: none !important;
        }
        
        /* THE SIRI EDGE GLOW */
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

        /* THE FLOATING AI ORB BUTTON */
        .hik-fab {
            position: fixed; bottom: 85px; right: 25px; width: 45px; height: 45px;
            background: linear-gradient(135deg, #1b60d4 0%, #7f3ab7 100%);
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-size: 20px; color: white; cursor: pointer; z-index: 999990;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 2px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
        }
        .hik-fab:hover { transform: scale(1.1); box-shadow: 0 6px 20px rgba(0, 191, 255, 0.6); }
        .hik-fab.listening { animation: fab-pulse 1.5s infinite; background: linear-gradient(135deg, #d44c5c 0%, #FF272A 100%); }
        @keyframes fab-pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 39, 42, 0.7); } 70% { box-shadow: 0 0 0 15px rgba(255, 39, 42, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 39, 42, 0); } }
    </style>
    <div id="hik-fab-btn" class="hik-fab" title="Initialize Hik Voice Engine">🎙️</div>
    """, unsafe_allow_html=True)

    # 4. EXECUTABLE JAVASCRIPT LOGIC
    # (Must be injected using st.html() to bypass React script-stripping)
    st.html("""
    <script>
        (function() {
            // Use a polling loop to ensure the button exists in the DOM before attaching the click event
            function bindHikLogic() {
                const fabBtn = document.getElementById('hik-fab-btn');
                if (!fabBtn) {
                    setTimeout(bindHikLogic, 500);
                    return;
                }
                
                // Prevent duplicate listeners on re-renders
                if (fabBtn.dataset.bound === 'true') return;
                fabBtn.dataset.bound = 'true';
                
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (!SpeechRecognition) {
                    fabBtn.addEventListener('click', () => alert("Voice assistant is not supported in this browser. Please use Chrome, Edge, or Safari."));
                    return;
                }
                
                const recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.interimResults = false;
                recognition.lang = 'en-US';
                
                let isListening = false;
                let isAwake = false;
                
                fabBtn.addEventListener('click', () => {
                    // 🛑 SAFARI HACK: Speak an empty string instantly on click to permanently unlock TTS context for the session
                    window.speechSynthesis.speak(new SpeechSynthesisUtterance(''));
                    
                    if (!isListening) {
                        try { 
                            recognition.start(); 
                            isListening = true;
                            fabBtn.classList.add('listening');
                        } catch(e){}
                    } else {
                        isListening = false;
                        recognition.stop();
                        fabBtn.classList.remove('listening');
                        document.body.classList.remove("hik-awake");
                    }
                });
                
                recognition.onend = function() {
                    if (isListening) {
                        setTimeout(() => { try { recognition.start(); } catch(e){} }, 1000);
                    }
                };

                function sendToStreamlit(text) {
                    document.body.classList.remove("hik-awake");
                    const targetInput = document.querySelector('input[aria-label="hik_bridge_input"]');
                    if (targetInput) {
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        nativeInputValueSetter.call(targetInput, text);
                        targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                        setTimeout(() => {
                            targetInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, which: 13, bubbles: true }));
                        }, 200);
                    }
                }

                recognition.onresult = function(event) {
                    const last = event.results.length - 1;
                    const transcript = event.results[last][0].transcript.trim().toLowerCase();
                    
                    const wakeRegex = /(hey hik|hey hick|hey heek|hey hake)/i;
                    const hasWakeWord = wakeRegex.test(transcript);
                    
                    if (hasWakeWord) {
                        const query = transcript.replace(wakeRegex, '').trim();
                        if (query.length > 3) {
                            sendToStreamlit(query);
                            isAwake = false;
                        } else {
                            isAwake = true;
                            document.body.classList.add("hik-awake");
                        }
                    } 
                    else if (isAwake && transcript.length > 2) {
                        sendToStreamlit(transcript);
                        isAwake = false;
                    }
                };
            }
            
            // Start the DOM polling loop immediately
            setTimeout(bindHikLogic, 500);
        })();
    </script>
    """)

    # 5. INVISIBLE PYTHON RECEIVER
    vocal_query = st.text_input("hik_bridge_input", key="hik_vocal_query", label_visibility="hidden")

    if vocal_query:
        if not client:
            st.html("""<script>document.body.classList.remove("hik-awake"); window.speechSynthesis.speak(new SpeechSynthesisUtterance("I am offline. No Gemini API Key was detected."));</script>""")
            st.session_state['hik_vocal_query'] = ""
            return
            
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"SYSTEM INSTRUCTION: {hik_system_prompt}\n\nUSER VOCAL QUERY: {vocal_query}"
            )
            answer = response.text.replace('"', "'").replace('\n', ' ')
            
            # Send TTS command back to browser
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