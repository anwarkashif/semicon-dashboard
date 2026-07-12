import time
import threading
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from nodes.extractor import ExtractorNode
from nodes.analyst import AnalystNode
from nodes.publisher import PublisherNode

# ==========================================
# 1. AGENT STATE CONTRACT (EXPANDED)
# ==========================================
class AgentState(TypedDict):
    execution_mode: str              # "AUTONOMOUS" or "CUSTOM_UI"
    current_target_urls: List[str]
    user_prompt: str
    extracted_markdown_context: List[Dict[str, str]]
    drafted_brief: Dict[str, Any]    # Legacy storage for dashboard updates
    ui_markdown: str                 # Dedicated channel for unconstrained custom output
    publish_status: str

# ==========================================
# 2. INITIALIZE NODES
# ==========================================
extractor = ExtractorNode()
analyst = AnalystNode()
publisher = PublisherNode()

def run_extractor(state: AgentState) -> AgentState:
    return extractor.execute(state)

def run_analyst(state: AgentState) -> AgentState:
    return analyst.execute(state)

def run_publisher(state: AgentState) -> AgentState:
    return publisher.execute(state)

# ==========================================
# 3. BUILD GRAPH ARCHITECTURE
# ==========================================
def build_agent_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("Extractor", run_extractor)
    workflow.add_node("Analyst", run_analyst)
    workflow.add_node("Publisher", run_publisher)
    
    workflow.set_entry_point("Extractor")
    workflow.add_edge("Extractor", "Analyst")
    workflow.add_edge("Analyst", "Publisher")
    workflow.add_edge("Publisher", END)
    
    return workflow.compile()

# ==========================================
# 4. AUTONOMOUS CRON LOOP (DAEMON MODE)
# ==========================================
def autonomous_agent_loop():
    print("🚀 [Agentic Engine] Autonomous Discovery Loop Initialized.")
    agent_app = build_agent_graph()

    while True:
        try:
            print("\n🔄 [Agentic Engine] Initializing autonomous intelligence sweep...")
            initial_state = {
                "execution_mode": "AUTONOMOUS",  # Explicitly locks mode to standard routing
                "current_target_urls": [], 
                "user_prompt": (
                    "Conduct an autonomous global beat sweep. Synthesize breaking technical and strategic developments "
                    "from the last 24 hours regarding semiconductor supply chains, advanced lithography export controls, "
                    "critical mineral asset control, and West Asia maritime chokepoints."
                ),
                "extracted_markdown_context": [],
                "drafted_brief": {},
                "ui_markdown": "",
                "publish_status": "Pending"
            }
            final_state = agent_app.invoke(initial_state)
            print(f"✅ [Agentic Engine] Autonomous cycle complete. Status: {final_state.get('publish_status')}")
        except Exception as e:
            print(f"⚠️ [Agentic Engine] Critical Execution Failure: {e}")
        time.sleep(1500) # Scheduled to run every 25 minutes

def start_agent_daemon():
    agent_thread = threading.Thread(target=autonomous_agent_loop, daemon=True)
    agent_thread.start()

# ==========================================
# 5. RUNTIME HANDLER
# ==========================================
if __name__ == "__main__":
    print("🚀 [Agentic Engine] Initiating Single-Pass Sweep (GitHub Actions Mode)...")
    agent_app = build_agent_graph()
    try:
        initial_state = {
            "execution_mode": "AUTONOMOUS",
            "current_target_urls": [], 
            "user_prompt": (
                "Conduct an autonomous global beat sweep. Synthesize breaking technical and strategic developments "
                "from the last 24 hours regarding semiconductor supply chains, advanced lithography export controls, "
                "critical mineral asset control, and West Asia maritime chokepoints."
            ),
            "extracted_markdown_context": [],
            "drafted_brief": {},
            "ui_markdown": "",
            "publish_status": "Pending"
        }
        agent_app.invoke(initial_state)
        print("✅ [Agentic Engine] Headless execution complete.")
    except Exception as e:
        print(f"⚠️ [Agentic Engine] Headless Execution Failure: {e}")