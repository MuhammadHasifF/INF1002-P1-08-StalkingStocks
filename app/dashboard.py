from typing import Any, Sequence

import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
from pandas import DataFrame
from plotly.subplots import make_subplots

# from app.engine.summary import generate_sector_summary
from app.services.core import compute_sdr, compute_sma

from .services.finance import (get_industry_data, get_industry_info,
                               get_sector_data, get_sectors, get_ticker_data,
                               get_ticker_info)
from .utils.helpers import (format_large_number, format_name, rolling_window,
                            timer)


def configure_page() -> None:
    st.set_page_config(page_title="Stalking Stocks", page_icon="📈", layout="wide")


def display_header() -> None:
    st.title("📈 Stalking Stocks")
    st.markdown(
        "<small style='color: gray;'>Made by Tim, Gin, Hasif, Dalton, Aamir</small>",
        unsafe_allow_html=True,
    )


def display_sector_overview(column, sector_data) -> None:
    overview = sector_data.overview
    # top_companies = sector_data.top_companies
    # top_etfs = sector_data.top_etfs
    # top_mutual_funds = sector_data.top_mutual_funds
    # industries = sector_data.industries

    column.subheader(sector_data.name)
    column.text(overview["description"])

    left, middle, right = column.columns(3, border=True)
    left.metric("Companies", overview["companies_count"])
    middle.metric("Industries", overview["industries_count"])
    right.metric("Employees", format_large_number(overview["employee_count"]))

    left, right = column.columns(2, border=True)
    left.metric("Market Cap", f"{format_large_number(overview["market_cap"])} USD")
    right.metric("Market Weight", f"{overview['market_weight']*100:.2f}%")


def display_industry_overview(column, industries) -> None:
    column.subheader("Sector Breakdown")
    industry_weights = {
        format_name(ind): get_industry_info(ind).market_weight for ind in industries
    }

    # industry_col.write(industry_weights)
    df = DataFrame(list(industry_weights.items()), columns=["Sub-Industry", "Weight"])
    # df["Weight"] = df["Weight"] * 100  # convert to %

    fig = px.treemap(
        df,
        path=["Sub-Industry"],
        values="Weight",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
    )
    fig.update_traces(
        texttemplate="%{label}<br>%{value:.2%}",  # show label and percentage
        textfont=dict(size=18),  # 👈 increase label size
    )
    column.plotly_chart(fig, use_container_width=True)


def display_filters(column, industries, top_companies) -> dict[str, Any]:
    selected_industry = column.selectbox(
        "Choose an industry", industries, format_func=format_name
    )

    # selected_top = filter_col.selectbox(
    #     "Select a list",
    #     ["top_companies", "top_etfs", "top_mutual_funds"],
    #     format_func=format_name,
    # )

    selected_ticker = column.selectbox("Select a ticker", top_companies)

    horizon_mapping = {
        "1 Day": {"n": 1, "unit": "days"},  # interval = 1m
        "5 Day": {"n": 5, "unit": "days"},
        "1 Month": {"n": 1, "unit": "months"},
        "6 Month": {"n": 6, "unit": "months"},
        "1 Year": {"n": 1, "unit": "years"},
        "3 Year": {"n": 3, "unit": "years"},
        "5 Year": {"n": 5, "unit": "years"},
    }

    selected_key = column.pills(
        "Time Horizon", options=list(horizon_mapping.keys()), default="1 Year"
    )

    selected_horizon = horizon_mapping[selected_key]

    intra_day_intervals = ["1m", "2m", "5m", "15m", "30m", "1h"]
    daily_intervals = ["5d", "1wk", "1mo", "3mo"]

    data_intervals = ["1d"]

    if selected_horizon["unit"] == "days":
        data_intervals = intra_day_intervals + data_intervals
    else:
        data_intervals += daily_intervals

    selected_interval = column.pills(
        "Data Interval", data_intervals, default=data_intervals[0]
    )

    indicator_mapping = {"SMA 5": 5, "SMA 20": 20, "SMA 50": 50}

    tech_indicators = column.multiselect(
        "Technical Indicators",
        options=list(indicator_mapping.keys()),
        default=[],
    )
    selected_indicators = [indicator_mapping[ind] for ind in tech_indicators]

    selected_candle = column.checkbox(
        "Candlestick Chart",
    )

    start, end = rolling_window(**selected_horizon)

    # can change to dataclass/basemodel
    filters = {
        "selected_industry": selected_industry,
        "selected_ticker": selected_ticker,
        "selected_horizon": (start, end),
        "selected_interval": selected_interval,
        "selected_indicators": selected_indicators,
        "selected_candle": selected_candle,
    }

    return filters


def display_graphs(column, data, filters) -> None:
    if data is None:
        column.error("No price data was found. Try again.")
    else:
        ticker_info = get_ticker_info(filters["selected_ticker"])
        column.subheader(f"{ticker_info.long_name} ({ticker_info.symbol})")
        column.write()

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
        )

        if filters["selected_candle"]:
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data["Open"],
                    high=data["High"],
                    low=data["Low"],
                    close=data["Close"],
                    name="Price",
                ),
                row=1,
                col=1,
            )
        else:
            # Overlay line chart (e.g., closing price line)
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["Close"],
                    mode="lines",
                    line=dict(color="blue", width=1.5),
                    name="Close Price",
                ),
                row=1,
                col=1,
            )

        for n in filters["selected_indicators"]:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=compute_sma(data["Close"], n),
                    mode="lines",
                    line=dict(width=1.5),
                    name=f"SMA {n}",
                ),
                row=1,
                col=1,
            )

        # fig.add_trace(
        #     go.Bar(x=ticker_data.index, y=ticker_data["Volume"], name="Volume"),
        #     row=2,
        #     col=1,
        # )

        fig.update_layout(
            # title=f"Candlestick Chart for {selected_ticker}",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Price"),
            margin=dict(l=0, r=0, t=0, b=0),
        )

        column.plotly_chart(fig)


@timer
def run_dashboard():
    configure_page()
    display_header()

    sector_col, industry_col = st.columns(2, border=True)
    sectors: Sequence[str] = get_sectors()

    selected_sector = sector_col.selectbox(
        "Choose a sector", sectors, index=9, format_func=format_name
    )

    sector_data = get_sector_data(selected_sector)

    display_sector_overview(sector_col, sector_data)
    display_industry_overview(industry_col, sector_data.industries)

    filter_col, graph_col = st.columns([1, 3], border=True)

    sector_dict = sector_data.model_dump()
    filters = display_filters(
        filter_col, sector_dict["industries"], sector_dict["top_companies"]
    )

    start, end = filters["selected_horizon"]
    ticker_data = get_ticker_data(
        filters["selected_ticker"],
        interval=filters["selected_interval"],
        start=start,
        end=end,
        progress=False,
        auto_adjust=True,
    )

    display_graphs(graph_col, ticker_data, filters)
