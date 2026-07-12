import os
import json
import datetime
from typing import Dict, Any

class PublisherNode:
    """
    Node 5: The Publisher Component
    Enforces mode isolation: Bypasses dashboard tracking logs entirely during 
    custom prompt cycles, while routing automated historical cron loops normally.
    """
    def __init__(self, output_dir="data/executive_home"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs("data", exist_ok=True)

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        mode = state.get("execution_mode", "AUTONOMOUS")
        brief = state.get("drafted_brief")
        ui_md = state.get("ui_markdown", "")
        
        if not brief and not ui_md:
            print("[Node 5] No valid brief or markdown context found in state pipeline.")
            return state

        current_time = datetime.datetime.now(datetime.timezone.utc)
        
        # ==========================================
        # ROUTE A: CUSTOM ON-SCREEN QUERY ENVELOPE
        # ==========================================
        if mode == "CUSTOM_UI":
            print("[Node 5] Custom Ad-Hoc Mode Active. Bypassing JSON Database logging to preserve history.")
            
            # Syncs custom markdown to file system for backend validation caching
            source_str = brief.get("Source", "Unknown") if brief else "Custom Feed"
            with open('data/agentic_email_body.md', 'w', encoding='utf-8') as f:
                f.write(f"{ui_md}\n\n---\n**Sources Scanned:**\n{source_str}")
                
            state["publish_status"] = "Success (Isolated Local Stream)"
            return state
            
        # ==========================================
        # ROUTE B: HOURLY AUTONOMOUS CRON DATABASE UPDATE
        # ==========================================
        else:
            print("[Node 5] Autonomous Mode Active. Commencing Database Logging and Email Synthesis...")
            
            final_brief = brief
            final_brief["Date"] = current_time.strftime("%Y-%m-%d %H:%M:%S UTC")
            source_str = brief.get('Source', '')
            
            email_md = f"### 🚨 {final_brief.get('Title', 'Agentic AI Strategic Brief')}\n\n"
            email_md += f"**Threat Level:** {final_brief.get('Threat_Level', 'STANDARD')}\n\n"
            email_md += f"#### 🎯 Bottom Line Up Front (BLUF)\n{final_brief.get('BLUF', 'No BLUF provided.')}\n\n"
            
            top_news = final_brief.get("Top_News", {})
            if isinstance(top_news, dict):
                email_md += "#### 🌍 Top News from the Globe\n"
                for region, items in top_news.items():
                    email_md += f"**{region}**\n"
                    for item in items: email_md += f"* {item}\n"
                    
            email_md += "\n#### 🔭 What to Watch Out For\n"
            for watch in final_brief.get("Watch_Out", []): email_md += f"* {watch}\n"
            
            rta = final_brief.get("Risk_And_Threat_Analysis", {})
            email_md += f"\n#### ⚖️ Risk and Threat Analysis\n**Overall Analysis:**\n{rta.get('Overall_Analysis', 'N/A')}\n\n"
            email_md += f"#### 🔮 Predictive Analysis\n{final_brief.get('Predictive_Analysis', 'N/A')}\n\n"
            email_md += f"---\n**Sources:**\n{source_str}"
            
            with open('data/agentic_email_body.md', 'w', encoding='utf-8') as f:
                f.write(email_md)

            # File System Append Routine
            target_file = os.path.join(self.output_dir, "tactical_events_24h.json")
            existing_data = []
            if os.path.exists(target_file):
                try:
                    with open(target_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list): existing_data = data
                except Exception as e:
                    print(f"[Node 5] File reading warning: {e}")

            existing_data.insert(0, final_brief)
            existing_data = existing_data[:100]

            try:
                with open(target_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=4)
                print(f"[Node 5] Successfully appended item to tracking array: {target_file}")
                state["publish_status"] = "Success (Database Appended)"
            except Exception as e:
                print(f"[Node 5] Write Error: {e}")
                state["publish_status"] = "Failed"

            return state