from langgraph.graph import StateGraph, END

from llm.state import AnalysisState

# Agent implementations
from llm.agents.exec_summary import exec_summary_agent
from llm.agents.trend_explanation import trend_explanation_agent
from llm.agents.risk_flags import risk_flags_agent
from llm.agents.benchmark import benchmark_agent
from llm.agents.final_narrative import final_narrative_agent

# Optional lightweight observability wrapper
from llm.observability import log_node_execution


def build_llm_graph():
    """
    Builds and compiles the LangGraph DAG for narrative generation.

    Topology:
    - Exec Summary runs first (acts as gate)
    - Trend / Risk / Benchmark agents run in parallel
    - Final Narrative agent consolidates outputs
    """

    graph = StateGraph(AnalysisState)

    # -----------------------------
    # Agent nodes (wrapped for logging)
    # -----------------------------
    graph.add_node(
        "exec_summary",
        log_node_execution("exec_summary", exec_summary_agent)
    )

    graph.add_node(
        "trend_explanation",
        log_node_execution("trend_explanation", trend_explanation_agent)
    )

    graph.add_node(
        "risk_flags",
        log_node_execution("risk_flags", risk_flags_agent)
    )

    graph.add_node(
        "benchmark",
        log_node_execution("benchmark", benchmark_agent)
    )

    graph.add_node(
        "final_narrative",
        log_node_execution("final_narrative", final_narrative_agent)
    )

    # -----------------------------
    # Graph structure
    # -----------------------------

    # Entry point
    graph.set_entry_point("exec_summary")

    # Parallel fan-out
    graph.add_edge("exec_summary", "trend_explanation")
    graph.add_edge("exec_summary", "risk_flags")
    graph.add_edge("exec_summary", "benchmark")

    # Fan-in to consolidator
    graph.add_edge("trend_explanation", "final_narrative")
    graph.add_edge("risk_flags", "final_narrative")
    graph.add_edge("benchmark", "final_narrative")

    # Exit
    graph.add_edge("final_narrative", END)

    # -----------------------------
    # Compile graph
    # -----------------------------
    return graph.compile()
