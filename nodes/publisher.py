import os
import json
import datetime
from typing import Dict, Any

class PublisherNode:
    """
    Node 5: The Publisher Component
    Saves the finalized, structured intelligence brief to the correct JSON schema.
    """
    def __init__(self, output_dir="data/executive_home"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        LangGraph Node execution logic step.
        Consumes: state["drafted_brief"]
        Produces: Saves to disk and updates state status.
        """
        brief = state.get("drafted_brief")
        
        if not brief:
            print("[Node 5] No valid brief found in state. Skipping publish.")
            return state

        print("[Node 5] Publishing Intelligence Payload to Dashboard...")

        # Add timestamp metadata
        current_time = datetime.datetime.now(datetime.timezone.utc)
        brief["Date"] = current_time.strftime("%Y-%m-%d %H:%M:%S UTC")

        target_file = os.path.join(self.output_dir, "tactical_events_24h.json")

        # Safely append to the existing JSON array so we don't wipe historical alerts
        existing_data = []
        if os.path.exists(target_file):
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        existing_data = data
                    elif isinstance(data, dict) and 'recent_actions' in data:
                        existing_data = data['recent_actions']
            except Exception as e:
                print(f"[Node 5] Warning: Could not read existing file. Overwriting. Error: {e}")

        # Prepend the new brief to the top of the list
        existing_data.insert(0, brief)
        
        # Enforce a hard cap of 100 events to prevent massive disk bloat
        existing_data = existing_data[:100]

        # Save back to disk
        try:
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=4)
            print(f"[Node 5] Successfully published to {target_file}")
            state["publish_status"] = "Success"
        except Exception as e:
            print(f"[Node 5] ⚠️ Critical Write Error: {e}")
            state["publish_status"] = "Failed"

        return state