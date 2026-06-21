# -*- coding: utf-8 -*-
"""Bulk-fetch intraday 15m bars for BAL universe tickers missing from cache.

Targets the BA-system trade universe (ticker_prune, avg liquidity >= 1B VND over
2023-2026 window). Merges into intraday_full.pkl. Incremental save every N tickers.
"""
import os, sys, pickle, time
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, os.path.join(WORKDIR, "stockquery"))
from stockquery_agent import StockQuery

INTRADAY_PKL = os.path.join(WORKDIR, "intraday_full.pkl")
START_DATE = "2023-09-01"
END_DATE   = "2026-05-12"
SAVE_EVERY = 10
SLEEP_BETWEEN = 0.3

# Liquid BAL universe (>= 1B VND avg daily liquidity 2023-2026, from BQ)
# Output of: ticker_prune ∩ avg(Volume_3M_P50 * Close) >= 1e9
# Sorted by liquidity DESC
TARGETS_SQL = """
SELECT t.ticker
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2023-09-01' AND DATE '2026-05-12'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker
HAVING AVG(t.Volume_3M_P50 * t.Close) >= 1e9
ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC
"""

UNIVERSE_CSV = os.path.join(WORKDIR, "data", "bal_universe_2024_25.csv")

def get_targets():
    """Read BAL universe ticker list (pre-generated via bq query)."""
    df = pd.read_csv(UNIVERSE_CSV)
    return df["ticker"].tolist()

def main():
    print("Loading existing intraday cache...")
    with open(INTRADAY_PKL, "rb") as f:
        intraday = pickle.load(f)
    print(f"  {len(intraday)} tickers already cached")

    print("Querying BAL universe (avg liq >= 1B VND)...")
    targets = get_targets()
    print(f"  {len(targets)} target tickers")

    missing = [t for t in targets if t not in intraday]
    print(f"  {len(missing)} missing, need to fetch")

    if not missing:
        print("Nothing to fetch."); return

    sq = StockQuery()
    sq.start_date = START_DATE
    sq.end_date = END_DATE

    fetched = 0; failed = []; t0 = time.time()
    for i, tk in enumerate(missing):
        try:
            df = sq.get_historical_symbol(tk, interval="15m")
            if df is None or len(df) < 50:
                failed.append(tk)
                print(f"  [{i+1}/{len(missing)}] {tk}: NO DATA")
            else:
                df["time"] = pd.to_datetime(df["time"])
                intraday[tk] = df
                fetched += 1
                elapsed = time.time() - t0
                rate = fetched / elapsed if elapsed > 0 else 0
                eta_s = (len(missing) - (i+1)) / rate if rate > 0 else 0
                print(f"  [{i+1}/{len(missing)}] {tk}: {len(df):,} bars "
                      f"({elapsed:.0f}s elapsed, ETA {eta_s/60:.1f}m)")
        except Exception as e:
            failed.append(tk)
            print(f"  [{i+1}/{len(missing)}] {tk}: ERROR {str(e)[:60]}")

        if fetched > 0 and fetched % SAVE_EVERY == 0:
            with open(INTRADAY_PKL, "wb") as f:
                pickle.dump(intraday, f)
            print(f"    [checkpoint saved -- {len(intraday)} tickers]")
        time.sleep(SLEEP_BETWEEN)

    with open(INTRADAY_PKL, "wb") as f:
        pickle.dump(intraday, f)
    print(f"\nDone. {fetched} new tickers fetched, {len(failed)} failed.")
    if failed:
        print("Failed:", failed)
    print(f"Total cache: {len(intraday)} tickers")

if __name__ == "__main__":
    main()
