import os
import json
import time
import re
from typing import Dict, Any, List
from google import genai
from google.genai import types

# 🛡️ THE FIX: Safely import Streamlit only if available (prevents headless server crashes)
try:
    import streamlit as st
except ImportError:
    st = None

class AnalystNode:
    """
    Node 4: The Geopolitical Analyst Component
    Consumes cleaned markdown, synthesizes intelligence, and enforces strict JSON schema output.
    Implements a strict 2-key backup cascade with a 10-second cooling window to mitigate 429 Quota errors.
    """
    def __init__(self):
        self.model_id = 'gemini-3.5-flash'

    def get_all_keys(self) -> List[str]:
        """Collects configured API keys from environment and secrets in strict priority order."""
        key_slots = [
            'GEMINI_API_KEY',
            'GEMINI_API_KEY_RAGAI'
        ]
        valid_keys = []
        for slot in key_slots:
            val = os.environ.get(slot)
            if not val and st is not None:
                try: val = st.secrets.get(slot)
                except Exception: pass
            if val and str(val).strip():
                valid_keys.append(str(val).strip())
        return valid_keys

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        extracted_data: List[Dict[str, str]] = state.get('extracted_markdown_context', [])
        user_cmd = state.get('user_prompt', 'Draft a standard intelligence brief based on the context.')

        print('[Node 4] Initializing Geopolitical Analysis...')
        
        compiled_context = 'RAW OSINT INTERCEPTS:\n'
        source_str = ''
        
        if not extracted_data:
            print('[Node 4] Warning: Direct URL extraction failed. Engaging Autonomous Web Grounding.')
            compiled_context += 'Direct URL extraction was blocked by the publisher\'s firewall. Rely on your built-in intelligence and live web search tools to fulfill the USER DIRECTIVE.\n'
            source_str = 'Autonomous Google Search Extraction' 
        else:
            for item in extracted_data:
                source_url = item.get('source_url', 'Unknown Source')
                content = item.get('content', '')[:8000] 
                compiled_context += f'\n--- Source: {source_url} ---\n{content}\n'
            source_str = ', '.join([item['source_url'] for item in extracted_data])

        system_instruction = """
        You are an autonomous, elite Geopolitical Intelligence Analyst for the SemicoN Dashboard.
        Your objective is to read the provided context and synthesize a highly professional, 
        actionable intelligence brief focusing on semiconductor supply chains, critical minerals, and geopolitics.
        
        CRITICAL RULES:
        1. You MUST use Google Search Grounding to find up-to-date facts if the provided context is insufficient.
        2. You MUST return your output STRICTLY as a raw JSON object. 
        3. DO NOT include any conversational text outside the JSON.
        4. The total length of the generated content inside the JSON must be between 250 and 500 words.
        
        Use this EXACT JSON schema:
        {
            "Title": "A gripping 10-12 word strategic headline",
            "Threat_Level": "Strictly one of: CRITICAL, ELEVATED, WATCH, or STANDARD",
            "Locations": [
                "Bullet point 1 detailing a major ongoing news event in a specific location",
                "Bullet point 2 detailing another major ongoing news event"
            ],
            "BLUF": "A cohesive paragraph explaining the Bottom Line Up Front.",
            "Top_News": {
                "Asia": ["Bullet point news 1", "Bullet point news 2"],
                "Middle East": ["Bullet point news 1"],
                "Europe": ["Bullet point news 1"]
            },
            "Watch_Out": [
                "Bullet point on what news to watch out for",
                "Bullet point on another upcoming trigger event"
            ],
            "Risk_And_Threat_Analysis": {
                "Risk_Analysis": "A full paragraph detailing immediate operational risks.",
                "Threat_Analysis": "A full paragraph detailing overarching geopolitical or supply chain threats.",
                "Overall_Analysis": "A concluding paragraph blending the risk and threat into a strategic summary."
            },
            "Predictive_Analysis": "A paragraph forecasting what to look out for in the next few hours.",
            "Recommendations": {
                "Global_Supply_Chain": "Impact on global logistics and shipping.",
                "Semiconductors_And_Rare_Earths": "Impact on chips, lithography, and critical minerals.",
                "Global_Business": "Impact on markets and multinational corporations.",
                "Travel": "Travel impact/restrictions determined by the locations mentioned.",
                "Whats_Next": "Actionable next steps based on the predictive analysis."
            }
        }
        """

        api_keys = self.get_all_keys()
        if not api_keys:
            print('[Node 4] ⚠️ CRITICAL FAILURE: No operational API keys discovered in system secrets configuration.')
            state['drafted_brief'] = None
            return state

        success = False
        for slot_idx, active_key in enumerate(api_keys):
            try:
                print(f'[Node 4] Attempting engine query via Key Slot {slot_idx + 1}/{len(api_keys)}...')
                client = genai.Client(api_key=active_key)
                
                response = client.models.generate_content(
                    model=self.model_id,
                    contents=f'USER DIRECTIVE: {user_cmd}\n\n{compiled_context}',
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2, 
                        response_mime_type="application/json", # 🛑 THE FIX: Restored JSON lock
                        tools=[{'google_search': {}}]
                    )
                )
                
                raw_text = response.text.strip()
                
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if json_match:
                    raw_text = json_match.group(0)
                else:
                    if raw_text.startswith('```json'): 
                        raw_text = raw_text[7:-3].strip()
                    elif raw_text.startswith('```'): 
                        raw_text = raw_text[3:-3].strip()
                
                brief_json = json.loads(raw_text)
                
                grounding_links = []
                try:
                    if response.candidates and response.candidates[0].grounding_metadata:
                        meta = response.candidates[0].grounding_metadata
                        if hasattr(meta, 'grounding_chunks') and meta.grounding_chunks:
                            for g_chunk in meta.grounding_chunks:
                                if hasattr(g_chunk, 'web') and getattr(g_chunk.web, 'uri', None):
                                    grounding_links.append(g_chunk.web.uri)
                except Exception: pass

                if grounding_links:
                    unique_links = list(set(grounding_links))[:4]
                    if 'Autonomous' in source_str:
                        source_str = 'Live Web Sources: ' + ', '.join(unique_links)
                    else:
                        source_str += ' | Google Grounded Links: ' + ', '.join(unique_links)

                brief_json['Source'] = source_str
                state['drafted_brief'] = brief_json
                
                email_md = f"### 🚨 {brief_json.get('Title', 'Agentic AI Strategic Brief')}\n\n"
                email_md += f"**Threat Level:** {brief_json.get('Threat_Level', 'STANDARD')}\n\n"
                
                email_md += "#### 📍 Locations & Major Ongoing News\n"
                for loc in brief_json.get("Locations", []):
                    email_md += f"* {loc}\n"
                email_md += "\n"

                email_md += f"#### 🎯 Bottom Line Up Front (BLUF)\n{brief_json.get('BLUF', 'No BLUF provided.')}\n\n"
                
                email_md += "#### 🌍 Top News from the Globe\n"
                top_news = brief_json.get("Top_News", {})
                if isinstance(top_news, dict):
                    for region, news_items in top_news.items():
                        email_md += f"**{region}**\n"
                        for item in news_items:
                            email_md += f"* {item}\n"
                email_md += "\n"

                email_md += "#### 🔭 What to Watch Out For\n"
                for watch in brief_json.get("Watch_Out", []):
                    email_md += f"* {watch}\n"
                email_md += "\n"

                email_md += "#### ⚖️ Risk and Threat Analysis\n"
                rta = brief_json.get("Risk_And_Threat_Analysis", {})
                email_md += f"**Risk Analysis:**\n{rta.get('Risk_Analysis', 'N/A')}\n\n"
                email_md += f"**Threat Analysis:**\n{rta.get('Threat_Analysis', 'N/A')}\n\n"
                email_md += f"**Overall Analysis:**\n{rta.get('Overall_Analysis', 'N/A')}\n\n"

                email_md += f"#### 🔮 Predictive Analysis\n{brief_json.get('Predictive_Analysis', 'N/A')}\n\n"

                email_md += "#### 💡 Recommendations & Impact\n"
                recs = brief_json.get("Recommendations", {})
                email_md += f"* **Global Supply Chain:** {recs.get('Global_Supply_Chain', 'N/A')}\n"
                email_md += f"* **Semiconductors & Rare Earths:** {recs.get('Semiconductors_And_Rare_Earths', 'N/A')}\n"
                email_md += f"* **Global Business:** {recs.get('Global_Business', 'N/A')}\n"
                email_md += f"* **Travel:** {recs.get('Travel', 'N/A')}\n"
                email_md += f"* **What's Next:** {recs.get('Whats_Next', 'N/A')}\n\n"

                email_md += f"---\n**Sources:**\n{source_str}"
                
                os.makedirs('data', exist_ok=True)
                with open('data/agentic_email_body.md', 'w', encoding='utf-8') as f:
                    f.write(email_md)

                print(f'[Node 4] Intelligence Brief successfully drafted using Key Slot {slot_idx + 1}.')
                success = True
                break 
                
            except Exception as e:
                print(f'[Node 4] Warning: Key Slot {slot_idx + 1} rejected payload execution: {e}')
                if slot_idx < len(api_keys) - 1:
                    print('🔄 [Node 4] Quota limit triggered. Engaging 10-second cooling window before shifting keys...')
                    time.sleep(10.0)
                    continue
                else:
                    print('[Node 4] ⚠️ All fallback API keys in the rotational matrix have been exhausted.')
                    state['drafted_brief'] = None

        # 🛑 THE FAILSAFE: Guarantee the email file exists even if Gemini crashes
        if not success:
            os.makedirs('data', exist_ok=True)
            with open('data/agentic_email_body.md', 'w', encoding='utf-8') as f:
                f.write("### ⚠️ [SYSTEM ALERT] Agentic AI Sweep Interrupted\n\n")
                f.write("The autonomous intelligence engine was unable to synthesize a valid brief during this cycle due to an API quota limit or a strict formatting rejection from the Gemini model. Normal operations will resume on the next scheduled cron cycle.")

        return state