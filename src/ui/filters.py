from typing import Any

from src.utils.helpers import rolling_window


def display_filters(column, top_companies) -> dict[str, Any]:
    """
       Build and return UI filter selections.

       Parameters
       ----------
       column
           Streamlit-like layout object that exposes `selectbox`, `pills`,
           `multiselect`, and `radio`.
       top_companies : Iterable[str]
           Ticker symbols to populate the ticker selector.

       Returns
       -------
       dict[str, Any]
           {
             "selected_ticker": str,
             "selected_horizon": {"start": datetime, "end": datetime},
             "selected_interval": str,
             "selected_indicators": list[int],
             "selected_chart_type": str,
           }
       """
    # Ticker selector
    selected_ticker = column.selectbox(
        "Select a ticker",
        top_companies,
        help="Choose the stock or asset you want to view.",
    )
    # Time horizon presets → arguments for rolling_window()
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
        "Time Horizon",
        options=list(horizon_mapping.keys()),
        default="1 Year",
        help="Select how far back the data should be shown.",
    )

    selected_horizon = horizon_mapping[selected_key]
    # Data interval choices depend on horizon.
    # DEV NOTE: The second `elif` below is unreachable because the first `if`
    # already captures unit == "days". Preserving logic as-is (no behavior change).
    # Consider refactoring to a clear decision table.
    # i lazy fix the error here AHHHHHH
    if selected_horizon["unit"] == "days":
        data_intervals = ["1m", "2m", "5m", "15m", "30m", "1h"]
    elif selected_horizon["unit"] == "days" and selected_horizon["n"] == 5:
        data_intervals = ["1m", "2m", "5m", "15m", "30m", "1h", "1d"]
    elif selected_horizon["unit"] == "months" and selected_horizon["n"] == 1:
        data_intervals = ["1d", "5d", "1wk", "1mo"]
    else:
        data_intervals = ["1d", "5d", "1wk", "1mo", "3mo"]

    selected_interval = column.pills(
        "Data Interval",
        data_intervals,
        default=data_intervals[0],
        help="Select how often data points are sampled (e.g. daily, weekly, or hourly).",
    )
    # Technical indicator presets (e.g., SMA)
    indicator_mapping = {"SMA 5": 5, "SMA 20": 20, "SMA 50": 50}

    tech_indicators = column.multiselect(
        "Technical Indicators",
        options=list(indicator_mapping.keys()),
        default=[],
        help="Apply indicators that reveal trends, momentum, and market strength.",
    )
    selected_indicators = [indicator_mapping[ind] for ind in tech_indicators]
    # Chart type selection
    selected_chart_type = column.radio(
        "Select a chart",
        options=["Line Chart", "Line Chart and Trend Markers", "Candlestick Chart"],
        captions=[
            "Simple view of how values change over time.",
            "Line chart with up/down trend runs.",
            "Shows price highs, lows, open, and close.",
        ],
        index=0,
        help="Choose how you’d like the data displayed.",
    )
    # Convert horizon preset to concrete date range
    start, end = rolling_window(**selected_horizon)

    # DEV NOTE: This could be a dataclass or Pydantic model later for validation.
    filters = {
        "selected_ticker": selected_ticker,
        "selected_horizon": {"start": start, "end": end},
        "selected_interval": selected_interval,
        "selected_indicators": selected_indicators,
        "selected_chart_type": selected_chart_type,
    }

    return filters
