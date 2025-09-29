# -*- coding: utf-8 -*-
from __future__ import annotations
import pandas as pd
import numpy as np
import yfinance as yf
"""
data.py

This module contains functionalities related to data pre/post processing and
ingestion for each feature within the application.

Notes:
    -
"""

"""
# Phase 2 (Aamir/Dalton)
### Data Acquisition, Preprocessing, Transformation & Validation

**Key Activities**
- Retrieve historical price data via yfinance API
- Remove non-trading dates, weekends, and duplicates
- Handle missing values and standardize date formats
- Transform data into analysis-ready structures (pivot tables, normalized series)
- Generate data-quality summary reports

**Deliverables**
- Analysis functions library
- Algorithm documentation
- Test results summary
"""

#Defining sectors and tickers
#Using a dictionary as it is easier to keep sector context, and can flatten into a list
# = to efficiency as can download
sectors = {
    "Tech": ["AAPL", "MSFT", "NVDA"],
    "Finance": ["JPM", "BAC", "MA"],
    "Healthcare": ["JNJ", "PFE", "ABBV"],
    "Consumer Goods": ["PEP", "MCD", "NKE"],
    "Energy": ["XOM", "SHEL", "CVX"],
}

#Flatten all tickers into a single list like ["AAPL", "MSFT", ...]
tickers = sum(sectors.values(), [])

#Quick sector lookup which allows to lookup like AAPL --> Tech etc..}
ticker_to_sector = {t: s for s, lst in sectors.items() for t in lst}

#Function for consistent logging
def log(msg: str):
    print(f"[INFO] {msg}")

#Setting helper Functions — Conditional Cleaning & Transforms
#these helpers check the data first, then change it only when needed.

#this checks that the index is timezone-naive DateTimeIndex and sorted ascending. If already is, wont be touching it
# def ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
#     needs_datetime = not isinstance(df.index, pd.DatetimeIndex)
#     needs_tz_strip = isinstance(df.index, pd.DatetimeIndex) and (df.index.tz is not None)
#     needs_sort = not df.index.is_monotonic_increasing

#     if needs_datetime:
#         log("Index is not DateTimeIndex → converting.")
#         df.index = pd.to_datetime(df.index)
#     if needs_tz_strip:
#         log("Index has timezone → stripping to tz-naive.")
#         df.index = df.index.tz_localize(None)
#     if needs_sort:
#         log("Index not sorted ascending → sorting.")
#         df = df.sort_index()

#     if not (needs_datetime or needs_tz_strip or needs_sort):
#         log("Index already clean DateTimeIndex and sorted.")
#     return df


