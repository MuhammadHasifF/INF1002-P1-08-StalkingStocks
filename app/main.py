"""
main.py

This is the main entry point for the finance dashboard application.

Note:
    At the moment, I'm using this as the main testing interface with the hope of
    eventually reorganising appropriately.
"""

import streamlit as st
from services.finance import get_ticker_data, get_ticker_info
from utils.helpers import timer


@timer
def main() -> None:
    ticker = st.text_input(label="Enter Ticker...", value="NVDA")
    info = get_ticker_info(ticker_symbol=ticker)
    df = get_ticker_data(ticker_symbols=ticker, auto_adjust=True, progress=False)

    st.write(info) 
    st.write(df) 


if __name__ == "__main__":
    main()
