import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# Import agent entrypoints
from agents.analyzer_agent import main as analyzer_main
from agents.architect_agent import main as architect_main
from agents.matcher_agent import main as matcher_main
from rag.rag_matcher_agent import match_project_to_employees
from agents.notifier_agent import main as notifier_main

# ---------------------------------------------------------------------
# Define State Schema (shared data between nodes)
# ---------------------------------------------------------------------
class SmartBenchState(TypedDict, total=False):
    """Defines workflow state passed between nodes."""
    messages: list
    analyzer_status: str
    architect_status: str
    matcher_status: str
    rag_status: str
    notifier_status: str


# ---------------------------------------------------------------------
# Define Each Node Function (simple Python functions, no @tool)
# ---------------------------------------------------------------------
def AnalyzerNode(state: SmartBenchState):
    print("\n🧠 [Analyzer Node] Starting...")
    analyzer_main()
    print("✅ [Analyzer Node] Done.")
    return {"analyzer_status": "completed"}

def ArchitectNode(state: SmartBenchState):
    print("\n🏗️ [Architect Node] Starting...")
    architect_main()
    print("✅ [Architect Node] Done.")
    return {"architect_status": "completed"}

def MatcherNode(state: SmartBenchState):
    print("\n⚙️ [Rule-based Matcher Node] Starting...")
    matcher_main()
    print("✅ [Matcher Node] Done.")
    return {"matcher_status": "completed"}

def RAGMatcherNode(state: SmartBenchState):
    print("\n🔍 [RAG Matcher Node] Starting...")
    match_project_to_employees(top_n=5)
    print("✅ [RAG Matcher Node] Done.")
    return {"rag_status": "completed"}

def NotifierNode(state: SmartBenchState):
    print("\n📨 [Notifier Node] Starting...")
    notifier_main()
    print("✅ [Notifier Node] Done.")
    return {"notifier_status": "completed"}


# ---------------------------------------------------------------------
# Build Graph Structure
# ---------------------------------------------------------------------
graph = StateGraph(SmartBenchState)

graph.add_node("Analyzer", AnalyzerNode)
graph.add_node("Architect", ArchitectNode)
graph.add_node("Matcher", MatcherNode)
graph.add_node("RAG_Matcher", RAGMatcherNode)
graph.add_node("Notifier", NotifierNode)

graph.add_edge(START, "Analyzer")
graph.add_edge("Analyzer", "Architect")
graph.add_edge("Architect", "Matcher")
graph.add_edge("Matcher", "RAG_Matcher")
graph.add_edge("RAG_Matcher", "Notifier")
graph.add_edge("Notifier", END)

workflow = graph.compile()

# ---------------------------------------------------------------------
# Run Workflow
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting SmartBench Workflow (Tool-free LangGraph)...\n")

    # initial shared state
    initial_state = {
        "messages": [{"role": "user", "content": "Start SmartBench workflow"}]
    }

    result = workflow.invoke(initial_state)

    print("\n✅ SmartBench Workflow Completed Successfully.")
    print("\n📊 Final State:")
    print(result)
