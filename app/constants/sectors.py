"""
sectors.py

This module provides a list of constant sector names used for interfacing with
the yfinance API. The `SECTORS` list can be used when filtering or querying
stock data by sector.

Attributes:
    SECTORS (List[str]): A list of sector names recognized by yfinance.
"""

SECTORS: list[str] = [
    "basic-materials",
    "communication-services",
    "consumer-cyclical",
    "consumer-defensive",
    "energy",
    "financial-services",
    "healthcare",
    "industrials",
    "real-estate",
    "technology",
    "utilities",
]
