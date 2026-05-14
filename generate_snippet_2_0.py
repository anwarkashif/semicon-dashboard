import os
import json
import glob
import datetime
from google import genai

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files: return None
    files.sort() 
    return files[-1]

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No API key found. Skipping Snippet 2.0 generation.")
        return
    client = genai.Client(api_key=api_key)

    latest_brief_path = get_latest_file('data/brief_*.json')
    tactical_path = 'data/tactical_events_24h.json'
    
    weekly_context = ""
    if latest_brief_path:
        with open(latest_brief_path, 'r') as f:
            brief_data = json.load(f)
            weekly_context = brief_data.get('brief_raw', '')

    tactical_context = ""
    if os.path.exists(tactical_path):
        with open(tactical_path, 'r') as f:
            tactical_context = json.dumps(json.load(f)[:10])

    prompt = f"""
    You are a senior geopolitical intelligence analyst.
    Based on this week's intelligence: {weekly_context}
    And these recent tactical events: {tactical_context}

    Write a highly professional "Friday's Snippet 2.0" Strategic Synthesis.
    CRITICAL INSTRUCTION: The total word count MUST be strictly between 1500 and 2000 words. Expand deeply on all geopolitical, OSINT, and supply chain ramifications. Use a highly professional, think-tank analytical tone. Use strict Markdown formatting. DO NOT USE HTML TAGS.

    Return ONLY a valid JSON object with EXACTLY these keys and length constraints:
    - "bluf": (Approx 150 words. Write a structured Actionable Intelligence BLUF using strict Markdown. Format exactly as: **BLUF:** [1-2 sentences on main threat]. **Impact:** [1-2 sentences]. **Evidence:** [2-3 brief bullets]. **Action:** [1-2 immediate actions]).
    - "executive_summary": (Approx. 400 words. Deep analysis of the macro threat landscape and supply chain resilience).
    - "threat_narrative": (Approx. 400 words. Detailed exploration of adversary intent, state actor posturing, and geopolitical shifts).
    - "risk_assessment": (Approx. 350 words. Extensive evaluation of market impacts, routing chokepoints, and physical/cyber vulnerabilities).
    - "tactical_indicators": (List of exactly 3 bullet points as strings. Approx. 200 words total. Emphasize Supply Chain, Geopolitical, and Cyber).
    - "predictive_analysis": (Approx. 300 words. Rigorous forecasting for the next 7-14 days).
    - "recommendations": (Approx. 200 words. Strict, actionable guidance).

    Do not include markdown blocks like ```json. Just output the raw JSON.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        snippet_data = json.loads(raw_text)
        
        snippet_data['date'] = datetime.datetime.now().strftime("%d %B %Y")
        snippet_data['title'] = "Friday's Snippet 2.0: Strategic Intelligence Synthesis"
        snippet_data['classification'] = "UNCLASSIFIED"

        os.makedirs('data', exist_ok=True)
        with open('data/snippet_2_0_live.json', 'w') as f:
            json.dump(snippet_data, f, indent=4)
        print("Successfully generated snippet_2_0_live.json")

    except Exception as e:
        print(f"Failed to generate Snippet 2.0: {e}")

if __name__ == "__main__":
    main()