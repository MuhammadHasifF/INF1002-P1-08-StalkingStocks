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

import pandas as pd
import numpy as np
from ..utils.helpers import timer


# computing SMA
@timer
def compute_sma(close: pd.Series, window: int = 5) -> pd.Series:
    """
    Compute simple moving averages (SMAs) manually.
    
    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) - single pass through data
    - Space Complexity: O(n) - stores output array
    - Algorithmic Efficiency: Optimal - uses sliding window technique
    
    Why O(n) time complexity?
    - We iterate through each price once
    - Sliding window: add new price, remove old price (constant time operations)
    - No nested loops needed
    
    Why O(n) space complexity?
    - Output array same size as input
    - Constant extra variables (running_sum)
    
    Args:
        close (pd.Series): closing prices
        window (int): window size
    Returns:
        pd.Series of SMA values (NaN where insufficient data)
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


# computing trend runs (up/down streaks)
@timer
def compute_streak(close: pd.Series) -> tuple[int, int]:
    """
    Compute longest upward and downward streaks manually.
    
    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) - single pass through data
    - Space Complexity: O(1) - constant extra space (optimized!)
    - Algorithmic Efficiency: Optimal - linear time, constant space solution
    
    Why O(n) time complexity?
    - Single pass: Process each price pair once (n-1 comparisons)
    - Each comparison and streak update is constant time
    - No nested loops needed
    
    Why O(1) space complexity?
    - Only uses constant extra variables (4 integers total - ultra-optimized!)
    - No arrays or lists needed - tracks streaks in real-time
    - Space usage doesn't grow with input size
    - Minimal memory footprint for maximum efficiency
    
    Args:
        close (pd.Series): closing prices
    Returns:
        (longest_up, longest_down) as tuple[int, int]
    """
    # Convert pandas input to NumPy array for computation (manual algorithms)
    values: np.ndarray = close.values
    n: int = len(values)
    
    # Handle edge case: need at least 2 prices to determine direction
    if n <= 1:
        return (0, 0)
    
    # Only 4 variables needed
    longest_up_streak: int = 0
    longest_down_streak: int = 0
    current_streak: int = 0
    current_direction: int = 0  # 0 = no direction, 1 = up, -1 = down
    
    # Single pass through data - process each price pair
    for i in range(1, n):
        previous_price: float = values[i - 1]
        current_price: float = values[i]
        
        # Determine direction using pure Python logic
        if current_price > previous_price:
            new_direction: int = 1  # Upward movement
        elif current_price < previous_price:
            new_direction: int = -1  # Downward movement
        else:
            new_direction: int = 0  # No change
        
        # Update streaks efficiently
        if new_direction == current_direction and new_direction != 0:
            # Continue current streak
            current_streak += 1
        else:
            # Direction changed - update longest streaks and reset
            if current_direction == 1 and current_streak > longest_up_streak:
                longest_up_streak = current_streak
            elif current_direction == -1 and current_streak > longest_down_streak:
                longest_down_streak = current_streak
            
            # Start new streak
            current_direction = new_direction
            current_streak = 1 if new_direction != 0 else 0
    
    # Handle final streak (don't forget the last run!)
    if current_direction == 1 and current_streak > longest_up_streak:
        longest_up_streak = current_streak
    elif current_direction == -1 and current_streak > longest_down_streak:
        longest_down_streak = current_streak

    return (longest_up_streak, longest_down_streak)


# daily returns
@timer
def compute_sdr(close: pd.Series) -> pd.Series:
    """
    Compute daily returns manually.
    
    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) - single pass through data
    - Space Complexity: O(n) - stores output array
    - Algorithmic Efficiency: Optimal - cannot do better than O(n)
    
    Why O(n) time complexity?
    - Must examine each price pair (current, previous)
    - n-1 comparisons for n prices
    - Each calculation is constant time
    
    Why O(n) space complexity?
    - Output array same size as input
    - Constant extra variables
    
    Formula: (P_t - P_{t-1}) / P_{t-1}
    
    Args:
        close (pd.Series): closing prices
    Returns:
        pd.Series of daily returns
    """
    # Convert pandas input to NumPy array for computation (manual algorithms)
    values: np.ndarray = close.values
    n: int = len(values)
    daily_returns: list[float | None] = [None]  # First day has no return (no previous day)
    
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


# Max profit
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
