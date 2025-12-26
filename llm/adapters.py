from llm.state import AnalysisState


def build_llm_state(
    analytics_result: dict,
    benchmark_result: dict | None = None
) -> AnalysisState:
    return {
        "ticker": analytics_result["ticker"],
        "analysis_period": analytics_result["period"],

        "dominant_trend": analytics_result["dominant_trend"],
        "trend_confidence": analytics_result["confidence"],
        "trend_distribution": analytics_result["trend_distribution"],
        "recent_trend": analytics_result["recent_trend"],

        "cagr": analytics_result["cagr"],
        "price_multiple": analytics_result["price_multiple"],

        "best_year": analytics_result.get("best_year"),
        "worst_year": analytics_result.get("worst_year"),
        "volatility_summary": analytics_result["volatility_summary"],
        "red_flags": analytics_result["red_flags"],

        "benchmark_comparison": benchmark_result or {
            "vs_index": "Not evaluated",
            "vs_sector": "Not evaluated",
        },

        "exec_summary": None,
        "trend_explanation": None,
        "risk_analysis": None,
        "benchmark_analysis": None,
        "final_narrative": None,
    }
