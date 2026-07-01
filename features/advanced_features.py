import streamlit as st
import pandas as pd
import json
import re
import os  # <-- Added to check for live JSON files
from utils.constants import COUNTRY_INFO
from utils.data_helpers import get_brief_mappings, extract_tag
from utils.engines import calculate_domain_threat

def render_threat_scoring():
    st.title("Quantitative Threat Scoring")
    st.markdown("Algorithmic ranking of regional supply chain vulnerability based on historical archive data.")
    
    archive_mapping = get_brief_mappings('data')
    if archive_mapping:
        scoring_data = {}
        for f_path in archive_mapping.values():
            try:
                with open(f_path, 'r') as file:
                    d = json.load(file)
                    actions = d.get('recent_actions', [])
                    
                    for action in actions:
                        loc = str(action.get('Location', '')).strip()
                        if loc and loc != "Global":
                            for country, data_tuple in COUNTRY_INFO.items():
                                if country.lower() in loc.lower():
                                    region = data_tuple[1]
                                    scoring_data[region] = scoring_data.get(region, 0) + 1
                                    break
            except: pass
        
        if scoring_data:
            score_df = pd.DataFrame(list(scoring_data.items()), columns=["Region", "Instability Actions Logged"])
            score_df = score_df.sort_values(by="Instability Actions Logged", ascending=False).reset_index(drop=True)
            
            def assign_threat(score):
                if score > 10: return "🔴 Critical"
                elif score > 5: return "🟠 High"
                elif score > 2: return "🟡 Elevated"
                else: return "🟢 Standard"
                
            score_df["Calculated Threat Level"] = score_df["Instability Actions Logged"].apply(assign_threat)
            st.table(score_df.set_index(score_df.columns[0]))
        else:
            st.warning("Not enough historical data to generate scores yet.")
    else:
        st.warning("No archives available.")


