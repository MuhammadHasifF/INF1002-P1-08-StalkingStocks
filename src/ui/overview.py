"""
ui/overview.py
==============
Streamlit UI renderers for sector & industry summaries and ticker charts.

Main entry points
-----------------
- display_sector_overview(column, sector_data): high-level sector metrics.
- display_industry_overview(column, industries): treemap of industry weights and daily change.
- display_basic_price_info(ticker_info, ticker_data): headline price stats (cached).
- display_charts(column, filters): price chart(s), indicators, and summary text.

Dependencies
------------
- Data/services: src.services.finance (ticker/industry fetch), src.services.core (analytics).
- Charts: src.ui.charts (Plotly builders).
- Utils: src.utils.helpers (formatters, timer).
- Streamlit for rendering; functions primarily produce side effects on `column`.

Notes
-----
- Cached helpers (`@st.cache_data`) are used to reduce repeated API calls during interaction.
- Expects ticker/industry dataframes with standard OHLC columns and datetime index.
"""

from typing import Any, Sequence

import pandas as pd
import streamlit as st

from src.services.core import (compute_max_profit, compute_sdr, compute_sma,
                               compute_streak)
from src.services.finance import (get_industry_info, get_ticker_data,
                                  get_ticker_info)
from src.ui.charts import (add_indicators, create_figure, set_candlechart,
                           set_line_trend_chart, set_linechart, set_treemap)
from src.utils.helpers import (format_date, format_large_number, format_name,
                               timer)


def display_sector_overview(column, sector_data) -> None:
    """
       Render the sector overview panel.

       Parameters
       ----------
       column
           Streamlit container/column used to render widgets.
       sector_data
           Object with `.name` and `.overview` mapping that includes
           description, company/industry counts, employee_count, market_cap,
           and market_weight.
    """
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


@st.cache_data
def create_industry_overview(industries):
    """
       Compute a cached industry overview mapping.

       Parameters
       ----------
       industries : Iterable[str]
           Industry identifiers.

       Returns
       -------
       dict
           {formatted_industry_name: {"weight": float, "pct_change": float}}
    """
    # RATIONALE (dev note):
    # - Cache industry stats to avoid repeated API calls during UI interactions.
    # - `format_name` normalizes display names for the treemap.
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
    """
        Render the sector’s industry breakdown (treemap).

        Parameters
        ----------
        column
            Streamlit container/column for rendering.
        industries : Iterable[str]
            Industry identifiers to summarize.
    """
    # DEV NOTE:
    # - Creates a DataFrame for Plotly treemap; color column derived from pct_change sign.
    column.subheader("Sector Breakdown")
    column.info("This shows a sector's industry weights and how they performed today.", icon=":material/info:")
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
    """
        Render top-level price metrics for the current ticker.

        Parameters
        ----------
        ticker_info
            Object providing `price`, `long_name`, `symbol`, and `description`.
        ticker_data : pd.DataFrame
            OHLCV data with columns: Open, High, Low, Close (indexed by datetime).

        Returns
        -------
        None
            Renders Streamlit metrics directly.
    """
    # RATIONALE (dev note):
    # - Computes simple daily return (SDR) for last point; guards a corner case where
    #   horizon/interval combinations yield a single row.
    close = ticker_data["Close"]
    open = ticker_data["Open"]
    high = ticker_data["High"]
    low = ticker_data["Low"]
    sdr = compute_sdr(close)

    # Handles NoneType/short series when interval and horizon match.
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
    """
        Render price chart(s), indicators, and summary stats for a ticker.

        Parameters
        ----------
        column
            Streamlit container/column for rendering.
        filters : dict[str, Any]
            Output from `display_filters`, including:
            - selected_ticker: str
            - selected_horizon: {"start": datetime, "end": datetime}
            - selected_interval: str
            - selected_indicators: list[int]
            - selected_chart_type: str

        Returns
        -------
        None
            Renders Plotly charts and text directly.
    """
    # DATA FETCH (dev note):
    # - `auto_adjust=True` for adjusted prices; `progress=False` to keep UI clean.
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

    # DEV NOTE:
    # - Keeps branching for chart types; indicators are added afterward.
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

        # SUMMARY TEXT (dev note):
        # - Uses greedy max-profit metric as a quick “best sequence” indicator.
        max_profit = compute_max_profit(close)
        horizon = filters["selected_horizon"]
        start_date = horizon["start"]
        end_date = horizon["end"]

        column.markdown(
            f"**In your best trading sequence from :red[{format_date(start_date)}] to :red[{format_date(end_date)}], could have earned :green[${max_profit:.2f}] total profit.**"
        )

        with column.expander(f"{display_name} Overview"):
            st.write(ticker_info.description)
