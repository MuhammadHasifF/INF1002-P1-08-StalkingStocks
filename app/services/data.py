"""
data.py

This module contains functionalities related to data preprocessing and ingestion
for the finance dashboard application. It provides utilities to load and map
sector information to their respective industries.
"""

from constants.sectors import SECTORS
from services.finance import get_industries


def load_mapping() -> dict[str, list[str]]:
    sector_to_industry_mapping = {sector: [] for sector in SECTORS}

    for sector in SECTORS:
        industry_list = get_industries(sector)
        sector_to_industry_mapping[sector] = industry_list

    return sector_to_industry_mapping
