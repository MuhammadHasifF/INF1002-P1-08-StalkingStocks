"""
core.py

This module provides the core functionality of the project, including
the main processing functions and algorithms for our application.

Notes:
    -
"""

import numpy as np
import pandas as pd
from ..utils.helpers import timer


@timer
def compute_sma(close: pd.Series, window: int = 5) -> pd.Series:
    """
    Compute the simple moving average of a sequence.

    Args:
        close (Series): Closing asset price
        window (int): window size

    Returns:
        Series containing moving average.
    """
    result: pd.Series = close.rolling(window=window).mean()
    return result


@timer
def compute_streak(close: pd.Series) -> tuple[int, int]:
    """
    Compute the number and total occurrences of consecutive upward
    and downward days (based on close-to-close changes), and identify
    the longest streaks for each direction.

    Args:
        close (Series): Closing asset price

    Returns:
        A tuple containing longest upward and downward runs of a stock's
        closing price.
    """
    diff: pd.Series = close.diff()
    signed: np.ndarray = np.sign(diff).fillna(0).astype(int)

    # create boolean masks
    pos: np.ndarray = signed == 1
    neg: np.ndarray = signed == -1

    # create "group ids" for contiguous regions of equal values in each mask
    gid_pos: np.ndarray = (pos != pos.shift(fill_value=False)).cumsum()
    gid_neg: np.ndarray = (neg != neg.shift(fill_value=False)).cumsum()

    # for each contiguous run label, sum the mask
    longest_pos: int = int(pos.groupby(gid_pos).sum().max()) or 0
    longest_neg: int = int(neg.groupby(gid_neg).sum().max()) or 0

    return longest_pos, longest_neg


@timer
def compute_sdr(close: pd.Series) -> pd.Series:
    """
    Computes the simple daily return of a series

    Args:
        close (Series): Closing asset price 

    Returns:
        A series containing daily returns.
    """
    result: pd.Series = close.pct_change(periods=1)
    return result


@timer
def compute_max_profit(close: pd.Series) -> float:
    """
    Computes a stock's potential maximum profit (assuming multiple buy/sell).

    Note:
        - This implementation of max profit was references from the following post:
        - https://stackoverflow.com/questions/7420401/interview-question-maximum-multiple-sell-profit

    Args:
        close (Series): Closing asset price

    Returns:
        The maximum potential profit 
    """
    profit: float = 0.0
    for i in range(len(close) - 1):
        curr_price: float = close.iloc[i]
        next_price: float = close.iloc[i + 1]
        if next_price > curr_price:
            profit += next_price - curr_price
    return profit
