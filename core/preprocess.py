import pandas as pd


def prepare_price_data(daily_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare daily price data for analytics.

    All prices are already adjusted for splits and dividends.
    """

    df = daily_df.copy()

    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    required_cols = ["open", "high", "low", "close"]
    df = df[required_cols]

    df = df.sort_index()

    return df
