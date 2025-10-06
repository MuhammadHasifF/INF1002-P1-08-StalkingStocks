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

from ..constants.sectors import SECTORS
from ..models.base import Industry, Sector, Ticker
from ..schemas.dataframe import (IndustryData, MultipleStockData,
                                 SingleStockData, StockDataFrame, TopGrowing,
                                 TopPerforming)
from ..utils.helpers import (timer, yf_industry_to_model, yf_sector_to_model,
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
    try:
        yf_sector = yf.Sector(key=sector_key)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve data for {sector_key}: {e}")

    return yf_sector_to_model(yf_sector)


@timer
def get_industry_data(industry_key: str, **kwargs: Any) -> IndustryData:
    try:
        yf_industry = yf.Industry(key=industry_key)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve data for {industry_key}: {e}")

    data: pd.DataFrame = yf_industry.ticker.history(**kwargs)
    validated: IndustryData = IndustryData.validate(data)

    return validated


@timer
def get_industry_info(industry_key: str) -> Industry:
    """
    Retrieves metadata on a single industry.

    Note:
        - A single sector contains multiple industries.
        - Each industry contains multiple company tickers.

    Args:
        sector_key (str): Sector key to be queried

    Returns:
        A Sector data model containing sector information.
    """
    try:
        yf_industry = yf.Industry(key=industry_key)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve data for {industry_key}: {e}")

    data: Industry = yf_industry_to_model(yf_industry)

    # data.top_performing = TopPerforming.validate(data.top_performing)
    # data.top_growing = TopGrowing.validate(data.top_growing)

    return data


@timer
def get_ticker_info(ticker_symbol: str, **kwargs: Any) -> Ticker:
    """
    Retrieve metadata for a single ticker symbol using Yahoo Finance. Args:
        ticker_symbol (str):
            The ticker symbol of the stock or asset (e.g., "AAPL", "MSFT").
        **kwargs (Any):
            Additional keyword arguments passed to `yfinance.Ticker`,
            such as `start`, `end`, `interval`, etc.

    Returns:
        Ticker Data Model
    """

    try:
        yf_ticker = yf.Ticker(ticker=ticker_symbol, **kwargs)
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve info for {ticker_symbol}: {e}")

    return yf_ticker_to_model(yf_ticker)


def get_ticker_data(
    ticker_symbols: str | list[str], **kwargs: Any
) -> StockDataFrame | None:
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
    data: pd.DataFrame = yf.download(tickers=ticker_symbols, **kwargs)

    if data.empty:
        return None

    # Handle single vs multi-ticker cases:
    if isinstance(ticker_symbols, str):
        data.columns = data.columns.droplevel(1)
        # Remove non-trading days (where data is missing)
        data = data.dropna(subset=["Open", "Close"])  # or just ["Volume"]
        data: StockDataFrame = SingleStockData.validate(data)
    else:
        # Collapse it into flat columns for validation
        data = data.stack(level=-1).reset_index().rename(columns={"level_1": "Ticker"})
        data: StockDataFrame = MultipleStockData.validate(data)

    return data
