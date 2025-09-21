"""
market.py

This module defines dataframe models used to validate OHLCV
(open, high, low, close, volume) data retrieved from yfinance.
"""

import pandera.pandas as pa
from pandera.typing import Series


class MarketData(pa.DataFrameModel):
    """Schema for validating historical market price and volume data."""

    Close: Series[float]
    High: Series[float]
    Low: Series[float]
    Open: Series[float]
    Volume: Series[int]

    class Config:
        coerce = True
        strict = False  # allow extra columns if yfinance adds fields
