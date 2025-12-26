import yfinance as yf
import pandas as pd


def load_daily_data(ticker: str, years: int) -> pd.DataFrame:
    """
    Load daily price data using yfinance.

    - Uses auto_adjust=True to ensure prices are split-adjusted
    - Returns Open, High, Low, Close (all adjusted)
    """

    period = f"{years}y"

    df = yf.download(
        ticker,
        period=period,
        auto_adjust=True,
        progress=False,
    )

    if df.empty:
        raise ValueError(f"No data returned for ticker {ticker}")

    # Flatten MultiIndex if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })

    return df
