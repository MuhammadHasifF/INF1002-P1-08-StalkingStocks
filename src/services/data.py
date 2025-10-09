"""
data.py

This module contains functionalities related to data pre/post processing and
ingestion for each feature within the application.

Notes:
    -
"""

import pandas as pd

from src.utils.helpers import timer


@timer
def check_missing_values(series: pd.Series) -> pd.Series:
    """
    Fill missing values in a time series using forward/back-fill.

    RATIONALE:
    - Financial time series may contain small gaps (API hiccups, partial days).
    - Forward-fill (ffill) carries the last known value forward; back-fill (bfill)
      covers leading gaps at the start. Together they remove NaNs without
      inventing new trends.

    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) — a couple of vectorized passes on the Series.
    - Space Complexity: O(n) — returns a new Series (input is not mutated).
    - Algorithmic Efficiency: Optimal for simple imputation; pure pandas ops.

    Args:
        series (pd.Series): Numeric Series indexed by dates (DatetimeIndex or coercible).

    Returns:
        pd.Series: Same index/shape as input with NaNs filled (ffill then bfill).

    Edge Cases:
        - All-NaN series returns all-NaN (no value to propagate).
        - Non-datetime index is accepted; only values are imputed here.
    """
    return series.ffill().bfill()


@timer
def remove_non_trading_days(series: pd.Series) -> pd.Series:
    """
    Remove weekend rows from a daily time series (Mon–Fri kept).

    RATIONALE:
    - Yahoo Finance typically returns trading days only, but upstream joins or
      exports may introduce weekends. Indicators and charts should operate on
      trading days for consistency.

    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) — boolean mask on the index.
    - Space Complexity: O(n) — returns a filtered view/copy of the Series.
    - Algorithmic Efficiency: Vectorized filter; minimal overhead.

    Args:
        series (pd.Series): Series with a DatetimeIndex (or coercible via to_datetime).

    Returns:
        pd.Series: Series filtered to weekdays only (dayofweek 0..4).

    Notes:
        - If the index is not datetime-like, it is converted via `pd.to_datetime`.
        - This function does not remove exchange holidays (weekdays with no trading);
          those generally do not appear in Yahoo data.
    """
    s = series.copy()
    if not isinstance(s.index, pd.DatetimeIndex):
        s.index = pd.to_datetime(s.index)
    return s[s.index.dayofweek < 5]  # 0=Mon ... 4=Fri


def clean_data(series: pd.Series) -> pd.Series:
    series = check_missing_values(series)
    cleaned = remove_non_trading_days(series)
    return cleaned

@timer
def outlier_mask_iqr(series: pd.Series, k: float = 3.0) -> pd.Series:
    """
    Detect potential outliers in a numeric Series using Tukey IQR fences.
    Detection-only: returns a boolean mask aligned to `series` (True = flagged).

    RATIONALE:
    - For stock analysis, don’t silently alter values. Flag them and let users decide.
    - IQR is robust to spikes and doesn’t assume normality.

    METHOD:
        Q1 = 25th percentile, Q3 = 75th percentile, IQR = Q3 - Q1
        Lower = Q1 - k*IQR, Upper = Q3 + k*IQR
        Flag if value < Lower or value > Upper

    COMPLEXITY:
    - O(n) for quantiles + vectorized mask; returns boolean Series (same index/len).
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    return ((series < lower) | (series > upper)).astype(bool).reindex(series.index)


@timer
def outlier_bounds_iqr(series: pd.Series, k: float = 3.0) -> dict:
    """
    Return Tukey IQR stats for UI/tooltips: Q1, Q3, IQR, Lower, Upper, k.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower": q1 - k * iqr,
        "upper": q3 + k * iqr,
        "k": k,
    }


@timer
def clean_data_with_mask(series: pd.Series, k: float = 3.0):
    """
    Compose existing cleaning + outlier detection (no mutation of values).

    FLOW:
      1) check_missing_values(series)
      2) remove_non_trading_days(...)
      3) outlier_mask_iqr(...)

    Returns:
      cleaned: pd.Series        # after gaps filled + weekdays filter
      mask:    pd.Series[bool]  # True where cleaned is flagged by IQR
    """
    cleaned = remove_non_trading_days(check_missing_values(series))
    mask = outlier_mask_iqr(cleaned, k=k)
    return cleaned, mask

@timer
def clean_outliers_iqr(
    series: pd.Series, replace_with_nan: bool = True, k: float = 3.0
) -> pd.Series:
    """
    Handle outliers in a numeric Series using Tukey IQR fences.

    RATIONALE:
    - Extreme values (bad ticks, split artifacts, data glitches) can distort
      indicators and dashboards. IQR is robust to spikes and does not assume
      normality (unlike z-score).

    METHOD:
        Q1 = 25th percentile, Q3 = 75th percentile, IQR = Q3 - Q1
        Lower = Q1 - k * IQR
        Upper = Q3 + k * IQR
        Outlier if value < Lower or value > Upper

    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) — percentile estimates + a vectorized mask.
    - Space Complexity: O(n) — returns a new Series (masked or clipped).
    - Algorithmic Efficiency: Vectorized; no Python loops.

    Args:
        series (pd.Series): Numeric Series (e.g., Close or Volume) with any index.
        replace_with_nan (bool): If True, mask outliers to NaN; if False, clip to [Lower, Upper].
        k (float): IQR multiplier. Use 1.5 for classic Tukey; 3.0 stricter for blue-chip stability.

    Returns:
        pd.Series: Cleaned Series (same index), with outliers masked or clipped.

    Edge Cases:
        - All-constant series → IQR=0 → Lower=Upper; no values flagged.
        - Heavy-tailed distributions may flag more points; tune `k` as needed.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr

    if replace_with_nan:
        return series.mask((series < lower) | (series > upper))
    else:
        return series.clip(lower=lower, upper=upper)
