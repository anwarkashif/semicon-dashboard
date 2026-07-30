import streamlit as st
import urllib.parse
from google import genai
import os

def render_hik_voice_assistant(client):
    """
    Core engine for the 'Hey Hik' voice assistant.
    Injects continuous listening JS, Edge Glow CSS, and the Gemini TTS bridge.
    """
    
    # 1. HIK'S IDENTITY & SYSTEM PROMPT
    # We define Hik's knowledge base, creator, and routing logic here.
    hik_system_prompt = """
    You are Hik, the exclusive voice assistant for the SemicoN Dashboard. 
    Your creator and the owner of this platform is Kashif Anwar. 
    You are designed to assist geopolitical researchers and strategic intelligence analysts.
    
    RULES FOR VOCAL RESPONSES:
    1. Keep responses conversational, concise, and easy to listen to (like Siri or Alexa).
    2. DO NOT use markdown formatting, bolding, asterisks, or bullet points. Speak in plain text sentences.
    3. If the user asks a simple question, answer it directly.
    4. If the user asks a complex research question, give a brief 1-2 sentence overview, and then explicitly guide them by saying: "For a deeper analysis of this topic, I recommend using the Intelligence Interrogation RAG or the Agentic AI module located in your left sidebar."
    """

    # 2. INJECT CSS FOR THE SIRI-STYLE EDGE GLOW
    st.markdown("""
    <style>
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
        
        /* Hidden input bridge to pass JS audio transcripts to Streamlit Python */
        .hik-bridge-container { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # 3. INJECT CONTINUOUS SPEECH RECOGNITION JAVASCRIPT
    st.html("""
    <script>
        // Check for browser support
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            let isAwake = false;
            
            // Auto-restart loop to keep listening in the background
            recognition.onend = function() {
                setTimeout(() => { try { recognition.start(); } catch(e){} }, 1000);
            };

            recognition.onresult = function(event) {
                const last = event.results.length - 1;
                const transcript = event.results[last][0].transcript.trim().toLowerCase();
                
                // WAKE WORD DETECTION (Accounts for slight AI misspellings of 'Hik')
                if (!isAwake && (transcript.includes("hey hik") || transcript.includes("hey hick") || transcript.includes("hey heek"))) {
                    isAwake = true;
                    document.body.classList.add("hik-awake");
                    
                    // Acknowledge wake word
                    const beep = new Audio('data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU'); 
                    // (Optional: add a real base64 blip sound here)
                    
                    // Hik is now listening for the actual command
                } 
                else if (isAwake && transcript.length > 3) {
                    // COMMAND RECEIVED. Send to Python.
                    isAwake = false;
                    
                    // Locate Streamlit's hidden text input
                    const inputs = window.parent.document.querySelectorAll('input[type="text"]');
                    let targetInput = null;
                    inputs.forEach(input => {
                        if (input.getAttribute('aria-label') === 'hik_bridge_input') {
                            targetInput = input;
                        }
                    });
                    
                    if (targetInput) {
                        // React 18 Value Setter Hack to force Streamlit to register the JS input
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                        nativeInputValueSetter.call(targetInput, transcript);
                        targetInput.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        setTimeout(() => {
                            targetInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
                        }, 100);
                    }
                }
            };
            
            // Start listening on page load (Browser requires user to click anywhere on the page first for mic perm)
            document.addEventListener('click', function initMic() {
                try { recognition.start(); } catch(e){}
                document.removeEventListener('click', initMic);
            });
        }
    </script>
    """)

    # 4. PYTHON-SIDE LISTENER & GENERATOR
    st.markdown('<div class="hik-bridge-container">', unsafe_allow_html=True)
    vocal_query = st.text_input("hik_bridge_input", key="hik_vocal_query", label_visibility="hidden")
    st.markdown('</div>', unsafe_allow_html=True)

    if vocal_query:
        # User spoke a command to Hik. Process it via Gemini.
        try:
            if not client:
                st.error("Hik Offline: No Gemini API Key configured.")
                return
                
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"SYSTEM INSTRUCTION: {hik_system_prompt}\n\nUSER VOCAL QUERY: {vocal_query}"
            )
            
            answer = response.text.replace('"', "'").replace('\n', ' ')
            
            # Send answer back to Javascript for Text-To-Speech (TTS)
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
            
            # Clear the input so it can listen again
            st.session_state['hik_vocal_query'] = ""
            
        except Exception as e:
            st.html("""<script>document.body.classList.remove("hik-awake"); window.speechSynthesis.speak(new SpeechSynthesisUtterance("I encountered an error connecting to the neural network."));</script>""")