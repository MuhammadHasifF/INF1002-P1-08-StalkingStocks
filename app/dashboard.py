import streamlit as st

from .services.finance import get_sector_data, get_sectors, get_ticker_data
from .utils.helpers import format_name, timer


@timer
def run_dashboard():
    st.title("Stalking Stocks")
    sectors: tuple[str] = get_sectors()
    # st.write(sectors)
    # st.write([format_name(s) for s in sectors])
    selection: str = st.pills(
        "Sectors", options=sectors, selection_mode="single", default=sectors[9]
    )
    # selected_sector: str = format_name(selection)

    st.write(f"Showing information on {selection}:")
    data = get_sector_data(selection)
    # overview = data.overview
    # top_companies = data.top_companies
    industries = data.industries

    st.write(industries)

    # st.write(overview)
    # st.write(get_ticker_data(top_companies, progress=False, auto_adjust=True))
    # st.write(industries)
    # selection: str = st.pills(
    #     "Industries", options=industries, selection_mode="single", default=industries[0]
    # )
