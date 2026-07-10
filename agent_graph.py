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
# This dictionary structure acts as the shared memory passed between nodes.
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

# Node wrapper functions to adapt class methods for LangGraph
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

    # Add the nodes to the graph
    workflow.add_node("Extractor", run_extractor)
    workflow.add_node("Analyst", run_analyst)
    workflow.add_node("Publisher", run_publisher)

    # Define the strict deterministic flow
    # It must scrape -> analyze -> publish
    workflow.set_entry_point("Extractor")
    workflow.add_edge("Extractor", "Analyst")
    workflow.add_edge("Analyst", "Publisher")
    workflow.add_edge("Publisher", END)

    # Compile the graph into a runnable application
    return workflow.compile()

# ==========================================
# 4. THE AUTONOMOUS LOOP (BACKGROUND THREAD)
# ==========================================
def autonomous_agent_loop():
    """
    Runs continuously in a background thread.
    An authentic, self-directed scout that dynamically searches 
    the web for breaking news rather than spamming static homepages.
    """
    print("🚀 [Agentic Engine] Autonomous Discovery Loop Initialized.")
    agent_app = build_agent_graph()

    while True:
        try:
            print("\n🔄 [Agentic Engine] Initializing autonomous intelligence sweep...")
            
            # 🌐 TRUE AGENTIC ROUTING: We pass zero hardcoded homepages to eliminate brittle 401 blocks.
            # Instead, we give the agent a high-level directive to scour the live web for breaking news.
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

            # Execute the Graph
            final_state = agent_app.invoke(initial_state)
            
            print(f"✅ [Agentic Engine] Autonomous cycle complete. Publish Status: {final_state.get('publish_status')}")

        except Exception as e:
            print(f"⚠️ [Agentic Engine] Critical Execution Failure: {e}")

        # Sleep for 1 hour (3600 seconds) before the next autonomous patrol sweep
        print("💤 [Agentic Engine] Entering standby mode for 1 hour...")
        time.sleep(3600)

# ==========================================
# 5. STARTUP SCRIPT EXPORT
# ==========================================
def start_agent_daemon():
    """
    Called exactly once by app.py to spin up the background thread.
    """
    agent_thread = threading.Thread(target=autonomous_agent_loop, daemon=True)
    agent_thread.start()