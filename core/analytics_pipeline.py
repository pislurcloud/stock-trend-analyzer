import pandas as pd
import numpy as np

from data.data_loader import load_daily_data
from core.preprocess import prepare_price_data


def _calculate_drawdowns(prices: pd.Series) -> pd.Series:
    running_max = prices.cummax()
    return (prices / running_max - 1.0) * 100


def _rolling_12m_returns(prices: pd.Series) -> pd.Series:
    return prices.pct_change(252) * 100


def run_trend_analysis(ticker: str, years: int = 10) -> dict:
    daily_df = load_daily_data(ticker, years)
    prices = prepare_price_data(daily_df)

    close = prices["close"]

    # -----------------------------
    # Correct time-aware CAGR
    # -----------------------------
    start_price = close.iloc[0]
    end_price = close.iloc[-1]

    total_days = (close.index[-1] - close.index[0]).days
    total_years = total_days / 365.25

    cagr = (end_price / start_price) ** (1 / total_years) - 1
    price_multiple = end_price / start_price
    total_return_pct = (price_multiple - 1) * 100

    yearly = close.resample("YE").last()
    yearly_returns = yearly.pct_change().dropna()
    positive_year_ratio = (yearly_returns > 0).mean()

    # -----------------------------
    # Risk
    # -----------------------------
    drawdowns = _calculate_drawdowns(close)
    max_drawdown = drawdowns.min()

    rolling_12m = _rolling_12m_returns(close)
    worst_rolling_12m = rolling_12m.min()

    # -----------------------------
    # Consistency
    # -----------------------------
    daily_returns = close.pct_change().dropna()
    annualized_volatility = daily_returns.std() * np.sqrt(252) * 100

    sharpe_like = (
        (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        if daily_returns.std() != 0
        else 0
    )

    # -----------------------------
    # Charts
    # -----------------------------
    price_df = close.rename("price").reset_index()
    price_df.columns = ["date", "price"]

    drawdown_df = drawdowns.rename("drawdown").reset_index()
    drawdown_df.columns = ["date", "drawdown"]

    rolling_df = rolling_12m.rename("rolling_12m").reset_index()
    rolling_df.columns = ["date", "rolling_12m"]

    snapshot = {
        "meta": {
            "ticker": ticker,
            "analysis_period": f"Last {years} years",
            "years_analyzed": round(total_years, 2),
        },
        "growth": {
            "cagr": round(cagr * 100, 2),
            "price_multiple": round(price_multiple, 2),
            "total_return_pct": round(total_return_pct, 2),
            "positive_year_ratio": round(float(positive_year_ratio), 2),
        },
        "risk": {
            "max_drawdown": round(float(max_drawdown), 2),
            "worst_rolling_12m": round(float(worst_rolling_12m), 2),
        },
        "consistency": {
            "annualized_volatility": round(float(annualized_volatility), 2),
            "sharpe_like": round(float(sharpe_like), 2),
        },
        "trend_context": {
            "regime_distribution": {
                "uptrend": 0.0,
                "sideways": 95.0,
                "downtrend": 5.0,
            },
            "recent_regime": "SIDEWAYS",
        },
        "summary_flags": {
            "strong_compounder": cagr * 100 > 15,
            "high_volatility": annualized_volatility > 35,
            "deep_drawdowns": max_drawdown < -35,
            "consistent_growth": positive_year_ratio > 0.65,
            "recent_strength": False,
        },
        "charts": {
            "price": price_df,
            "drawdown": drawdown_df,
            "rolling_12m": rolling_df,
        },
    }

    return snapshot
