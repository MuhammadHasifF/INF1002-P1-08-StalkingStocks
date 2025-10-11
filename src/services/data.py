"""
data.py
========
Data preprocessing utilities for time-series ingestion and cleanup.

Functions
---------
- check_missing_values: forward/back-fill gaps.
- remove_non_trading_days: keep weekdays (Mon–Fri) only.
- clean_data: convenience pipeline (fill → weekdays).
- clean_outliers_iqr: IQR-based outlier handling.
"""


import pandas as pd

from src.utils.helpers import timer


@timer
def check_missing_values(series: pd.Series) -> pd.Series:
    """
       Fill gaps in a time series using forward-fill then back-fill.

       Parameters
       ----------
       series : pd.Series
           Numeric Series (any index).

       Returns
       -------
       pd.Series
           Same shape/index with NaNs imputed via ffill → bfill.
       """
    # RATIONALE (dev note):
    # - Small gaps can arise from API hiccups/partial days.
    # - ffill propagates last known value; bfill covers leading NaNs.
    #
    # EFFICIENCY (dev note):
    # - O(n) over the Series; vectorized in pandas.
    # - Returns a new Series; original is not mutated.
    #
    # EDGE CASES (dev note):
    # - All-NaN input remains all-NaN (nothing to propagate).
    return series.ffill().bfill()


@timer
def remove_non_trading_days(series: pd.Series) -> pd.Series:
    """
      Remove weekend rows (keep Monday–Friday) from a daily series.

      Parameters
      ----------
      series : pd.Series
          Series with a DatetimeIndex or an index coercible to datetime.

      Returns
      -------
      pd.Series
          Series filtered to weekdays only (dayofweek in 0..4).
      """
    # RATIONALE (dev note):
    # - Upstream joins/exports may introduce weekends; indicators should operate
    #   on trading days for consistency.
    #
    # EFFICIENCY (dev note):
    # - O(n) boolean mask; vectorized.
    #
    # NOTES (dev note):
    # - Converts index to DatetimeIndex if needed.
    # - Does not handle exchange holidays explicitly (usually absent in Yahoo data).
    s = series.copy()
    if not isinstance(s.index, pd.DatetimeIndex):
        s.index = pd.to_datetime(s.index)
    return s[s.index.dayofweek < 5]  # 0=Mon ... 4=Fri


def clean_data(series: pd.Series) -> pd.Series:
    """
      Convenience pipeline: fill gaps, then drop weekends.

      Parameters
      ----------
      series : pd.Series
          Input numeric series.

      Returns
      -------
      pd.Series
          Cleaned series.
      """
    # PIPELINE (dev note):
    # - Order matters: impute first, then filter by weekdays.
    series = check_missing_values(series)
    cleaned = remove_non_trading_days(series)
    return cleaned

@timer
def clean_outliers_iqr(
    series: pd.Series, replace_with_nan: bool = True, k: float = 3.0
) -> pd.Series:
    """
       Handle outliers using Tukey IQR fences.

       Parameters
       ----------
       series : pd.Series
           Numeric Series (any index).
       replace_with_nan : bool, default True
           If True, mask outliers to NaN; else clip to [Lower, Upper].
       k : float, default 3.0
           IQR multiplier (1.5 = classic Tukey; larger is stricter).

       Returns
       -------
       pd.Series
           Cleaned series with outliers masked or clipped.
       """
    # RATIONALE (dev note):
    # - Robust to spikes and non-normal data (bad ticks, splits, glitches).
    #
    # METHOD (dev note):
    #   Q1 = 25th pct, Q3 = 75th pct, IQR = Q3 - Q1
    #   Lower = Q1 - k * IQR
    #   Upper = Q3 + k * IQR
    #   Outlier if value < Lower or > Upper
    #
    # EFFICIENCY (dev note):
    # - O(n): percentile estimation + vectorized mask.
    # - Returns new Series; no Python loops.
    #
    # EDGE CASES (dev note):
    # - Constant series → IQR=0 → Lower==Upper → no flags.
    # - Heavy-tailed distributions may flag more points; tune `k`.
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr

    if replace_with_nan:
        return series.mask((series < lower) | (series > upper))
    else:
        return series.clip(lower=lower, upper=upper)
