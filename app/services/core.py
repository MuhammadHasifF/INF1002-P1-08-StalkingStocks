"""
core.py

This module provides the core functionality of the project, including
the main processing functions and algorithms for our application.

Notes:
    - Manual (pure Python) implementations for SMA, trend runs,
      daily returns, and max profit.
    - These functions operate on lists of dicts (rows) or simple lists,
      not directly on DataFrames (to keep it "manual").
"""

# ============================================================
# 1. SIMPLE MOVING AVERAGE (SMA)
# ============================================================

def compute_sma_manual(values, window: int):
    """
    Compute simple moving averages (SMAs) with nothing but Python.
    - values: list of numbers (closing prices)
    - window: how many days to average (5, 20, 50, etc.)
    Returns a list the same length as input, with None for the first
    (window-1) entries where not enough data exists yet.
    """
    n = len(values)
    out = [None] * n  # pre-fill with None

    if window <= 0 or n == 0:
        return out

    running_sum = 0.0
    for i, v in enumerate(values):
        if v is None:             # skip bad/missing values
            out[i] = None
            continue

        running_sum += float(v)   # add current value

        if i >= window:           # drop value that just slid out of window
            running_sum -= float(values[i - window])

        if i >= window - 1:       # only valid once we’ve seen at least 'window' values
            out[i] = running_sum / window

    return out

# Example usage (in notebook/test):
# closes = [100, 101, 102, 103, 104, 105]
# print(compute_sma_manual(closes, 3))


# ============================================================
# 2. TREND RUNS (UP/DOWN STREAKS)
# ============================================================

def compute_trend_runs_manual(rows):
    """
    Compute up/down runs manually for each ticker.
    rows: list of dicts, each like {"Ticker": "AAPL", "Date": "2022-01-01", "Close": 145.0}

    Returns: list of dicts summarising trend runs per ticker:
      - Ticker
      - Total Up Runs
      - Longest Up Run
      - Total Down Runs
      - Longest Down Run
    """
    tickers = sorted(set(r["Ticker"] for r in rows))
    out = []

    for tkr in tickers:
        g = sorted([r for r in rows if r["Ticker"] == tkr],
                   key=lambda r: r["Date"])
        closes = [r["Close"] for r in g]

        # build direction list
        dirs = [0]
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                dirs.append(1)
            elif closes[i] < closes[i-1]:
                dirs.append(-1)
            else:
                dirs.append(0)

        # count runs
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

        out.append({
            "Ticker": tkr,
            "Total Up Runs": len(up_runs),
            "Longest Up Run": max(up_runs) if up_runs else 0,
            "Total Down Runs": len(down_runs),
            "Longest Down Run": max(down_runs) if down_runs else 0
        })

    return out

# Example usage:
# rows = long_df.to_dict("records")
# summary = compute_trend_runs_manual(rows)
# print(summary[:5])


# ============================================================
# 3. DAILY RETURNS
# ============================================================

def add_daily_returns_manual(rows):
    """
    Compute daily returns for each ticker using only Python.
    Daily return formula:
        r_t = (P_t - P_{t-1}) / P_{t-1}
            = P_t / P_{t-1} - 1
    - rows: list of dicts, each like {"Ticker": "AAPL", "Date": "2022-01-01", "Close": 145.0}
    - Returns a new list of dicts with Daily_Return field added
    """
    # group rows manually by ticker
    grouped = {}
    for row in rows:
        tkr = row["Ticker"]
        grouped.setdefault(tkr, []).append(row)

    output = []

    # process each ticker separately
    for tkr, g in grouped.items():
        # sort rows by date so changes are chronological
        g = sorted(g, key=lambda r: r["Date"])
        prev_close = None

        for row in g:
            if prev_close is None:
                # first row per ticker has no prior → daily return is None
                row["Daily_Return"] = None
            else:
                # apply formula: (current - prior) / prior
                row["Daily_Return"] = (row["Close"] - prev_close) / prev_close
            prev_close = row["Close"]
            output.append(row)

    return output

# Example usage:
# rows = long_df.to_dict("records")
# out = add_daily_returns_manual(rows)
# print(out[:5])


# ============================================================
# 4. MAX PROFIT (BEST TIME II — SUM OF RISES)
# ============================================================

def extract_trades_for_ticker_manual(rows, ticker: str):
    """
    For one ticker:
      - Buy just before a price rise (when price goes up after today)
      - Sell at the peak (just before a drop, or on the very last day)
    Returns:
      - list of dicts, where each dict = one completed trade
        (buy_date, buy_price, sell_date, sell_price, profit)
    """
    # keep only the rows for the requested ticker
    g = [r for r in rows if r["Ticker"] == ticker]

    # sort the rows by Date to ensure proper time order
    g = sorted(g, key=lambda r: r["Date"])

    trades = []                     # final list to hold all completed trades
    holding = False                 # flag: are we currently "in" a trade?
    buy_date = buy_price = None     # placeholders for buy signal info

    # loop through rows starting at the 2nd one (need prev+curr to compare)
    for i in range(1, len(g)):
        # get yesterday’s and today’s closing prices
        prev_p, cur_p = g[i-1]["Close"], g[i]["Close"]

        # also track the dates (for recording trades later)
        prev_d, cur_d = g[i-1]["Date"], g[i]["Date"]

        # BUY RULE:
        if not holding and cur_p > prev_p:
            holding = True
            buy_date, buy_price = prev_d, prev_p

        # SELL RULE:
        is_last = (i == len(g) - 1)
        next_drop_or_end = (cur_p > prev_p and (is_last or g[i+1]["Close"] < cur_p))

        if holding and next_drop_or_end:
            sell_date, sell_price = cur_d, cur_p
            trades.append({
                "Ticker": ticker,
                "buy_date": buy_date, "buy_price": buy_price,
                "sell_date": sell_date, "sell_price": sell_price,
                "profit": sell_price - buy_price
            })
            holding = False   # reset after selling

    return trades


def trades_for_all_manual(rows):
    """
    Collect trades for *all* tickers in the dataset.
    Steps:
      - build list of unique tickers
      - run extract_trades_for_ticker_manual on each
      - extend all results into one combined list
    """
    out = []  # combined trades from all tickers
    tickers = sorted(set(r["Ticker"] for r in rows))   # unique tickers
    for tkr in tickers:
        out.extend(extract_trades_for_ticker_manual(rows, tkr))
    return out


def max_profit_summary_manual(rows):
    """
    Compute max profit (sum of rises) per ticker.
    Steps:
      - for each ticker, collect all its trades
      - sum all 'profit' values from those trades
      - build a summary dict: {"Ticker": TKR, "Max_Profit": total}
      - return all tickers sorted by Max_Profit (descending)
    """
    out = []
    tickers = sorted(set(r["Ticker"] for r in rows))   # unique tickers
    for tkr in tickers:
        trades = extract_trades_for_ticker_manual(rows, tkr)
        total = sum(t["profit"] for t in trades)   # sum of all profits
        out.append({"Ticker": tkr, "Max_Profit": total})

    # sort by highest profit first
    out.sort(key=lambda x: x["Max_Profit"], reverse=True)
    return out

# Example usage:
# rows = long_df.to_dict("records")
# print(extract_trades_for_ticker_manual(rows, "AAPL"))
# print(trades_for_all_manual(rows)[:5])
# print(max_profit_summary_manual(rows)[:5])
