from typing import Sequence
import plotly.express as px
from pandas import DataFrame
import plotly.graph_objs as go
import streamlit as st
from plotly.subplots import make_subplots

# from app.engine.summary import generate_sector_summary
from app.services.core import compute_sdr

from .services.finance import (get_industry_data, get_industry_info, get_sector_data, get_sectors,
                               get_ticker_data, get_ticker_info)
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
    column.subheader("Sector Breakdown by Market Weight")
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
        textfont=dict(size=18)   # 👈 increase label size
    )
    column.plotly_chart(fig, use_container_width=True)

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

    selected_industry = filter_col.selectbox(
        "Choose an industry", sector_data.industries, format_func=format_name
    )

    # selected_top = filter_col.selectbox(
    #     "Select a list",
    #     ["top_companies", "top_etfs", "top_mutual_funds"],
    #     format_func=format_name,
    # )

    selected_ticker = filter_col.selectbox(
        "Select a ticker", sector_data.model_dump()["top_companies"]
    )

    horizon_mapping = {
        "1 Day": {"n": 1, "unit": "days"},  # interval = 1m
        "5 Day": {"n": 5, "unit": "days"},
        "1 Month": {"n": 1, "unit": "months"},
        "6 Month": {"n": 6, "unit": "months"},
        "1 Year": {"n": 1, "unit": "years"},
        "3 Year": {"n": 3, "unit": "years"},
        "5 Year": {"n": 5, "unit": "years"},
    }

    selected_key = filter_col.pills(
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

    selected_interval = filter_col.pills(
        "Data Interval", data_intervals, default=data_intervals[0]
    )

    options = filter_col.multiselect(
        "Technical Indicators",
        ["SMA 5", "SMA 20", "SMA 50"],
        default=[],
    )


    start, end = rolling_window(**selected_horizon)

    ticker_data = get_ticker_data(
        selected_ticker,
        interval=selected_interval,
        start=start,
        end=end,
        progress=False,
        auto_adjust=True,
    )

    if ticker_data is None:
        graph_col.error("No price data was found. Try again.")
    else:
        ticker_info = get_ticker_info(selected_ticker)
        graph_col.subheader(f"{ticker_info.long_name} ({ticker_info.symbol})")
        graph_col.write()

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
        )

        fig.add_trace(
            go.Candlestick(
                x=ticker_data.index,
                open=ticker_data["Open"],
                high=ticker_data["High"],
                low=ticker_data["Low"],
                close=ticker_data["Close"],
                name="Price",
            ),
            row=1,
            col=1,
        )

        # Overlay line chart (e.g., closing price line)
        fig.add_trace(
            go.Scatter(
                x=ticker_data.index,
                y=ticker_data["Close"],
                mode="lines",
                line=dict(color="blue", width=1.5),
                name="Close Price",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Bar(x=ticker_data.index, y=ticker_data["Volume"], name="Volume"),
            row=2,
            col=1,
        )

        fig.update_layout(
            # title=f"Candlestick Chart for {selected_ticker}",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Price"),
            margin=dict(l=0, r=0, t=0, b=0),
        )

        graph_col.plotly_chart(fig)

    # for ind in sector_data.industries:
    #     industry_col.write(get_industry_info(ind))


    # display_industry_overview(industry_col, industry_data)

    # col1, col2 = st.columns(2)
    #
    # st.divider()

    # col1, col2 = st.columns([1, 3], border=True)
    #
    #
    #
    # # get the nested dict directly
    #
    #
    # st.write("You selected:", options)
    #
    #
    #     meow1, meow2, meow3 = st.columns(3)
    #     with col2:
    #         meow1.metric("Companies", overview["companies_count"], border=True)
    #
    #     with col2:
    #         meow2.metric("Industries", overview["industries_count"], border=True)
    #
    #     with col2:
    #         meow3.metric(
    #             "Employees",
    #             format_large_number(overview["employee_count"]),
    #             border=True,
    #         )
    #
