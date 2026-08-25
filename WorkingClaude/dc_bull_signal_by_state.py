# -*- coding: utf-8 -*-
"""dc_bull_signal_by_state.py — 3-book design Q2b: does the DC (double-confirm) book have signal
in BULL, or does it also go quiet like LAG?

Reuses converge_portfolio_backtest.py's exact build_signal_panel() (no re-implementation) —
computes dbl (double-confirm matrix) then joins DT5G state per day, breaks down active-set size
by state. Job Taylor_20260825_142021 Part 2b.
"""
import os, sys
import pandas as pd

WORKDIR = os.environ.get("WORKDIR", "/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)

import converge_portfolio_backtest as cpb

print("Loading caches ...")
basket = cpb.load_parking_basket()
price = cpb.load_prices(set(cpb.WL_TK) | set(basket["ticker"]))
fin = cpb.load_financials()
dt5g = cpb.load_dt5g()
rat = cpb.load_ratings()

calendar = pd.DatetimeIndex(sorted(price["time"].unique()))
calendar = calendar[calendar >= pd.Timestamp(cpb.START)]

buy, strong, dbl = cpb.build_signal_panel(price, fin, dt5g, rat, calendar)
dc_counts = dbl.sum(axis=1)

# dt5g state series aligned to calendar
state = dt5g.set_index("time")["state"].reindex(calendar).ffill()

df = pd.DataFrame({"dc_count": dc_counts, "state": state}).dropna()
STATE_NAME = {0: "CRISIS", 1: "BEAR", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
# vnindex_5state_dt5g_live state col convention check
print("state value counts:", df["state"].value_counts().to_dict())

df["state_label"] = df["state"].map(STATE_NAME).fillna(df["state"].astype(str))

print("\n=== Active-set size (double-confirm names) by DT5G state ===")
g = df.groupby("state_label")["dc_count"].agg(["count", "mean", "median",
                                                lambda s: (s > 0).mean() * 100])
g.columns = ["n_days", "mean_active", "median_active", "pct_days_with_signal"]
print(g.to_string())

# BULL-specific detail vs overall
bull = df[df["state_label"] == "BULL"]
other = df[df["state_label"] != "BULL"]
print(f"\nBULL: {len(bull)} days, mean active {bull['dc_count'].mean():.2f}, "
      f"%days>=1 signal {100*(bull['dc_count']>0).mean():.1f}%, "
      f"%days>=3 signal {100*(bull['dc_count']>=3).mean():.1f}%")
print(f"non-BULL: {len(other)} days, mean active {other['dc_count'].mean():.2f}, "
      f"%days>=1 signal {100*(other['dc_count']>0).mean():.1f}%")

print("\nDone.")
