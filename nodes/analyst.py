# -*- coding: utf-8 -*-
import os
import json
import time
import re
import requests
import urllib3
from datetime import datetime, timezone
from typing import Dict, Any, List
from google import genai
from google.genai import types

# Suppress insecure request warnings for mapping APIs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import streamlit as st
except ImportError:
    st = None

class AnalystNode:
    """
    Node 4: The Geopolitical Analyst Component
    Features an Intent Engine Router, strict conversational isolation, 
    an automated Source Sanitizer, and an 8-Tier Geospatial Consensus Engine.
    """
    def __init__(self):
        self.model_id = 'gemini-3.1-flash-lite'
        self.source_blacklist = [
            "wikipedia.org",
            "wikimedia.org",
            "conflictradar360.com",
            "cr360-api.vercel.app",
            "scalytics.io",
            "pizzint.watch",
            "monitor-the-situation.com",
            "monitorthesituation.com",
            "iranmonitor.org",
            "redroom.live",
            "track-wanted.live",
            "usstrikeradar.com",
            "geoconfirmed.org",
            "skyosint.io",
            "earthengine.google.com",
            "liveuamap.com",
            "warmonitor.app",
            "war-monitor.com",
            "psyopoly.pro",
            "worldmonitor.app",
            "cartocdn.com",
            "api.currentsapi.services",
            "gnews.io",
            "google.com/ccm",
            "adtrafficquality.google"
        ]

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
        val = os.environ.get(token_name)
        if not val and st is not None:
            try: val = st.secrets.get(token_name)
            except Exception: pass
        return str(val).strip() if val else ""

    def clean_urls(self, text: str) -> List[str]:
        raw_urls = re.findall(r'https?://[^\s<>"]+', text)
        return [url.rstrip(')\]}.,;') for url in raw_urls]

    def sanitize_sources_and_text(self, text: str) -> str:
        """
        Deterministic Python filter that strips blacklisted sources,
        Wikipedia links, and backend aggregators from the entire output text.
        """
        # 1. Strip blacklisted URLs from the text
        for domain in self.source_blacklist:
            pattern = rf'https?://[^\s<>"]*{re.escape(domain)}[^\s<>"]*'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            # Also remove markdown bracketed forms: [URL: ...] or [https://...]
            bracket_pattern = rf'\[(?:URL:\s*)?https?://[^\s<>"]*{re.escape(domain)}[^\s<>"]*\]'
            text = re.sub(bracket_pattern, '', text, flags=re.IGNORECASE)

        # 2. Clean up multiple empty lines or dangling spaces in Sources section
        sources_match = re.search(r'(SOURCES?:\s*(?:Agentic AI)?\s*\n?)([\s\S]*?)(?=\n\n📍|\n\n🧭|\n\n\(Agent Note:|$)', text, re.IGNORECASE)
        if sources_match:
            header = sources_match.group(1).strip()
            body = sources_match.group(2)
            
            raw_urls = re.findall(r'https?://[^\s<>"]+', body)
            valid_urls = []
            for u in raw_urls:
                u_clean = u.rstrip(')\]}.,;')
                if not any(b in u_clean.lower() for b in self.source_blacklist) and u_clean not in valid_urls:
                    valid_urls.append(u_clean)
            
            if valid_urls:
                cleaned_sources_block = f"SOURCES: Agentic AI\n" + "\n".join(valid_urls)
            else:
                cleaned_sources_block = "SOURCES: Agentic AI (Direct Real-time OSINT Feeds)"
                
            text = text[:sources_match.start()] + cleaned_sources_block + text[sources_match.end():]

        # 3. Clean up extra blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        mode = state.get("execution_mode", "AUTONOMOUS")
        user_cmd = state.get('user_prompt', '').strip()
        chat_history = state.get('chat_history', [])
        extracted_data: List[Dict[str, str]] = state.get('extracted_markdown_context', [])
        
        current_date_str = datetime.now(timezone.utc).strftime("%A, %B %d, %Y")
        
        api_keys = self.get_all_keys()
        if not api_keys: return state

        # 🧠 SEMANTIC TOOL ROUTER MATRIX
        use_tables = False
        use_maps = False
        
        if mode == "CUSTOM_UI":
            try:
                router_client = genai.Client(api_key=api_keys[0])
                router_instruct = """
                You are the Dynamic Tool Router for an advanced intelligence node. Analyze the user's prompt.
                Classify it into a strict JSON object with exactly three keys: "mode", "use_tables", and "use_maps".
                
                RULES:
                - "mode": 'CUSTOM_UI' if the prompt is a complex research request/briefing. 'CONVERSATIONAL' if it's a short greeting/chat.
                - "use_tables": true ONLY if the prompt asks for metrics, anomalies, costs, delays, numbers, comparisons, or structured data. Otherwise false.
                - "use_maps": true ONLY if the prompt explicitly asks for a map, locations, or coordinates, OR if it focuses heavily on physical conflict zones, kinetic strikes, and frontline geography. Otherwise false.
                
                Output ONLY valid JSON.
                """
                router_res = router_client.models.generate_content(
                    model=self.model_id,
                    contents=f"USER PROMPT:\n{user_cmd}",
                    config=types.GenerateContentConfig(system_instruction=router_instruct, temperature=0.1, response_mime_type="application/json")
                )
                
                try:
                    routing_data = json.loads(router_res.text.strip())
                    mode = routing_data.get("mode", mode)
                    use_tables = routing_data.get("use_tables", False)
                    use_maps = routing_data.get("use_maps", False)
                    state["execution_mode"] = mode
                    print(f"[Node 4] Router engaged. Mode: {mode} | Tables: {use_tables} | Maps: {use_maps}")
                except Exception as json_err:
                    print(f"[Node 4] Router JSON parse failed, falling back to false tools: {json_err}")
                    
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

        # 🌍 DYNAMIC INSTRUCTION BUILDER
        table_directive = ""
        if use_tables:
            table_directive = """
            [DYNAMIC MARKDOWN TABLES TRIGGERED]
            You MUST generate a detailed, highly professional Markdown table organizing the complex metrics, delays, anomaly scores, or financial impacts derived from your analysis. Place this table near the end of your report.
            """
            
        map_directive = ""
        if use_maps:
            map_directive = """
            [GEOSPATIAL MAP RENDERING TRIGGERED]
            You MUST generate mapping coordinates to visualize the geographic threat. Append a list of exact location tags at the absolute bottom of your response (strictly AFTER the Sources section).

            TAG SYNTAX FORMAT:
            [GEO_TARGET: Location Name | Romanized Local Name | Country Name]

            STRICT GEOSPATIAL EXTRACTION RULES:
            1. STRICT CONTEXT-ONLY RULE: You MUST ONLY generate [GEO_TARGET] tags for specific cities, ports, military bases, straits, or towns that are EXPLICITLY discussed in your analytical text above.
            2. ZERO PROMPT CONTAMINATION: NEVER output sample names or locations that are not part of the active intelligence report.
            3. NO SECTION HEADERS OR INTRODUCTORY PROSE: Do NOT write any headings, bullet titles, or intro sentences. Output ONLY the raw bracketed [GEO_TARGET: ...] tags on their own lines at the very end.
            """

        # ==========================================
        # PATHWAY A: FLUID CHAT ENVIRONMENT
        # ==========================================
        if mode == "CONVERSATIONAL":
            sys_instruct = f"""
            You are an elite, highly personalized, and empathetic conversational AI co-pilot powering the SemicoN Agentic Engine. 
            
            CRITICAL CONVERSATIONAL & REFINEMENT CRITERIA:
            1. DYNAMIC CONVERSATIONAL STYLES: Adapt seamlessly to the user's basic conversation inputs. 
            2. SMALL TALK & GREETING OVERRIDE (CRITICAL SPEED DIRECTIVE): If the user prompt is a simple greeting or basic small talk, you must COMPLETELY IGNORE the `RAW OSINT INTERCEPTS`. Keep your response under 50 words.
            3. PERSONALIZED & WARM TONE: Converse naturally, empathetically, and directly using "I" and "you". NEVER format your conversational responses as a rigid "STATUS REPORT".
            4. NO META-COMMENTARY: Silently ignore garbage intercepts and answer the user's request using your own elite internal knowledge.
            5. ZERO SOURCES & NO ATTRIBUTION BLOCKS FOR CHAT/GUIDANCE: Keep it a clean, natural chat.
            6. STRICT SOURCE REPUTATION & WIKIPEDIA BAN: You are STRICTLY FORBIDDEN from using Wikipedia anywhere in your output.
            7. TEMPORAL ANCHORING: The current date is {current_date_str}. All intelligence must be grounded in the {current_date_str} timeline.
            8. STRICT SOURCE ATTRIBUTION (ONLY ON DEMAND): DO NOT output any URLs or sources in this conversational mode UNLESS the user explicitly asks for links.
            9. CLEAN OUTPUT: Do not use block code fences (```) or JSON wrappers.
            
            {table_directive}
            {map_directive}
            """
            contents_payload = f"{formatted_history}\nCURRENT OPERATOR INPUT: {user_cmd}\n\n{compiled_context}"
            gen_config = types.GenerateContentConfig(
                system_instruction=sys_instruct, 
                temperature=0.7,
                max_output_tokens=8192
            )

        # ==========================================
        # PATHWAY B: RIGID DYNAMIC BRIEF
        # ==========================================
        elif mode == "CUSTOM_UI":
            sys_instruct = f"""
            You are an autonomous, elite Geopolitical Intelligence Analyst. Your absolute directive is to read the provided context and fulfill the USER DIRECTIVE perfectly.
            CURRENT SYSTEM DATE: {current_date_str}.
            
            CRITICAL FORMATTING RULES:
            1. MANDATORY LENGTH & STRUCTURAL EXPANSION (1500-2000+ WORDS): Under EVERY SINGLE HEADER requested by the user, you MUST create at least 3 explicitly named sub-themes or sub-headings. 
            2. STRICT TEMPORAL ANCHORING (TODAY'S NEWS ONLY): You MUST prioritize the most recent, specific kinetic events, policy shifts, and market anomalies from the RAW OSINT INTERCEPTS that occurred leading up to {current_date_str}. DO NOT write generic, timeless overviews. State exactly WHAT happened TODAY, WHO was involved, and WHERE it occurred.
            3. You MUST follow the exact structural layout, headers, bullet counts, and instructions requested in the USER DIRECTIVE.
            4. You MUST NOT use markdown header hashes (###) or markdown bold stars (**). Write all section headers in plain-text capital letters.
            5. STRICT SOURCE REPUTATION & WIKIPEDIA BAN: You must rely ONLY on verifiable, reputed, and well-known publishers. NEVER cite Wikipedia.
            6. Under the Sources section, you MUST strictly use this exact format pattern:
               SOURCES: Agentic AI
               [List exact news article URLs found inside the text of the OSINT Intercepts]
            7. STRICT DEEP-LINK SOURCE ATTRIBUTION & BLACKLIST: Extract and print ONLY verified article URLs. Do not cite generic homepages, Wikipedia, or backend aggregators. DO NOT include URLs containing 'osint.scalytics.io', 'pizzint.watch', 'monitor-the-situation.com', 'conflictradar360.com', 'iranmonitor.org', 'redroom.live', 'track-wanted.live', 'usstrikeradar.com', 'geoconfirmed.org', or 'skyosint.io' in the Sources section.
            8. NO DESIGNATIONS: You MUST NOT include an 'Owned By', 'Agent Name', or any analyst designation block anywhere in your output. The report must remain completely unbranded and ready for the user to append their own credentials.
            9. ZERO-KNOWLEDGE OVERRIDE (ANTI-REPORT HALLUCINATION): Your analysis MUST be grounded in the RAW OSINT INTERCEPTS. Silently ignore irrelevant text. As long as you have AT LEAST ONE relevant piece of geopolitical data, generate the full report. ONLY abort and output exactly "⚠️ Intelligence Constraint Triggered" if absolutely ZERO relevant geopolitical data exists.
            
            {table_directive}
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
            legacy_instruction = f"""
            You are an autonomous, elite Geopolitical Intelligence Analyst for the SemicoN Dashboard.
            CURRENT SYSTEM DATE: {current_date_str}.
            
            Synthesize a highly professional, exhaustive daily intelligence brief focusing on semiconductor supply chains, critical minerals, defense, and geopolitics.
            
            CRITICAL FORMATTING & STRICT VERIFIABILITY RULES:
            1. STRICT TEMPORAL ANCHORING & FACTUAL GROUNDING: Every reported event MUST be grounded strictly in the RAW OSINT INTERCEPTS for {current_date_str}. You are FORBIDDEN from generating speculative, uncorroborated, or generic boilerplate text. Every single news item MUST contain a specific entity/actor, a concrete kinetic/diplomatic action, and an exact geographic locus.
            2. MANDATORY TOPICAL CRITERIA: You MUST actively scan the intercepts and extract verifiable news covering the following high-priority intelligence vectors:
               - Geopolitics, geoeconomics, national security, defense, conflict, war, military action, threats, weaponry, arsenal, military assets, warships, long-range missile systems, rocket & weapon manufacturing.
               - Rare Earth elements, semiconductors, global supply chains, and critical minerals.
               - Legislative & Government: US House, bills, acts, official/unofficial delegations, embassy/embassies.
               - Financial & Economic: Global financial system, financial sanctions, asset seizure/sold, reimbursement, debt, NATO share, and damage costs.
               - Nuclear & Strategic: Nuclear weapons, nuclear plants, denuclearisation.
               - High-Value Targets: Assassination, assassination attempts, killed/survived metrics, headquarters (security, safety, damage, collapse, attack), target & legitimate target designations.
               - Kinetic/Security: Incursions, attacks, blockades, naval/aerial/land threats, shooting/stabbing incidents, terrorist attacks, bomb blasts, surgical strikes, invasions, drone/kamikaze operations.
               - Natural Disasters: flood, earthquake, tsunami, landslide, cyclone, tornado, hurricane, flash flood, cloud burst, wildfire, and heatwave.
               - Outer space: NASA, ISRO, CNSA, Roscosmos, ESA, commercial space (SpaceX), reconnaissance satellites, orbital assets, and space stations.
               - Multilateral & Key States: US, Russia, P5, India, EU, SAARC, ASEAN and ASEAN related news, NATO, CIA, MI6, Mossad, UN, BRICS, SCO, G20, AU, AUKUS, GCC, and national intelligence agencies.
            3. DYNAMIC REGIONAL PRUNING (ZERO-HALLUCINATION ENFORCEMENT): 
               - You MUST NOT output placeholder, generic, or passive filler entries (e.g., FORBIDDEN: "No specific events reported", "Agencies are monitoring", "Security remains a priority").
               - If the RAW OSINT INTERCEPTS do NOT contain concrete, verifiable news for a specific regional category occurring today, YOU MUST COMPLETELY OMIT THAT KEY FROM 'Top_News'. 
               - For any region that is included, provide up to 10 (minimum 1, maximum 10) distinct, highly detailed news items.
            4. DEDICATED TACTICAL OSINT & NATURAL DISASTERS SECTION:
               - You MUST dynamically include a key named 'Tactical_OSINT_And_Natural_Disasters' inside 'Top_News' exclusively for real-time tactical and environmental incidents (strikes, shootings, stabbings, bombings, floods, earthquakes, etc.). 
               - If zero such incidents occurred today, COMPLETELY OMIT the 'Tactical_OSINT_And_Natural_Disasters' key. Do not leave it empty.
            5. STRICT GLOBAL DIVERSITY & ANTI-DUPLICATION:
               - You MUST NOT mention the same country, event, or incident in more than one category. If an event is listed in 'Southeast_Asia', it CANNOT appear in 'Global_Multilateral' or 'Tactical_OSINT_And_Natural_Disasters'.
            6. MANDATORY LENGTH & STRUCTURAL EXPANSION:
               - Write exhaustive, dense analytical prose for BLUF, Executive Summary, Situational Update, Operational Impacts, Risk Analysis, and Predictive Analysis.
            7. STRICT SOURCE REPUTATION & WIKIPEDIA BAN: You are STRICTLY FORBIDDEN from using, referencing, or citing Wikipedia.
            8. ZERO-KNOWLEDGE OVERRIDE: Silently ignore noise or paywalls. Ground analysis strictly in RAW OSINT INTERCEPTS. ONLY abort with "⚠️ Intelligence Constraint Triggered" if absolutely ZERO relevant geopolitical data exists.
            9. Return your output strictly as a JSON object matching the exact schema below. Do not include markdown formatting like ```json in the output.
            
            VALID REGIONAL KEYS FOR 'Top_News' (Include ONLY keys with verified news today):
            - "South_Asia", "Central_Asia", "Southeast_Asia", "East_Asia", "West_Asia_Middle_East", "Northern_Europe", "Eastern_Europe", "Central_Europe", "Western_Europe", "Southern_Europe", "North_America", "South_America", "Africa", "Oceania", "Outer_Space", "Global_Multilateral", "Tactical_OSINT_And_Natural_Disasters"

            STRICT JSON SCHEMA REQUIRED:
            {{
              "Title": "Strategic Intelligence Brief",
              "Threat_Level": "LOW/MODERATE/HIGH/CRITICAL/EXTREME",
              "BLUF": "Dense BLUF summary...",
              "Executive_Summary": "Exhaustive executive summary...",
              "Top_News": {{
                 "[DYNAMIC_VALID_REGION_KEY_1]": ["Verified fact-grounded event 1", "Verified fact-grounded event 2"],
                 "[DYNAMIC_VALID_REGION_KEY_2]": ["Verified fact-grounded event 1", "Verified fact-grounded event 2", "Verified fact-grounded event 3", "Verified fact-grounded event 4", "Verified fact-grounded event 5", "Verified fact-grounded event 6"],
                 "Tactical_OSINT_And_Natural_Disasters": ["Specific kinetic strike, bombing, shooting, or severe natural disaster 1", "Specific kinetic strike, bombing, shooting, or severe natural disaster 2"]
              }},
              "Watch_Out": ["Trend 1", "Trend 2", "Trend 3", "Trend 4", "Trend 5", "Trend 6", "Trend 7", "Trend 8", "Trend 9", "Trend 10", "Trend 11", "Trend 12", "Trend 13", "Trend 14", "Trend 15"],
              "Situational_Update_And_Threat_Telemetry": {{
                 "Overall_Analysis": "Detailed analytical breakdown..."
              }},
              "Operational_Impacts": {{
                 "Overall_Analysis": "Supply chain, logistical, and infrastructure impacts..."              
              }},
              "Risk_And_Threat_Analysis": {{
                 "Overall_Analysis": "Near-term and medium-term tactical risks..."
              }},
              "Predictive_Analysis": "30 to 72 hour strategic forecast..."
            }}
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
                
                # 🛑 ZERO-KNOWLEDGE OVERRIDE
                if "⚠️ Intelligence Constraint Triggered" in raw_text:
                    print("[Node 4] ZERO-KNOWLEDGE OVERRIDE ENGAGED. Purging payload.")
                    raw_text = "⚠️ **Intelligence Constraint:** The autonomous scraper intercepted irrelevant data. To adhere to strict Zero-Hallucination protocols, the analysis has been aborted."
                    
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

                if mode in ["CUSTOM_UI", "CONVERSATIONAL"]:
                    if raw_text.startswith("```markdown"): raw_text = raw_text[11:-3].strip()
                    elif raw_text.startswith("```"): raw_text = raw_text[3:-3].strip()

                    if mode == "CUSTOM_UI":
                        raw_text = raw_text.replace("###", "").replace("**", "")

                    # 🛡️ DETERMINISTIC PYTHON SOURCE SANITIZATION (Bans Wikipedia & Aggregators)
                    raw_text = self.sanitize_sources_and_text(raw_text)

                    # 🌍 AGENTIC TOOL EXECUTION: 8-Tier Geospatial Consensus Array
                    geo_matches = re.findall(r'\[GEO_TARGET:\s*(.+?)\]', raw_text)
                    
                    if geo_matches:
                        raw_text = re.sub(r'\[GEO_TARGET:\s*.+?\]', '', raw_text).strip()
                        
                        for location_raw in set([m.strip() for m in geo_matches]):
                            location_tokens = [t.strip() for t in re.split(r'[,|]', location_raw) if t.strip()]
                            location_name = location_tokens[0] if location_tokens else location_raw
                            safe_location = requests.utils.quote(location_name)
                            
                            fallback_location = requests.utils.quote(location_tokens[1]) if len(location_tokens) > 1 else None
                            global_headers = {"User-Agent": "SemicoN/1.0 (contact: support@semirare.in)"}
                            
                            candidates = [] 

                            # 🛰️ TIER 0: Direct Context Extraction Engine
                            try:
                                combined_search_space = f"{user_cmd} \n {compiled_context}"
                                text_matches = re.findall(r'(-?\d{1,2}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)', combined_search_space)
                                for tm in text_matches:
                                    lat_txt, lon_txt = float(tm[0]), float(tm[1])
                                    if -90 <= lat_txt <= 90 and -180 <= lon_txt <= 180:
                                        candidates.append({"lat": lat_txt, "lon": lon_txt, "address": f"{location_name} (Forced Operator GPS Input)", "source": "Forced Coordinate Core", "weight": 200})
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

                            # 🛰️ TIER 3: Mapbox Places v5
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

                            # 🛰️ TIER 4: Nominatim
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

                            # 🛰️ TIER 5: QGIS Foundation
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

                            # 🛰️ EMERGENCY FALLBACK TIER
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

                            # 🧠 CONSENSUS EVALUATION
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
                    
                    state['drafted_brief'] = {
                        "is_custom_prompt": True,
                        "Title": "Conversational Dialogue Mode" if mode == "CONVERSATIONAL" else "Custom Analysis Pass",
                        "Threat_Level": "CUSTOM",
                        "BLUF": raw_text,
                        "Source": source_str
                    }
                    
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

                print(f'[Node 4] Geopolitical Analysis execution layer successful.')
                break 
                
            except Exception as e:
                print(f'[Node 4] Warning: Key Slot {slot_idx + 1} processing failed: {e}')
                if slot_idx < len(api_keys) - 1: time.sleep(10.0)
                else: state['drafted_brief'] = None

        return state