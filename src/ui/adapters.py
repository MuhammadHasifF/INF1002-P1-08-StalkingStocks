"""
converts domain to view data
"""

from typing import Any, Sequence

import pandas as pd
import streamlit as st

from src.services.core import (compute_max_profit, compute_sdr, compute_sma,
                               compute_streak)
from src.services.data import clean_data
from src.services.finance import (IndustryOverview, get_industry_overview,
                                  get_sector_data, get_sectors,
                                  get_ticker_data, get_ticker_info)
from src.utils.helpers import format_date, format_name


def make_sector_inputs(column):
    sectors: Sequence[str] = get_sectors()

    selected_sector = column.selectbox(
        "Choose a sector", options=sectors, index=9, format_func=format_name
    )

    sector_data = get_sector_data(selected_sector)
    overview = sector_data.overview
    return sector_data, overview


def make_price_metrics(ticker_info, ticker_data):
    # keep in mind, ticker_data is already cleaned
    close = ticker_data["Close"]
    open = ticker_data["Close"]
    high = ticker_data["Close"]
    low = ticker_data["Open"]

    # handles NoneType error when interval and horizon match
    if close.isna().any() and len(close) == 1:
        st.error("Whoops, could not fetch data!")
    else:
        sdr = compute_sdr(close)
        latest_price = ticker_info.price
        latest_return = sdr.iloc[-1]
        previous_close = close.iloc[-2]
        absolute_change = latest_price - previous_close
        latest_open = open.iloc[-1]
        days_range = f"{low.iloc[-1]:.2f} - {high.iloc[-1]:.2f}"

        return {
            "sdr": sdr,
            "latest_price": latest_price,
            "latest_return": latest_return,
            "previous_close": previous_close,
            "absolute_change": absolute_change,
            "latest_open": latest_open,
            "days_range": days_range,
        }


@st.cache_data
def make_industry_summary_df(industries: list[str]) -> pd.DataFrame:
    """Convert service data → display-ready DataFrame (adds formatted name + color)."""
    overview: IndustryOverview = get_industry_overview(industries)
    df = pd.DataFrame(list(overview))  # realize iterable once
    df.rename(columns={"industry": "raw_industry"}, inplace=True)

    df.insert(0, "industry", df["raw_industry"].map(format_name))
    df["color"] = df["pct_change"].apply(lambda x: "green" if float(x) >= 0 else "red")

    return df[["industry", "weight", "pct_change", "color"]]


def make_indicator_inputs(close, indicators):
    out = {}

    for n in indicators:
        out[n] = compute_sma(close, n)
    return out


def clean_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["Open", "High", "Low", "Close"]
    # guard against missing columns
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")
    return df[cols].apply(clean_data, axis=0)


@st.cache_data
def make_chart_inputs(filters: dict[str, Any]) -> dict[str, Any]:
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

    return {
        "ticker_info": ticker_info,
        "ticker_data": cleaned,
        "up_streaks": up,
        "down_streaks": down,
        "streak_mask": mask,
    }


def make_insight_input(close, horizon):
    max_profit = compute_max_profit(close)
    start_date = format_date(horizon["start"])
    end_date = format_date(horizon["end"])

    return max_profit, start_date, end_date
