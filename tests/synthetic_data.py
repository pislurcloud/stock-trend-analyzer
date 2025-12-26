import pandas as pd
import numpy as np


def synthetic_uptrend(n_weeks=260):
    dates = pd.date_range("2015-01-01", periods=n_weeks, freq="W")
    prices = np.linspace(50, 150, n_weeks)
    return pd.DataFrame({"close": prices}, index=dates)


def synthetic_downtrend(n_weeks=260):
    dates = pd.date_range("2015-01-01", periods=n_weeks, freq="W")
    prices = np.linspace(150, 50, n_weeks)
    return pd.DataFrame({"close": prices}, index=dates)


def synthetic_sideways(n_weeks=260):
    dates = pd.date_range("2015-01-01", periods=n_weeks, freq="W")
    prices = np.random.normal(100, 2, n_weeks)
    return pd.DataFrame({"close": prices}, index=dates)