#this drops duplicates (Date,Ticker) rows in the long table (prevents double counting)
def drop_dup_long(long_df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate (Date, Ticker) rows only if any exist."""
    dup_count = long_df.duplicated(subset=["Date", "Ticker"]).sum()
    if dup_count > 0:
        log(f"Found {dup_count} duplicate (Date,Ticker) rows → dropping.")
        long_df = long_df.drop_duplicates(subset=["Date", "Ticker"])
    else:
        log("No duplicate (Date,Ticker) rows.")
    return long_df

#Converts Date to datetime and keeps date-only, and sorts by (Ticker, Date)
def standardize_date_column(long_df: pd.DataFrame) -> pd.DataFrame:
    """Ensure 'Date' column is date-only and rows ordered by (Ticker, Date)."""
    if not pd.api.types.is_datetime64_any_dtype(long_df["Date"]):
        log("Converting 'Date' to datetime.")
        long_df["Date"] = pd.to_datetime(long_df["Date"])
    # Always keep only the date part (cheap and consistent)
    log("Stripping time component from 'Date'.")
    long_df["Date"] = long_df["Date"].dt.date

    #the sorting if needed
    sorted_df = long_df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
    if not sorted_df.index.equals(long_df.index):
        log("Sorting by ['Ticker','Date'].")
    return sorted_df

#Within each tickerm a forward-fill if there are NaNs. This prevents indicators from breaking without inventing values
def ffill_if_needed(long_df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    #Forward-fill missing values within each ticker only if there are NaNs.
    total_na = long_df[cols].isna().sum().sum()
    if total_na > 0:
        log(f"Missing values detected ({total_na}) in {cols} → forward-filling by ticker.")
        long_df[cols] = (
            long_df
            .sort_values(["Ticker", "Date"])
            .groupby("Ticker")[cols]
            .apply(lambda g: g.ffill())
            .reset_index(level=0, drop=True)
        )
    else:
        log(f"No missing values in {cols} → no forward-fill needed.")
    return long_df

#Within each ticker, linearly interpolates only price columns, only if NaNs remain
def interpolate_if_needed(long_df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    #Linear interpolation within each ticker, only if NaNs remain. (not for volume)
    remaining_na = long_df[cols].isna().sum().sum()
    if remaining_na > 0:
        log(f"{remaining_na} missing values remain in {cols} → linear interpolation.")
        long_df[cols] = (
            long_df
            .sort_values(["Ticker", "Date"])
            .groupby("Ticker")[cols]
            .apply(lambda g: g.interpolate(method="linear", limit_direction="forward"))
            .reset_index(level=0, drop=True)
        )
    else:
        log(f"No remaining missing values in {cols} → no interpolation needed.")
    return long_df

#pivots long to wide matrix (rows=Date, cols=Ticker) for given field, forward-fill if the pivot created gaps
def make_wide(field: str, long_df: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    #Pivot to wide matrix (rows=Date, cols=Ticker). Forward-fill only if needed.
    wide = long_df.pivot(index="Date", columns="Ticker", values=field).reindex(columns=tickers)
    na_after = wide.isna().sum().sum()
    if na_after > 0:
        log(f"[{field}] {na_after} NaNs after pivot → forward-filling down columns.")
        wide = wide.sort_index().ffill()
    else:
        log(f"[{field}] No NaNs after pivot.")
    return wide

# Outlier helpers (IQR)

def _iqr_bounds(series: pd.Series, k: float = 3.0) -> tuple[float, float]:
    """
    Compute lower/upper outlier fences using Tukey-style IQR bounds:
        lower = Q1 - k*IQR, upper = Q3 + k*IQR
    Default k=3.0 is stricter (fewer false positives) for financial data.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    return lower, upper


def compute_iqr_outlier_flags(long_df: pd.DataFrame, k: float = 3.0) -> dict[str, pd.DataFrame]:
    """
    Build two wide True/False matrices (rows=Date, cols=Ticker):
        - 'close_return_outliers': outliers on daily pct_change of Close
        - 'volume_outliers': outliers on Volume levels
    Flags only — data is not changed/deleted.
    """
    # Ensure we don't break if columns missing
    required_cols = {"Date", "Ticker", "Close", "Volume"}
    if not required_cols.issubset(long_df.columns):
        log(f"Missing columns for outlier computation; need {required_cols}. Skipping flags.")
        return {"close_return_outliers": pd.DataFrame(), "volume_outliers": pd.DataFrame()}

    # Work on a copy to avoid mutating the input
    df = long_df.copy()
    # Compute daily returns per ticker from Close
    df = df.sort_values(["Ticker", "Date"])
    df["Close_Return"] = df.groupby("Ticker")["Close"].pct_change()

    # -------- Close return outliers (IQR on returns per ticker) --------
    def flag_returns(g: pd.DataFrame) -> pd.Series:
        s = g["Close_Return"]
        # If all NaN or constant, no flags
        if s.dropna().empty:
            return pd.Series([False] * len(g), index=g.index)
        lower, upper = _iqr_bounds(s.dropna(), k=k)
        flags = (s < lower) | (s > upper)
        return flags.fillna(False)

    log(f"Computing IQR outliers on Close returns (k={k}).")
    close_flags = df.groupby("Ticker", group_keys=False).apply(flag_returns)
    df["Close_Return_Outlier"] = close_flags.values

    close_return_outliers = df.pivot(index="Date", columns="Ticker", values="Close_Return_Outlier").fillna(False)

    # -------- Volume outliers (IQR on volume per ticker) --------
    def flag_volume(g: pd.DataFrame) -> pd.Series:
        s = g["Volume"]
        if s.dropna().empty:
            return pd.Series([False] * len(g), index=g.index)
        lower, upper = _iqr_bounds(s.dropna(), k=k)
        flags = (s < lower) | (s > upper)
        return flags.fillna(False)

    log(f"Computing IQR outliers on Volume (k={k}).")
    vol_flags = df.groupby("Ticker", group_keys=False).apply(flag_volume)
    df["Volume_Outlier"] = vol_flags.values

    volume_outliers = df.pivot(index="Date", columns="Ticker", values="Volume_Outlier").fillna(False)

    return {
        "close_return_outliers": close_return_outliers,
        "volume_outliers": volume_outliers,
    }

# Core builder
# ------------------------------
def build_datasets(years: int = 3, iqr_k: float = 3.0) -> dict[str, pd.DataFrame]:
    """
    Main entrypoint to build all Phase-2 datasets.

    Returns a dict with:
        - 'long_df'
        - 'open_df', 'high_df', 'low_df', 'close_df', 'adjclose_df', 'volume_df'
        - 'close_return_outliers' (True/False wide matrix)
        - 'volume_outliers' (True/False wide matrix)
    """
    # 1) Download (Yahoo returns trading days)
    end = pd.Timestamp.today().normalize()
    start = end - pd.DateOffset(years=years)
    raw = yf.download(tickers, start=start, end=end, auto_adjust=False, group_by="ticker")

    # Ensure index is clean *only if needed*
   # raw = ensure_datetime_index(raw)

    # 2) Build long (tidy) table
    fields = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    long_rows: list[pd.DataFrame] = []

    for tkr in tickers:
        if tkr not in raw.columns.get_level_values(0):
            log(f"Ticker '{tkr}' missing in download → skipping.")
            continue

        df_t = raw[tkr].copy()
        df_t["Ticker"] = tkr
        df_t["Date"] = df_t.index
        df_t = df_t[["Date", "Ticker"] + fields]
        long_rows.append(df_t.reset_index(drop=True))

    long_df = pd.concat(long_rows, ignore_index=True)
    log(f"Long table built: {long_df.shape[0]} rows × {long_df.shape[1]} cols.")

    # 3) Conditional cleaning
    long_df = drop_dup_long(long_df)
    long_df = standardize_date_column(long_df)

    numeric_cols = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    price_cols   = ["Open", "High", "Low", "Close", "Adj Close"]

    long_df = ffill_if_needed(long_df, numeric_cols)      # ffill prices + volume
    long_df = interpolate_if_needed(long_df, price_cols)  # interpolate prices only

    # 4) Transform → wide matrices (only fill if needed)
    open_df     = make_wide("Open",       long_df, tickers)
    high_df     = make_wide("High",       long_df, tickers)
    low_df      = make_wide("Low",        long_df, tickers)
    close_df    = make_wide("Close",      long_df, tickers)
    adjclose_df = make_wide("Adj Close",  long_df, tickers)
    volume_df   = make_wide("Volume",     long_df, tickers)

    # 5) IQR Outlier flags (Close returns + Volume)
    flags = compute_iqr_outlier_flags(long_df, k=iqr_k)
    close_return_outliers = flags["close_return_outliers"]
    volume_outliers = flags["volume_outliers"]

    return {
        "long_df": long_df,
        "open_df": open_df,
        "high_df": high_df,
        "low_df": low_df,
        "close_df": close_df,
        "adjclose_df": adjclose_df,
        "volume_df": volume_df,
        "close_return_outliers": close_return_outliers,
        "volume_outliers": volume_outliers,
    }

# ------------------------------
# Quick check for outlier DataFrames
# ------------------------------
def quick_check_outliers(df: pd.DataFrame, name: str, n: int = 5) -> None:
    """
    Print basic info and head for an outlier DataFrame (True/False matrix).
    Shows shape, total flagged outliers, and first n rows.
    """
    if df.empty:
        log(f"{name}: EMPTY DataFrame.")
        return
    r, c = df.shape
    total_flags = int(df.values.sum())  # count True values
    log(f"{name}: shape={r}×{c} | total outliers flagged={total_flags}")
    print(df.head(n))

if __name__ == "__main__":
    datasets = build_datasets(years=3, iqr_k=3.0)

    # Quick check for core matrices
    for key in ["open_df", "high_df", "low_df", "close_df", "adjclose_df", "volume_df"]:
        quick_check_outliers(datasets[key], key)  # reuses logger style

    # Specific check for outlier matrices
    quick_check_outliers(datasets["close_return_outliers"], "close_return_outliers")
    quick_check_outliers(datasets["volume_outliers"], "volume_outliers")