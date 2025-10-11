import streamlit as st

from src.ui.filters import display_filters
from src.ui.overview import (display_charts, display_industry_overview,
                             display_sector_overview)
from src.utils.helpers import timer


def configure_page() -> None:
    st.set_page_config(page_title="Stalking Stocks", page_icon="📈", layout="wide")


def display_header() -> None:
    st.title("📈 Stalking Stocks")
    st.markdown(
        "<small style='color: gray;'>Made by Aamir, Dalton, Gin, Hasif, and Tim.</small>",
        unsafe_allow_html=True,
    )


def display_sector_industry_overview():
    """contains sector and industry overview sections"""
    sector_col, industry_col = st.columns(2, border=True)
    sector_data = display_sector_overview(sector_col)
    display_industry_overview(industry_col, sector_data.industries)
    return sector_data.model_dump()  # this will be passed to filters


def display_filter_and_charts(sector_data):
    """contains filter and chart sections"""
    filter_col, chart_col = st.columns([1, 3], border=True)
    filters = display_filters(filter_col, sector_data)
    display_charts(chart_col, filters)


def display_body():
    # sector data will be passed to filters for chart generation
    sector_data = display_sector_industry_overview()
    display_filter_and_charts(sector_data)


@timer
def run_dashboard():
    configure_page()
    display_header()
    display_body()
