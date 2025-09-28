"""
main.py

This is the main entry point for the finance dashboard application.
"""

import streamlit as st
from utils.helpers import timer

@timer
def main() -> None:
    st.title("Stalking Stocks") 

if __name__ == "__main__":
    main()
