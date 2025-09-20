"""
helpers.py

This module contains general-purpose utility functions and helpers used across
the application. 

The module is intended to provide reusable tools that simplify data ingestion,
processing, and analysis workflows. Additional helper functions may be added
as the application evolves.
"""


from datetime import date
from functools import wraps
from time import time
from typing import Callable, ParamSpec, TypeVar

import pandas as pd


def n_year_window(n: int, timezone: str = "Asia/Singapore") -> tuple[date, date]:
    """
    Compute a rolling n-year (start, end) window ending at the current date.

    Args:
        n (int): Number of years to look back from.
        timezone (str): Time zone for time which Timestamp will have.

    Returns:
        A tuple containing start and end dates
    """
    end_ts: pd.Timestamp = pd.Timestamp.now(tz=timezone).normalize()
    start_ts: pd.Timestamp = end_ts - pd.DateOffset(years=n)
    return start_ts.date(), end_ts.date()


P = ParamSpec("P")
R = TypeVar("R")


def timer(func: Callable[P, R]) -> Callable[P, R]:
    """
    Measures wall clock-time of two points.

    Args:
        func (Callable): Function to be timed.

    Returns:
        A wrapped function that behaves like `func` but prints the time
        it took to execute.
    """
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        """Wrapper function that times the execution of `func`."""
        start = time()
        output = func(*args, **kwargs)
        end = time()
        print(f"[INFO] {func.__name__} took {end - start:.6f} seconds.")
        return output
    return wrapper


def yf_to_model():
    """Parses yfinance classes into data models"""
    pass
