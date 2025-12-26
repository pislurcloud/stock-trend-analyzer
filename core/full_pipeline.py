from core.analytics_pipeline import run_trend_analysis
from llm.adapters import build_llm_state
from llm.graph import build_llm_graph


def run_full_analysis(ticker: str, years: int = 10) -> dict:
    """
    Orchestrates analytics + LLM narrative generation.

    Fails fast if analytics cannot be computed.
    """

    # -----------------------------
    # Run deterministic analytics
    # -----------------------------
    analytics = run_trend_analysis(ticker, years)

    if analytics is None:
        raise RuntimeError(
            f"Trend analysis failed for ticker {ticker}"
        )

    # -----------------------------
    # Build LLM state
    # -----------------------------
    llm_state = build_llm_state(analytics)

    # -----------------------------
    # Run LangGraph
    # -----------------------------
    graph = build_llm_graph()
    final_state = graph.invoke(llm_state)

    return final_state
