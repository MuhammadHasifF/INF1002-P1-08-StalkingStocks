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


# ============================================================
# 1. SIMPLE MOVING AVERAGE (SMA)
# ============================================================
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


# ============================================================
# 2. TREND RUNS (UP/DOWN STREAKS)
# ============================================================
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


# ============================================================
# 3. DAILY RETURNS
# ============================================================
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


# ============================================================
# 4. MAX PROFIT (BEST TIME II — SUM OF RISES)
# ============================================================
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


# ============================================================
# --- EXTRA HELPERS (manual only, not in main tests) ---
# ============================================================

def extract_trades_for_ticker_manual(rows: list[dict], ticker: str) -> list[dict]:
    """
    For one ticker:
      - Buy just before a rise
      - Sell at the peak (before drop or last day)
    Returns list of trades.
    """
    g = [r for r in rows if r["Ticker"] == ticker]
    g = sorted(g, key=lambda r: r["Date"])

    trades = []
    holding = False
    buy_date = buy_price = None

    for i in range(1, len(g)):
        prev_p, cur_p = g[i - 1]["Close"], g[i]["Close"]
        prev_d, cur_d = g[i - 1]["Date"], g[i]["Date"]

        if not holding and cur_p > prev_p:
            holding = True
            buy_date, buy_price = prev_d, prev_p

        is_last = (i == len(g) - 1)
        next_drop_or_end = (cur_p > prev_p and (is_last or g[i + 1]["Close"] < cur_p))

        if holding and next_drop_or_end:
            trades.append({
                "Ticker": ticker,
                "buy_date": buy_date,
                "buy_price": buy_price,
                "sell_date": cur_d,
                "sell_price": cur_p,
                "profit": cur_p - buy_price
            })
            holding = False

    return trades


def trades_for_all_manual(rows: list[dict]) -> list[dict]:
    """
    Collect trades for all tickers manually.
    Returns list of trades across all tickers.
    """
    tickers = sorted(set(r["Ticker"] for r in rows))
    out = []
    for tkr in tickers:
        out.extend(extract_trades_for_ticker_manual(rows, tkr))
    return out


def max_profit_summary_manual(rows: list[dict]) -> list[dict]:
    """
    Summarise max profit (sum of rises) per ticker manually.
    Returns sorted list of dicts.
    """
    tickers = sorted(set(r["Ticker"] for r in rows))
    out = []
    for tkr in tickers:
        trades = extract_trades_for_ticker_manual(rows, tkr)
        total = sum(t["profit"] for t in trades)
        out.append({"Ticker": tkr, "Max_Profit": total})

    out.sort(key=lambda x: x["Max_Profit"], reverse=True)
    return out

# ------------------------------------------------------------------
# NOTE: These helpers (`extract_trades_for_ticker`, `trades_for_all`,
#       and `max_profit_summary`) are not used in automated tests.
#       They are provided for application-level use cases such as:
#           - Plotting buy/sell markers on price charts
#           - Showing per-ticker trade history
#           - Ranking tickers by profit potential
# ------------------------------------------------------------------