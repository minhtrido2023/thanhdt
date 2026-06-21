#!/usr/bin/env python3
"""
seed_phosphorus_history.py — one-time backfill of P4 price history into the weekly feed
=======================================================================================
The live scraper (phosphorus_dgc_weekly.py) only sees the latest ~6 daily prints on
SunSirs prodetail-708. To give the trend a full ~3-month history immediately (matching
the chart window 2026-03 -> 2026-06), this seeds the SunSirs *benchmark* price points
quoted verbatim in the SunSirs weekly review articles. Benchmark == the same series the
prodetail "Price" column reports, so the points are directly comparable to live prints.

Provenance: each point cites its SunSirs article id (detail_news-<id>.html). Run once;
the live feed densifies the series from here. Idempotent (dedupe by date; live prints win).
"""
import os, sys
import pandas as pd
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

WORKDIR = os.environ.get("WORKDIR_8L", os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(WORKDIR, "data", "phosphorus_weekly.csv")

# (date, SunSirs benchmark price RMB/ton, source article)  — see data/dgc_phosphorus_watch.md note
SEED = [
    ("2026-03-02", 24172.67, "news-31680"),  # "beginning of March" benchmark
    ("2026-03-20", 25000.00, "news-31680"),  # recovery start
    ("2026-03-27", 26796.00, "news-31680"),  # benchmark (+10.85% vs beg-March)
    ("2026-04-02", 27166.67, "news-32138"),  # "early April" benchmark
    ("2026-04-15", 31162.67, "news-32138"),  # benchmark (+14.71% vs early-April)
    ("2026-05-18", 32096.00, "news-33016"),
    ("2026-05-19", 32429.33, "news-33016"),  # benchmark (+44.16% YoY noted in article)
]


def main():
    seed = pd.DataFrame([{"date": d, "price_rmb": p, "src": "sunsirs_news", "fetched": s} for d, p, s in SEED])
    if os.path.exists(CSV):
        old = pd.read_csv(CSV)
        # live daily prints (src='sunsirs') win over a seed on the same date
        comb = pd.concat([seed, old], ignore_index=True).drop_duplicates(subset=["date"], keep="last")
    else:
        comb = seed
    comb = comb.sort_values("date").reset_index(drop=True)
    comb.to_csv(CSV, index=False)
    print(f"Seeded {len(SEED)} benchmark points -> {CSV} now {len(comb)} rows "
          f"({comb['date'].iloc[0]} .. {comb['date'].iloc[-1]})")
    print(comb.to_string(index=False))


if __name__ == "__main__":
    main()
