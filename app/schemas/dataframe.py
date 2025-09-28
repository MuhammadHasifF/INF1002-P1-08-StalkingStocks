"""
market.py

This module defines dataframe models/schema used to validate OHLCV
(open, high, low, close, volume) data retrieved from yfinance.

Notes:
    - `DataFrameModel` is used instead of `SchemaModel`, which will be deprecated.
    - In this context, the terms 'model' and 'schema' are used interchangeably to
    describe data validation structures.

Classes:
    TopPerforming: Represents dataframe schema for top performing companies.
    TopGrowing: Represents dataframe schema for top growth companies.
    MarketData: Represents dataframe schema for stock data.
"""

from pandera.pandas import DataFrameModel, Field
from pandera.typing import Series


class TopPerforming(DataFrameModel):
    """Schema for validating top-performing company data."""

    name: Series[str] = Field(nullable=True)
    ytd_return: Series[float] = Field(nullable=True)
    last_price: Series[float] = Field(nullable=True)
    target_price: Series[float] = Field(nullable=True)

    class Config:
        coerce = True
        strict = False  # future proof toallow extra columns


class TopGrowing(DataFrameModel):
    """Schema for validating top-performing company data."""

    name: Series[str] = Field(nullable=True)
    ytd_return: Series[float] = Field(nullable=True)
    growth_estimate: Series[float] = Field(nullable=True)

    class Config:
        coerce = True
        strict = False  # future proof toallow extra columns


class MarketData(DataFrameModel):
    """Schema for validating historical market price and volume data."""

    close: Series[float] = Field(alias='Close')
    high: Series[float] = Field(alias='High')
    low: Series[float] = Field(alias='Low')
    open: Series[float] = Field(alias='Open')
    volume: Series[int] = Field(alias='Volume')

    class Config:
        coerce = True
        strict = False  # allow extra columns if yfinance adds fields


class SingleStockData(DataFrameModel):
    """Schema for validating historical market price and volume data."""
    pass


class MultipleStockData(DataFrameModel):
    """Schema for validating historical (multi-indexed) market price and volume data."""
    pass
