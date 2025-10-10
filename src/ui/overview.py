from typing import Sequence

import streamlit as st

from src.services.core import (compute_max_profit, compute_sdr, compute_sma,
                               compute_streak)
from src.services.finance import (get_industry_overview, get_sector_data,
                                  get_sectors)
from src.ui.adapters import make_chart_inputs, make_industry_summary_df
from src.ui.charts import (add_indicators, create_figure, set_candlechart,
                           set_line_trend_chart, set_linechart, set_treemap)
from src.utils.helpers import (format_date, format_large_number, format_name,
                               timer)


@timer
def display_sector_overview(column) -> list[str]:
    sectors: Sequence[str] = get_sectors()

    selected_sector = column.selectbox(
        "Choose a sector", options=sectors, index=9, format_func=format_name
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


@timer
def display_industry_overview(column, industries) -> None:
    column.subheader("Sector Breakdown")
    column.info(
        "This shows a sector's industry weights and how they performed today.",
        icon=":material/info:",
    )
    overview = get_industry_overview(industries)
    summary_df = make_industry_summary_df(overview)
    fig = set_treemap(summary_df)

    column.plotly_chart(fig, use_container_width=True)


@timer
@st.cache_data
def display_basic_price_info(ticker_info, ticker_data):
    # keep in mind, ticker_data is already cleaned
    close = ticker_data["Close"]
    open = ticker_data["Close"]
    high = ticker_data["Close"]
    low = ticker_data["Open"]
    sdr = compute_sdr(close)

    # handles NoneType error when interval and horizon match
    if sdr.isna().any() and len(sdr) == 1:
        st.error("Whoops, could not fetch data!")
    else:
        latest_price = ticker_info.price
        latest_return = sdr.iloc[-1]
        previous_close = close.iloc[-2]
        absolute_change = latest_price - previous_close
        latest_open = open.iloc[-1]
        days_range = f"{low.iloc[-1]:.2f} - {high.iloc[-1]:.2f}"

        st.metric(
            "Price", f"{latest_price:.2f} USD", f"{latest_return:.2%}", border=False
        )
        st.metric("Abs. Change", f"{absolute_change:.2f} USD", border=False)
        st.metric("Today's Open", f"{latest_open:.2f} USD", border=False)
        st.metric("Day's Range", days_range, border=False)


@timer
def display_charts(column, filters) -> None:
    ticker_info, ticker_data, up, down, mask = make_chart_inputs(filters)
    close = ticker_data["Close"]

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

        # this adds technical indicator overlaid onto existing charts
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
