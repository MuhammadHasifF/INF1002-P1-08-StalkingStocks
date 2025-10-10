"""
core.py

- This module provides the core functionality of the project, including
- the main processing functions and algorithms for our application.

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
    - All computation is done manually with Python.
    - Pandas/Numpy modules are only used for input/output compatibility.
"""

import numpy as np
import pandas as pd

from src.utils.helpers import timer


@timer
def compute_sma(close: pd.Series, window: int = 5) -> pd.Series:
    """
    Compute simple moving averages (SMAs) manually using a sliding window.

    RATIONALE:
    - SMA smooths out price fluctuations by averaging the last N closes.
    - Common windows: 5 (short-term), 20 (≈1 trading month), 50 (medium-term).
    - Used to identify market trends and reduce noise in time-series data.

    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) — single pass through all prices.
    - Space Complexity: O(n) — stores output values.
    - Algorithmic Efficiency: Optimal — uses sliding window to avoid recomputation.

    Why O(n) time complexity?
    - Each price is processed once.
    - Running sum updated in constant time (add new, remove old).
    - Avoids nested loops or recomputing averages from scratch.

    Why O(n) space complexity?
    - Output array same size as input.
    - Only constant extra variables needed (running_sum).

    Formula:
        SMA_t = (P_t + P_{t-1} + ... + P_{t-N+1}) / N

    Args:
        close (pd.Series): Closing prices
        window (int): Lookback window size (5, 20, 50, etc.)

    Returns:
        pd.Series of SMA values (NaN where insufficient data)

    Reference:
        https://www.investopedia.com/ask/answers/122414/what-are-most-common-periods-used-creating-moving-average-ma-lines.asp
    """
    # Convert pandas input to NumPy array for computation (manual algorithms)
    values: np.ndarray = close.values
    n: int = len(values)
    out: np.ndarray = np.full(n, np.nan, dtype=float)

    # Handle edge cases
    if window <= 0 or n == 0:
        return pd.Series(out, index=close.index)

    # Calculate SMA using sliding window approach
    running_sum: float = 0.0
    for i, current_price in enumerate(values):
        # Add current price to running sum
        running_sum += float(current_price)

        # Remove price that's now outside the window (if we have enough data)
        if i >= window:
            running_sum -= float(values[i - window])

        # Calculate SMA only when we have enough data points
        if i >= window - 1:
            out[i] = running_sum / window

    # Convert Python result back to pandas Series for output
    return pd.Series(out, index=close.index)


@timer
def compute_streak(close: pd.Series) -> tuple[int, int, pd.Series]:
    """
    Compute longest upward and downward streaks of consecutive days manually.

    RATIONALE:
    - Measures persistence of trends (momentum vs. reversals).
    - Up run = consecutive days with Close_t > Close_{t-1}.
    - Down run = consecutive days with Close_t < Close_{t-1}.
    - Flat days (Close_t == Close_{t-1}) are neutral — they break streaks but do not count.
    - Adds a direction mask (-1, 0, 1) for visualisation of trend segments in plots.

    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) — single pass through data.
    - Space Complexity: O(1) auxiliary (O(n) for returned mask array).
    - Algorithmic Efficiency: Optimal — minimal variable tracking, no redundant passes.

    Why O(n) time complexity?
    - Each price compared once to previous.
    - Update streak counters in constant time.

    Why O(1) auxiliary space complexity?
    - Uses only four counters (longest_up, longest_down, current_streak, direction).
    - Mask array is part of expected output, not auxiliary storage.

    Formula:
        Up streak: max consecutive (Close_t > Close_{t-1})
        Down streak: max consecutive (Close_t < Close_{t-1})
        Mask: 1 = Up, -1 = Down, 0 = Flat

    Args:
        close (pd.Series): Closing prices

    Returns:
        tuple[int, int, pd.Series]: (longest_up, longest_down, trend_mask)
            - longest_up: longest upward run length.
            - longest_down: longest downward run length.
            - trend_mask: Series of daily direction values for plotting.

    Reference:
        Wald–Wolfowitz Runs Test (handling ties):
        https://en.wikipedia.org/wiki/Wald%E2%80%93Wolfowitz_runs_test
    """

    # Convert pandas input to NumPy array for computation (manual algorithms)
    values: np.ndarray = close.values
    n: int = len(values)

    # Handle edge case: need at least 2 prices to determine direction
    if n <= 1:
        return (0, 0, pd.Series(np.zeros(n, dtype=int), index=close.index))

    # Initialize counters and mask
    longest_up_streak: int = 0
    longest_down_streak: int = 0
    current_streak: int = 0
    current_direction: int = 0  # 0 = no direction, 1 = up, -1 = down
    mask: np.ndarray = np.zeros(n, dtype=int)

    # Single pass through all prices
    for i in range(1, n):
        previous_price: float = values[i - 1]
        current_price: float = values[i]

        # Determine movement direction
        if current_price > previous_price:
            new_direction: int = 1  # Upward movement
        elif current_price < previous_price:
            new_direction: int = -1  # Downward movement
        else:
            new_direction: int = 0  # Flat day

        # Record daily trend in mask for plotting
        mask[i] = new_direction

        # Update streaks efficiently
        if new_direction == current_direction and new_direction != 0:
            current_streak += 1
        else:
            # Direction change — update longest streaks before reset
            if current_direction == 1 and current_streak > longest_up_streak:
                longest_up_streak = current_streak
            elif current_direction == -1 and current_streak > longest_down_streak:
                longest_down_streak = current_streak

            # Reset for next streak
            current_direction = new_direction
            current_streak = 1 if new_direction != 0 else 0

    # Final streak check (include last run)
    if current_direction == 1 and current_streak > longest_up_streak:
        longest_up_streak = current_streak
    elif current_direction == -1 and current_streak > longest_down_streak:
        longest_down_streak = current_streak

    # Return results with mask as Series
    return (longest_up_streak, longest_down_streak, pd.Series(mask, index=close.index))


