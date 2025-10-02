"""
core.py

Manual (pure Python) implementations for:
    - Simple Moving Average (SMA)
    - Streaks (trend runs)
    - Daily Returns
    - Max Profit (Best Time II rule)

Extras:
    - Helper functions for trade extraction, trades for all tickers,
      and profit summaries (all manual).
    - These are *not* part of the main test pipeline but can be used
      in notebooks, Streamlit, or further analysis.

Notes:
    - All computation is done with plain Python.
    - Pandas is only used for input/output compatibility.
"""

import pandas as pd
from ..utils.helpers import timer


# computing SMA
@timer
def compute_sma(close: pd.Series, window: int = 5) -> pd.Series:
    """
    Compute simple moving averages (SMAs) manually.
    Args:
        close (pd.Series): closing prices
        window (int): window size
    Returns:
        pd.Series of SMA values (NaN where insufficient data)
    """
    values = close.tolist()
    n = len(values)
    out = [None] * n

    if window <= 0 or n == 0:
        return pd.Series(out, index=close.index)

    running_sum = 0.0
    for i, v in enumerate(values):
        running_sum += float(v)
        if i >= window:
            running_sum -= float(values[i - window])
        if i >= window - 1:
            out[i] = running_sum / window

    return pd.Series(out, index=close.index)


# computing trend runs (up/down streaks)
@timer
def compute_streak(close: pd.Series) -> tuple[int, int]:
    """
    Compute longest upward and downward streaks manually.
    Args:
        close (pd.Series): closing prices
    Returns:
        (longest_up, longest_down) as tuple[int, int]
    """
    values = close.tolist()
    dirs = [0]
    for i in range(1, len(values)):
        if values[i] > values[i - 1]:
            dirs.append(1)
        elif values[i] < values[i - 1]:
            dirs.append(-1)
        else:
            dirs.append(0)

    runs = []
    current_dir, run_len = 0, 0
    for d in dirs:
        if d == current_dir and d != 0:
            run_len += 1
        else:
            if current_dir != 0:
                runs.append((current_dir, run_len))
            current_dir = d
            run_len = 1 if d != 0 else 0
    if current_dir != 0:
        runs.append((current_dir, run_len))

    up_runs = [r[1] for r in runs if r[0] == 1]
    down_runs = [r[1] for r in runs if r[0] == -1]

    return (max(up_runs) if up_runs else 0,
            max(down_runs) if down_runs else 0)


# daily returns
@timer
def compute_sdr(close: pd.Series) -> pd.Series:
    """
    Compute daily returns manually.
    Formula: (P_t - P_{t-1}) / P_{t-1}
    Args:
        close (pd.Series): closing prices
    Returns:
        pd.Series of daily returns
    """
    values = close.tolist()
    out = [None]
    for i in range(1, len(values)):
        prev, curr = values[i - 1], values[i]
        out.append((curr - prev) / prev if prev else None)

    return pd.Series(out, index=close.index)


# Max profit
@timer
def compute_max_profit(close: pd.Series) -> float:
    """
    Compute max profit (sum of rises) manually.
    Args:
        close (pd.Series): closing prices
    Returns:
        float total profit
    """
    values = close.tolist()
    profit = 0.0
    for i in range(len(values) - 1):
        if values[i + 1] > values[i]:
            profit += values[i + 1] - values[i]
    return float(profit)
