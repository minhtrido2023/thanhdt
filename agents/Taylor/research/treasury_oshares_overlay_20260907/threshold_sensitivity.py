#!/usr/bin/env python3
"""
Sensitivity sweep on SUSPECT_RATIO_PCT (match_overlay.py) — job Taylor_20260907_170327,
patch #2 requested after quant-skeptic verify. Reads overlay_results.csv (which already carries
delta_pct_of_prev_oshares for every MEDIUM-eligible row, computed at match time — this script does
NOT re-run the matcher, it only re-applies the downgrade rule at different thresholds to rows that
were classified MEDIUM or SUSPECT by the pinned run).
"""
import csv
from collections import defaultdict

rows = list(csv.DictReader(open("overlay_results.csv")))

# rows eligible for the SUSPECT downgrade rule are exactly those with confidence in
# {MEDIUM, SUSPECT} in the pinned run (HIGH rows are shares_delta-confirmed, never downgraded).
eligible = [r for r in rows if r["confidence"] in ("MEDIUM", "SUSPECT")]
for r in eligible:
    r["ratio"] = float(r["delta_pct_of_prev_oshares"])

print(f"eligible (MEDIUM+SUSPECT) rows: {len(eligible)}")
print("ratio distribution (sorted):")
ratios_sorted = sorted(r["ratio"] for r in eligible)
for x in ratios_sorted:
    print(f"  {x:6.2f}")

def classify_ticker(all_rows_by_ticker, threshold):
    """Re-derive ticker-level HIGH/MEDIUM/SUSPECT/unexplained bucket at a given threshold pct."""
    out = {}
    for t, rs in all_rows_by_ticker.items():
        confs = []
        for r in rs:
            if r["matched"] != "True":
                continue
            if r["confidence"] == "HIGH":
                confs.append("HIGH")
            elif r["confidence"] in ("MEDIUM", "SUSPECT"):
                confs.append("SUSPECT" if r["ratio"] > threshold else "MEDIUM")
        if any(c in ("HIGH", "MEDIUM") for c in confs):
            out[t] = "handled"
        elif confs:
            out[t] = "suspect"
        else:
            out[t] = "unexplained"
    return out

by_ticker = defaultdict(list)
for r in rows:
    r["ratio"] = float(r["delta_pct_of_prev_oshares"]) if r["delta_pct_of_prev_oshares"] else None
    by_ticker[r["ticker"]].append(r)

BASE = 15.0
SWEEP = [10.0, 12.0, 15.0, 18.0, 20.0]
classifications = {th: classify_ticker(by_ticker, th) for th in SWEEP}
base_class = classifications[BASE]

print("\n=== tier counts per threshold ===")
for th in SWEEP:
    c = classifications[th]
    n_h = sum(1 for v in c.values() if v == "handled")
    n_s = sum(1 for v in c.values() if v == "suspect")
    n_u = sum(1 for v in c.values() if v == "unexplained")
    print(f"  {th:5.1f}%: handled={n_h} suspect={n_s} unexplained={n_u}")

print("\n=== tickers that CHANGE tier vs baseline 15% ===")
all_tickers = sorted(by_ticker.keys())
for th in SWEEP:
    if th == BASE:
        continue
    changed = [t for t in all_tickers if classifications[th][t] != base_class[t]]
    print(f"\n-- threshold {th}% vs 15% baseline: {len(changed)} ticker(s) changed --")
    for t in changed:
        print(f"  {t}: {base_class[t]} -> {classifications[th][t]}")

print("\n=== tickers within +/-3pp of 15% boundary (any eligible row) ===")
near = sorted(
    {(r["ticker"], r["ratio"]) for r in eligible if 12.0 <= r["ratio"] <= 18.0},
    key=lambda x: x[1],
)
for t, ratio in near:
    print(f"  {t}: ratio={ratio:.2f}%")

print("\n=== 24 buy_done/sell_done tickers with 0 rows in ticker_financial/oshares_timeseries ===")
oshares_tickers = set()
with open("oshares_timeseries.csv") as f:
    for row in csv.DictReader(f):
        oshares_tickers.add(row["ticker"])
events_tickers = set()
with open("treasury_events.csv") as f:
    for row in csv.DictReader(f):
        if row["action_type"] in ("buy_done", "sell_done"):
            events_tickers.add(row["ticker"])
missing = sorted(events_tickers - oshares_tickers)
print(f"count: {len(missing)}")
print(missing)
