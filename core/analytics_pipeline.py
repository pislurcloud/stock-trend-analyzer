import pandas as pd
import numpy as np

from data.data_loader import load_daily_data
from core.preprocess import prepare_price_data


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _calculate_drawdowns(prices: pd.Series) -> pd.Series:
    running_max = prices.cummax()
    return (prices / running_max - 1.0) * 100


def _rolling_12m_returns(prices: pd.Series) -> pd.Series:
    return prices.pct_change(252) * 100


def _compute_metrics(close: pd.Series) -> dict:
    start_price = close.iloc[0]
    end_price = close.iloc[-1]

    total_days = (close.index[-1] - close.index[0]).days
    total_years = total_days / 365.25

    cagr = (end_price / start_price) ** (1 / total_years) - 1
    price_multiple = end_price / start_price
    total_return_pct = (price_multiple - 1) * 100

    daily_returns = close.pct_change().dropna()
    annualized_volatility = daily_returns.std() * np.sqrt(252) * 100

    drawdowns = _calculate_drawdowns(close)
    max_drawdown = drawdowns.min()

    return {
        "cagr": round(cagr * 100, 2),
        "price_multiple": round(price_multiple, 2),
        "total_return_pct": round(total_return_pct, 2),
        "annualized_volatility": round(float(annualized_volatility), 2),
        "max_drawdown": round(float(max_drawdown), 2),
        "years": round(total_years, 2),
    }


# -------------------------------------------------
# Main analytics pipeline
# -------------------------------------------------
def run_trend_analysis(ticker: str, years: int = 10) -> dict:
    # -----------------------------
    # Load stock data
    # -----------------------------
    stock_df = load_daily_data(ticker, years)
    stock_prices = prepare_price_data(stock_df)
    stock_close = stock_prices["close"]

    stock_metrics = _compute_metrics(stock_close)

    yearly = stock_close.resample("YE").last()
    yearly_returns = yearly.pct_change().dropna()
    positive_year_ratio = (yearly_returns > 0).mean()

    rolling_12m = _rolling_12m_returns(stock_close)
    worst_rolling_12m = rolling_12m.min()

    # -----------------------------
    # Select benchmark
    # -----------------------------
    if ticker.endswith(".NS"):
        benchmark_ticker = "^NSEI"
    else:
        benchmark_ticker = "^GSPC"

    bench_df = load_daily_data(benchmark_ticker, years)
    bench_prices = prepare_price_data(bench_df)
    bench_close = bench_prices["close"]

    benchmark_metrics = _compute_metrics(bench_close)

    # -----------------------------
    # Charts (stock only for MVP)
    # -----------------------------
    price_df = stock_close.rename("price").reset_index()
    price_df.columns = ["date", "price"]

    drawdown_df = _calculate_drawdowns(stock_close).rename("drawdown").reset_index()
    drawdown_df.columns = ["date", "drawdown"]

    rolling_df = rolling_12m.rename("rolling_12m").reset_index()
    rolling_df.columns = ["date", "rolling_12m"]

    # -----------------------------
    # Final snapshot
    # -----------------------------
    snapshot = {
        "meta": {
            "ticker": ticker,
            "benchmark": benchmark_ticker,
            "analysis_period": f"Last {years} years",
        },
        "growth": {
            "cagr": stock_metrics["cagr"],
            "price_multiple": stock_metrics["price_multiple"],
            "total_return_pct": stock_metrics["total_return_pct"],
            "positive_year_ratio": round(float(positive_year_ratio), 2),
        },
        "risk": {
            "max_drawdown": stock_metrics["max_drawdown"],
            "worst_rolling_12m": round(float(worst_rolling_12m), 2),
        },
        "consistency": {
            "annualized_volatility": stock_metrics["annualized_volatility"],
        },
        "benchmark": benchmark_metrics,
        "summary_flags": {
            "outperformed_benchmark": stock_metrics["cagr"] > benchmark_metrics["cagr"],
            "higher_volatility_than_benchmark": (
                stock_metrics["annualized_volatility"]
                > benchmark_metrics["annualized_volatility"]
            ),
        },
        "charts": {
            "price": price_df,
            "drawdown": drawdown_df,
            "rolling_12m": rolling_df,
        },
    }

    return snapshot
