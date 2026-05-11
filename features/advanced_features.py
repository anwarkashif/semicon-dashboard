import streamlit as st
import pandas as pd
import json
import re
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

def render_rag_interrogation(client, model_name):
    st.title("Intelligence Interrogation (RAG)")
    st.markdown("Query the historical SemicoN database. Responses are generated strictly from your vetted archives.")

    if not client:
        st.error("⚠️ GEMINI_API_KEY is missing from Koyeb Environment Variables. Please add it to unlock this feature.")
        return # Use return instead of st.stop() inside a component function

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
            message_placeholder.markdown("Scanning intelligence archives & calculating threat models... 🕵️‍♂️")

            archive_mapping = get_brief_mappings('data')
            context_data = ""
            
            user_keywords = [w.lower() for w in re.findall(r'\b\w+\b', prompt) if len(w) > 2 and w.lower() not in ['what', 'when', 'where', 'which', 'who', 'why', 'how', 'were', 'was', 'this', 'that', 'with', 'from', 'about', 'the', 'and', 'for', 'are', 'did', 'have', 'has']]

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
                            if len(txt.strip()) > 20:
                                score = calculate_domain_threat(name, txt, d)
                                context_data += f"- {name}: {score}%\n"
                                
                        context_data += "\nRAW INTELLIGENCE TEXT:\n"
                        context_data += r_text
                        context_data += f"\nLOGGED STATE ACTIONS:\n{json.dumps(d.get('recent_actions', []))}"
                except: pass

            sys_prompt = f"""
            You are an elite geopolitical intelligence AI assistant for the SemicoN Dashboard.
            Your primary directive is to answer the user's question using ONLY the provided historical intelligence archives below.
            CRITICAL RAG 2.0 DIRECTIVE: Cite "Algorithmic Threat Scores" to ground your reasoning.
            ARCHIVES CONTEXT:
            {context_data}
            """
            
            try:
                full_response = ""
                response = client.models.generate_content_stream(
                    model=model_name,
                    contents=[sys_prompt, prompt]
                )
                for chunk in response:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌") 
                        
                message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"⚠️ Error querying the intelligence database: {e}"
                message_placeholder.markdown(full_response)
        st.session_state.rag_messages.append({"role": "assistant", "content": full_response})