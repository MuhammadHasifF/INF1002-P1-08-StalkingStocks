# tests/test_core.py
'''py -m tests.test_core'''
import os
import sys

# --- Ensure repo root is in sys.path ---
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.append(repo_root)

# --- Import dataset builder + core functions ---
from app.services import data
from app.services.core import (
    compute_sma_manual,
    compute_trend_runs_manual,
    add_daily_returns_manual,
    trades_for_all_manual,
    max_profit_summary_manual,
)

# --- Load dataset using data.py ---
datasets = data.build_datasets(years=1, iqr_k=3.0)
long_df = datasets["long_df"]


# === TESTS ===

def test_sma():
    print("\n=== Testing SMA Manual ===")
    closes = long_df[long_df["Ticker"] == "AAPL"]["Close"].tolist()[:10]
    sma5 = compute_sma_manual(closes, 5)
    print("Close prices:", closes)
    print("SMA(5):", sma5)


def test_trend_runs():
    print("\n=== Testing Trend Runs Manual ===")
    rows = long_df.to_dict("records")
    summary = compute_trend_runs_manual(rows)
    print("Trend run summary (first 5):", summary[:5])


def test_daily_returns():
    print("\n=== Testing Daily Returns Manual ===")
    rows = long_df.to_dict("records")
    out = add_daily_returns_manual(rows)
    print("Daily returns (first 5 rows):", out[:5])


def test_trades_all():
    print("\n=== Testing Trades for All Manual ===")
    rows = long_df.to_dict("records")
    trades = trades_for_all_manual(rows)
    print("Trades (first 5):", trades[:5])


def test_max_profit():
    print("\n=== Testing Max Profit Manual ===")
    rows = long_df.to_dict("records")
    summary = max_profit_summary_manual(rows)
    print("Max profit summary (top 5):", summary[:5])


# === MAIN RUNNER ===
if __name__ == "__main__":
    test_sma()
    test_trend_runs()
    test_daily_returns()
    test_trades_all()
    test_max_profit()
