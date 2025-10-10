"""
data.py

This module contains functionalities related to data pre/post processing and
ingestion for each feature within the application.

Notes:
    -
"""

import pandas as pd
import warnings

from src.utils.helpers import timer

@timer
def has_missing(series: pd.Series) -> bool:
    """
    Check if a time series contains any missing values (NaNs).

    RATIONALE:
    - Some UI/analysis paths only need to *know* whether gaps exist to decide
      if messaging/tooltips should appear (transparency) or if filling is required.
    - Separating detection from action matches SRP and keeps pipelines explicit.

    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) — vectorized null check.
    - Space Complexity: O(1) — returns a scalar boolean.

    Args:
        series (pd.Series): Numeric Series indexed by dates (DatetimeIndex or coercible).

    Returns:
        bool: True if at least one element is NaN; False otherwise.

    Edge Cases:
        - All-NaN series → returns True.
        - Non-datetime index is fine; only values are inspected.
    """
    return pd.isna(series).any()

@timer
def fill_gaps(series: pd.Series) -> pd.Series:
    """
    Fill missing values in a time series using forward/back-fill.

    RATIONALE:
    - Financial series may contain small gaps (API hiccups, partial days).
    - Forward-fill (ffill) carries the last known value forward; back-fill (bfill)
      covers leading gaps. Together they remove NaNs without inventing new trends.

    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) — two vectorized passes.
    - Space Complexity: O(n) — returns a new Series (input not mutated).
    - Algorithmic Efficiency: Pure pandas ops; optimal for simple imputation.

    Args:
        series (pd.Series): Numeric Series indexed by dates (DatetimeIndex or coercible).

    Returns:
        pd.Series: Same index/shape as input with NaNs filled (ffill then bfill).

    Edge Cases:
        - All-NaN series → still all-NaN (no value to propagate).
        - Non-datetime index is accepted; only values are imputed here.
    """
    return series.ffill().bfill()

@timer
def check_missing_values(series: pd.Series) -> pd.Series:
    """
    [DEPRECATED NAME] Fill missing values in a time series using forward/back-fill.

    NOTE:
    - This function *fills* values. For detection-only, use `has_missing()`.
    - Preferred filler name is `fill_gaps()`; this alias is kept for compatibility.

    RATIONALE:
    - Matches previous project API while we migrate call sites to clearer names.

    EFFICIENCY ANALYSIS:
    - Time Complexity: O(n) — two vectorized passes via `fill_gaps()`.
    - Space Complexity: O(n) — returns a new Series.

    Args:
        series (pd.Series): Numeric Series indexed by dates.

    Returns:
        pd.Series: Series with NaNs filled (ffill then bfill).
    """
    warnings.warn(
        "check_missing_values() fills values. "
        "Use has_missing() to detect or fill_gaps() to fill. "
        "This alias will remain for compatibility.",
        DeprecationWarning,
        stacklevel=2,
    )
    return fill_gaps(series)


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
    series = fill_gaps(series)
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
      1) fill_gaps(series)
      2) remove_non_trading_days(...)
      3) outlier_mask_iqr(...)

    Returns:
      cleaned: pd.Series        # after gaps filled + weekdays filter
      mask:    pd.Series[bool]  # True where cleaned is flagged by IQR
    """
    cleaned = remove_non_trading_days(fill_gaps(series))
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
