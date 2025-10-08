from typing import Sequence

import streamlit as st

from src.services.finance import get_sector_data, get_sectors
from src.ui.filters import display_filters
from src.ui.overview import (display_charts, display_industry_overview,
                             display_sector_overview)
from src.utils.helpers import format_name, timer


def configure_page() -> None:
    st.set_page_config(page_title="Stalking Stocks", page_icon="📈", layout="wide")


def display_header() -> None:
    st.title("📈 Stalking Stocks")
    st.markdown(
        "<small style='color: gray;'>Made by Aamir, Dalton, Gin, Hasif, and Tim.</small>",
        unsafe_allow_html=True,
    )


def render_sector_overview():
    """contains sector and industry overviews"""
    # need to think where to relocate this
    sectors: Sequence[str] = get_sectors()
    sector_col, industry_col = st.columns(2, border=True)
    selected_sector = sector_col.selectbox(
        "Choose a sector", options=sectors, index=9, format_func=format_name
    )
    sector_data = get_sector_data(selected_sector)
    display_sector_overview(sector_col, sector_data)
    display_industry_overview(industry_col, sector_data.industries)
    return sector_data  # this will be passed to filters


def render_filter_and_charts(sector_data):
    filter_col, chart_col = st.columns([1, 3], border=True)

    sector_dict = sector_data.model_dump()

    # filters are used for chart generation
    filters = display_filters(
        filter_col,
        top_companies=sector_dict["top_companies"],
    )

    display_charts(chart_col, filters)


def display_body():
    # sector data will be passed to filters for chart generation
    sector_data = render_sector_overview()
    render_filter_and_charts(sector_data)


@timer
def run_dashboard():
    configure_page()
    display_header()
    display_body()
