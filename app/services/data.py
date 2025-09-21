"""
data.py

This module contains functionalities related to data pre/post processing and 
ingestion for each feature within the application.
"""

from utils.helpers import timer
from constants.sectors import SECTORS
from services.finance import get_industries

@timer
def load_mapping() -> dict[str, list[str]]:
    sector_to_industry_mapping = {sector: [] for sector in SECTORS}

    for sector in SECTORS:
        industry_list = get_industries(sector)
        sector_to_industry_mapping[sector] = industry_list

    return sector_to_industry_mapping
