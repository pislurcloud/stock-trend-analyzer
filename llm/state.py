from typing import TypedDict, Dict, List, Optional


class AnalysisState(TypedDict):
    """
    Canonical LangGraph state.

    Deterministic analytics populate the top section.
    LLM agents ONLY read analytics fields and write their own outputs.
    """

    # -----------------------------
    # Identifiers
    # -----------------------------
    ticker: str
    analysis_period: str

    # -----------------------------
    # Deterministic analytics
    # -----------------------------
    dominant_trend: str
    trend_confidence: float
    trend_distribution: Dict[str, float]
    recent_trend: str

    cagr: float
    price_multiple: float

    best_year: Optional[int]
    worst_year: Optional[int]
    volatility_summary: str
    red_flags: List[str]

    benchmark_comparison: Dict[str, str]

    # -----------------------------
    # LLM agent outputs
    # -----------------------------
    exec_summary: Optional[str]
    trend_explanation: Optional[str]
    risk_analysis: Optional[str]
    benchmark_analysis: Optional[str]
    final_narrative: Optional[str]
