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


def get_ticker(ticker_symbol: str, **kwargs: Any):
    """

    Returns:
        Single-level dataframe.
    """
    kwargs.pop("tickers", None)  # remove if exists
    data = yf.download(tickers=ticker_symbol, **kwargs)
    return data


def get_tickers(ticker_symbols: list[str], **kwargs: Any):
    """

    Returns:
        Multi-indexed dataframe.
    """
    kwargs.pop("tickers", None)  # remove if exists
    data = yf.download(tickers=ticker_symbols, **kwargs)
    return data
