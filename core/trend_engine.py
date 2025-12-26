import pandas as pd
import numpy as np
from typing import List, Dict
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression


# -----------------------------
# Data contracts
# -----------------------------

@dataclass
class TrendWindowResult:
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    trend_score: float
    trend_label: str
    confidence: float
    direction_score: float
    structure_score: float
    volatility_score: float


# -----------------------------
# Scoring helpers
# -----------------------------

def _direction_score(prices: pd.Series) -> float:
    """
    Direction score based on normalized linear regression slope.
    Returns score in range [0, 40]
    """
    y = prices.values.reshape(-1, 1)
    x = np.arange(len(y)).reshape(-1, 1)

    model = LinearRegression().fit(x, y)
    slope = model.coef_[0][0]

    price_range = prices.max() - prices.min()
    if price_range == 0:
        return 20.0  # neutral

    normalized_slope = slope / price_range

    if normalized_slope > 0.15:
        return 40.0
    elif normalized_slope > 0.05:
        return 30.0
    elif normalized_slope > -0.05:
        return 20.0
    elif normalized_slope > -0.15:
        return 10.0
    else:
        return 0.0


def _structure_score(prices: pd.Series) -> float:
    """
    Structure score based on HH/HL behavior and MA stability.
    Returns score in range [0, 40]
    """
    score = 0.0

    # --- Higher highs / higher lows ---
    highs = prices.rolling(3).max()
    lows = prices.rolling(3).min()

    hh = (highs.diff() > 0).mean()
    hl = (lows.diff() > 0).mean()
    structure_ratio = np.nanmean([hh, hl])

    if structure_ratio > 0.7:
        score += 13
    elif structure_ratio > 0.5:
        score += 8
    else:
        score += 3

    # --- Moving averages ---
    ma_50 = prices.rolling(50).mean()
    ma_200 = prices.rolling(200).mean()

    above_50 = (prices > ma_50).mean()
    above_200 = (prices > ma_200).mean()

    if above_50 > 0.7 and above_200 > 0.7:
        score += 13
    elif above_50 > 0.7:
        score += 8
    else:
        score += 3

    # --- MA stability ---
    crossovers = ((ma_50 > ma_200).astype(int).diff().abs() == 1).sum()

    if crossovers <= 1:
        score += 13
    elif crossovers <= 3:
        score += 8
    else:
        score += 3

    return float(score)


def _volatility_score(prices: pd.Series) -> float:
    """
    Volatility context score.
    Returns score in range [0, 20]
    """
    returns = prices.pct_change().dropna()
    vol = returns.std()

    price_change = prices.iloc[-1] - prices.iloc[0]

    if price_change > 0 and vol < returns.mean() * 2:
        return 20.0
    elif price_change > 0:
        return 15.0
    elif abs(price_change) < prices.std():
        return 8.0
    else:
        return 0.0


def _trend_label(score: float) -> str:
    if score >= 70:
        return "UPTREND"
    elif score >= 40:
        return "SIDEWAYS"
    else:
        return "DOWNTREND"


def _confidence(score: float) -> float:
    """
    Simple confidence proxy based on distance from regime boundaries.
    """
    if score >= 70:
        return min(100.0, 60 + (score - 70))
    elif score >= 40:
        return 50.0
    else:
        return max(20.0, score)


# -----------------------------
# Public API
# -----------------------------

def compute_trend_windows(
    weekly_df: pd.DataFrame,
    price_col: str = "close",
    window_months: int = 12,
    step_months: int = 3
) -> List[Dict]:
    """
    Compute rolling trend regimes from weekly price data.

    weekly_df:
        DateTimeIndex
        must contain `price_col`
    """

    results = []

    weeks_per_month = 4
    window_size = window_months * weeks_per_month
    step_size = step_months * weeks_per_month

    prices = weekly_df[price_col].dropna()

    for start in range(0, len(prices) - window_size, step_size):
        window_prices = prices.iloc[start:start + window_size]
        if len(window_prices) < window_size:
            continue

        d_score = _direction_score(window_prices)
        s_score = _structure_score(window_prices)
        v_score = _volatility_score(window_prices)

        total_score = d_score + s_score + v_score
        label = _trend_label(total_score)
        confidence = _confidence(total_score)

        results.append({
            "start_date": window_prices.index[0],
            "end_date": window_prices.index[-1],
            "trend_score": round(total_score, 2),
            "trend_label": label,
            "confidence": round(confidence, 2),
            "direction_score": round(d_score, 2),
            "structure_score": round(s_score, 2),
            "volatility_score": round(v_score, 2),
        })

    return results
