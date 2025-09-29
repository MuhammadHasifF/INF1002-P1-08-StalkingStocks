"""
core.py

This module provides the core functionality of the project, including
the main processing functions and algorithms for our application.

Notes:
    -
"""

import numpy as np
import pandas as pd
from utils.helpers import timer


@timer
def compute_sma(close: pd.Series, window: int = 5) -> pd.Series:
    """
    Compute the simple moving average of a sequence.

    Args:
        close (Series): Closing asset price to compute SMA on
        window (int): window size

    Returns:
        Series containing moving average.
    """
    return close.rolling(window=window).mean()


@timer
def compute_streak(close: pd.Series):
    """
    Compute the number and total occurrences of consecutive upward
    and downward days (based on close-to-close changes), and identify
    the longest streaks for each direction.

    Args:
        -

    Returns:
        -
    """
    diff = close.diff()
    signed = np.sign(diff).fillna(0).astype(int)

    # create boolean masks
    pos = signed == 1
    neg = signed == -1

    # create "group ids" for contiguous regions of equal values in each mask
    gid_pos = (pos != pos.shift(fill_value=False)).cumsum()
    gid_neg = (neg != neg.shift(fill_value=False)).cumsum()

    # for each contiguous run label, sum the mask
    longest_pos = pos.groupby(gid_pos).sum().max() or 0
    longest_neg = neg.groupby(gid_neg).sum().max() or 0

    return int(longest_pos), int(longest_neg)


@timer
def compute_sdr(close: pd.Series) -> pd.Series:
    """Computes the simple daily return of a series"""
    return close.pct_change(periods=1)


@timer
def compute_max_profit(close: pd.Series) -> np.float64:
    """
    https://stackoverflow.com/questions/7420401/interview-question-maximum-multiple-sell-profit
    """
    profit = 0
    for i in range(len(close) - 1):
        curr_price = close.iloc[i]
        next_price = close.iloc[i + 1]
        if next_price > curr_price:
            profit += next_price - curr_price
    return profit
