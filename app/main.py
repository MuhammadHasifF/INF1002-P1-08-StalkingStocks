"""
main.py

This is the main entry point for the finance dashboard application.

Note:
    At the moment, I'm using this as the main testing interface with the hope of
    eventually reorganising appropriately.
"""

from pprint import pprint
from services.data import load_mapping
from services.finance import get_ticker, get_top_performers_by_industry
from utils.helpers import n_year_window, timer


@timer
def main() -> None:
    sector_map = load_mapping()
    tech = sector_map["technology"]
    software = tech[3]
    performers = get_top_performers_by_industry(software)

    print(software)
    print(f"{performers}\n")

    # start, end = n_year_window(n=3)
    # print(f"start: {start}, end: {end}\n")
    #
    # for tkr in performers:
    #     data = get_ticker_data(
    #         tickers=tkr, start=start, end=end, auto_adjust=True, progress=False
    #     )
    #
    #     print(f"{tkr}: {len(data)}")
    #     # print(data.describe())
    #     # break
    #     print()
    # # pprint(sector_map)
    # pprint(sector_map)


if __name__ == "__main__":
    main()
