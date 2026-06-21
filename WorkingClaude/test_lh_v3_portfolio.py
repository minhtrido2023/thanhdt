#!/usr/bin/env python3
"""
test_lh_v3_portfolio.py
=======================
Portfolio backtest using multi-factor composites as selection signal.

Builds fa_ratings_lh_v3_{name}.csv (composite-based tier classification)
then runs simulate_lh_nav.py on each.

Tests: C6 / C7 / C9 vs v8c baseline (LH v1).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics, _CACHE

INIT_NAV = 50e9

# Load factor panel v2
df = pd.read_csv("lh_v3_factor_panel_v2.csv", parse_dates=["time"])
fa_orig = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time","Release_Date"])

# For each composite candidate, build a fa_ratings_lh-style file
TIER_BANDS = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]

def tier_of(pct):
    for n, lo, hi in TIER_BANDS:
        if lo <= pct <= hi: return n
    return "E"

CANDIDATES = ["C6_smart_value", "C7_balanced_VQC", "C9_value_mom_blend"]

# Build composite-based ratings files
for comp in CANDIDATES:
    print(f"\nBuilding fa_ratings_lh_{comp}.csv ...")
    d = df.dropna(subset=[comp]).copy()
    # Rank within quarter (global, not sub-sector — composite is universal)
    d["pct"] = d.groupby("quarter")[comp].rank(pct=True)
    d["tier"] = d["pct"].apply(tier_of)
    d["score"] = d[comp]  # use composite as score
    # Merge meta from original fa_ratings_lh
    orig_meta = fa_orig[["ticker","quarter","time","Release_Date","sub","ICB_Code","MktCap","Volume_3M_P50","Close"]]
    out = orig_meta.merge(d[["ticker","quarter","score","pct","tier"]], on=["ticker","quarter"], how="inner")
    # Ensure complete data
    out = out.dropna(subset=["score","tier"]).sort_values(["quarter","ticker"]).reset_index(drop=True)
    fname = f"fa_ratings_lh_{comp}.csv"
    out.to_csv(fname, index=False)
    print(f"  {len(out):,} rows → tier dist: {out['tier'].value_counts().to_dict()}")

# Backup original and run each variant
print("\n" + "="*120)
print("  LH v3 PORTFOLIO BACKTEST (50B canonical, A+B staggered, CRISIS gated)")
print("="*120)

results = {}
# Baseline (LH v1 with v8c)
print(f"\n--- BASELINE: LH v1 (v8c tier) ---", flush=True)
_CACHE.clear()
results["v8c_baseline"] = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                                   refresh_mode="staggered", crisis_gate=True, init_nav=INIT_NAV)

# Each composite
for comp in CANDIDATES:
    print(f"\n--- {comp} ---", flush=True)
    fname = f"fa_ratings_lh_{comp}.csv"
    # Swap files
    os.rename("fa_ratings_lh.csv", "fa_ratings_lh.csv.bak")
    os.rename(fname, "fa_ratings_lh.csv")
    try:
        _CACHE.clear()
        results[comp] = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                                refresh_mode="staggered", crisis_gate=True, init_nav=INIT_NAV)
    finally:
        os.rename("fa_ratings_lh.csv", fname)
        os.rename("fa_ratings_lh.csv.bak", "fa_ratings_lh.csv")

# Report metrics
print("\n" + "="*120)
print("  METRICS BY PERIOD")
print("="*120)

periods = [
    ("FULL_12y",  pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("PRE_2024",  pd.Timestamp("2014-04-01"), pd.Timestamp("2023-12-31")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2022",     pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026",   pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]

for pname, ps, pe in periods:
    print(f"\n─── {pname} ───")
    print(f"  {'Variant':<25}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}{'avg_pos':>10}")
    for label, res in results.items():
        nav = res["nav"]["nav"]
        s = nav[(nav.index >= ps) & (nav.index <= pe)]
        if len(s) < 30: continue
        m = compute_metrics(INIT_NAV * s/s.iloc[0], ps, pe)
        avg_p = res["nav"]["n_pos"].mean()
        print(f"  {label:<25}{m['CAGR']:>+10.2%}{m['Sharpe']:>+10.2f}{m['MaxDD']:>+10.2%}{m['Calmar']:>+10.2f}{avg_p:>+10.2f}")

# 5-ticker lifecycle on best composite
print("\n" + "="*120)
print("  5-TICKER LIFECYCLE (BEST COMPOSITE vs v8c)")
print("="*120)

CASES = ["VCS","DGC","VNM","FPT","MWG"]
prices = pd.read_csv("prices_lh.csv", parse_dates=["time"])

for label in ["v8c_baseline", "C7_balanced_VQC", "C6_smart_value"]:
    if label not in results: continue
    tr = results[label]["trades"]
    print(f"\n--- {label} ---")
    for tk in CASES:
        p = prices[prices["ticker"]==tk].sort_values("time")
        peak_dt = p.loc[p["Close"].idxmax(), "time"]
        peak_px = p["Close"].max()
        tk_tr = tr[tr["ticker"]==tk] if len(tr) > 0 else pd.DataFrame()
        if len(tk_tr) == 0:
            print(f"  {tk} (peak {peak_px:.0f} on {peak_dt.date()}): NOT PICKED")
            continue
        buys = tk_tr[tk_tr["side"]=="BUY"]
        sells = tk_tr[tk_tr["side"].isin(["SELL","TRAIL_STOP"])]
        first_buy = buys.iloc[0]
        last_sell = sells.iloc[-1] if len(sells) > 0 else None
        first_off = (peak_dt - first_buy["dt"]).days
        if last_sell is not None:
            last_off = (last_sell["dt"] - peak_dt).days
            ret = (last_sell["px"]/first_buy["px"] - 1) * 100
            print(f"  {tk} (peak {peak_px:.0f}): buy {first_buy['dt'].strftime('%Y-%m-%d')} @ {first_buy['px']:.0f} (peak{first_off:+d}d) → exit @ {last_sell['px']:.0f} (peak{last_off:+d}d)  net {ret:+.1f}%")
        else:
            ret = (p["Close"].iloc[-1]/first_buy["px"] - 1) * 100
            print(f"  {tk} (peak {peak_px:.0f}): buy {first_buy['dt'].strftime('%Y-%m-%d')} @ {first_buy['px']:.0f} → STILL HOLDING, current {p['Close'].iloc[-1]:.0f} ({ret:+.1f}%)")

# Save
print("\nDONE")
