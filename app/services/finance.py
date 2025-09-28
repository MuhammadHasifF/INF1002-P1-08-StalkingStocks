"""
finance.py

This module provides core functionalities for interacting with the yfinance API,
including retrieving sector and industry data, obtaining top-performing companies,
and downloading stock price data for single or multiple tickers.

It serves as the primary interface between the application and financial data sources,
abstracting away raw API calls into convenient, reusable functions.

The module is intended for data ingestion, preprocessing, and real-time querying
of financial data to support dashboards, analytics, and reporting features.
"""

from typing import Any, Sequence

import pandas as pd
import yfinance as yf
from constants.sectors import SECTORS
from models.base import Industry, Sector, Ticker
from schemas.dataframe import MarketData, TopGrowing, TopPerforming
from utils.helpers import (timer, yf_industry_to_model, yf_sector_to_model,
                           yf_ticker_to_model)


def get_sectors() -> Sequence[str]:
    """Returns a read-only iterable of sector names."""
    return SECTORS


@timer
def get_sector_data(sector_key: str) -> Sector:
    """
    Returns data on a single domain sector.

    Args:
        sector_key (str): Sector key to be queried

    Returns:
        A Sector data model containing sector information.
    """
    data: Sector = yf_sector_to_model(key=sector_key)
    return data


@timer
def get_industry_data(industry_key: str) -> Industry:
    """
    Returns data on a single industry.

    Note:
        - A single sector contains multiple industries.
        - Each industry contains multiple company tickers.

    Args:
        sector_key (str): Sector key to be queried

    Returns:
        A Sector data model containing sector information.
    """
    data: Industry = yf_industry_to_model(key=industry_key)

    data.top_performing = TopPerforming.validate(data.top_performing)
    data.top_growing = TopGrowing.validate(data.top_growing)

    return data


@timer
def get_ticker_info(ticker_symbol: str, **kwargs: Any) -> Ticker:
    """
    Retrieve metadata for a single ticker symbol using Yahoo Finance.

    Args:
        ticker_symbol (str):
            The ticker symbol of the stock or asset (e.g., "AAPL", "MSFT").
        **kwargs (Any):
            Additional keyword arguments passed to `yfinance.Ticker`,
            such as `start`, `end`, `interval`, etc.

    Returns:
        Ticker Data Model
    """
    kwargs.pop("symbol", None)  # remove if exists
    ticker: Ticker = yf_ticker_to_model(symbol=ticker_symbol, **kwargs)
    return ticker


@timer
def get_ticker_data(ticker_symbols: str | list[str], **kwargs: Any) -> pd.DataFrame:
    """
    Retrieve historical market data for one or multiple ticker symbols using
    Yahoo Finance.

    Args:
        ticker_symbols (list[str]):
            A list of ticker symbols (e.g., ["AAPL", "MSFT", "GOOG"]).
        **kwargs (Any):
            Additional keyword arguments passed to `yfinance.download`,
            such as `start`, `end`, `interval`, etc.

    Returns:
        A validated dataframe of OHLCV (open, high, low, close, volume) data
        from yfinance.
    """
    kwargs.pop("tickers", None)  # remove if exists
    data: pd.DataFrame = yf.download(tickers=ticker_symbols, **kwargs)

    # Handle single vs multi-ticker cases:
    if isinstance(ticker_symbols, str):
        data.columns = data.columns.droplevel(1)
        data = MarketData.validate(data)

    # not sure how i want to handle multi-indexed dataframes yet
    # else:
    #     # Collapse it into flat columns for validation
    #     data = data.stack(level=0).rename_axis(["Date", "Ticker"]).reset_index()

    return data
