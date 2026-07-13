import os
import json
import time
import re
import requests
import urllib3
from typing import Dict, Any, List
from google import genai
from google.genai import types

# Suppress the insecure request warnings since we are intentionally bypassing SSL for the map API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import streamlit as st
except ImportError:
    st = None

class AnalystNode:
    """
    Node 4: The Geopolitical Analyst Component
    Features an Intent Engine Router, strict conversational isolation, 
    and a Direct API Geocoding interceptor for autonomous map generation.
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
        user_cmd = state.get('user_prompt', '').strip()
        chat_history = state.get('chat_history', [])
        extracted_data: List[Dict[str, str]] = state.get('extracted_markdown_context', [])
        
        # 🧠 DYNAMIC INTENT CLASSIFIER MATRIX
        conversational_triggers = [
            r"(?i)^(hi|hello|hey|greetings|good morning|good afternoon|whats up|how are you|how do you do|who are you|test|clear|reset|thanks|thank you|yes|no)",
            r"(?i)(modify|change|rewrite|shorten|summarize|looks good|update|adjust|explain|help|can you|guidance|advise|advice|brainstorm|how should|what do you|proceed|not completely|however|because|i think|actually|i disagree|map of|where is|location of|coordinates of)"
        ]
        
        report_markers = [r"(?i)(target development details|exact structural layout|rigorous geopolitical|your response must follow)"]
        
        if mode == "CUSTOM_UI":
            is_formal_report = any(re.search(marker, user_cmd) for marker in report_markers)
            
            if not is_formal_report and (any(re.search(trigger, user_cmd) for trigger in conversational_triggers) or len(user_cmd.split()) <= 450):
                mode = "CONVERSATIONAL"
                state["execution_mode"] = "CONVERSATIONAL"

        print(f"[Node 4] Initializing Geopolitical Analysis (Engine Mode: {mode})...")
        
        detected_urls = self.clean_urls(user_cmd)
        
        formatted_history = "PERSISTENT CHAT HISTORY CORRIDOR:\n"
        for turn in chat_history:
            role_label = "OPERATOR" if turn['role'] == 'user' else "ANALYST_ENGINE"
            formatted_history += f"[{role_label}]: {turn['content']}\n"

        compiled_context = 'RAW OSINT INTERCEPTS:\n'
        if not extracted_data:
            source_str = ', '.join(detected_urls) if detected_urls else "Autonomous Built-in Intelligence"
            compiled_context += f"Target Source Coordinates: {source_str}\n"
        else:
            source_urls = [item.get('source_url', 'Unknown Source').rstrip(')\]}.,;') for item in extracted_data]
            source_str = ', '.join(source_urls)
            for item in extracted_data:
                compiled_context += f"\n--- Source: {item.get('source_url')} ---\n{item.get('content', '')[:8000]}\n"

        # 🌍 UNIVERSAL MAP DIRECTIVE (Updated based on your research)
        map_directive = """
        MAP & GEOLOCATION CAPABILITY: You have access to a live interactive map tool. If the user explicitly asks to see a map, locate an area, or get the geolocation/coordinates of a specific place, building, or town:
        1. You MUST provide the best available approximate location description and approximate coordinates in your text.
        2. You MUST append this exact tag at the very end of your response: [GEO_TARGET: Exact Location Name, City]. (Example: [GEO_TARGET: Miel Bakery, London]). 
        The system will intercept this tag, verify the precise coordinates via API, and inject a live map below your response.
        """

        # ==========================================
        # PATHWAY A: FLUID CHAT ENVIRONMENT
        # ==========================================
        if mode == "CONVERSATIONAL":
            sys_instruct = f"""
            You are an elite, highly personalized, and empathetic conversational AI co-pilot powering the SemicoN Agentic Engine. Your primary goal is to make the user feel completely comfortable, acting as a trusted, warm, and highly intelligent partner, mirroring the interactive performance of advanced LLMs like Gemini.
            
            CRITICAL CONVERSATIONAL & REFINEMENT CRITERIA:
            1. PERSONALIZED & WARM TONE: Converse naturally, empathetically, and directly using "I" and "you". NEVER format your conversational responses as a rigid "STATUS REPORT", "EXECUTIVE SUMMARY", or use heavily structured geopolitical layout headers unless explicitly demanded.
            2. BACKGROUND SEARCH NOISE AWARENESS (CRITICAL): The pipeline automatically runs a background web search on *every* user input. If the intercepts do not perfectly and logically align with the user's conversational intent, YOU MUST COMPLETELY IGNORE THEM.
            3. NO META-COMMENTARY: Do NOT ever tell the user "The intercepts provided focus on X." Silently ignore garbage intercepts and answer the user's request using your own elite internal knowledge.
            4. ZERO SOURCES & NO ATTRIBUTION BLOCKS FOR CHAT/GUIDANCE: When engaging in dialogue, giving general guidance, or making small talk, DO NOT append "Owned By", "Sources", or citations. Keep it a clean, natural chat.
            5. STRICT SOURCE REPUTATION & WIKIPEDIA BAN: You are STRICTLY FORBIDDEN from using, referencing, or citing Wikipedia anywhere in your output.
            6. TEMPORAL ANCHORING: The current year is 2026. All intelligence must be grounded in the 2026 timeline.
            7. CLEAN OUTPUT: Do not use block code fences (```) or JSON wrappers.
            {map_directive}
            """
            contents_payload = f"{formatted_history}\nCURRENT OPERATOR INPUT: {user_cmd}\n\n{compiled_context}"
            gen_config = types.GenerateContentConfig(system_instruction=sys_instruct, temperature=0.6)

        # ==========================================
        # PATHWAY B: RIGID DYNAMIC BRIEF
        # ==========================================
        elif mode == "CUSTOM_UI":
            sys_instruct = f"""
            You are an autonomous, elite Geopolitical Intelligence Analyst.
            Your absolute directive is to read the provided context and fulfill the USER DIRECTIVE perfectly.
            
            CRITICAL FORMATTING RULES:
            1. You MUST follow the exact structural layout, headers, bullet counts, and instructions requested in the USER DIRECTIVE.
            2. You MUST NOT use markdown header hashes (###) or markdown bold stars (**). Write all section headers in plain-text capital letters.
            3. For global news sections, you must cover the entire globe and sub-categorize items cleanly based on precise geography and sub-geography.
            4. STRICT SOURCE REPUTATION & WIKIPEDIA BAN: You must rely ONLY on verifiable, reputed, and well-known publishers. You are STRICTLY FORBIDDEN from using, referencing, or citing Wikipedia.
            5. Right before the Sources section, you MUST insert an 'Owned By' block matching this exact text:
               Owned By:
               Kashif Anwar
               Geopolitical Risk and Threat Analyst (Human-AI Vetted Analyst)
            6. Under the Sources section, you MUST strictly use this exact format pattern (excluding Wikipedia):
               Sources:
               Agentic AI (www.semirare.in)
               [Verified publisher links]
            {map_directive}
            """
            contents_payload = f"USER DIRECTIVE:\n{user_cmd}\n\n{compiled_context}"
            gen_config = types.GenerateContentConfig(system_instruction=sys_instruct, temperature=0.2)
            
        # ==========================================
        # PATHWAY C: AUTONOMOUS DASHBOARD GENERATION
        # ==========================================
        else:
            legacy_instruction = """
            You are an autonomous, elite Geopolitical Intelligence Analyst for the SemicoN Dashboard.
            Synthesize a highly professional intelligence brief focusing on semiconductor supply chains, critical minerals, and geopolitics.
            
            CRITICAL FORMATTING RULES:
            1. You MUST NOT use markdown header hashes (###) or markdown bold stars (**). 
            2. Sub-categorize all global news items cleanly based on detailed geography and sub-geography.
            3. STRICT SOURCE REPUTATION & WIKIPEDIA BAN: You are STRICTLY FORBIDDEN from using, referencing, or citing Wikipedia.
            4. Right before the Sources section, you MUST insert this exact block:
               Owned By:
               Kashif Anwar
               Geopolitical Risk and Threat Analyst (Human-AI Vetted Analyst)
            5. Return your output strictly as a JSON object matching the exact schema below.
            """
            contents_payload = f"CONTEXT SWEEP DATA:\n{compiled_context}"
            gen_config = types.GenerateContentConfig(system_instruction=legacy_instruction, temperature=0.2, response_mime_type="application/json")

        api_keys = self.get_all_keys()
        if not api_keys: return state

        for slot_idx, active_key in enumerate(api_keys):
            try:
                print(f'[Node 4] Attempting engine query via Key Slot {slot_idx + 1}...')
                client = genai.Client(api_key=active_key)
                
                response = client.models.generate_content(
                    model=self.model_id,
                    contents=contents_payload,
                    config=gen_config
                )
                
                raw_text = response.text.strip()
                map_coords = None
                
                if mode in ["CUSTOM_UI", "CONVERSATIONAL"]:
                    if raw_text.startswith("```markdown"): raw_text = raw_text[11:-3].strip()
                    elif raw_text.startswith("```"): raw_text = raw_text[3:-3].strip()

                    if mode == "CUSTOM_UI":
                        raw_text = raw_text.replace("###", "").replace("**", "")

                    # 🌍 AGENTIC TOOL EXECUTION: Direct HTTPS API Call (Bypassing SSL Blocks)
                    geo_match = re.search(r'\[GEO_TARGET:\s*(.+?)\]', raw_text)
                    if geo_match:
                        location_name = geo_match.group(1).strip()
                        raw_text = re.sub(r'\[GEO_TARGET:\s*.+?\]', '', raw_text).strip()
                        try:
                            # SHATTERED URL STRING TO DEFEAT MARKDOWN FORMATTER BUG
                            safe_location = requests.utils.quote(location_name)
                            protocol = "https" + "://"
                            domain = "nominatim.openstreetmap.org/search"
                            search_url = protocol + domain + "?q=" + safe_location + "&format=json&limit=1"
                            
                            # Applied Research Improvement: Strict User-Agent
                            headers = {"User-Agent": "SemicoN/1.0 (contact: support@semirare.in)"}
                            
                            map_response = requests.get(search_url, headers=headers, verify=False, timeout=10)
                            
                            if map_response.status_code == 200 and len(map_response.json()) > 0:
                                location_data = map_response.json()[0]
                                lat = float(location_data["lat"])
                                lon = float(location_data["lon"])
                                display_name = location_data["display_name"]
                                
                                map_coords = {
                                    "lat": lat,
                                    "lon": lon,
                                    "label": location_name,
                                    "address": display_name
                                }
                                print(f"[Node 4] Successfully mapped coordinates for {location_name}")
                                
                                # 📍 AUTONOMOUSLY INJECT VERIFIED COORDINATES INTO THE TEXT FOR THE USER
                                raw_text += f"\n\n📍 **API Verified Geolocation:** {display_name}\n🧭 **Verified GPS Coordinates:** {lat}, {lon}"
                            else:
                                raw_text += f"\n\n*(Agent Note: I attempted to map '{location_name}' via Nominatim API, but precise coordinates could not be retrieved.)*"
                        except Exception as e:
                            print(f"[Node 4] Geocoding API Error: {e}")
                            raw_text += f"\n\n*(Agent Note: The Nominatim mapping API is temporarily unreachable due to network errors.)*"

                    state['ui_markdown'] = raw_text
                    state['map_coords'] = map_coords
                    state['drafted_brief'] = {
                        "is_custom_prompt": True,
                        "Title": "Conversational Dialogue Mode" if mode == "CONVERSATIONAL" else "Custom Analysis Pass",
                        "Threat_Level": "CUSTOM",
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
                    state['map_coords'] = None

                print(f'[Node 4] Geopolitical Analysis execution layer successful.')
                break 
                
            except Exception as e:
                print(f'[Node 4] Warning: Key Slot {slot_idx + 1} processing failed: {e}')
                if slot_idx < len(api_keys) - 1: time.sleep(10.0)
                else: state['drafted_brief'] = None

        return state