import streamlit as st
import random
import re
from agent_graph import build_agent_graph

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

    # 3. BASE CSS: DEEP SPACE, RED GLOW OVERHAUL, TIGHT CHAT GAPS & ANTI-DIMMING
    base_css = """
    <style>
    /* 🛑 ANTI-STALE DIMMING FIX: Prevents the screen from going dull during processing */
    [data-stale="true"], [data-testid="stAppViewBlockContainer"][data-stale="true"] {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }
    .stMainBlockContainer, [data-testid="stAppViewContainer"] {
        opacity: 1 !important; 
        transition: none !important;
    }

    /* Clean up the main canvas padding */
    .block-container { padding-top: 3rem !important; max-width: 100% !important; padding-bottom: 150px !important; }
    
    /* 🛑 SIDEBAR FIX: Keep the header transparent so the hamburger button remains clickable */
    header[data-testid="stHeader"] { background-color: transparent !important; }

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
        overflow: hidden !important; 
    }
    
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
        margin-bottom: -15px !important; 
        padding-bottom: 0px !important;
        gap: 0.5rem !important; 
    }
    
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
    st.markdown(base_css, unsafe_allow_html=True)

    # 4. DYNAMIC CENTER LAYOUT (Only applies when chat is empty)
    # 🛑 THE FIX: Using a dedicated empty container ensures Streamlit obliterates the text instantly
    greeting_container = st.empty()
    chat_container = st.container()

    if is_empty:
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
        greeting_container.markdown(center_css + f'<div class="agent-wrapper"><div class="agent-greeting">{st.session_state.agentic_greeting}</div></div>', unsafe_allow_html=True)
    else:
        greeting_container.empty() # 🛑 Destroys the Ghost Text instantly
        with chat_container:
            for msg in st.session_state.agentic_messages:
                avatar_icon = "👤" if msg["role"] == "user" else "✨"
                with st.chat_message(msg["role"], avatar=avatar_icon):
                    st.markdown(msg["content"])
            
    # 6. THE INPUT HANDLER & LANGGRAPH TRIGGER
    agent_query = st.chat_input("Ask the geopolitical and OSINT pipeline...")
    
    if agent_query:
        # Display user query instantly to prevent screen dimming
        st.session_state.agentic_messages.append({"role": "user", "content": agent_query})
        st.rerun()

    # 7. PROCESS LATEST MESSAGE IF IT WAS FROM USER
    if not is_empty and st.session_state.agentic_messages[-1]["role"] == "user":
        latest_query = st.session_state.agentic_messages[-1]["content"]
        
        with chat_container: # Keeps the spinner perfectly aligned with the chat
            with st.chat_message("assistant", avatar="✨"):
                with st.spinner("Agentic Engine actively sweeping targets and synthesizing data..."):
                    try:
                        agent_app = build_agent_graph()
                        
                        initial_state = {
                            "execution_mode": "CUSTOM_UI",  
                            "current_target_urls": [],     
                            "user_prompt": latest_query,
                            "extracted_markdown_context": [],
                            "drafted_brief": {},
                            "ui_markdown": "",
                            "publish_status": "Pending"
                        }
                        
                        # Execute the graph
                        final_state = agent_app.invoke(initial_state)
                        
                        # Read directly from the raw Markdown channel
                        if final_state.get("ui_markdown"):
                            response_md = final_state["ui_markdown"]
                        else:
                            brief = final_state.get("drafted_brief", {})
                            response_md = f"### 🚨 {brief.get('Title', 'Intelligence Brief')}\n\n"
                            response_md += f"**Threat Level:** {brief.get('Threat_Level', 'UNKNOWN')}\n\n"
                            response_md += f"{brief.get('BLUF', 'No data generated.')}"
                            
                    except Exception as e:
                        response_md = f"⚠️ Critical Graph Execution Failure: {e}"

                    st.markdown(response_md)
                
        # Append final response to history
        st.session_state.agentic_messages.append({"role": "assistant", "content": response_md})