# ==========================================
# --- UPGRADED 4-NODE RAG ENGINE ---
# ==========================================
def render_rag_interrogation(api_keys, model_name, text_summary="", text_section_1="", text_section_2="", text_section_3="", text_section_4="", text_military="", text_india="", text_wa="", text_ews=""):
    st.title("Intelligence Interrogation (RAG)")
    st.markdown("Query the historical SemicoN database and live platform feeds. Responses are generated strictly from your vetted archives and current geopolitical dashboards.")

    if not api_keys:
        st.error("⚠️ GEMINI_API_KEY is missing from Koyeb Environment Variables. Please add it to unlock this feature.")
        return 

    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = []

    for message in st.session_state.rag_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a strategic question:"):
        st.session_state.rag_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Scanning live feeds, intelligence archives & calculating threat models... 🕵️‍♂️")

            context_data = ""

            # ==========================================
            # 1. INGEST LIVE DASHBOARD TEXT FEEDS
            # ==========================================
            context_data += "\n\n=== LIVE DASHBOARD TEXT FEEDS ===\n"
            live_texts = {
                "Executive Summary": text_summary,
                "Global Foundry Market": text_section_1,
                "AI Chip Demand & Lithography": text_section_2,
                "Critical Minerals (REE)": text_section_3,
                "Export Controls & Geopolitics": text_section_4,
                "Military & Outer Space": text_military,
                "India Developments": text_india,
                "West Asia / Middle East": text_wa,
                "Early Warning Systems": text_ews
            }
            for section, txt in live_texts.items():
                if txt and len(str(txt).strip()) > 10:
                    context_data += f"\n--- {section.upper()} ---\n{txt}\n"

            # ==========================================
            # 2. INGEST LIVE AUTONOMOUS JSON DATA
            # ==========================================
            live_files = [
                ('data/executive_home/tactical_events_24h.json', 'EXECUTIVE HOME TACTICAL'),
                ('data/executive_home/flush_brief_24h.json', 'EXECUTIVE HOME BRIEF'),
                ('data/today_snippet/tactical_events_24h.json', 'TODAY SNIPPET TACTICAL'),
                ('data/today_snippet/shift_brief.json', 'TODAY SNIPPET BRIEF'),
                ('data/weekly_tactical/tactical_events_24h.json', 'WEEKLY TACTICAL EVENTS')
            ]
            context_data += "\n\n=== LIVE AUTONOMOUS JSON FEEDS ===\n"
            for file_path, label in live_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            d = json.load(f)
                            if isinstance(d, list): d = d[:25]
                            elif isinstance(d, dict) and 'recent_actions' in d: d['recent_actions'] = d['recent_actions'][:25]
                            context_data += f"\n--- {label} ---\n{json.dumps(d)}\n"
                    except: pass

            # ==========================================
            # 3. EXISTING: HISTORICAL ARCHIVE RAG LOGIC
            # ==========================================
            archive_mapping = get_brief_mappings('data')
            context_data += "\n\n=== HISTORICAL ARCHIVES ===\n"
            
            user_keywords = [w.lower() for w in re.findall(r'\b\w+\b', prompt) if len(w) > 2 and w.lower() not in ['what', 'when', 'where', 'which', 'who', 'why', 'how', 'were', 'was', 'this', 'that', 'with', 'from', 'about', 'the', 'and', 'for', 'are', 'did', 'have', 'has']]

            file_scores = []
            if archive_mapping:
                for f_path in archive_mapping.values():
                    try:
                        with open(f_path, 'r') as file:
                            d = json.load(file)
                            content = d.get('brief_raw', '').lower() + json.dumps(d.get('recent_actions', [])).lower()
                            score = sum(content.count(kw) for kw in user_keywords)
                            file_scores.append((score, f_path))
                    except: pass

                file_scores.sort(key=lambda x: x[0], reverse=True)
                top_files = [fs[1] for fs in file_scores if fs[0] > 0][:3]
                if not top_files:
                    top_files = list(archive_mapping.values())[:2]
                
                for f_path in top_files:
                    try:
                        with open(f_path, 'r') as file:
                            d = json.load(file)
                            r_text = d.get('brief_raw', '')
                            categories = [
                                ("Global Foundry Market", extract_tag('EXEC', r_text) or ""),
                                ("AI Chip Demand", extract_tag('LITHO', r_text) or ""),
                                ("Critical Minerals (REE)", extract_tag('REE', r_text) or ""),
                                ("Export Controls", extract_tag('GEO', r_text) or ""),
                                ("Military & Outer Space", extract_tag('MILITARY', r_text) or ""),
                                ("India Developments", extract_tag('INDIA', r_text) or ""),
                                ("West Asia / Middle East", extract_tag('WEST_ASIA', r_text) or "")
                            ]
                            
                            context_data += f"\n\n--- INTELLIGENCE BRIEF DATE: {d.get('date', 'Unknown')} ---\n"
                            context_data += "ALGORITHMIC THREAT SCORES:\n"
                            for name, txt in categories:
                                if len(txt.strip()) > 25:
                                    score = calculate_domain_threat(name, txt, d)
                                    context_data += f"- {name}: {score}%\n"
                                    
                            context_data += "\nRAW INTELLIGENCE TEXT:\n"
                            context_data += r_text
                            context_data += f"\nLOGGED STATE ACTIONS:\n{json.dumps(d.get('recent_actions', [])[:25])}"
                    except: pass

            sys_prompt = f"""
            You are an elite geopolitical intelligence AI assistant for the SemicoN Dashboard.
            Your primary directive is to answer the user's question using the provided intelligence context below, and supplement with external information if needed.
            
            CRITICAL GROUNDING & CITATION DIRECTIVES:
            1. STRICTLY DO NOT use, reference, or cite www.wikipedia.org. Filter it out completely from your knowledge and external searches.
            2. When citing internal dashboard data, format citations with the exact section and date. Example: [Reported in/by Archive and Live Context: Today Snippet Tactical on 2026-06-05] or [Reported in/by Archive and Live Context: Intelligence Brief Date: May 7-14, 2026].
            3. DO NOT use standard bracketed footnote numbers (e.g., avoid). Use explicit inline text citations based on the context provided.
            
            ARCHIVES AND LIVE CONTEXT:
            {context_data}
            """
            
            try:
                from google import genai
                import time
                full_response = ""
                success = False
                
                # 🚀 Loop through the 4-Key Cascade
                for attempt, api_key in enumerate(api_keys):
                    try:
                        client = genai.Client(api_key=api_key)
                        # 🛑 THE FIX: Use standard blocking generation to prevent websocket timeouts with heavy RAG payloads
                        response = client.models.generate_content(
                            model=model_name,
                            contents=[sys_prompt, prompt]
                        )
                        full_response = response.text
                        message_placeholder.markdown(full_response)
                        success = True
                        break # Node worked, exit retry loop
                        
                    except Exception as e:
                        # If node fails and we have backup keys remaining
                        if attempt < len(api_keys) - 1:
                            message_placeholder.markdown("⚠️ Try Again... Shifting to backup node 🕵️‍♂️")
                            time.sleep(1.5)
                            continue
                        else:
                            raise e # Last node failed, trigger main error handler
                            
            except Exception as e:
                error_str = str(e).lower()
                if "503" in error_str or "429" in error_str or "unavailable" in error_str or "quota" in error_str or "limit" in error_str or "exhausted" in error_str:
                    full_response = "⚠️ Server Down. Please try after sometime."
                else:
                    full_response = f"⚠️ Error querying the intelligence database: {e}"
                message_placeholder.markdown(full_response)
                
        st.session_state.rag_messages.append({"role": "assistant", "content": full_response})