@timer
def compute_sdr(close: pd.Series) -> pd.Series:
    """
    Compute daily returns manually as percentage changes in closing price.

    RATIONALE:
    - Normalizes price movements across tickers.
    - Used to analyze volatility, compare stocks, and calculate risk metrics.
    - Positive = stock went up, Negative = stock went down, Zero = no change.

    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) — single pass through data.
    - Space Complexity: O(n) — output array same size as input.
    - Algorithmic Efficiency: Optimal — step-by-step ratio comparisons.

    Why O(n) time complexity?
    - Each pair of consecutive prices compared once.
    - Calculation (curr - prev) / prev is constant time.

    Why O(n) space complexity?
    - Output series has same length as input.
    - Only constant extra variables used.

    Formula:
        r_t = (P_t - P_{t-1}) / P_{t-1}
            = P_t / P_{t-1} - 1

    Edge Cases:
    - First row has no prior price → return = None.
    - If previous price = 0, return = None (avoids divide-by-zero).

    Args:
        close (pd.Series): Closing prices

    Returns:
        pd.Series of daily returns

    Reference:
        Pandas pct_change (we reimplemented manually):
        https://pandas.pydata.org/docs/reference/api/pandas.Series.pct_change.html
    """

    # Convert pandas input to NumPy array for computation (manual algorithms)
    values: np.ndarray = close.values
    n: int = len(values)
    daily_returns: list[float | None] = [
        None
    ]  # First day has no return (no previous day)

    # Calculate daily returns using pure Python
    for i in range(1, n):
        previous_price: float = values[i - 1]
        current_price: float = values[i]

        if previous_price != 0:  # Avoid division by zero
            # Daily return = (current_price - previous_price) / previous_price
            daily_return: float = (current_price - previous_price) / previous_price
            daily_returns.append(daily_return)
        else:
            daily_returns.append(None)  # Handle zero price case

    # Convert Python result back to pandas Series for output
    return pd.Series(daily_returns, index=close.index)


@timer
def compute_max_profit(close: pd.Series) -> float:
    """
    Compute max profit (sum of rises) manually.

    This implements the "Best Time to Buy and Sell Stock II" algorithm using a greedy approach.

    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) - single pass through data
    - Space Complexity: O(1) - constant extra space
    - Algorithmic Efficiency: Optimal - greedy algorithm

    Why O(n) time complexity?
    - Must examine each price pair to find profitable trades
    - n-1 comparisons for n prices
    - Each comparison and calculation is constant time

    Why O(1) space complexity?
    - Only uses constant extra variables (total_profit, current_price, next_price)
    - No additional arrays or data structures needed
    - Space usage doesn't grow with input size

    Why greedy algorithm is optimal?
    - Local optimal choice (profit from each rise) leads to global optimum
    - No need to look ahead or backtrack
    - Mathematical proof shows this captures all possible profits

    Algorithm Source: LeetCode Problem 122 - Best Time to Buy and Sell Stock II
    Reference: https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/

    Greedy Strategy: Buy before every price increase, sell after it.
    This approach captures all possible profits by making a transaction whenever
    the next day's price is higher than the current day's price.

    Args:
        close (pd.Series): closing prices
    Returns:
        float total profit from optimal trading strategy
    """
    # Convert pandas input to NumPy array for computation (manual algorithms)
    values: np.ndarray = close.values
    n: int = len(values)
    total_profit: float = 0.0

    # Calculate max profit by summing all positive price increases
    # Strategy: Buy before every price increase, sell after it
    for i in range(n - 1):
        current_price: float = values[i]
        next_price: float = values[i + 1]

        if next_price > current_price:
            # If next day's price is higher, we can profit by buying today and selling tomorrow
            profit_from_transaction: float = next_price - current_price
            total_profit += profit_from_transaction

    return float(total_profit)
