#!/usr/bin/env python3
"""
investigate_lh_lifecycle.py
===========================
Test LH system's ability to catch multi-year uptrends AND exit at FA reversal:
  - VCS:  up 2015-2018, then declined
  - DGC:  up 2020-2022, then declined
  - VNM:  up 2010-2017, then long decline to now
  - FPT:  up 2020-2025, then declined Q1 2026
  - MWG:  up 2015-2021, then declined

For each:
  1) Plot price journey alongside FA tier history
  2) Identify LH entry (first A/B tier appearance in universe)
  3) Identify LH exit triggers (tier drop to C/D/E) — does the system "see" the reversal?
  4) Compute "capture ratio": (up-trend % captured + down-trend % avoided) / total swing
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

TICKERS = ["VCS", "DGC", "VNM", "FPT", "MWG"]

# Load ratings + prices
ratings = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time"])
prices = pd.read_csv("prices_lh.csv", parse_dates=["time"])

for tk in TICKERS:
    print(f"\n{'='*100}")
    print(f"  {tk} — LH lifecycle analysis")
    print('='*100)

    r = ratings[ratings["ticker"] == tk].sort_values("time").reset_index(drop=True)
    p = prices[prices["ticker"] == tk].sort_values("time").reset_index(drop=True)

    if len(r) == 0 or len(p) == 0:
        print(f"  No data"); continue

    # Price peak and trough
    peak_idx = p["Close"].idxmax(); trough_idx_post_peak = p.loc[peak_idx:]["Close"].idxmin()
    peak_dt = p.loc[peak_idx, "time"]; peak_px = p.loc[peak_idx, "Close"]
    trough_dt = p.loc[trough_idx_post_peak, "time"]; trough_px = p.loc[trough_idx_post_peak, "Close"]
    drawdown_pct = (trough_px / peak_px - 1) * 100

    print(f"\nPrice history span: {p['time'].min().date()} → {p['time'].max().date()}")
    print(f"  Start price: {p['Close'].iloc[0]:.0f} VND  →  End: {p['Close'].iloc[-1]:.0f} VND")
    print(f"  Peak: {peak_px:.0f} on {peak_dt.date()}  →  Trough since: {trough_px:.0f} on {trough_dt.date()}  (DD {drawdown_pct:+.1f}%)")

    # Tier history
    print(f"\nFA tier history ({len(r)} quarters):")
    # Show tier per year
    r["yr_q"] = r["time"].dt.to_period("Q").astype(str)
    tier_pivot = r.set_index("yr_q")[["tier", "score"]]
    print(f"  {'Q':<10}{'Date':<12}{'Tier':<6}{'Score':<7}  Notable")
    for _, row in r.iterrows():
        # Closest price on row.time
        px_near = p[p["time"] <= row["time"]].tail(1)
        px_v = px_near["Close"].iloc[0] if len(px_near) else np.nan
        # Mark if tier transitioned
        marker = ""
        idx = r.index[r["time"] == row["time"]][0]
        if idx > 0 and r.loc[idx-1, "tier"] != row["tier"]:
            marker = f" ← TRANSITION from {r.loc[idx-1, 'tier']}"
        print(f"  {row['yr_q']:<10}{row['time'].date()!s:<12}{row['tier']:<6}{row['score']:.3f}  px={px_v:.0f}{marker}")

    # LH simulation: hold while tier in A/B
    print(f"\nLH-style hold simulation (buy on first A, sell when tier drops to C/D/E):")
    in_position = False; entry_dt = None; entry_px = None
    trades = []
    for _, row in r.iterrows():
        px_at_q = p[p["time"] <= row["time"]].tail(1)
        if len(px_at_q) == 0: continue
        px_v = px_at_q["Close"].iloc[0]
        if not in_position and row["tier"] in ("A", "B"):
            in_position = True; entry_dt = row["time"]; entry_px = px_v
        elif in_position and row["tier"] not in ("A", "B"):
            ret = (px_v / entry_px - 1) * 100
            trades.append((entry_dt, row["time"], entry_px, px_v, ret, row["tier"]))
            in_position = False
    if in_position:
        last_px = p["Close"].iloc[-1]
        ret = (last_px / entry_px - 1) * 100
        trades.append((entry_dt, p["time"].iloc[-1], entry_px, last_px, ret, "STILL_HOLD"))

    for entry_dt, exit_dt, entry_px, exit_px, ret, exit_reason in trades:
        years = (exit_dt - entry_dt).days / 365.25
        ann_ret = (1 + ret/100)**(1/max(years, 0.1)) - 1
        print(f"  {entry_dt.date()} → {exit_dt.date()}  ({years:.1f}y)  {entry_px:.0f} → {exit_px:.0f}  "
              f"{ret:+.1f}% total, {ann_ret*100:+.1f}%/yr  exit_reason={exit_reason}")

    # Capture-ratio analysis
    # "Optimal trade" = bought at start, sold at peak; "actual" = LH trade(s)
    # "Worst case" = bought at start, sold at trough
    start_px = p["Close"].iloc[0]
    optimal_ret = (peak_px / start_px - 1) * 100
    bh_ret = (p["Close"].iloc[-1] / start_px - 1) * 100
    actual_ret = sum(t[4] for t in trades) if trades else 0
    print(f"\nCapture analysis:")
    print(f"  Optimal (start → peak):   {optimal_ret:+.1f}%")
    print(f"  Buy & hold (start → end): {bh_ret:+.1f}%")
    print(f"  LH actual (A/B hold):     {actual_ret:+.1f}%")
    if optimal_ret > 0:
        capture = actual_ret / optimal_ret * 100
        print(f"  Capture vs optimal:       {capture:.1f}%")

# Summary
print(f"\n{'='*100}")
print("  SUMMARY — does LH system catch reversal at FA tier drop?")
print('='*100)
print("""
Key question: does FA tier track PRICE direction, or just FUNDAMENTAL quality?

If FA tier never drops despite multi-year price decline → LH system holds through entire down-cycle.
If FA tier drops at/before price peak → LH catches reversal correctly.
""")
