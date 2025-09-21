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

from typing import Any

import yfinance as yf
from constants.sectors import SECTORS
from models.base import Ticker
from schemas.market import MarketData
from utils.helpers import timer, yf_ticker_to_model


@timer
def load_mapping() -> dict[str, list[str]]:
    """
    Loads sector and industry data.

    Returns:
        A dictionary mapping sectors with their relevant industries.
    """
    sector_to_industry_mapping = {sector: [] for sector in SECTORS}

    for sector in SECTORS:
        industry_list = get_industries(sector)
        sector_to_industry_mapping[sector] = industry_list

    return sector_to_industry_mapping


@timer
def get_industries(sector_key: str) -> list[str]:
    """Retrieves a list of industries within a domain sector.

    Args:
        sector_key (str): sector key from yfinance API.

    Returns:
        A list of industries within a sector.
    """
    sector = yf.Sector(sector_key)
    industries = sector.industries
    return list(industries.index)


@timer
def get_top_performers_by_industry(industry: str) -> list[str]:
    """
    Retrieves an industries top performers (at most 5).

    Args:
        industry (str): Industry key as specified in yfinance API

    Returns:
        A list of tickers of top performing companies
    """
    industry_data = yf.Industry(industry)
    top_performers = industry_data.top_performing_companies
    return list(top_performers.index) if top_performers is not None else []


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
    ticker = yf_ticker_to_model(symbol=ticker_symbol, **kwargs)
    return ticker


@timer
def get_ticker_data(ticker_symbols: str | list[str], **kwargs: Any) -> MarketData:
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
    data = yf.download(tickers=ticker_symbols, **kwargs)

    # Handle single vs multi-ticker cases:
    if isinstance(ticker_symbols, str):
        data.columns = data.columns.droplevel(1)
        validated = MarketData.validate(data)
    else:
        print("multplie tickers coming right up!")
    #     # Multi-ticker case: yfinance gives column MultiIndex
    #     # Collapse it into flat columns for validation
    #     data = data.stack(level=0).rename_axis(["Date", "Ticker"]).reset_index()
    #     validated = MarketData.validate(data)

    return validated
