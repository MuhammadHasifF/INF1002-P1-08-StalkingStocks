import pandas as pd

from app.services.core import (compute_max_profit, compute_sdr, compute_sma,
                               compute_streak)


def test_compute_sma(sample_close: pd.Series) -> None:
    sma_5: pd.Series = compute_sma(sample_close, window=5)
    assert len(sma_5) == 100  # ensure length is retained
    assert sma_5.hasnans == True  # ensure result in not an empty series
    assert (
        sma_5.isna().sum() == 4
    )  # ensure rolling operation produces correct number of nans

    sma_20: pd.Series = compute_sma(sample_close, window=20)
    assert len(sma_20) == 100  # ensure length is retained
    assert sma_20.hasnans == True  # ensure result in not an empty series
    assert (
        sma_20.isna().sum() == 19
    )  # ensure rolling operation produces correct number of nans

    sma_50: pd.Series = compute_sma(sample_close, window=50)
    assert len(sma_50) == 100  # ensure length is retained
    assert sma_50.hasnans == True  # ensure result in not an empty series
    assert (
        sma_50.isna().sum() == 49
    )  # ensure rolling operation produces correct number of nans


def test_compute_streak(sample_close: pd.Series) -> None:
    up_streak, down_streak = compute_streak(sample_close)
    assert isinstance(up_streak, int)
    assert up_streak == 99

    assert isinstance(down_streak, int)
    assert down_streak == 0


def test_compute_sdr(sample_close: pd.Series) -> None:
    sdr: pd.Series = compute_sdr(sample_close)
    assert len(sdr) == 100  # ensure length is retained
    assert sdr.hasnans == True  # ensure result in not an empty series
    assert (
        sdr.isna().sum() == 1
    )  # ensure rolling operation produces correct number of nans


def test_compute_max_profit(sample_close: pd.Series) -> None:
    profit: float = compute_max_profit(sample_close)
    assert isinstance(profit, float)
    assert profit == 99.0
