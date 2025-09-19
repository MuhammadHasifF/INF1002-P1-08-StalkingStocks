
import pandas as pd
import numpy as np
import yfinance as yf

#Defining sectors and tickers
#Using a dictionary as it is easier to keep sector context, and can flatten into a list
# = to efficiency as can download
sectors = {
    "Tech": ["AAPL", "MSFT", "NVDA"],
    "Finance": ["JPM", "BAC", "MA"],
    "Healthcare": ["JNJ", "PFE", "ABBV"],
    "Consumer Goods": ["PEP", "MCD", "NKE"],
    "Energy": ["XOM", "SHEL", "CVX"],
}

#Flatten all tickers into a single list like ["AAPL", "MSFT", ...]
tickers = sum(sectors.values(), [])

#Quick sector lookup which allows to lookup like AAPL --> Tech etc..}
ticker_to_sector = {t: s for s, lst in sectors.items() for t in lst}

#Function for consistent logging
def log(msg: str):
    print(f"[INFO] {msg}")

#Setting helper Functions — Conditional Cleaning & Transforms
#these helpers check the data first, then change it only when needed.

#this checks that the index is timezone-naive DateTimeIndex and sorted ascending. If already is, wont be touching it
def ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    needs_datetime = not isinstance(df.index, pd.DatetimeIndex)
    needs_tz_strip = isinstance(df.index, pd.DatetimeIndex) and (df.index.tz is not None)
    needs_sort = not df.index.is_monotonic_increasing

    if needs_datetime:
        log("Index is not DateTimeIndex → converting.")
        df.index = pd.to_datetime(df.index)
    if needs_tz_strip:
        log("Index has timezone → stripping to tz-naive.")
        df.index = df.index.tz_localize(None)
    if needs_sort:
        log("Index not sorted ascending → sorting.")
        df = df.sort_index()

    if not (needs_datetime or needs_tz_strip or needs_sort):
        log("Index already clean DateTimeIndex and sorted.")
    return df


