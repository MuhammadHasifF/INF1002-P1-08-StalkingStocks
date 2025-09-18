import pandas as pd
import numpy as np
import yfinance as yf
#These are libraries
#Pandas is a tool for data tables to read clean and save them
#Numpy is useful for us to do mathamatical computations and handling NaN values
#yfinance is what we are using to pull Yahoo Finance Data, and its easier to use than things like AlphaVantage which need API Keys
#test
sectors = {
    "Tech": ["AAPL", "MSFT", "NVDA"],
    "Finance": ["JPM", "BAC", "MA"],
    "Healthcare": ["JNJ", "PFE", "ABBV"],
    "Consumer Goods": ["PEP", "MCD", "NKE"],
    "Energy": ["XOM", "SHEL", "CVX"],
}
#Grouped the tickers according to sectors. 
#Storing them in a dictionary like this makes it clear to see which stock belongs to which sector

tickers = sum(sectors.values(), [])
#This line is basically turning the dictionary above to one list of tickers so yfinance can be used

# HASIF EDITS — precompute a fast ticker→sector lookup for reuse.
# Reason: we need Sector when attaching MultiIndex to wide DataFrames later.
sector_map = {t: sec for sec, lst in sectors.items() for t in lst}

end = pd.Timestamp.today().normalize()
start = end - pd.DateOffset(years=3)
#End is todays date, and we have normalised it to be 00:00:00 for the time.
#Start is basically the oldest date

raw = yf.download(tickers, start=start, end=end, auto_adjust=False, group_by="ticker")
#This is basically calling the api to download the data

raw.index = pd.to_datetime(raw.index)
raw = raw.sort_index()
#Converts the data downloaded to datetime and sort it based on it

long_rows = []
# HASIF EDITS — removed "Adj Close" from fields since team decided not to use it.
fields = ["Open", "High", "Low", "Close", "Volume"]

for tkr in tickers:
    if tkr not in raw.columns.get_level_values(0):
        continue
    df_t = raw[tkr].copy()
    df_t["Ticker"] = tkr
    # HASIF EDITS — add Sector column so sector metadata is carried through downstream.
    # Reason: later analysis/visualisation may group/aggregate by sector.
    # We find the sector by scanning the sectors dict once; cheap for 15 tickers.
    df_t["Sector"] = next((sec for sec, lst in sectors.items() if tkr in lst), None)
    df_t["Date"] = df_t.index
    df_t = df_t[["Date", "Ticker", "Sector"] + fields]  # HASIF EDITS — include Sector in column order.
    long_rows.append(df_t.reset_index(drop=True))
#Here we are collecting the ticker data from the multi columns, adding ticker and date as explicit column and only keeping impt fields    

long_df = pd.concat(long_rows, ignore_index=True)
long_df = long_df.drop_duplicates(subset=["Date", "Ticker"])
long_df = long_df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
#These concatenates all tickers into one big dataframe. Then it drops duplicate rows, and sorts by ticker + date

# HASIF EDITS — removed "Adj Close" from numeric columns because it’s no longer used.
numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
long_df[numeric_cols] = (
    long_df
    .groupby("Ticker")[numeric_cols]
    .apply(lambda g: g.ffill())
    .reset_index(level=0, drop=True)
)
#This is to fill missing numeric values within each ticker by carrying the LAST known value forward

# HASIF EDITS — removed "Adj Close" from interpolation columns to match removal.
interp_cols = ["Open", "High", "Low", "Close"]
long_df[interp_cols] = (
    long_df
    .groupby("Ticker")[interp_cols]
    .apply(lambda g: g.interpolate(method="linear", limit_direction="forward"))
    .reset_index(level=0, drop=True)
)

long_df["Date"] = pd.to_datetime(long_df["Date"]).dt.date
#converts date to plain date objects (no time)

# HASIF EDITS — Outlier logic now uses Close returns (Adj Close removed).
def flag_outliers(group: pd.DataFrame) -> pd.Series:
    ret = group["Close"].pct_change()
    std = ret.std(ddof=0)
    z = (ret - ret.mean()) / (std if std not in [0, np.nan] else 1)
    return (z.abs() > 3).fillna(False)
#for each ticker, calculates the daily returns, finds z scores, and flags outliers

long_df["Return_Outlier"] = (
    long_df
    .groupby("Ticker", group_keys=False)
    .apply(flag_outliers)
    .reset_index(level=0, drop=True)
)
#outlier check to each tickers data, adds a boolean column

def _attach_sector_multiindex(wide_df: pd.DataFrame) -> pd.DataFrame:
    # HASIF EDITS — attach Sector as top-level column via MultiIndex so sector carries over.
    # Reason: downstream wide matrices can groupby/select by Sector cleanly.
    sec_level = [sector_map.get(col, None) for col in wide_df.columns]
    wide_df.columns = pd.MultiIndex.from_arrays([sec_level, list(wide_df.columns)],
                                                names=["Sector", "Ticker"])
    return wide_df

def make_wide(field: str) -> pd.DataFrame:
    wide = long_df.pivot(index="Date", columns="Ticker", values=field)
    wide = wide.reindex(columns=tickers)
    wide = wide.sort_index().ffill()
    # HASIF EDITS — attach (Sector, Ticker) MultiIndex columns
    wide = _attach_sector_multiindex(wide)
    return wide
#pivots long data into a wide table (Date x Ticker) for a chosen field

open_df     = make_wide("Open")
high_df     = make_wide("High")
low_df      = make_wide("Low")
close_df    = make_wide("Close")
# HASIF EDITS — removed adjclose_df since Adj Close is not used anymore.
volume_df   = make_wide("Volume")
#This is to build six seperate wide tables

# HASIF EDITS — make outlier_df sector-aware too (MultiIndex columns)
outlier_df = long_df.pivot(index="Date", columns="Ticker", values="Return_Outlier").fillna(False)
outlier_df = outlier_df.reindex(columns=tickers)
outlier_df = _attach_sector_multiindex(outlier_df)
#Builds a boolean wide matrix of outlier flags

print("✅ Finished. Rows:", len(long_df))
print(long_df.head())
# HASIF EDITS — print Close matrix (now with MultiIndex columns: (Sector, Ticker)).
print(close_df.head())

# Example saves (optional)
# open_df.to_csv("open_matrix.csv")
# high_df.to_csv("high_matrix.csv")
# low_df.to_csv("low_matrix.csv")
# close_df.to_csv("close_matrix.csv")
# HASIF EDITS — removed adjclose_df save since it no longer exists.
# volume_df.to_csv("volume_matrix.csv")
# outlier_df.to_csv("return_outliers.csv")
