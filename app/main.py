"""
main.py

This is the main entry point for the finance dashboard application.

Note:
    At the moment, I'm using this as the main testing interface with the hope of
    eventually reorganising appropriately.
"""

import streamlit as st
from services.finance import get_sector_data, get_sectors, get_industry_data, get_ticker_data, get_ticker_info
from utils.helpers import timer

@timer
def main() -> None:
    # ticker = st.text_input(label="Enter Ticker...", value="NVDA")
    # info = get_ticker_info(ticker_symbol=ticker)
    # df = get_ticker_data(ticker_symbols=ticker, auto_adjust=True, progress=False)
    # st.write(info) 
    # st.write(df) 
    
    # sectors = get_sectors()
    #
    # for s in tqdm(sectors):
    #     data = get_sector_data(sector_key=s)
    #     st.write(data.industries)
    #     break

    data = get_industry_data('software-application')
    st.subheader("Top Performing")
    st.write(data.top_performing)
    st.subheader("Top Growing")
    st.write(data.top_growing)

if __name__ == "__main__":
    main()