# ==========================================
# PHASE 2 STEP B: HYBRID NATIVE RAG FAB ENGINE 
# ==========================================
def render_fab_chat(api_keys, model_name, text_summary="", text_section_1="", text_section_2="", text_section_3="", text_section_4="", text_military="", text_india="", text_wa="", text_ews=""):
    import os
    import json
    import re
    from utils.data_helpers import get_brief_mappings

    # 1. Initialize State
    if "fab_open" not in st.session_state:
        st.session_state.fab_open = False
    if "fab_rag_messages" not in st.session_state:
        st.session_state.fab_rag_messages = []

    @st.fragment
    def render_isolated_fab():
        def toggle_fab():
            st.session_state.fab_open = not st.session_state.fab_open

        # 2. ULTRA-FAST NATIVE CSS
        st.markdown("""
        <style>
        div[data-testid="stElementContainer"]:has(#fab-anchor),
        div[data-testid="stElementContainer"]:has(#chat-anchor) { display: none !important; }

        /* FAB BUTTON */
        div[data-testid="stElementContainer"]:has(#fab-anchor) + div {
            position: fixed !important; bottom: 30px !important; right: 30px !important; z-index: 999999 !important;
        }
        div[data-testid="stElementContainer"]:has(#fab-anchor) + div button {
            width: 65px !important; height: 65px !important; border-radius: 50% !important;
            background: radial-gradient(circle, #2d2d2d, #000000) !important;
            border: 1px solid #444 !important; box-shadow: 0 4px 20px rgba(0,0,0,0.8) !important; padding: 0 !important;
        }

        /* CHAT WINDOW */
        div[data-testid="stElementContainer"]:has(#chat-anchor) + div {
            position: fixed !important; bottom: 110px !important; right: 30px !important;
            width: 380px !important; height: 550px !important; background: #000000 !important;
            border: 1px solid #2d2d2d !important; border-radius: 16px !important; z-index: 999998 !important;
            padding: 20px !important; box-shadow: 0 10px 50px rgba(0,0,0,0.95) !important; overflow-y: auto !important;
        }

        /* --- GRADIENT CHAT BUBBLES --- */
        div[data-testid="stChatMessage"] { background: transparent !important; }
        
        div[data-testid="stChatMessageContent"] {
            border-radius: 12px !important; color: #f8fafc !important;
            padding: 12px 16px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
        }

        /* Force Streamlit's default grey text background to be transparent */
        div[data-testid="stChatMessageContent"] > div {
            background: transparent !important;
        }

        /* Query (User) - Gradient Red using Bulletproof Wildcards */
        div[data-testid="stChatMessage"]:has([data-testid*="user"]) div[data-testid="stChatMessageContent"],
        div[data-testid="stChatMessage"]:has([aria-label*="user"]) div[data-testid="stChatMessageContent"],
        div[data-testid="stChatMessage"]:has(svg[title*="user"]) div[data-testid="stChatMessageContent"] {
            background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%) !important;
            border: 1px solid #991b1b !important;
        }

        /* Response (Assistant) - Gradient Sky Blue using Bulletproof Wildcards */
        div[data-testid="stChatMessage"]:has([data-testid*="assistant"]) div[data-testid="stChatMessageContent"],
        div[data-testid="stChatMessage"]:has([aria-label*="assistant"]) div[data-testid="stChatMessageContent"],
        div[data-testid="stChatMessage"]:has(svg[title*="assistant"]) div[data-testid="stChatMessageContent"] {
            background: linear-gradient(135deg, #0284c7 0%, #082f49 100%) !important;
            border: 1px solid #0369a1 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # 3. CHAT LOGIC 
        if st.session_state.fab_open:
            st.markdown('<span id="chat-anchor"></span>', unsafe_allow_html=True)
            with st.container():
                c1, c2 = st.columns([5,1])
                with c1:
                    st.markdown("<h4 style='color: #00bfff; margin:0;'>RAG Analysis</h4>", unsafe_allow_html=True)
                with c2:
                    st.button("✖", key="close_fab", on_click=toggle_fab)

                st.markdown("<hr style='border-color: #333; margin-top: 5px; margin-bottom: 15px;'>", unsafe_allow_html=True)

                if not api_keys:
                    st.error("⚠️ GEMINI_API_KEY is missing.")
                else:
                    for message in st.session_state.fab_rag_messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

                    if st.session_state.get("fab_pending_query"):
                        query = st.session_state.fab_pending_query
                        st.session_state.fab_pending_query = None

                        with st.chat_message("assistant"):
                            message_placeholder = st.empty()
                            message_placeholder.markdown("Scanning live feeds & archives... 🕵️‍♂️")

                            context_data = ""
                            context_data += "\n\n=== LIVE DASHBOARD TEXT FEEDS ===\n"
                            live_texts = {
                                "Executive Summary": text_summary, "Global Foundry Market": text_section_1,
                                "AI Chip Demand & Lithography": text_section_2, "Critical Minerals (REE)": text_section_3,
                                "Export Controls": text_section_4, "Military & Outer Space": text_military,
                                "India": text_india, "West Asia": text_wa, "Early Warning": text_ews
                            }
                            for section, txt in live_texts.items():
                                if txt and len(str(txt).strip()) > 10:
                                    context_data += f"\n--- {section.upper()} ---\n{txt}\n"

                            live_files = [
                                ('data/executive_home/tactical_events_24h.json', 'EXECUTIVE HOME TACTICAL'),
                                ('data/executive_home/flush_brief_24h.json', 'EXECUTIVE HOME BRIEF'),
                                ('data/today_snippet/tactical_events_24h.json', 'TODAY SNIPPET TACTICAL'),
                                ('data/today_snippet/shift_brief.json', 'TODAY SNIPPET BRIEF'),
                                ('data/weekly_tactical/tactical_events_24h.json', 'WEEKLY TACTICAL EVENTS')
                            ]
                            context_data += "\n\n=== LIVE AUTONOMOUS JSON FEEDS ===\n"
                            for file_path, label in live_files:
                                if os.path.exists(file_path):
                                    try:
                                        with open(file_path, 'r') as f:
                                            file_data = json.load(f)
                                            if isinstance(file_data, list): file_data = file_data[:25]
                                            elif isinstance(file_data, dict) and 'recent_actions' in file_data: file_data['recent_actions'] = file_data['recent_actions'][:25]
                                            context_data += f"\n--- {label} ---\n{json.dumps(file_data)}\n"
                                    except: pass

                            archive_mapping = get_brief_mappings('data')
                            context_data += "\n\n=== HISTORICAL ARCHIVES ===\n"
                            user_keywords = [w.lower() for w in re.findall(r'\b\w+\b', query) if len(w) > 2 and w.lower() not in ['what', 'when', 'where', 'which', 'who', 'why', 'how', 'were', 'was', 'this', 'that', 'with', 'from', 'about', 'the', 'and', 'for', 'are', 'did', 'have', 'has']]
                            
                            if archive_mapping:
                                file_scores = []
                                for f_path in archive_mapping.values():
                                    try:
                                        with open(f_path, 'r') as file:
                                            d = json.load(file)
                                            content = d.get('brief_raw', '').lower() + json.dumps(d.get('recent_actions', [])).lower()
                                            score = sum(content.count(kw) for kw in user_keywords)
                                            file_scores.append((score, f_path))
                                    except: pass

                                file_scores.sort(key=lambda x: x[0], reverse=True)
                                top_files = [fs[1] for fs in file_scores if fs[0] > 0][:3]
                                if not top_files:
                                    top_files = list(archive_mapping.values())[:2]
                                
                                for f_path in top_files:
                                    try:
                                        with open(f_path, 'r') as file:
                                            d = json.load(file)
                                            context_data += f"\n\n--- INTELLIGENCE BRIEF DATE: {d.get('date', 'Unknown')} ---\n"
                                            context_data += "\nRAW INTELLIGENCE TEXT:\n" + d.get('brief_raw', '')
                                            context_data += f"\nLOGGED STATE ACTIONS:\n{json.dumps(d.get('recent_actions', [])[:10])}"
                                    except: pass

                            sys_prompt = f"""
                            You are an elite geopolitical intelligence AI assistant for the SemicoN Dashboard.
                            Answer the user's question concisely using the provided context and supplement with external web information if needed.
                            
                            CRITICAL GROUNDING & CITATION DIRECTIVES:
                            1. STRICTLY DO NOT use, reference, or cite www.wikipedia.org. Filter it out completely from your knowledge and external searches.
                            2. When citing internal dashboard data, format citations with the exact section and date. Example: [Reported in/by Archive and Live Context: Today Snippet Tactical on 2026-06-05] or [Reported in/by Archive and Live Context: Intelligence Brief Date: May 7-14, 2026].
                            3. DO NOT use standard bracketed footnote numbers (e.g., avoid). Use explicit inline text citations based on the context provided.
                            
                            ARCHIVES AND LIVE CONTEXT:
                            {context_data}
                            """
                            
                            try:
                                from google import genai
                                import time
                                full_response = ""
                                unique_urls = set()
                                sources_md = ""
                                success = False
                                
                                # 🚀 Loop through the 4-Key Cascade
                                for attempt, api_key in enumerate(api_keys):
                                    try:
                                        client = genai.Client(api_key=api_key)
                                        # 🛑 THE FIX: Shift to blocking generation for Google Search grounding to stop Streamlit crashes
                                        response = client.models.generate_content(
                                            model=model_name,
                                            contents=[sys_prompt, query],
                                            config={"tools": [{"google_search": {}}]}
                                        )
                                        
                                        full_response = response.text
                                        unique_urls = set()
                                        sources_md = ""
                                        
                                        # Intercept Grounding Metadata safely after generation completes
                                        try:
                                            if response.candidates and response.candidates[0].grounding_metadata:
                                                meta = response.candidates[0].grounding_metadata
                                                if hasattr(meta, 'grounding_chunks') and meta.grounding_chunks:
                                                    for g_chunk in meta.grounding_chunks:
                                                        if hasattr(g_chunk, 'web') and getattr(g_chunk.web, 'uri', None):
                                                            title = getattr(g_chunk.web, 'title', 'Source link')
                                                            url = g_chunk.web.uri
                                                            if url not in unique_urls:
                                                                unique_urls.add(url)
                                                                sources_md += f"\n* [{title}]({url})"
                                        except Exception: pass
                                            
                                        success = True
                                        break # Node worked, exit retry loop

                                    except Exception as e:
                                        if attempt < len(api_keys) - 1:
                                            message_placeholder.markdown("⚠️ Try Again... Shifting to backup node 🕵️‍♂️")
                                            time.sleep(1.5)
                                            continue
                                        else:
                                            raise e

                                if success:
                                    if sources_md:
                                        full_response += f"\n\n---\n**🌐 Live Web Search Grounding Activated:**\n{sources_md}"
                                    if not full_response.strip():
                                        full_response = "Intelligence processing completed. Re-indexing data models..."
                                    message_placeholder.markdown(full_response)
                                
                            except Exception as e:
                                error_str = str(e).lower()
                                if "503" in error_str or "429" in error_str or "unavailable" in error_str or "quota" in error_str or "limit" in error_str or "exhausted" in error_str:
                                    full_response = "⚠️ Server Down. Please try after sometime."
                                else:
                                    full_response = f"⚠️ Error querying database: {e}"
                                    
                                message_placeholder.markdown(full_response)
                                
                        st.session_state.fab_rag_messages.append({"role": "assistant", "content": full_response})
                        st.rerun()

                    if "fab_input_text" not in st.session_state:
                        st.session_state.fab_input_text = ""
                        
                    def submit_fab_chat():
                        if st.session_state.fab_input_text:
                            st.session_state.fab_rag_messages.append({"role": "user", "content": st.session_state.fab_input_text})
                            st.session_state.fab_pending_query = st.session_state.fab_input_text
                            st.session_state.fab_input_text = "" 
                            
                    st.text_input("Ask the dashboard...", key="fab_input_text", on_change=submit_fab_chat)

        st.markdown('<span id="fab-anchor"></span>', unsafe_allow_html=True)
        st.button("RAG", key="fab_main_toggle", on_click=toggle_fab)

    # 4. EXECUTE THE ISOLATED FRAGMENT
    render_isolated_fab()