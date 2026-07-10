import streamlit as st
import random

def render_agentic_home():
    # 1. INITIALIZE CHAT STATE
    if "agentic_messages" not in st.session_state:
        st.session_state.agentic_messages = []
        
    is_empty = len(st.session_state.agentic_messages) == 0

    # 2. RANDOMIZED GREETING LOGIC
    greetings = [
        "Hi! What’s the next move?",
        "Any new ideas to explore?",
        "Where should we start?",
        "What should we focus on?",
        "Ready when you are",
        "Hi! Lets get into it",
        "What’s Next"
    ]
    
    if "agentic_greeting" not in st.session_state:
        st.session_state.agentic_greeting = random.choice(greetings)

    # 🌌 3. BASE CSS: DEEP SPACE, RED GLOW OVERHAUL & TIGHT CHAT GAPS
    base_css = """
    <style>
    /* Clean up the main canvas padding */
    .block-container { padding-top: 1rem !important; max-width: 100% !important; padding-bottom: 100px !important; }
    header { visibility: hidden !important; }

    /* 🌌 Deep Space Gemini Background */
    [data-testid="stAppViewContainer"] {
        background-color: #040406 !important;
        background-image: 
            radial-gradient(ellipse 60% 40% at 50% 100%, rgba(147, 51, 234, 0.08) 0%, transparent 70%),
            radial-gradient(ellipse 70% 50% at 50% 0%, rgba(30, 58, 138, 0.12) 0%, transparent 70%) !important;
        background-attachment: fixed !important;
    }

    /* 🛑 SAFELY HIDE THE RAG BUTTON ONLY ON THIS PAGE VIA CSS */
    div[data-testid="stElementContainer"]:has(#fab-anchor) + div { display: none !important; }

    /* 🟢 RESURRECT THE ROOT CHAT CONTAINERS ONLY FOR THE AGENTIC PAGE */
    [data-testid="stBottom"], 
    [data-testid="stChatFloatingInputContainer"] {
        display: block !important; 
        height: auto !important; 
        opacity: 1 !important; 
        pointer-events: auto !important; 
    }

    /* 🛑 ERADICATE THE BOTTOM GREY BAR COMPLETELY */
    [data-testid="stBottom"] { background-color: transparent !important; }
    [data-testid="stBottom"] > div { background: transparent !important; border-top: none !important; }
    [data-testid="stBottom"]::before, [data-testid="stBottom"]::after { display: none !important; }
    a.scroll-top-btn { display: none !important; opacity: 0 !important; visibility: hidden !important; }

    /* 🖱️ Style the inner wrapper */
    [data-testid="stChatInputContainer"] {
        display: flex !important; 
        opacity: 1 !important;
        pointer-events: auto !important;
        background-color: transparent !important;
        border: none !important;
        padding-bottom: 20px !important;
    }
    
    /* 🔴 THE DEFCON PULSE GLOW ANIMATION */
    @keyframes defconPulseChat {
        0% { box-shadow: 0 0 15px rgba(255, 0, 0, 0.5); }
        50% { box-shadow: 0 0 40px rgba(255, 0, 0, 1); }
        100% { box-shadow: 0 0 15px rgba(255, 0, 0, 0.5); }
    }

    /* 🔴 THE INPUT BOX: Pitch Black, Pill-Curved, Defcon Pulse */
    [data-testid="stChatInput"] {
        background-color: #000000 !important;
        border: 2px solid #ff0000 !important;
        border-radius: 50px !important; 
        animation: defconPulseChat 2s infinite !important;
        margin: 0 auto !important;
        overflow: hidden !important; /* 🛑 Forces the inner box to cut off exactly at the curve */
    }
    
    /* 🛑 Forces the inner text wrapper to match the curve perfectly */
    [data-testid="stChatInput"] > div {
        border-radius: 50px !important; 
    }
    
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        font-size: 1.1rem !important;
    }

    /* 🎨 PROFESSIONAL CHAT BUBBLE GRADIENTS & AGGRESSIVE GAP REDUCTION */
    div[data-testid="stChatMessage"] { 
        background: transparent !important; 
        margin-top: 0px !important;
        margin-bottom: -30px !important; /* 🛑 Pulls chat bubbles aggressively closer */
        padding-bottom: 0px !important;
        gap: 0.2rem !important; /* Neutralize Flexbox internal gaps */
    }
    
    /* Vertical block cleanup */
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }
    
    div[data-testid="stChatMessageContent"] {
        border-radius: 12px !important; padding: 12px 20px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important; color: #ffffff !important;
    }
    div[data-testid="stChatMessageContent"] * { color: #ffffff !important; }

    /* User Bubble (Deep Obsidian / Slate) */
    div[data-testid="stChatMessage"]:has([data-testid*="user"]) div[data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border: 1px solid #334155 !important;
    }
    /* AI Bubble (Deep Cosmic Indigo) */
    div[data-testid="stChatMessage"]:has([data-testid*="assistant"]) div[data-testid="stChatMessageContent"] {
        background: linear-gradient(135deg, #1e1b4b 0%, #172554 100%) !important;
        border: 1px solid #3730a3 !important;
    }
    
    /* Hide default avatar background */
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] {
        background-color: transparent !important;
    }
    </style>
    """

    # 4. DYNAMIC CENTER LAYOUT (Only applies when chat is empty)
    center_css = """
    <style>
    .agent-wrapper {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        height: 50vh; width: 100%;
    }
    .agent-greeting {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
        font-size: 2.5rem; font-weight: 500; letter-spacing: -0.5px; color: #e2e8f0; 
        text-align: center; margin-bottom: 20px; text-shadow: 0 0 20px rgba(255,255,255,0.1); 
    }
    /* Rip input to center */
    [data-testid="stChatInputContainer"] {
        position: absolute !important;
        bottom: 40vh !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 100% !important;
        max-width: 800px !important;
    }
    </style>
    """
    
    st.markdown(base_css, unsafe_allow_html=True)
    
    # 5. CONDITIONAL RENDERING
    if is_empty:
        st.markdown(center_css, unsafe_allow_html=True)
        st.markdown(f'<div class="agent-wrapper"><div class="agent-greeting">{st.session_state.agentic_greeting}</div></div>', unsafe_allow_html=True)
    else:
        for msg in st.session_state.agentic_messages:
            avatar_icon = "👤" if msg["role"] == "user" else "✨"
            with st.chat_message(msg["role"], avatar=avatar_icon):
                st.markdown(msg["content"])
                
    # 6. THE INPUT HANDLER & LANGGRAPH TRIGGER
    agent_query = st.chat_input("Ask the Agentic OSINT Command...")
    
    if agent_query:
        # Display user query
        st.session_state.agentic_messages.append({"role": "user", "content": agent_query})
        
        # 1. Parse the prompt for any specific URLs using Regex
        import re
        raw_urls = re.findall(r'(https?://[^\s]+)', agent_query)
        # 🛑 FIX: Strip trailing punctuation (quotes, periods) that break URLs and cause 404s
        extracted_urls = [url.rstrip('"\'.,;)') for url in raw_urls]
        
        # If the user provided a URL, use it. Otherwise, default to standard OSINT sweeps.
        target_urls = extracted_urls if extracted_urls else [
            "https://www.reuters.com/technology", 
            "https://asia.nikkei.com/Business/Tech/Semiconductors"
        ]

        # 2. Invoke the LangGraph Engine Live
        from agent_graph import build_agent_graph
        try:
            agent_app = build_agent_graph()
            
            # Pass the targets directly into the AgentState memory
            initial_state = {
                "current_target_urls": target_urls,
                "user_prompt": agent_query,
                "extracted_markdown_context": [],
                "drafted_brief": {},
                "publish_status": "Pending"
            }
            
            # Execute the 5-node graph synchronously for the UI
            final_state = agent_app.invoke(initial_state)
            
            # 3. Format the JSON output from Node 4/5 into a beautiful chat response
            brief = final_state.get("drafted_brief", {})
            if brief:
                response_md = f"### 🚨 {brief.get('Title', 'Intelligence Alert')}\n\n"
                response_md += f"**Threat Level:** {brief.get('Threat_Level', 'UNKNOWN')}\n\n"
                response_md += f"**BLUF:** {brief.get('Action', '')}\n\n"
                response_md += f"**Predictive Analysis:** {brief.get('Predictive_Analysis', '')}\n\n"
                response_md += f"*Sources Scanned:* {brief.get('Source', 'Internal Engine')}"
            else:
                response_md = "⚠️ Agent completed the sweep but failed to synthesize a valid brief."
                
        except Exception as e:
            response_md = f"⚠️ Critical Graph Execution Failure: {e}"

        # Display the final intelligence product
        st.session_state.agentic_messages.append({"role": "assistant", "content": response_md})
        st.rerun()