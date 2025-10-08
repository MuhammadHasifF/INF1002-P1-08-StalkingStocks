from typing import Any, Sequence

import pandas as pd
import streamlit as st

from src.services.core import (compute_max_profit, compute_sdr, compute_sma,
                               compute_streak)
from src.services.finance import (get_industry_info, get_sector_data,
                                  get_sectors, get_ticker_data,
                                  get_ticker_info)
from src.ui.charts import (add_indicators, create_figure, set_candlechart,
                           set_line_trend_chart, set_linechart, set_treemap)
from src.utils.helpers import (format_date, format_large_number, format_name,
                               timer)


def display_sector_overview(column) -> list[str]:
    sectors: Sequence[str] = get_sectors()

    selected_sector = column.selectbox(
        "Choose a sector", 
        options=sectors, 
        index=9, 
        format_func=format_name
    )
    sector_data = get_sector_data(selected_sector)

    overview = sector_data.overview

    column.subheader(sector_data.name)
    column.text(overview["description"])

    left, middle, right = column.columns(3, border=True)

    left.metric("Companies", overview["companies_count"])
    middle.metric("Industries", overview["industries_count"])
    right.metric("Employees", format_large_number(overview["employee_count"]))

    left, right = column.columns(2, border=True)

    left.metric("Market Cap", f"{format_large_number(overview["market_cap"])} USD")
    right.metric("Market Weight", f"{overview['market_weight']*100:.2f}%")

    return sector_data


@st.cache_data
def create_industry_overview(industries):
    industry_info = {}

    for ind in industries:
        info = get_industry_info(ind)
        market_weight = info.market_weight
        pct_change = info.pct_change  # percentage change from previous close
        formatted_ind = format_name(ind)
        industry_info[formatted_ind] = {
            "weight": market_weight,
            "pct_change": pct_change,
        }

    return industry_info


def display_industry_overview(column, industries) -> None:
    column.subheader("Sector Breakdown")
    column.info(
        "This shows a sector's industry weights and how they performed today.",
        icon=":material/info:",
    )
    industry_info = create_industry_overview(industries)
    summary_df = pd.DataFrame.from_dict(industry_info, orient="index").reset_index()
    summary_df.rename(columns={"index": "industry"}, inplace=True)

    summary_df["color"] = summary_df["pct_change"].apply(
        lambda x: "green" if x >= 0 else "red"
    )

    fig = set_treemap(summary_df)

    column.plotly_chart(fig, use_container_width=True)


@st.cache_data
def display_basic_price_info(ticker_info, ticker_data):
    close = ticker_data["Close"]
    open = ticker_data["Open"]
    high = ticker_data["High"]
    low = ticker_data["Low"]
    sdr = compute_sdr(close)

    # handles NoneType error when interval and horizon match
    if sdr.isna().any() and len(sdr) == 1:
        st.error("Whoops, could not fetch data!")
    else:
        latest_price = ticker_info.price
        latest_return = sdr.iloc[-1]
        previous_close = close.iloc[-2]
        absolute_change = latest_price - previous_close
        latest_open = open[-1]
        days_range = f"{low[-1]:.2f} - {high[-1]:.2f}"

        st.metric(
            "Price", f"{latest_price:.2f} USD", f"{latest_return:.2%}", border=False
        )
        st.metric("Abs. Change", f"{absolute_change:.2f} USD", border=False)
        st.metric("Today's Open", f"{latest_open:.2f} USD", border=False)
        st.metric("Day's Range", days_range, border=False)


def display_charts(column, filters) -> None:
    ticker_data = get_ticker_data(
        filters["selected_ticker"],
        interval=filters["selected_interval"],
        **filters["selected_horizon"],
        progress=False,
        auto_adjust=True,
    )

    if ticker_data is None:
        st.error("Whoops, could not fetch data!")

    ticker_info = get_ticker_info(filters["selected_ticker"])
    close = ticker_data["Close"]
    up, down, mask = compute_streak(close)

    display_name = f"{ticker_info.long_name} ({ticker_info.symbol})"

    column.subheader(display_name)

    row = column.container(horizontal=True)

    with row:
        display_basic_price_info(ticker_info, ticker_data)

    if ticker_data is None:
        column.error("No price data was found. Try again.")
    else:
        fig = create_figure()

        if filters["selected_chart_type"] == "Line Chart":
            fig = set_linechart(fig, close)
        elif filters["selected_chart_type"] == "Line Chart and Trend Markers":
            fig = set_line_trend_chart(fig, close, up, down, mask)
        else:
            fig = set_candlechart(fig, ticker_data)

        for n in filters["selected_indicators"]:
            computed_close = compute_sma(close, n)
            fig = add_indicators(fig, computed_close, n)

        fig.update_layout(
            xaxis=dict(type="date", tickformat="%b %d, %Y"),
            yaxis=dict(title="Price"),
            margin=dict(l=0, r=0, t=0, b=0),
        )

        column.plotly_chart(fig, use_container_width=True)

        max_profit = compute_max_profit(close)
        horizon = filters["selected_horizon"]
        start_date = horizon["start"]
        end_date = horizon["end"]

        column.markdown(
            f"**In your best trading sequence from :red[{format_date(start_date)}] to :red[{format_date(end_date)}], could have earned :green[${max_profit:.2f}] total profit.**"
        )

        with column.expander(f"{display_name} Overview"):
            st.write(ticker_info.description)
