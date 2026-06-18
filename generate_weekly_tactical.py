import os
import json
import glob
import datetime
from google import genai
from huggingface_hub import HfApi

def get_latest_file(pattern):
    files = glob.glob(pattern)
    if not files: return None
    files.sort() 
    return files[-1]

def update_fallback_title(target_title):
    """
    FAILSAFE: If the AI API crashes or times out, this forcefully updates 
    the date on the existing dashboard file so the UI never displays the wrong week.
    """
    file_path = 'data/weekly_tactical_live.json'
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            data['title'] = target_title
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"⚠️ AI generation failed, but successfully force-updated title to: {target_title}")
            
            # --- Sync the fallback to Hugging Face so the updated title persists ---
            HF_TOKEN = os.environ.get("HF_TOKEN")
            REPO_ID = os.environ.get("SPACE_ID") or "YOUR_HF_USERNAME/YOUR_SPACE_NAME" 
            if HF_TOKEN and REPO_ID:
                try:
                    api = HfApi()
                    api.upload_file(
                        path_or_fileobj=file_path,
                        path_in_repo=file_path,
                        repo_id=REPO_ID,
                        repo_type="space",
                        token=HF_TOKEN,
                        commit_message=f"Auto-sync Fallback Tactical Title: {target_title}"
                    )
                    print("✅ Locked fallback title into permanent storage.")
                except Exception as e:
                    print(f"❌ Failed to sync fallback to Hub: {e}")
        except Exception as e:
            print(f"Fallback title update failed: {e}")

def main():
    # ==========================================
    # 1. CALCULATE MATHEMATICAL FRIDAY ANCHOR FIRST
    # ==========================================
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # Calculate days since last Friday (0 = Monday, 4 = Friday)
    days_since_friday = (now.weekday() - 4) % 7
    
    last_friday = now - datetime.timedelta(days=days_since_friday)
    previous_friday = last_friday - datetime.timedelta(days=7)

    # Time-gate: Hold the date until Friday 12:30 UTC (6:00 PM IST)
    if now.weekday() == 4 and (now.hour < 12 or (now.hour == 12 and now.minute < 30)):
        last_friday = last_friday - datetime.timedelta(days=7)
        previous_friday = previous_friday - datetime.timedelta(days=7)
    
    if last_friday.month == previous_friday.month:
        date_string = f"{last_friday.strftime('%B')} {previous_friday.day}-{last_friday.day}, {last_friday.year}"
    else:
        date_string = f"{previous_friday.strftime('%B %d')} - {last_friday.strftime('%B %d')}, {last_friday.year}"
        
    target_title = f"Tactical Weekly Brief: Strategic Intelligence Synthesis - {date_string}"

    # ==========================================
    # 2. ATTEMPT AI GENERATION
    # ==========================================
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("No API key found. Skipping Weekly Tactical Brief generation.")
        update_fallback_title(target_title)
        return
        
    client = genai.Client(api_key=api_key)

    latest_brief_path = get_latest_file('data/brief_*.json')
    tactical_path = 'data/weekly_tactical/tactical_events_24h.json'
    
    weekly_context = ""
    if latest_brief_path:
        try:
            with open(latest_brief_path, 'r') as f:
                brief_data = json.load(f)
                weekly_context = brief_data.get('brief_raw', '')
        except Exception:
            pass

    tactical_context = ""
    if os.path.exists(tactical_path):
        try:
            with open(tactical_path, 'r') as f:
                tactical_context = json.dumps(json.load(f)[:10])
        except Exception:
            pass

    prompt = f"""
    You are a senior geopolitical intelligence analyst.
    Based on this week's intelligence: {weekly_context}
    And these recent tactical events: {tactical_context}

    Write a highly professional "Tactical Weekly Brief" Strategic Synthesis.
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
        
        # Apply the mathematically verified title
        snippet_data['title'] = target_title
        
        # Remove old static keys so they don't break the new UI format
        snippet_data.pop('date', None)
        snippet_data.pop('classification', None)

        os.makedirs('data', exist_ok=True)
        output_file = 'data/weekly_tactical_live.json'
        with open(output_file, 'w') as f:
            json.dump(snippet_data, f, indent=4)
        print(f"✅ Successfully generated and saved {output_file} for {date_string}")

        # ==========================================
        # ☁️ HUGGING FACE PERMANENT RETENTION SYNC
        # ==========================================
        HF_TOKEN = os.environ.get("HF_TOKEN")
        REPO_ID = os.environ.get("SPACE_ID") or "YOUR_HF_USERNAME/YOUR_SPACE_NAME" 
        
        if HF_TOKEN and REPO_ID:
            try:
                api = HfApi()
                print(f"☁️ Uploading {output_file} to permanent storage on {REPO_ID}...")
                api.upload_file(
                    path_or_fileobj=output_file,
                    path_in_repo=output_file,
                    repo_id=REPO_ID,
                    repo_type="space",
                    token=HF_TOKEN,
                    commit_message=f"Auto-sync Weekly Tactical Brief: {date_string}"
                )
                print("✅ Successfully locked weekly tactical brief into permanent Hugging Face storage!")
            except Exception as e:
                print(f"❌ Failed to sync to Hub. File is only in temporary memory! Error: {e}")
        else:
            print("⚠️ HF_TOKEN or REPO_ID missing. File saved locally but will be lost on container restart.")
        # ==========================================

    except Exception as e:
        print(f"❌ Failed to generate Weekly Tactical Brief: {e}")
        # Trigger the failsafe to ensure the date is always correct on the UI
        update_fallback_title(target_title)

if __name__ == "__main__":
    main()