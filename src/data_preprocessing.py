from __future__ import annotations

import numpy as np
import pandas as pd


def load_brent_data(filepath: str = "data/raw/BrentOilPrices.csv") -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%y", errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

    if df["Price"].isna().any():
        df["Price"] = df["Price"].interpolate(method="linear")

    return df


def calculate_returns(df: pd.DataFrame, price_col: str = "Price") -> pd.DataFrame:
    out = df.copy()
    out["Returns"] = out[price_col].pct_change()
    out["Log_Returns"] = np.log(out[price_col]) - np.log(out[price_col].shift(1))
    return out.dropna().reset_index(drop=True)


def load_events_data(filepath: str = "data/events/key_events.csv") -> pd.DataFrame:
    events = pd.read_csv(filepath)
    events["Date"] = pd.to_datetime(events["Date"], errors="coerce")
    return events.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)


def test_stationarity(series: pd.Series) -> dict:
    from statsmodels.tsa.stattools import adfuller

    result = adfuller(series.dropna())
    return {
        "adf_stat": float(result[0]),
        "p_value": float(result[1]),
        "is_stationary": bool(result[1] < 0.05),
    }
