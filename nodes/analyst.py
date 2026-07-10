import os
import json
import time
import streamlit as st
from typing import Dict, Any, List
from google import genai
from google.genai import types

class AnalystNode:
    """
    Node 4: The Geopolitical Analyst Component
    Consumes cleaned markdown, synthesizes intelligence, and enforces strict JSON schema output.
    Implements a multi-key backup cascade with a 10-second cooling window to mitigate 429 Quota errors.
    """
    def __init__(self):
        self.model_id = 'gemini-3.5-flash'

    def get_all_keys(self) -> List[str]:
        """Collects all configured API keys from environment and secrets in strict priority order."""
        key_slots = [
            'GEMINI_API_KEY',
            'RAG_GEMINI_API_KEY',
            'RAG_GEMINI_API_KEY_2',
            'RAG_GEMINI_API_KEY_3',
            'RAG_GEMINI_API_KEY_4',
            'RAG_GEMINI_API_KEY_5'
        ]
        valid_keys = []
        for slot in key_slots:
            val = os.environ.get(slot)
            if not val:
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
        
        Use this EXACT JSON schema:
        {
            "Title": "A gripping, strategic headline",
            "Threat_Level": "Strictly one of: CRITICAL, ELEVATED, WATCH, or STANDARD",
            "Action": "A 1-sentence BLUF (Bottom Line Up Front)",
            "Location": "The primary country or region affected",
            "Actor": "The primary entity",
            "Predictive_Analysis": "1 paragraph on what is likely to happen next"
        }
        """

        # Fetch the rotational cascade list
        api_keys = self.get_all_keys()
        if not api_keys:
            print('[Node 4] ⚠️ CRITICAL FAILURE: No operational API keys discovered in system secrets configuration.')
            state['drafted_brief'] = None
            return state

        success = False
        # Fallback rotation loop starts execution
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
                        tools=[{'google_search': {}}]
                    )
                )
                
                # Safe syntax stripping to keep clipboard actions from breaking strings
                raw_text = response.text.strip()
                if raw_text.startswith('```json'): 
                    raw_text = raw_text[7:-3].strip()
                elif raw_text.startswith('```'): 
                    raw_text = raw_text[3:-3].strip()
                
                brief_json = json.loads(raw_text)
                
                # Intercept Google Grounding Links
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
                print(f'[Node 4] Intelligence Brief successfully drafted using Key Slot {slot_idx + 1}.')
                success = True
                break # Escape cascade loop on clean execution
                
            except Exception as e:
                print(f'[Node 4] Warning: Key Slot {slot_idx + 1} rejected payload execution: {e}')
                if slot_idx < len(api_keys) - 1:
                    print('🔄 [Node 4] Quota limit triggered. Engaging 10-second cooling window before shifting keys...')
                    time.sleep(10.0)
                    continue
                else:
                    print('[Node 4] ⚠️ All fallback API keys in the rotational matrix have been exhausted.')
                    state['drafted_brief'] = None

        return state