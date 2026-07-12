import os
import json
import time
import re
from typing import Dict, Any, List
from google import genai
from google.genai import types

try:
    import streamlit as st
except ImportError:
    st = None

class AnalystNode:
    def __init__(self):
        self.model_id = 'gemini-3.1-flash-lite'

    def get_all_keys(self) -> List[str]:
        key_slots = ['GEMINI_API_KEY', 'GEMINI_API_KEY_RAGAI']
        valid_keys = []
        for slot in key_slots:
            val = os.environ.get(slot)
            if not val and st is not None:
                try: val = st.secrets.get(slot)
                except Exception: pass
            if val and str(val).strip():
                valid_keys.append(str(val).strip())
        return valid_keys

    def clean_urls(self, text: str) -> List[str]:
        raw_urls = re.findall(r'https?://[^\s<>"]+', text)
        return [url.rstrip(')\]}.,;') for url in raw_urls]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        mode = state.get("execution_mode", "AUTONOMOUS")
        user_cmd = state.get('user_prompt', '')
        extracted_data: List[Dict[str, str]] = state.get('extracted_markdown_context', [])
        
        print(f"[Node 4] Initializing Geopolitical Analysis (Engine Mode: {mode})...")
        
        detected_urls = self.clean_urls(user_cmd)
        compiled_context = 'RAW OSINT INTERCEPTS:\n'
        
        if not extracted_data:
            source_str = ', '.join(detected_urls) if detected_urls else "Autonomous Built-in Intelligence"
            compiled_context += f"Target Source Coordinates: {source_str}\n"
        else:
            source_urls = [item.get('source_url', 'Unknown Source').rstrip(')\]}.,;') for item in extracted_data]
            source_str = ', '.join(source_urls)
            for item in extracted_data:
                compiled_context += f"\n--- Source: {item.get('source_url')} ---\n{item.get('content', '')[:8000]}\n"

        # ==========================================
        # ENGINE PATHWAY A: UNCONSTRAINED CUSTOM MARKOOWN
        # ==========================================
        if mode == "CUSTOM_UI":
            sys_instruct = """
            You are an autonomous, elite Geopolitical Intelligence Analyst.
            Your absolute directive is to read the provided context and fulfill the USER DIRECTIVE perfectly.
            
            CRITICAL RULES:
            1. You MUST follow the exact structural layout, headers, bullet counts, and instructions requested in the USER DIRECTIVE.
            2. Output your response as pure, professional text/Markdown. 
            3. Do NOT wrap your response in JSON format. Do NOT include conversational greetings.
            """
            gen_config = types.GenerateContentConfig(system_instruction=sys_instruct, temperature=0.2)
            
        # ==========================================
        # ENGINE PATHWAY B: CORES DASHBOARD SCHEMAS
        # ==========================================
        else:
            legacy_instruction = """
            You are an autonomous, elite Geopolitical Intelligence Analyst for the SemicoN Dashboard.
            Your objective is to read the provided context and synthesize a highly professional, 
            actionable intelligence brief focusing on semiconductor supply chains, critical minerals, and geopolitics.
            
            CRITICAL RULES:
            1. Base your analysis STRICTLY on the provided context.
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
            gen_config = types.GenerateContentConfig(system_instruction=legacy_instruction, temperature=0.2, response_mime_type="application/json")

        api_keys = self.get_all_keys()
        if not api_keys: return state

        for slot_idx, active_key in enumerate(api_keys):
            try:
                print(f'[Node 4] Attempting engine query via Key Slot {slot_idx + 1}...')
                client = genai.Client(api_key=active_key)
                
                response = client.models.generate_content(
                    model=self.model_id,
                    contents=f'USER DIRECTIVE:\n{user_cmd}\n\n{compiled_context}',
                    config=gen_config
                )
                
                raw_text = response.text.strip()
                
                if mode == "CUSTOM_UI":
                    if raw_text.startswith("```markdown"): raw_text = raw_text[11:-3].strip()
                    elif raw_text.startswith("```"): raw_text = raw_text[3:-3].strip()

                    # Directly populates the pristine markdown vector channel
                    state['ui_markdown'] = raw_text
                    
                    # Populates basic fallback mappings for any legacy frontends
                    state['drafted_brief'] = {
                        "Title": "Custom Analysis Pass",
                        "Threat_Level": "HIGH",
                        "BLUF": raw_text,
                        "Source": source_str
                    }
                else:
                    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    if json_match: raw_text = json_match.group(0)
                    brief_json = json.loads(raw_text)
                    brief_json['Source'] = source_str
                    state['drafted_brief'] = brief_json
                    state['ui_markdown'] = ""

                print(f'[Node 4] Geopolitical Analysis execution layer successful.')
                break 
                
            except Exception as e:
                print(f'[Node 4] Warning: Key Slot {slot_idx + 1} processing failed: {e}')
                if slot_idx < len(api_keys) - 1: time.sleep(10.0)
                else: state['drafted_brief'] = None

        return state