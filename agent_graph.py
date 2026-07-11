import time
import threading
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from nodes.extractor import ExtractorNode
from nodes.analyst import AnalystNode
from nodes.publisher import PublisherNode

# ==========================================
# 1. DEFINE THE AGENT'S MEMORY (STATE)
# ==========================================
class AgentState(TypedDict):
    current_target_urls: List[str]
    user_prompt: str
    extracted_markdown_context: List[Dict[str, str]]
    drafted_brief: Dict[str, Any]
    publish_status: str

# ==========================================
# 2. INITIALIZE THE NODES
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
# 3. BUILD THE EXECUTION GRAPH
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
# 4. THE AUTONOMOUS LOOP (STREAMLIT DAEMON)
# ==========================================
def autonomous_agent_loop():
    print("🚀 [Agentic Engine] Autonomous Discovery Loop Initialized.")
    agent_app = build_agent_graph()

    while True:
        try:
            print("\n🔄 [Agentic Engine] Initializing autonomous intelligence sweep...")
            initial_state = {
                "current_target_urls": [], 
                "user_prompt": (
                    "Conduct an autonomous global beat sweep. Synthesize breaking technical and strategic developments "
                    "from the last 24 hours regarding semiconductor supply chains, advanced lithography export controls, "
                    "critical mineral asset control, and West Asia maritime chokepoints."
                ),
                "extracted_markdown_context": [],
                "drafted_brief": {},
                "publish_status": "Pending"
            }
            final_state = agent_app.invoke(initial_state)
            print(f"✅ [Agentic Engine] Autonomous cycle complete. Publish Status: {final_state.get('publish_status')}")
        except Exception as e:
            print(f"⚠️ [Agentic Engine] Critical Execution Failure: {e}")
        time.sleep(3600)

def start_agent_daemon():
    agent_thread = threading.Thread(target=autonomous_agent_loop, daemon=True)
    agent_thread.start()

# ==========================================
# 5. GITHUB ACTIONS HEADLESS TRIGGER
# ==========================================
# 🛑 THE FIX: This block tells Python to actually run the graph when triggered by GitHub Actions
if __name__ == "__main__":
    print("🚀 [Agentic Engine] Initiating Single-Pass Sweep (GitHub Actions Mode)...")
    agent_app = build_agent_graph()
    try:
        initial_state = {
            "current_target_urls": [], 
            "user_prompt": (
                "Conduct an autonomous global beat sweep. Synthesize breaking technical and strategic developments "
                "from the last 24 hours regarding semiconductor supply chains, advanced lithography export controls, "
                "critical mineral asset control, and West Asia maritime chokepoints."
            ),
            "extracted_markdown_context": [],
            "drafted_brief": {},
            "publish_status": "Pending"
        }
        agent_app.invoke(initial_state)
        print("✅ [Agentic Engine] Single-pass headless execution complete.")
    except Exception as e:
        print(f"⚠️ [Agentic Engine] Headless Execution Failure: {e}")