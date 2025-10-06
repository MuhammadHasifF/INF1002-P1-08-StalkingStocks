"""
helpers.py

This module contains general-purpose utility functions and helpers used across
the application.

The module is intended to provide reusable tools that simplify data ingestion,
processing, and analysis workflows. Additional helper functions may be added
as the application evolves.
"""

import logging
from datetime import date
from functools import wraps
from time import perf_counter
from typing import Any, Callable, ParamSpec, TypeVar

import pandas as pd
import yfinance as yf

from ..models.base import Industry, Sector, Ticker

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)


def has_null_values(df: pd.DataFrame) -> bool:
    """Checks for null values"""
    return df.isnull().values.any()


def format_name(name: str) -> str:
    """Formats name of sector/industry to be usable by API"""
    # replace dashes
    name = name.replace("-", " ")
    # replace underscores 
    name = name.replace("_", " ")
    return name.title()


def rolling_window(
    n: int, unit: str = "years", timezone: str = "Asia/Singapore"
) -> tuple[date, date]:
    """
    Compute a rolling (start, end) window ending at the current date.

    Args:
        n (int): Number of units to look back from.
        unit (str): Time unit for the window. One of {"days", "weeks", "months", "years"}.
        timezone (str): Time zone for the Timestamp.

    Returns:
        A tuple containing start and end dates.
    """
    end_ts: pd.Timestamp = pd.Timestamp.now(tz=timezone).normalize()

    if unit == "days":
        start_ts = end_ts - pd.Timedelta(days=n)
    elif unit == "weeks":
        start_ts = end_ts - pd.Timedelta(weeks=n)
    elif unit == "months":
        start_ts = end_ts - pd.DateOffset(months=n)
    elif unit == "years":
        start_ts = end_ts - pd.DateOffset(years=n)
    else:
        raise ValueError("unit must be one of {'days', 'weeks', 'months', 'years'}")

    return start_ts.date(), end_ts.date()


def yf_ticker_to_model(ticker_obj: yf.Ticker) -> Ticker:
    """
    Converts a yfinance Ticker into a structured Ticker model.

    Note:
        Certain ticker information is unavailable. To handle this we use
        the dictionary get() method which returns None when a key does not exist.

    Args:
        symbol (str): Ticker symbol

    Return:
        A Ticker data model.
    """
    info: dict[str, Any] = ticker_obj.info

    return Ticker(
        symbol=info.get("symbol"),
        display_name=info.get("displayName"),
        long_name=info.get("longName"),
        short_name=info.get("shortName"),
        market_cap=info.get("marketCap"),
        price=info.get("currentPrice"),
        sector=info.get("sector"),
        industry=info.get("industry"),
        description=info.get("longBusinessSummary"),
        dividend_rate=info.get("dividendRate"),
        dividend_yield=info.get("dividendYield"),
        volume=info.get("volume"),
    )


def yf_industry_to_model(industry_obj: yf.Industry) -> Industry:
    """Converts a yfinance Industry into a structured Industry model."""

    overview = industry_obj.overview

    # top_performing = industry_obj.top_performing_companies
    # top_growing = industry_obj.top_growth_companies
    #
    # top_performing.columns = (
    #     top_performing.columns.str.strip().str.lower().str.replace(" ", "_")
    # )
    # top_growing.columns = (
    #     top_growing.columns.str.strip().str.lower().str.replace(" ", "_")
    # )

    return Industry(
        description=overview.get('description'),
        employee_count=overview.get('employee_count'),
        market_cap=overview.get('market_cap'),
        market_weight=overview.get('market_weight'),
        # top_performing=top_performing, 
        # top_growing=top_growing
    )


def yf_sector_to_model(sector_obj: yf.Sector) -> Sector:
    """Converts a yfinance Sector into a structured Sector model."""

    return Sector(
        key=sector_obj.key,
        name=sector_obj.name,
        overview=sector_obj.overview,
        top_companies=sector_obj.top_companies.index,
        top_etfs=sector_obj.top_etfs.keys(),
        top_mutual_funds=sector_obj.top_mutual_funds.keys(),
        industries=sector_obj.industries.index,
    )


def format_large_number(n: int | float) -> str:
    """
    Convert a large numeric value into a human-readable string with suffixes.

    Parameters:
        n (int | float ): The numeric value to format.

    Returns:
        A string representing the number in a shortened, human-readable format:
        - Thousands (K) for numbers >= 1,000
        - Millions (M) for numbers >= 1,000,000
        - Billions (B) for numbers >= 1,000,000,000
        - Trillions (T) for numbers >= 1,000,000,000,000
        - Otherwise, returns the number as a string
    """
    if n >= 1_000_000_000_000:
        return f"{n/1_000_000_000_000:.2f}T"
    elif n >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n/1_000:.2f}K"
    return str(n)


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
        start = perf_counter()
        output = func(*args, **kwargs)
        end = perf_counter()
        logging.info(f"{func.__name__} executed in {(end - start):.6f} seconds")
        return output

    return wrapper
