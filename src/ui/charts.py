"""
charts.py

this module handles chart generation
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def create_figure() -> go.Figure:
    fig: go.Figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
    )
    fig.update_xaxes(showticklabels=True, row=1, col=1)
    return fig


def set_treemap(summary_df: pd.DataFrame) -> go.Figure:
    fig: go.Figure = px.treemap(
        summary_df,
        path=["industry"],  # unique leaves
        values="weight",
        color=summary_df["pct_change"] >= 0,  # boolean → True/False
        color_discrete_map={True: "#2ca02c", False: "#d62728"},
        custom_data=["pct_change"],
    )
    fig.update_traces(
        texttemplate="%{label}<br>Weight: %{value:.2%}<br>Change: %{customdata[0]:.2f}%",
        textfont=dict(size=18),
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
    )

    return fig


def set_linechart(fig: go.Figure, close: pd.Series) -> go.Figure:
    """Simple line chart of closing prices."""
    fig.add_trace(
        go.Scatter(
            x=close.index,
            y=close.values,
            mode="lines",
            line=dict(color="blue"),
            name="Close Price",
        )
    )
    return fig


def set_line_trend_chart(
    fig: go.Figure, close: pd.Series, up: pd.Series, down: pd.Series, mask: pd.Series
) -> go.Figure:
    marker_colors = ["green" if m == 1 or m == 0 else "red" for m in mask]
    mode = "lines+markers"
    line_color = "gray"

    fig.add_trace(
        go.Scatter(
            x=close.index,
            y=close.values,
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
    return fig


def set_candlechart(fig: go.Figure, ticker_data: pd.DataFrame) -> go.Figure:
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
    return fig


def add_indicators(fig: go.Figure, close: pd.Series, n: int) -> go.Figure:
    """Add SMA or other indicators to existing figure."""
    fig.add_trace(
        go.Scatter(
            x=close.index, y=close, mode="lines", line=dict(width=1.5), name=f"SMA {n}"
        )
    )

    return fig
