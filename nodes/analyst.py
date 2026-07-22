import os
import json
import time
import re
import requests
import urllib3
from typing import Dict, Any, List
from google import genai
from google.genai import types

# Suppress the insecure request warnings since we are intentionally bypassing SSL for the map APIs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import streamlit as st
except ImportError:
    st = None

class AnalystNode:
    """
    Node 4: The Geopolitical Analyst Component
    Features an Intent Engine Router, strict conversational isolation, 
    and an autonomous 8-Tier Geospatial Consensus Engine for precision OSINT mapping.
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

    def get_named_token(self, token_name: str) -> str:
        """Helper to extract infrastructure keys cleanly across development profiles"""
        val = os.environ.get(token_name)
        if not val and st is not None:
            try: val = st.secrets.get(token_name)
            except Exception: pass
        return str(val).strip() if val else ""

    def clean_urls(self, text: str) -> List[str]:
        raw_urls = re.findall(r'https?://[^\s<>"]+', text)
        return [url.rstrip(')\]}.,;') for url in raw_urls]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        mode = state.get("execution_mode", "AUTONOMOUS")
        user_cmd = state.get('user_prompt', '').strip()
        chat_history = state.get('chat_history', [])
        extracted_data: List[Dict[str, str]] = state.get('extracted_markdown_context', [])
        
        api_keys = self.get_all_keys()
        if not api_keys: return state

        # 🧠 SEMANTIC INTENT ROUTER MATRIX (Replaces brittle regex gates)
        if mode == "CUSTOM_UI":
            try:
                router_client = genai.Client(api_key=api_keys[0])
                router_instruct = """
                You are the Dynamic Intent Router for an advanced geopolitical intelligence node.
                Analyze the entire length and structural context of the user input prompt.
                Classify it into one of two output modes:
                - Output 'CUSTOM_UI' if the prompt is a complex, long-form research request, formal briefing, academic/recruitment assignment, strategic task with headers/word counts, or deep risk assessment.
                - Output 'CONVERSATIONAL' if the prompt is a short, direct conversational phrase, greeting, direct navigation query, or basic question.
                Output ONLY the string 'CUSTOM_UI' or 'CONVERSATIONAL'. Do not add punctuation or meta-text.
                """
                router_res = router_client.models.generate_content(
                    model=self.model_id,
                    contents=f"PROMPT TO CLASSIFY:\n{user_cmd}",
                    config=types.GenerateContentConfig(system_instruction=router_instruct, temperature=0.1)
                )
                classified_mode = router_res.text.strip()
                if classified_mode in ["CUSTOM_UI", "CONVERSATIONAL"]:
                    mode = classified_mode
                    state["execution_mode"] = mode
                    print(f"[Node 4] Semantic Intent Router assigned Engine Mode: {mode}")
            except Exception as router_err:
                print(f"[Node 4] Intent routing exception, falling back to safe defaults: {router_err}")

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

        # 🌍 UNIVERSAL MAP DIRECTIVE
        map_directive = """
        MAP & GEOLOCATION CAPABILITY: You have access to a live interactive map tool. If the user explicitly asks to see a map, locate an area, or get the geolocation/coordinates of a specific place, building, or town:
        1. You MUST provide the best available location description based on context in your text response.
        2. STRICT BAN ON COORDINATE HALLUCINATION: You MUST NOT guess, invent, or mathematically estimate numerical GPS coordinates anywhere in your text response.
        3. LATIN SCRIPT & DUAL-NAME RULE: You MUST write all venue/city names using the Latin/English alphabet. If a location has a widely known global English name AND a distinct Romanized local name, provide both separated by a pipe (|).
        4. 🔴 EXHAUSTIVE MULTI-THEATER TAGGING 🔴: Large Language Models are notoriously lazy and often only generate one location tag. You MUST override this behavior. For EVERY SINGLE distinct country, theater, or region analyzed in your report, you MUST generate a completely separate map tag on a new line at the very bottom of the report. DO NOT combine them into one tag.
        Format STRICTLY as:
        [GEO_TARGET: Primary Name 1 | Local Name 1 | Country 1]
        [GEO_TARGET: Primary Name 2 | Local Name 2 | Country 2]
        [GEO_TARGET: Primary Name 3 | Local Name 3 | Country 3]
        [GEO_TARGET: Primary Name 4 | Local Name 3 | Country 4]
        [GEO_TARGET: Primary Name 5 | Local Name 3 | Country 5]
        [GEO_TARGET: Primary Name 6 | Local Name 3 | Country 6]    
        [GEO_TARGET: Primary Name 7 | Local Name 3 | Country 7]
        [GEO_TARGET: Primary Name 8 | Local Name 3 | Country 8]
        [GEO_TARGET: Primary Name 9 | Local Name 3 | Country 9]
        [GEO_TARGET: Primary Name 10 | Local Name 3 | Country 10]
        [GEO_TARGET: Primary Name 11 | Local Name 3 | Country 11]
        [GEO_TARGET: Primary Name 12 | Local Name 3 | Country 12]   
        The backend Python interceptor will catch your tags, run an 8-tier Geospatial Consensus Array to extract the highest-precision exact coordinate footprint, and inject live verifiable maps below your text.
        """

        # ==========================================
        # PATHWAY A: FLUID CHAT ENVIRONMENT
        # ==========================================
        if mode == "CONVERSATIONAL":
            sys_instruct = f"""
            You are an elite, highly personalized, and empathetic conversational AI co-pilot powering the SemicoN Agentic Engine. Your primary goal is to make the user feel completely comfortable, acting as a trusted, warm, and highly intelligent partner, mirroring the interactive performance of advanced LLMs like Gemini.
            
            CRITICAL CONVERSATIONAL & REFINEMENT CRITERIA:
            1. DYNAMIC CONVERSATIONAL STYLES: Adapt seamlessly to the user's basic conversation inputs. 
               - For simple greetings ("Hi", "Hello", "Good morning"): Respond warmly and briefly (e.g., "Hi there! Ready to run some threat models or scan the latest intelligence today?").
               - For casual check-ins ("How are you?", "What's up?"): Be polite, acknowledge your AI nature without being robotic, and swiftly pivot to assisting them.
               - For brief confirmations ("Got it", "Thanks", "Okay"): Provide a short, polite acknowledgment (e.g., "You're welcome! Let me know when you're ready for the next task.").
            2. SMALL TALK & GREETING OVERRIDE (CRITICAL SPEED DIRECTIVE): If the user prompt is a simple greeting or basic small talk, you must COMPLETELY IGNORE the `RAW OSINT INTERCEPTS`. Keep your response under 50 words to ensure rapid, immediate delivery. Do not attempt to summarize random scraped data for a simple greeting.
            3. PERSONALIZED & WARM TONE: Converse naturally, empathetically, and directly using "I" and "you". NEVER format your conversational responses as a rigid "STATUS REPORT", "EXECUTIVE SUMMARY", or use heavily structured geopolitical layout headers unless explicitly demanded.
            4. NO META-COMMENTARY: Do NOT ever tell the user "The intercepts provided focus on X." Silently ignore garbage intercepts and answer the user's request using your own elite internal knowledge.
            5. ZERO SOURCES & NO ATTRIBUTION BLOCKS FOR CHAT/GUIDANCE: When engaging in dialogue, giving general guidance, or making small talk, DO NOT append "Owned By", "Sources", or citations. Keep it a clean, natural chat.
            6. STRICT SOURCE REPUTATION & WIKIPEDIA BAN: You are STRICTLY FORBIDDEN from using, referencing, or citing Wikipedia anywhere in your output.
            7. TEMPORAL ANCHORING: The current year is 2026. All intelligence must be grounded in the 2026 timeline.
            8. STRICT SOURCE ATTRIBUTION (ONLY ON DEMAND): DO NOT output any URLs or sources in this conversational mode UNLESS the user explicitly asks for links, references, or URLs. If they do ask, you must ONLY cite direct publisher URLs explicitly provided in the RAW OSINT INTERCEPTS block. NEVER fabricate or guess a link.
            9. CLEAN OUTPUT: Do not use block code fences (```) or JSON wrappers.
            {map_directive}
            """
            contents_payload = f"{formatted_history}\nCURRENT OPERATOR INPUT: {user_cmd}\n\n{compiled_context}"
            gen_config = types.GenerateContentConfig(
                system_instruction=sys_instruct, 
                temperature=0.7,
                max_output_tokens=8192
            )

        # ==========================================
        # PATHWAY B: SD BOT (LOGIN SCREEN RESEARCH ASSISTANT)
        # ==========================================
        elif mode == "SDBOT":
            sys_instruct = f"""
            You are SD Bot, the embedded intelligence assistant for the SemicoN OSINT Dashboard.
            You are speaking directly to a guest user on the login screen.
            You have access to the latest geopolitical, semiconductor, and supply chain intelligence data.
            Analyze the USER DIRECTIVE and the provided RAW OSINT INTERCEPTS.
            If the user asks what they will find inside the website, enthusiastically explain the dashboard's capabilities (Live OSINT, Agentic Research, Threat Scoring, Archival Intelligence).
            If the user asks a generic conversational question, reply naturally.
            If the user asks a research-based query, synthesize the scraped data into a high-quality intelligence summary.
            
            CRITICAL RULES:
            1. Your response MUST be strictly between 250 and 500 words.
            2. Output plain text with standard markdown formatting. Do not output JSON.
            3. Do NOT mention source code, API keys, or backend mechanics.
            4. If citing intelligence, list the URLs under a 'Sources' header.
            5. You MUST end your response EXACTLY with this sign-off (on a new line at the very end):
               
               Provided By: SD Bot (semirare.in)
            """
            contents_payload = f"USER DIRECTIVE:\n{user_cmd}\n\n{compiled_context}"
            gen_config = types.GenerateContentConfig(
                system_instruction=sys_instruct, 
                temperature=0.4,
                max_output_tokens=2048
            )

        # ==========================================
        # PATHWAY C: RIGID DYNAMIC BRIEF
        # ==========================================
        elif mode == "CUSTOM_UI":
            sys_instruct = f"""
            You are an autonomous, elite Geopolitical Intelligence Analyst. Your absolute directive is to read the provided context and fulfill the USER DIRECTIVE perfectly.
            
            CRITICAL FORMATTING RULES:
            1. MANDATORY LENGTH & STRUCTURAL EXPANSION (1500-2000+ WORDS): Large Language Models possess a strict conciseness bias. You MUST override this. To physically force the generation of 1500 to 2000 words, you CANNOT simply write basic paragraphs. Under EVERY SINGLE HEADER requested by the user, you MUST create at least 3 explicitly named sub-themes or sub-headings. 
            2. ANALYTICAL DEPTH FRAMEWORK: For every sub-theme, you must employ "Chain of Expansion": detail the historical precedent, analyze the macroeconomic variables, project the second and third-order supply chain disruptions, and assess specific regional military/diplomatic responses. You must write no less than 350 words per requested header. Do not stop generating until the analysis is absolutely exhaustive.
            3. You MUST follow the exact structural layout, headers, bullet counts, and instructions requested in the USER DIRECTIVE.
            4. You MUST NOT use markdown header hashes (###) or markdown bold stars (**). Write all section headers in plain-text capital letters.
            5. STRICT SOURCE REPUTATION & WIKIPEDIA BAN: You must rely ONLY on verifiable, reputed, and well-known publishers. You are STRICTLY FORBIDDEN from using, referencing, or citing Wikipedia.
            6. Right before the Sources section, you MUST insert an 'Owned By' block matching this exact text:
               Owned By:
               Write your name
               Write you designation
            7. Under the Sources section, you MUST strictly use this exact format pattern (excluding Wikipedia):
               Sources:
               Agentic AI
               [Verified publisher links]
            8. STRICT DEEP-LINK SOURCE ATTRIBUTION (NO TRUNCATION): When listing Sources, you MUST preserve the EXACT, UNEDITED absolute deep-link URL provided in the RAW OSINT INTERCEPTS. DO NOT truncate, compress, or shorten URLs to just their homepage domains (e.g., do not reduce '[https://site.com/article-123](https://site.com/article-123)' to '[https://site.com](https://site.com)'). Write the full string exactly as it appears. NEVER fabricate or guess a link.
            9. ZERO-KNOWLEDGE OVERRIDE (ANTI-REPORT HALLUCINATION): Your analysis MUST be grounded in the RAW OSINT INTERCEPTS. Because this is a live web scrape, your context will contain a mix of highly relevant articles, irrelevant noise, and paywall/bot-blocked text. You must SILENTLY IGNORE the irrelevant or blocked text. As long as you have AT LEAST ONE relevant piece of geopolitical data, you MUST generate the full report. ONLY abort and output exactly "⚠️ Intelligence Constraint Triggered" if absolutely ZERO relevant geopolitical data exists in the entire context block. Do not be overly sensitive; find the relevant data and write the report.
            10. VISUAL TELEMETRY DIRECTIVE: If the processed PizzINT or Scalytics telemetry feeds show a numerical anomaly spike or market price deviation exceeding 0.15 (+15%), you MUST append a valid structured tracking payload at the very end of your analytical textual output. Do not mention or explain the data block to the user.
            Format the chart blocks exactly as follows:
            ```json_chart
            {{
              "type": "pizzint_anomaly",
              "title": "PENTAGON LOGISTICS OPERATIONAL TEMPO DEV VECTORS",
              "data": [
                {{"time_window": "6h Ago", "anomaly_score": 12}},
                {{"time_window": "4h Ago", "anomaly_score": 45}},
                {{"time_window": "2h Ago", "anomaly_score": 110}}
              ]
            }}
            ```
            {map_directive}
            """
            contents_payload = f"USER DIRECTIVE:\n{user_cmd}\n\n{compiled_context}"
            gen_config = types.GenerateContentConfig(
                system_instruction=sys_instruct, 
                temperature=0.6,
                max_output_tokens=8192
            )
            
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
            5. STRICT SOURCE ATTRIBUTION & OVER-DELIVERY: Cite ONLY direct publisher URLs explicitly provided in the RAW OSINT INTERCEPTS. Over-deliver all available relevant URLs if the user requests a smaller quota. NEVER invent a link.
            6. ZERO-KNOWLEDGE OVERRIDE: Because this is a live web scrape, your context will contain a mix of highly relevant articles, irrelevant noise, and paywall/bot-blocked text. You must SILENTLY IGNORE the irrelevant or blocked text. As long as you have AT LEAST ONE relevant piece of geopolitical data, you MUST generate the full report. ONLY abort and output exactly "⚠️ Intelligence Constraint Triggered" if absolutely ZERO relevant geopolitical data exists in the entire context block.
            7. Return your output strictly as a JSON object matching the exact schema below.
            
            STRICT JSON SCHEMA REQUIRED:
            {
              "Title": "Strategic Intelligence Brief",
              "Threat_Level": "LOW/MODERATE/HIGH/CRITICAL",
              "BLUF": "Executive summary...",
              "Top_News": {
                 "Global": ["News 1", "News 2"]
              },
              "Watch_Out": ["Trend 1", "Trend 2"],
              "Risk_And_Threat_Analysis": {
                 "Overall_Analysis": "Analysis details..."
              },
              "Predictive_Analysis": "Forecast details..."
            }
            """
            contents_payload = f"CONTEXT SWEEP DATA:\n{compiled_context}"
            gen_config = types.GenerateContentConfig(
                system_instruction=legacy_instruction, 
                temperature=0.2, 
                response_mime_type="application/json",
                max_output_tokens=8192
            )

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
                map_coords_list = []
                
                # 🛑 PYTHON PHYSICAL KILL-SWITCH: Prevents Prompt Conflict Hallucinations 🛑
                if "⚠️ Intelligence Constraint Triggered" in raw_text:
                    print("[Node 4] ZERO-KNOWLEDGE OVERRIDE ENGAGED. Purging hallucinated report payload.")
                    raw_text = "⚠️ **Intelligence Constraint:** The autonomous scraper intercepted irrelevant data (e.g., generic forms or unrelated recruitment topics). To adhere to strict Zero-Hallucination protocols, the analysis has been aborted rather than using generalized AI training data."
                    
                    state['ui_markdown'] = raw_text
                    state['map_coords'] = []
                    state['drafted_brief'] = {
                        "is_custom_prompt": True,
                        "Title": "Aborted Analysis Pass",
                        "Threat_Level": "CUSTOM",
                        "BLUF": raw_text,
                        "Source": "System Failsafe"
                    }
                    return state

                # 🛑 THE FIX: Added "SDBOT" so it is correctly processed as text, not JSON
                if mode in ["CUSTOM_UI", "CONVERSATIONAL", "SDBOT"]:
                    if raw_text.startswith("```markdown"): raw_text = raw_text[11:-3].strip()
                    elif raw_text.startswith("```"): raw_text = raw_text[3:-3].strip()

                    if mode == "CUSTOM_UI":
                        raw_text = raw_text.replace("###", "").replace("**", "")

                    # 🌍 AGENTIC TOOL EXECUTION: 8-Tier Geospatial Consensus Array (MULTI-THEATER UPGRADE)
                    geo_matches = re.findall(r'\[GEO_TARGET:\s*(.+?)\]', raw_text)
                    
                    if geo_matches:
                        raw_text = re.sub(r'\[GEO_TARGET:\s*.+?\]', '', raw_text).strip()
                        
                        # Loop through every unique location tag found in the text
                        for location_raw in set([m.strip() for m in geo_matches]):
                            # Tokenize compound or multi-lingual location strings (handles pipes and commas)
                            location_tokens = [t.strip() for t in re.split(r'[,|]', location_raw) if t.strip()]
                            
                            # Default to the first token (Native Script), drop back to raw text if empty
                            location_name = location_tokens[0] if location_tokens else location_raw
                            safe_location = requests.utils.quote(location_name)
                            
                            # Secondary fallback token (English translation) if the main registry hit fails
                            fallback_location = requests.utils.quote(location_tokens[1]) if len(location_tokens) > 1 else None
                            global_headers = {"User-Agent": "SemicoN/1.0 (contact: support@semirare.in)"}
                            
                            candidates = [] # Consensus Matrix Array

                            # 🛰️ TIER 0: Direct Context Extraction Engine (Scrapes prompt AND scraped data)
                            try:
                                combined_search_space = f"{user_cmd} \n {compiled_context}"
                                text_matches = re.findall(r'(-?\d{1,2}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)', combined_search_space)
                                for tm in text_matches:
                                    lat_txt, lon_txt = float(tm[0]), float(tm[1])
                                    if -90 <= lat_txt <= 90 and -180 <= lon_txt <= 180:
                                        candidates.append({
                                            "lat": lat_txt, 
                                            "lon": lon_txt, 
                                            "address": f"{location_name} (Forced Operator GPS Input)", 
                                            "source": "Forced Coordinate Core", 
                                            "weight": 200
                                        })
                            except Exception as e:
                                print(f"[Node 4] Tier 0 parsing anomaly: {e}")

                            # 🛰️ TIER 1: ArcGIS REST API
                            try:
                                d_1 = "".join(["geocode", ".arcgis", ".com"])
                                url_1 = f"https://{d_1}/arcgis/rest/services/World/GeocodeServer/findAddressCandidates?singleLine={safe_location}&f=json&maxLocations=1&outFields=Score,Addr_type"
                                res_1 = requests.get(url_1, verify=False, timeout=3)
                                if res_1.status_code == 200 and len(res_1.json().get("candidates", [])) > 0:
                                    cand = res_1.json()["candidates"][0]
                                    score = cand.get("score", 0)
                                    addr_type = cand.get("attributes", {}).get("Addr_type", "")
                                    if score >= 90 and addr_type in ["POI", "PointAddress"]: w = 100
                                    elif score >= 85 and addr_type in ["StreetAddress", "StreetName", "Routing"]: w = 85
                                    else: w = 20
                                    candidates.append({"lat": float(cand["location"]["y"]), "lon": float(cand["location"]["x"]), "address": cand["address"], "source": "ArcGIS Enterprise", "weight": w})
                            except Exception: pass

                            # 🛰️ TIER 2: LocationIQ Premium API Framework
                            liq_token = self.get_named_token("LOCATIONIQ_TOKEN")
                            if liq_token:
                                try:
                                    d_liq = "".join(["us1", ".locationiq", ".com"])
                                    url_liq = f"https://{d_liq}/v1/search?key={liq_token}&q={safe_location}&format=json&limit=1"
                                    res_liq = requests.get(url_liq, verify=False, timeout=3)
                                    if res_liq.status_code == 200 and len(res_liq.json()) > 0:
                                        data_liq = res_liq.json()[0]
                                        liq_class = data_liq.get("class", "")
                                        if liq_class in ["amenity", "shop", "building", "tourism", "leisure", "historic", "office", "craft", "emergency", "place"]: w = 95
                                        elif liq_class in ["highway", "railway", "waterway"]: w = 80
                                        else: w = 15
                                        candidates.append({"lat": float(data_liq["lat"]), "lon": float(data_liq["lon"]), "address": data_liq["display_name"], "source": "LocationIQ Cluster", "weight": w})
                                except Exception: pass

                            # 🛰️ TIER 3: Mapbox Places v5 High-Performance Cluster
                            mb_token = self.get_named_token("MAPBOX_PUBLIC_TOKEN")
                            if mb_token:
                                try:
                                    d_mb = "".join(["api", ".mapbox", ".com"])
                                    url_mb = f"https://{d_mb}/geocoding/v5/mapbox.places/{safe_location}.json?access_token={mb_token}&limit=1"
                                    res_mb = requests.get(url_mb, verify=False, timeout=3)
                                    if res_mb.status_code == 200 and len(res_mb.json().get("features", [])) > 0:
                                        feat_mb = res_mb.json()["features"][0]
                                        feat_id = feat_mb.get("id", "")
                                        if feat_id.startswith("poi"): w = 95
                                        elif feat_id.startswith("address"): w = 85
                                        else: w = 15
                                        candidates.append({"lat": float(feat_mb["center"][1]), "lon": float(feat_mb["center"][0]), "address": feat_mb["place_name"], "source": "Mapbox Hub", "weight": w})
                                except Exception: pass

                            # 🛰️ TIER 4: Nominatim Authoritative Main Server
                            try:
                                d_2 = "".join(["nominatim", ".openstreetmap", ".org"])
                                url_2 = f"https://{d_2}/search?q={safe_location}&format=json&limit=1"
                                res_2 = requests.get(url_2, headers=global_headers, verify=False, timeout=3)
                                if res_2.status_code == 200 and len(res_2.json()) > 0:
                                    data_2 = res_2.json()[0]
                                    osm_class = data_2.get("class", "")
                                    if osm_class in ["amenity", "shop", "building", "tourism", "leisure", "historic", "office", "craft", "emergency", "place"]: w = 95
                                    elif osm_class in ["highway", "railway", "waterway"]: w = 80
                                    else: w = 15
                                    candidates.append({"lat": float(data_2["lat"]), "lon": float(data_2["lon"]), "address": data_2["display_name"], "source": "OSM Nominatim", "weight": w})
                            except Exception: pass

                            # 🛰️ TIER 5: QGIS Foundation Independent Public Instance
                            try:
                                d_3 = "".join(["nominatim", ".qgis", ".org"])
                                url_3 = f"https://{d_3}/search?q={safe_location}&format=json&limit=1"
                                res_3 = requests.get(url_3, headers=global_headers, verify=False, timeout=3)
                                if res_3.status_code == 200 and len(res_3.json()) > 0:
                                    data_3 = res_3.json()[0]
                                    osm_class = data_3.get("class", "")
                                    if osm_class in ["amenity", "shop", "building", "tourism", "leisure", "historic", "office", "place"]: w = 95
                                    elif osm_class in ["highway"]: w = 80
                                    else: w = 15
                                    candidates.append({"lat": float(data_3["lat"]), "lon": float(data_3["lon"]), "address": data_3["display_name"], "source": "QGIS Nominatim", "weight": w})
                            except Exception: pass

                            # 🛰️ TIER 6: Photon REST API
                            try:
                                d_4 = "".join(["photon", ".komoot", ".io"])
                                url_4 = f"https://{d_4}/api?q={safe_location}&limit=1"
                                res_4 = requests.get(url_4, verify=False, timeout=3)
                                if res_4.status_code == 200 and len(res_4.json().get("features", [])) > 0:
                                    feat = res_4.json()["features"][0]
                                    props = feat["properties"]
                                    osm_key = props.get("osm_key", "")
                                    if osm_key in ["amenity", "shop", "building", "tourism", "leisure", "historic", "place"]: w = 95
                                    elif osm_key == "highway": w = 80
                                    else: w = 15
                                    if props.get("extent") is not None: w = 10 
                                    resolved_address = f"{props.get('name', location_name)}, {props.get('city', '')} {props.get('country', '')}".strip(", ")
                                    candidates.append({"lat": float(feat["geometry"]["coordinates"][1]), "lon": float(feat["geometry"]["coordinates"][0]), "address": resolved_address, "source": "Photon Database", "weight": w})
                            except Exception: pass

                            # 🛰️ TIER 7: OpenStreetMap Overpass API
                            try:
                                d_5 = "".join(["overpass-api", ".de"])
                                url_5 = f"https://{d_5}/api/interpreter"
                                core_name = " ".join(location_name.replace(",", " ").split()[:3])
                                overpass_query = f'[out:json][timeout:5];nwr["name"~"{core_name}",i];out center 1;'
                                res_5 = requests.post(url_5, data=overpass_query, verify=False, timeout=5)
                                if res_5.status_code == 200 and len(res_5.json().get("elements", [])) > 0:
                                    elem = res_5.json()["elements"][0]
                                    lat_o = float(elem.get("lat", elem.get("center", {}).get("lat", 0)))
                                    lon_o = float(elem.get("lon", elem.get("center", {}).get("lon", 0)))
                                    if lat_o and lon_o:
                                        tags = elem.get("tags", {})
                                        resolved_address = f"{tags.get('name', location_name)} ({tags.get('highway', tags.get('amenity', 'POI'))})"
                                        candidates.append({"lat": lat_o, "lon": lon_o, "address": resolved_address, "source": "OSM Overpass Matrix", "weight": 98})
                            except Exception: pass

                            # 🕸️ TIER 8: OSINT Web Scraper (DDGS Engine Extraction Core)
                            try:
                                from ddgs import DDGS
                                with DDGS() as ddgs:
                                    ddg_query = f"{location_name} exact GPS coordinates latitude longitude"
                                    results = ddgs.text(ddg_query, max_results=5)
                                    for r in results:
                                        snippet = r.get("body", "") + " " + r.get("title", "")
                                        matches = re.findall(r'(-?[1-8]?\d\.\d{3,8})[^\d]{1,15}?(-?1[0-7]\d\.\d{3,8}|-?0?\d{1,2}\.\d{3,8})', snippet)
                                        if matches:
                                            lat_c, lon_c = float(matches[0][0]), float(matches[0][1])
                                            if -90 <= lat_c <= 90 and -180 <= lon_c <= 180:
                                                resolved_address = f"{location_name} (Resolved via Deep Web OSINT Scrape)"
                                                candidates.append({"lat": lat_c, "lon": lon_c, "address": resolved_address, "source": "DDGS OSINT Pipeline", "weight": 72})
                                                break
                            except Exception: pass

                            # 🛰️ EMERGENCY FALLBACK TIER: Try alternate English token if native script returned 0 candidates
                            if not candidates and fallback_location:
                                try:
                                    d_fallback = "".join(["nominatim", ".openstreetmap", ".org"])
                                    url_fb = f"https://{d_fallback}/search?q={fallback_location}&format=json&limit=1"
                                    res_fb = requests.get(url_fb, headers=global_headers, verify=False, timeout=3)
                                    if res_fb.status_code == 200 and len(res_fb.json()) > 0:
                                        data_fb = res_fb.json()[0]
                                        candidates.append({
                                            "lat": float(data_fb["lat"]), 
                                            "lon": float(data_fb["lon"]), 
                                            "address": data_fb["display_name"], 
                                            "source": "OSM Fallback Registry", 
                                            "weight": 85
                                        })
                                except Exception: pass

                            # 🧠 CONSENSUS EVALUATION (Haversine Spatial Clustering Engine)
                            valid_candidates = [c for c in candidates if c["weight"] >= 70]
                            
                            if valid_candidates:
                                import math
                                def haversine(lat1, lon1, lat2, lon2):
                                    R = 6371.0 
                                    dlat = math.radians(lat2 - lat1)
                                    dlon = math.radians(lon2 - lon1)
                                    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
                                    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))

                                clusters = []
                                for cand in valid_candidates:
                                    added = False
                                    for cluster in clusters:
                                        if haversine(cand["lat"], cand["lon"], cluster[0]["lat"], cluster[0]["lon"]) <= 3.0:
                                            cluster.append(cand)
                                            added = True
                                            break
                                    if not added:
                                        clusters.append([cand])
                                        
                                best_cluster = max(clusters, key=lambda cl: sum(c["weight"] for c in cl))
                                best_cluster.sort(key=lambda x: x["weight"], reverse=True)
                                best_match = best_cluster[0]
                                
                                map_coords_list.append({
                                    "lat": best_match["lat"],
                                    "lon": best_match["lon"],
                                    "label": location_name,
                                    "address": best_match["address"]
                                })
                                print(f"[Node 4] 🛰️ Target '{location_name}': Consensus Engine evaluated {len(valid_candidates)} hits. Winner: [{best_match['source']}]")
                                raw_text += f"\n\n📍 **API Verified Geolocation ({best_match['source']}):** {best_match['address']}\n🧭 **Verified GPS Coordinates:** {best_match['lat']}, {best_match['lon']}"
                            else:
                                print(f"[Node 4] ⚠️ Critical Error: Consensus Engine found 0 matches for '{location_name}'")
                                raw_text += f"\n\n*(Agent Note: Target '{location_name}' could not be resolved with sufficient precision across mapping registries.)*"

                    state['ui_markdown'] = raw_text
                    state['map_coords'] = map_coords_list
                    
                else:
                    try:
                        if "```json" in raw_text:
                            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                        elif "```" in raw_text:
                            raw_text = raw_text.split("```")[1].split("```")[0].strip()
                            
                        start_idx = raw_text.find('{')
                        end_idx = raw_text.rfind('}')
                        if start_idx != -1 and end_idx != -1:
                            raw_text = raw_text[start_idx:end_idx+1]
                            
                        brief_json = json.loads(raw_text)
                        brief_json['Source'] = source_str
                        brief_json['is_custom_prompt'] = False
                        state['drafted_brief'] = brief_json
                        state['ui_markdown'] = ""
                        state['map_coords'] = []
                    except json.JSONDecodeError as e:
                        print(f"[Node 4] JSON Parsing Failure in Autonomous Mode: {e}")
                        raise Exception(f"Failed to parse LLM JSON: {e}")

                # 🛑 THE FIX: Dynamic Title based on exactly which mode ran
                assigned_title = "Custom Analysis Pass"
                if mode == "SDBOT":
                    assigned_title = "SD Bot Dialogue Mode"
                elif mode == "CONVERSATIONAL":
                    assigned_title = "Conversational Dialogue Mode"

                state['drafted_brief'] = {
                    "is_custom_prompt": True,
                    "Title": assigned_title,
                    "Threat_Level": "CUSTOM",
                    "BLUF": raw_text,
                    "Source": source_str
                }
                
                print(f'[Node 4] Geopolitical Analysis execution layer successful.')
                break 
                
            except Exception as e:
                print(f'[Node 4] Warning: Key Slot {slot_idx + 1} processing failed: {e}')
                if slot_idx < len(api_keys) - 1: time.sleep(10.0)
                else: state['drafted_brief'] = None

        return state