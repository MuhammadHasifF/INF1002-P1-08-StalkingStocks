"""
base.py

This module defines Pydantic data models representing financial entities
such as industries, sectors, and individual stock tickers.
These models can be used for data validation, serialization, and
interfacing with APIs or other data sources.

Notes:
    This module is experimental and may change in future releases.
    API and data model structures are not yet finalized.

Classes:
    Industry: Represents an industry and its top-performing companies.
    Sector: Represents a market sector containing multiple industries.
    Ticker: Represents an individual stock with relevant financial attributes.
"""

from pydantic import BaseModel


class Industry(BaseModel):
    """Represents an industry and its top-performing companies."""

    top_performers: list[str]


class Sector(BaseModel):
    """Represents a market sector containing multiple industries."""

    key: str
    name: str
    industries: list[Industry]


class Ticker(BaseModel):
    """Represents an individual stock with financial attributes."""

    symbol: str
    name: str
    market_cap: float
    price: float
    sector: str
    industry: str
