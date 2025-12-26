from core.analytics_pipeline import run_trend_analysis


def test_aapl_like_compounder():
    result = run_trend_analysis("AAPL", years=10)

    assert result["price_multiple"] >= 3
    assert result["cagr"] >= 10
    assert result["dominant_trend"] == "UPTREND"


def test_strong_compounder():
    result = run_trend_analysis("NVDA", years=10)

    assert result["price_multiple"] >= 5
    assert result["cagr"] >= 15
    assert result["dominant_trend"] == "UPTREND"
    assert result["confidence"] >= 70


def test_true_sideways_stock():
    result = run_trend_analysis("GE", years=10)

    assert result["price_multiple"] < 2
    assert result["dominant_trend"] == "SIDEWAYS"