#this drops duplicates (Date,Ticker) rows in the long table (prevents double counting)
def drop_dup_long(long_df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate (Date, Ticker) rows only if any exist."""
    dup_count = long_df.duplicated(subset=["Date", "Ticker"]).sum()
    if dup_count > 0:
        log(f"Found {dup_count} duplicate (Date,Ticker) rows → dropping.")
        long_df = long_df.drop_duplicates(subset=["Date", "Ticker"])
    else:
        log("No duplicate (Date,Ticker) rows.")
    return long_df

#Converts Date to datetime and keeps date-only, and sorts by (Ticker, Date)
def standardize_date_column(long_df: pd.DataFrame) -> pd.DataFrame:
    """Ensure 'Date' column is date-only and rows ordered by (Ticker, Date)."""
    if not pd.api.types.is_datetime64_any_dtype(long_df["Date"]):
        log("Converting 'Date' to datetime.")
        long_df["Date"] = pd.to_datetime(long_df["Date"])
    # Always keep only the date part (cheap and consistent)
    log("Stripping time component from 'Date'.")
    long_df["Date"] = long_df["Date"].dt.date

    #the sorting if needed
    sorted_df = long_df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
    if not sorted_df.index.equals(long_df.index):
        log("Sorting by ['Ticker','Date'].")
    return sorted_df

#Within each tickerm a forward-fill if there are NaNs. This prevents indicators from breaking without inventing values
def ffill_if_needed(long_df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    #Forward-fill missing values within each ticker only if there are NaNs.
    total_na = long_df[cols].isna().sum().sum()
    if total_na > 0:
        log(f"Missing values detected ({total_na}) in {cols} → forward-filling by ticker.")
        long_df[cols] = (
            long_df
            .sort_values(["Ticker", "Date"])
            .groupby("Ticker")[cols]
            .apply(lambda g: g.ffill())
            .reset_index(level=0, drop=True)
        )
    else:
        log(f"No missing values in {cols} → no forward-fill needed.")
    return long_df

#Within each ticker, linearly interpolates only price columns, only if NaNs remain
def interpolate_if_needed(long_df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    #Linear interpolation within each ticker, only if NaNs remain. (not for volume)
    remaining_na = long_df[cols].isna().sum().sum()
    if remaining_na > 0:
        log(f"{remaining_na} missing values remain in {cols} → linear interpolation.")
        long_df[cols] = (
            long_df
            .sort_values(["Ticker", "Date"])
            .groupby("Ticker")[cols]
            .apply(lambda g: g.interpolate(method="linear", limit_direction="forward"))
            .reset_index(level=0, drop=True)
        )
    else:
        log(f"No remaining missing values in {cols} → no interpolation needed.")
    return long_df

#pivots long to wide matrix (rows=Date, cols=Ticker) for given field, forward-fill if the pivot created gaps
def make_wide(field: str, long_df: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    #Pivot to wide matrix (rows=Date, cols=Ticker). Forward-fill only if needed.
    wide = long_df.pivot(index="Date", columns="Ticker", values=field).reindex(columns=tickers)
    na_after = wide.isna().sum().sum()
    if na_after > 0:
        log(f"[{field}] {na_after} NaNs after pivot → forward-filling down columns.")
        wide = wide.sort_index().ffill()
    else:
        log(f"[{field}] No NaNs after pivot.")
    return wide

#start/end for the last 3 years
#yf.download for all 15 tickers, auto adjust=false so that can keep raw OHLC plus a seprate adjust close
#by right yahoo already excludes weekends/holidays so non trading days arent present
end = pd.Timestamp.today().normalize()
start = end - pd.DateOffset(years=3)

raw = yf.download(tickers, start=start, end=end, auto_adjust=False, group_by="ticker")
raw = ensure_datetime_index(raw)

print("[INFO] Raw rows (dates):", raw.shape[0])
#this ensure_datetime_index(raw) when run prints how many dates were returned

# Build a long (tidy) DataFrame
# Create a single table with columns: Date, Ticker, Sector, and OHLC(V) fields.
#Using long tables as its easier to group by ticker, consistent cleaning, and can pivot safely to wide

fields = ["Open", "High", "Low", "Close", "Volume"]

long_rows = []
for tkr in tickers:
    if tkr not in raw.columns.get_level_values(0):
        log(f"Ticker '{tkr}' missing in download → skipping.")
        continue

    df_t = raw[tkr].copy()
    df_t["Ticker"] = tkr
    df_t["Sector"] = ticker_to_sector.get(tkr, "Unknown")
    df_t["Date"] = df_t.index
    df_t = df_t[["Date", "Ticker", "Sector"] + fields]
    long_rows.append(df_t.reset_index(drop=True))

long_df = pd.concat(long_rows, ignore_index=True)
log(f"Long table: {long_df.shape[0]} rows × {long_df.shape[1]} cols.")
long_df.head()

# Conditional Cleaning. Only fix what's broken (drop duplicates, standardize 'Date', fill gaps).

#Drop duplicate (Date, Ticker) rows if any
long_df = drop_dup_long(long_df)

#Ensure 'Date' is date-only and sort by (Ticker, Date)
long_df = standardize_date_column(long_df)

#Fill missing values only if they exist
numeric_cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in long_df.columns]
price_cols   = [c for c in ["Open", "High", "Low", "Close"] if c in long_df.columns]

#Forward fill both prices and volume if needed
long_df = ffill_if_needed(long_df, numeric_cols)

#Interpolate only prices if needed (never volume)
long_df = interpolate_if_needed(long_df, price_cols)

print("[INFO] Total NaNs after cleaning:", long_df.isna().sum().sum())
long_df.head()

#Transform to Wide Matrices (OHLCV)
#Create one matrix per field where rows=Date and columns=Tickers.
#This makes later calculations simple and fast (e.g., rolling means).

open_df   = make_wide("Open",  long_df, tickers)
high_df   = make_wide("High",  long_df, tickers)
low_df    = make_wide("Low",   long_df, tickers)
close_df  = make_wide("Close", long_df, tickers)
volume_df = make_wide("Volume",long_df, tickers)

#A store holding all matrices to pass around
frames = {
    "Open": open_df,
    "High": high_df,
    "Low": low_df,
    "Close": close_df,
    "Volume": volume_df,
}

# Quick preview
close_df.head()

