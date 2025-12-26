from core.trend_engine import compute_trend_windows
from tests.synthetic_data import (
    synthetic_uptrend,
    synthetic_downtrend,
    synthetic_sideways,
)


def test_uptrend_detected():
    df = synthetic_uptrend()
    windows = compute_trend_windows(df)

    assert windows
    assert windows[-1]["trend_label"] == "UPTREND"
    assert windows[-1]["confidence"] >= 60


def test_downtrend_detected():
    df = synthetic_downtrend()
    windows = compute_trend_windows(df)

    assert windows
    assert windows[-1]["trend_label"] == "DOWNTREND"


def test_sideways_not_uptrend():
    df = synthetic_sideways()
    windows = compute_trend_windows(df)

    assert windows
    assert all(w["trend_label"] != "UPTREND" for w in windows)
