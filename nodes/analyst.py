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
    """
    Node 4: The Geopolitical Analyst Component
    Features complete text cleanup rules to block raw markdown tokens (###, **)
    and organizes global intercepts by detailed geographic sub-categories.
    """
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
        # PATHWAY A: UNCONSTRAINED CUSTOM DIRECTION
        # ==========================================
        if mode == "CUSTOM_UI":
            sys_instruct = f"""
            You are an autonomous, elite Geopolitical Intelligence Analyst.
            Your absolute directive is to read the provided context and fulfill the USER DIRECTIVE perfectly.
            
            CRITICAL FORMATTING RULES:
            1. You MUST NOT use markdown header hashes (###) or markdown bold stars (**). Write all section headers in plain-text capital letters (e.g., TITLE:, CATEGORY:, INCIDENT BRIEF:).
            2. For global news sections, you must cover the entire globe and sub-categorize items cleanly based on precise geography and sub-geography (e.g., Asia-Pacific, North America, Europe, West Asia/Middle East, Africa).
            3. Right before the Sources section, you MUST insert an 'Owned By' block matching this exact text:
               Owned By:
               Add your name
               Add your position
            4. Under the Sources section, you MUST strictly use this exact format pattern:
               Sources:
               Agentic AI (www.semirare.in)
               {source_str}
            """
            gen_config = types.GenerateContentConfig(system_instruction=sys_instruct, temperature=0.2)
            
        # ==========================================
        # PATHWAY B: STANDARD HOURLY DISPATCH
        # ==========================================
        else:
            legacy_instruction = f"""
            You are an autonomous, elite Geopolitical Intelligence Analyst for the SemicoN Dashboard.
            Synthesize a highly professional intelligence brief focusing on semiconductor supply chains, critical minerals, and geopolitics.
            
            CRITICAL FORMATTING RULES:
            1. You MUST NOT use markdown header hashes (###) or markdown bold stars (**). 
            2. Sub-categorize all global news items cleanly based on detailed geography and sub-geography (covering Asia-Pacific, Americas, Europe, West Asia, Africa).
            3. Right before the Sources section, you MUST insert this exact block:
               Owned By:
               Kashif Anwar
               Geopolitical Risk and Threat Analyst (Human-AI Vetted Analyst)
            4. Return your output strictly as a JSON object matching the exact schema below.
            
            JSON Schema:
            {{
                "Title": "Strategic headline text without hashes or stars",
                "Threat_Level": "CRITICAL, ELEVATED, WATCH, or STANDARD",
                "Locations": ["Bullet point news event"],
                "BLUF": "Cohesive paragraph explaining the Bottom Line Up Front.",
                "Top_News": {{
                    "Asia-Pacific": ["Bullet news 1"],
                    "West Asia / Middle East": ["Bullet news 1"],
                    "Europe": ["Bullet news 1"],
                    "Americas": ["Bullet news 1"],
                    "Africa": ["Bullet news 1"]
                }},
                "Watch_Out": ["Upcoming trigger event"],
                "Risk_And_Threat_Analysis": {{
                    "Overall_Analysis": "Strategic summary summary text."
                }},
                "Predictive_Analysis": "Paragraph forecasting upcoming event metrics.",
                "Sources_List": [
                    "Agentic AI (www.semirare.in)",
                    "Live verified references: {source_str}"
                ]
            }}
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

                    # Direct clean up to ensure absolute protection from stray markdown formats
                    raw_text = raw_text.replace("###", "").replace("**", "")

                    state['ui_markdown'] = raw_text
                    state['drafted_brief'] = {
                        "is_custom_prompt": True,
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
                    brief_json['is_custom_prompt'] = False
                    state['drafted_brief'] = brief_json
                    state['ui_markdown'] = ""

                print(f'[Node 4] Geopolitical Analysis execution layer successful.')
                break 
                
            except Exception as e:
                print(f'[Node 4] Warning: Key Slot {slot_idx + 1} processing failed: {e}')
                if slot_idx < len(api_keys) - 1: time.sleep(10.0)
                else: state['drafted_brief'] = None

        return state