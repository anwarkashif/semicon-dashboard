import streamlit as st
import random
import re
from agent_graph import build_agent_graph
import folium
from streamlit_folium import st_folium

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

    # 3. BASE CSS MATRIX: RED GLOW OVERHAUL & ANTI-DIMMING CONTROLS
    base_css = """
    <style>
    [data-stale="true"], [data-testid="stAppViewBlockContainer"][data-stale="true"] {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }
    .stApp, .stMainBlockContainer, [data-testid="stAppViewContainer"] {
        opacity: 1 !important; 
        transition: none !important;
    }
    .block-container { padding-top: 3rem !important; max-width: 100% !important; padding-bottom: 150px !important; }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stAppViewContainer"] {
        background-color: #040406 !important;
        background-image: 
            radial-gradient(ellipse 60% 40% at 50% 100%, rgba(147, 51, 234, 0.08) 0%, transparent 70%),
            radial-gradient(ellipse 70% 50% at 50% 0%, rgba(30, 58, 138, 0.12) 0%, transparent 70%) !important;
        background-attachment: fixed !important;
    }
    div[data-testid="stElementContainer"]:has(#fab-anchor) + div { display: none !important; }
    [data-testid="stBottom"], [data-testid="stChatFloatingInputContainer"] {
        display: block !important; height: auto !important; opacity: 1 !important; pointer-events: auto !important; 
    }
    [data-testid="stBottom"] { background-color: transparent !important; }
    [data-testid="stBottom"] > div { background: transparent !important; border-top: none !important; }
    [data-testid="stBottom"]::before, [data-testid="stBottom"]::after { display: none !important; }
    a.scroll-top-btn { display: none !important; opacity: 0 !important; visibility: hidden !important; }
    [data-testid="stChatInputContainer"] {
        display: flex !important; opacity: 1 !important; pointer-events: auto !important; background-color: transparent !important; border: none !important; padding-bottom: 20px !important;
    }
    @keyframes defconPulseChat {
        0% { box-shadow: 0 0 15px rgba(255, 0, 0, 0.5); }
        50% { box-shadow: 0 0 40px rgba(255, 0, 0, 1); }
        100% { box-shadow: 0 0 15px rgba(255, 0, 0, 0.5); }
    }
    [data-testid="stChatInput"] {
        background-color: #000000 !important; border: 2px solid #ff0000 !important; border-radius: 50px !important; animation: defconPulseChat 2s infinite !important; margin: 0 auto !important; overflow: hidden !important; 
    }
    [data-testid="stChatInput"] > div { border-radius: 50px !important; }
    [data-testid="stChatInput"] textarea { color: #ffffff !important; font-size: 1.1rem !important; }
    div[data-testid="stChatMessage"] { background: transparent !important; margin-top: 0px !important; margin-bottom: -15px !important; padding-bottom: 0px !important; gap: 0.5rem !important; }
    div[data-testid="stVerticalBlock"] { gap: 0rem !important; }
    div[data-testid="stChatMessageContent"] { border-radius: 12px !important; padding: 12px 20px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important; color: #ffffff !important; }
    div[data-testid="stChatMessageContent"] * { color: #ffffff !important; }
    div[data-testid="stChatMessage"]:has([data-testid*="user"]) div[data-testid="stChatMessageContent"] { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important; border: 1px solid #334155 !important; }
    div[data-testid="stChatMessage"]:has([data-testid*="assistant"]) div[data-testid="stChatMessageContent"] { background: linear-gradient(135deg, #1e1b4b 0%, #172554 100%) !important; border: 1px solid #3730a3 !important; }
    div[data-testid="stChatMessageAvatarUser"], div[data-testid="stChatMessageAvatarAssistant"] { background-color: transparent !important; }
    </style>
    """
    st.markdown(base_css, unsafe_allow_html=True)

    greeting_container = st.empty()
    chat_container = st.container()

    if not is_empty:
        greeting_container.empty()
    else:
        center_css = """
        <style>
        .agent-wrapper { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 50vh; width: 100%; }
        .agent-greeting { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 2.5rem; font-weight: 500; letter-spacing: -0.5px; color: #e2e8f0; text-align: center; margin-bottom: 20px; text-shadow: 0 0 20px rgba(255,255,255,0.1); }
        [data-testid="stChatInputContainer"] { position: absolute !important; bottom: 40vh !important; left: 50% !important; transform: translateX(-50%) !important; width: 100% !important; max-width: 800px !important; }
        </style>
        """
        greeting_container.markdown(center_css + f'<div class="agent-wrapper"><div class="agent-greeting">{st.session_state.agentic_greeting}</div></div>', unsafe_allow_html=True)

    # 🌍 RENDER HISTORICAL CHAT WITH INJECTED MAPS
    if not is_empty:
        with chat_container:
            for idx, msg in enumerate(st.session_state.agentic_messages):
                avatar_icon = "👤" if msg["role"] == "user" else "✨"
                with st.chat_message(msg["role"], avatar=avatar_icon):
                    st.markdown(msg["content"])
                    
                    # If this specific chat bubble contains map data, draw the interactive map!
                    if msg.get("map_data"):
                        coords = msg["map_data"]
                        m = folium.Map(location=[coords["lat"], coords["lon"]], zoom_start=13)
                        folium.Marker([coords["lat"], coords["lon"]], popup=coords["label"], tooltip=coords.get("address", coords["label"])).add_to(m)
                        # Replaced width=700 with use_container_width=True
                        st_folium(m, use_container_width=True, height=400, key=f"hist_map_{idx}")
            
    agent_query = st.chat_input("Ask the geopolitical and OSINT pipeline...")
    
    if agent_query:
        greeting_container.empty()
        st.session_state.agentic_messages.append({"role": "user", "content": agent_query})
        st.rerun()

    # 7. EXECUTE STATE FLOW WHEN USER INPUT PENDS
    if not is_empty and st.session_state.agentic_messages[-1]["role"] == "user":
        latest_query = st.session_state.agentic_messages[-1]["content"]
        
        with chat_container:
            with st.chat_message("assistant", avatar="✨"):
                greeting_container.empty()
                with st.spinner("Typing...💬"):
                    try:
                        agent_app = build_agent_graph()
                        
                        initial_state = {
                            "execution_mode": "CUSTOM_UI",  
                            "current_target_urls": [],     
                            "user_prompt": latest_query,
                            "chat_history": st.session_state.agentic_messages[:-1], 
                            "extracted_markdown_context": [],
                            "drafted_brief": {},
                            "ui_markdown": "",
                            "map_coords": None, 
                            "publish_status": "Pending"
                        }
                        
                        final_state = agent_app.invoke(initial_state)
                        response_md = final_state.get("ui_markdown", "⚠️ State error extracting markdown payload.")
                        map_data = final_state.get("map_coords")
                            
                    except Exception as e:
                        response_md = f"⚠️ Critical Graph Execution Failure: {e}"
                        map_data = None

                    st.markdown(response_md)
                    
                    # 🌍 RENDER LIVE NEW MAP
                    if map_data:
                        m = folium.Map(location=[map_data["lat"], map_data["lon"]], zoom_start=13)
                        folium.Marker([map_data["lat"], map_data["lon"]], popup=map_data["label"], tooltip=map_data.get("address", map_data["label"])).add_to(m)
                        # Replaced width=700 with use_container_width=True
                        st_folium(m, use_container_width=True, height=400, key=f"live_map_{len(st.session_state.agentic_messages)}")
                
        # Append final response & map coordinates to history
        st.session_state.agentic_messages.append({
            "role": "assistant", 
            "content": response_md,
            "map_data": map_data
        })