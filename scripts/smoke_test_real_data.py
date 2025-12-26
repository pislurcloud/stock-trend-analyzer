from core.analytics_pipeline import run_trend_analysis
#from workspaces.stock-trend-analyzer.core.analytics_pipeline import run_trend_analysis

if __name__ == "__main__":
    result = run_trend_analysis("AAPL", years=10)

    print("Ticker:", result["ticker"])
    print("Dominant Trend:", result["dominant_trend"])
    print("Recent Trend:", result["recent_trend"])
    print("Confidence:", result["confidence"])
    print("Total Windows:", len(result["trend_windows"]))
