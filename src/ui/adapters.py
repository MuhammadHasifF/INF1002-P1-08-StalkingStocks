"""
converts domain to view data
"""

import pandas as pd
import streamlit as st

from src.services.core import compute_streak
from src.services.data import clean_data
from src.services.finance import (IndustryOverview, get_ticker_data,
                                  get_ticker_info)
from src.utils.helpers import format_name


@st.cache_data
def make_industry_summary_df(items: IndustryOverview) -> pd.DataFrame:
    """Convert service data → display-ready DataFrame (adds formatted name + color)."""
    df = pd.DataFrame(list(items))  # realize iterable once
    df.rename(columns={"industry": "raw_industry"}, inplace=True)

    df.insert(0, "industry", df["raw_industry"].map(format_name))
    df["color"] = df["pct_change"].apply(lambda x: "green" if float(x) >= 0 else "red")

    return df[["industry", "weight", "pct_change", "color"]]


def clean_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Open", "High", "Low", "Close"]
    # guard against missing columns
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")
    return df[cols].apply(clean_data, axis=0)


@st.cache_data
def make_chart_inputs(filters):
    ticker_data = get_ticker_data(
        filters["selected_ticker"],
        interval=filters["selected_interval"],
        **filters["selected_horizon"],
        progress=False,
        auto_adjust=True,
    )

    if ticker_data is None:
        st.error("Whoops, could not fetch data!")

    cleaned = clean_ohlc(ticker_data)

    ticker_info = get_ticker_info(filters["selected_ticker"])
    up, down, mask = compute_streak(cleaned["Close"])
    return ticker_info, cleaned, up, down, mask
