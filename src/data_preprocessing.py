from __future__ import annotations

from pathlib import Path

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


def load_brent_data(path):
    p = Path(path)
    if p.exists():
        df = pd.read_csv(p, parse_dates=["Date"], infer_datetime_format=True)
        # normalize column names
        if "Price" not in df.columns:
            # try a common alternative
            possible = [c for c in df.columns if "price" in c.lower()]
            if possible:
                df = df.rename(columns={possible[0]: "Price"})
        df = df[["Date", "Price"]].dropna()
        df = df.sort_values("Date").reset_index(drop=True)
        return df
    # fallback: create small sample
    dates = pd.date_range(start="2000-01-01", end="2020-12-31", freq="D")
    prices = 50 + np.cumsum(np.random.randn(len(dates)) * 0.1)
    return pd.DataFrame({"Date": dates, "Price": prices})
