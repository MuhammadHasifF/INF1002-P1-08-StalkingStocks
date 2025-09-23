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
import yfinance as yf
from models.base import Industry, Sector, Ticker


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


def yf_ticker_to_model(symbol: str) -> Ticker:
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
    yf_ticker = yf.Ticker(ticker=symbol)
    info = yf_ticker.info

    return Ticker(
        symbol=symbol,
        name=info["shortName"],
        market_cap=info.get("marketCap"),
        price=info.get("currentPrice"),
        sector=info.get("sector"),
        industry=info.get("industry"),
    )


def yf_industry_to_model(key: str):
    """Converts a yfinance Industry into a structured Industry model."""
    yf_industry = yf.Industry(key=key)

    top_performing = yf_industry.top_performing_companies
    top_growing = yf_industry.top_growth_companies

    top_performing.columns = (
        top_performing.columns.str.strip().str.lower().str.replace(" ", "_")
    )
    top_growing.columns = (
        top_growing.columns.str.strip().str.lower().str.replace(" ", "_")
    )

    return Industry(top_performing=top_performing, top_growing=top_growing)


def yf_sector_to_model(key: str) -> Sector:
    """Converts a yfinance Sector into a structured Sector model."""
    yf_sector = yf.Sector(key=key)

    return Sector(
        key=key,
        name=yf_sector.name,
        overview=yf_sector.overview,
        top_companies=[
            yf_ticker_to_model(tkr) for tkr in yf_sector.top_companies.index
        ],
        top_etfs=yf_sector.top_etfs,
        top_mutual_funds=yf_sector.top_mutual_funds,
        industries=list(yf_sector.industries.index),
    )


def yf_download_to_model(
    symbols: str | list[str], start: str, end: str, interval: str = "1d", **kwargs
) -> pd.DataFrame:
    data = yf.download(
        tickers=symbols, start=start, end=end, interval=interval, **kwargs
    )

    return data
