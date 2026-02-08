# fmt: off
"""Time series utilities for Brent oil analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd


def load_brent_prices(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y", errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    df["Price"] = df["Price"].interpolate(method="linear")
    return df


def add_log_returns(df: pd.DataFrame, price_col: str = "Price") -> pd.DataFrame:
    out = df.copy()
    out["Log_Returns"] = np.log(out[price_col]) - np.log(out[price_col].shift(1))
    return out.dropna().reset_index(drop=True)


def rolling_volatility(series: pd.Series, window: int = 30) -> pd.Series:
    return series.rolling(window=window).std()


def adf_test(series: pd.Series) -> dict:
    from statsmodels.tsa.stattools import adfuller

    stat, p_value, *_ = adfuller(series.dropna())
    return {
        "adf_stat": float(stat),
        "p_value": float(p_value),
        "is_stationary": p_value < 0.05,
    }
# fmt: on
