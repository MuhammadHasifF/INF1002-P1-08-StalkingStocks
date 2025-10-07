from typing import Any, Sequence

import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
from pandas import DataFrame
from plotly.subplots import make_subplots

# from app.engine.summary import generate_sector_summary
from app.services.core import (compute_max_profit, compute_sdr, compute_sma,
                               compute_streak)

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
        "<small style='color: gray;'>Made by Aamir, Dalton, Gin, Hasif, and Tim.</small>",
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

    industry_info = {}

    for ind in industries:
        info = get_industry_info(ind)
        market_weight = info.market_weight
        pct_change = info.pct_change  # percentage change from previous close
        formatted_ind = format_name(ind)
        industry_info[formatted_ind] = {"weight": market_weight, "pct_change": pct_change}

    # industry_col.write(industry_weights)
    # df = DataFrame(list(industry_weights.items()), columns=["Sub-Industry", "Weight"])
    df = DataFrame.from_dict(industry_info, orient='index').reset_index()
    df.rename(columns={'index': 'industry'}, inplace=True)
    # df["weight"] = df["weight"] * 100  # convert to %
    # column.write(df)

    df['color'] = df['pct_change'].apply(lambda x: 'green' if x >= 0 else 'red')

    fig = px.treemap(
        df,
        path=['industry'],  # unique leaves
        values='weight',
        color=df['pct_change'] >= 0,  # boolean → True/False
        color_discrete_map={True:'#2ca02c', False:'#d62728'},
        custom_data=['pct_change']
    )
    fig.update_traces(
        texttemplate="%{label}<br>Weight: %{value:.2%}<br>Change: %{customdata[0]:.2f}%",
        textfont=dict(size=18)
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
    )


    column.plotly_chart(fig, use_container_width=True)


def display_filters(column, industries, top_companies) -> dict[str, Any]:
    # selected_industry = column.selectbox(
    #     "Choose an industry", industries, format_func=format_name
    # )

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

    # intra_day_intervals = ["1m", "2m", "5m", "15m", "30m", "1h"]
    # daily_intervals = ["5d", "1wk", "1mo", "3mo"]
    #
    # data_intervals = ["1d"]

    # i lazy fix the error here AHHHHHH
    if selected_horizon["unit"] == "days":
        data_intervals = ["1m", "2m", "5m", "15m", "30m", "1h"] 
    elif selected_horizon['unit'] == "days" and selected_horizon['n'] == 5:
        data_intervals = ["1m", "2m", "5m", "15m", "30m", "1h", "1d"] 
    else:
        data_intervals = ["1d", "5d", "1wk", "1mo", "3mo"]

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

    selected_candle = column.checkbox("Show Candlestick Chart")
    selected_trend_runs = column.checkbox("Show Trend Runs")
    # selected_trend_runs = right_container.checkbox("c")

    start, end = rolling_window(**selected_horizon)

    # can change to dataclass/basemodel
    filters = {
        # "selected_industry": selected_industry,
        "selected_ticker": selected_ticker,
        "selected_horizon": (start, end),
        "selected_interval": selected_interval,
        "selected_indicators": selected_indicators,
        "selected_candle": selected_candle,
        "selected_trend_runs": selected_trend_runs,
    }

    return filters


def display_basic_price_info(ticker_info, ticker_data):
    close = ticker_data["Close"]
    open = ticker_data["Open"]
    high = ticker_data["High"]
    low = ticker_data["Low"]
    sdr = compute_sdr(close)
    
    latest_price = ticker_info.price
    latest_return = sdr.iloc[-1] * 100
    previous_close = close.iloc[-2]
    absolute_change = latest_price - previous_close
    latest_open = open[-1]
    days_range = f"{low[-1]:.2f} - {high[-1]:.2f}"

    st.metric(
        "Price", f"{latest_price:.2f} USD", f"{latest_return:.2f} %", border=False
    )
    st.metric("Abs. Change", f"{absolute_change:.2f} USD", border=False)
    st.metric("Today's Open", f"{latest_open:.2f} USD", border=False)
    st.metric("Day's Range", days_range, border=False)

    # max_profit = compute_max_profit(ticker_data["Close"])
    # st.metric("Max Profit", f"{max_profit:.2f} USD")


def display_graphs(column, data, filters) -> None:

    if data is None:
        st.error("Whoops, could not fetch data!")

    ticker_info = get_ticker_info(filters["selected_ticker"])
    up, down, mask = compute_streak(data["Close"])

    display_name = f"{ticker_info.long_name} ({ticker_info.symbol})"

    column.subheader(display_name)

    row = column.container(horizontal=True)
    with row:
        display_basic_price_info(ticker_info, data)

    if data is None:
        column.error("No price data was found. Try again.")
    else:

        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
        )
        fig.update_xaxes(showticklabels=True, row=1, col=1)

        if filters["selected_candle"] and not filters["selected_trend_runs"]:
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
        elif filters["selected_trend_runs"] and not filters["selected_candle"]:
            marker_colors = ["green" if m == 1 or m == 0 else "red" for m in mask]
            mode = "lines+markers"
            line_color = "gray"

            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["Close"],
                    mode=mode,
                    line=dict(color=line_color),  # fallback, ignored by marker coloring
                    marker=dict(color=marker_colors, size=8),  # color points
                    name="Close Price",
                ),
                row=1,
                col=1,
            )

            # Add static annotation (paper coordinates)
            fig.add_annotation(
                x=0.02,
                y=0.98,  # 2% from left, 2% from top
                xref="paper",
                yref="paper",  # relative to figure, not data
                text=f"📈 Longest Up Run: {up} days<br>📉 Longest Down Run: {down} days",
                showarrow=False,
                font=dict(size=13, color="black"),
                align="left",
                bgcolor="rgba(255,255,255,0.6)",  # semi-transparent background for visibility
                bordercolor="black",
                borderwidth=1,
                borderpad=4,
            )

        else:
            mode = "lines"
            line_color = "blue"

            # line chart (e.g., closing price line)
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["Close"],
                    mode=mode,
                    line=dict(color=line_color),  # fallback, ignored by marker coloring
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

        fig.update_layout(
            xaxis=dict(type="date", tickformat="%b %d, %Y"),
            yaxis=dict(title="Price"),
            margin=dict(l=0, r=0, t=0, b=0),
        )

        column.plotly_chart(fig)

        max_profit = compute_max_profit(data["Close"])
        column.markdown(
            f"**Your best trading sequence could have earned :green[${max_profit:.2f}] total profit.**"
        )

        with column.expander(f"{display_name} Overview"):
            st.write(ticker_info.description)


@timer
def run_dashboard():
    configure_page()
    display_header()

    sectors: Sequence[str] = get_sectors()

    sector_col, industry_col = st.columns(2, border=True)
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
