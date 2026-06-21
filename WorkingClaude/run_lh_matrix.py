#!/usr/bin/env python3
"""
run_lh_matrix.py
================
Sweep long-hold portfolio configurations and compare to VNINDEX B&H.
Matrix: hold_quarters x n_positions x tier_set x incl_sub
Also reports OOS slice (2024-2026).
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, run_vnindex_bh, compute_metrics, load_data

ratings, prices, vnindex = load_data()

def slice_oos(nav_series, start, end):
    """Re-compute metrics on a sub-slice of nav."""
    s = nav_series[(nav_series.index >= pd.Timestamp(start)) & (nav_series.index <= pd.Timestamp(end))]
    if len(s) < 30: return None
    return compute_metrics(s, pd.Timestamp(start), pd.Timestamp(end))

CONFIGS = [
    # (name, hold_Q, n_pos, tier_set, incl_sub, refresh)
    # Staggered (continuous signal refresh)
    ("LH_6M_10A_stag",     2, 10, ("A",),     "all",        "staggered"),
    ("LH_1Y_10A_stag",     4, 10, ("A",),     "all",        "staggered"),
    ("LH_2Y_10A_stag",     8, 10, ("A",),     "all",        "staggered"),
    ("LH_1Y_10AB_stag",    4, 10, ("A","B"),  "all",        "staggered"),
    ("LH_2Y_10AB_stag",    8, 10, ("A","B"),  "all",        "staggered"),
    # Lumpy (rebal-everything every H quarters)
    ("LH_6M_10A_lump",     2, 10, ("A",),     "all",        "lumpy"),
    ("LH_1Y_10A_lump",     4, 10, ("A",),     "all",        "lumpy"),
    ("LH_2Y_10A_lump",     8, 10, ("A",),     "all",        "lumpy"),
    ("LH_1Y_10AB_lump",    4, 10, ("A","B"),  "all",        "lumpy"),
    ("LH_2Y_10AB_lump",    8, 10, ("A","B"),  "all",        "lumpy"),
    # Position-count variants
    ("LH_1Y_5A_lump",      4,  5, ("A",),     "all",        "lumpy"),
    ("LH_1Y_20A_lump",     4, 20, ("A",),     "all",        "lumpy"),
    ("LH_1Y_20AB_lump",    4, 20, ("A","B"),  "all",        "lumpy"),
    # Sector inclusion
    ("LH_1Y_10AB_noREIT",  4, 10, ("A","B"),  "excl_reit",  "lumpy"),
    ("LH_1Y_10AB_noALLre", 4, 10, ("A","B"),  "excl_all_re","lumpy"),
]

results = []
nav_store = {}
for name, hQ, n, tier, sub, refresh in CONFIGS:
    print(f"Running {name} ...", flush=True)
    res = run_lh(hold_quarters=hQ, n_positions=n, tier_set=tier, incl_sub=sub, refresh_mode=refresh, verbose=False)
    m = res["metrics"]; nav = res["nav"]["nav"]
    nav_store[name] = nav
    # Full + OOS slices
    full = m
    oos2024 = slice_oos(nav, "2024-01-01", "2026-05-13") or {}
    pre2024 = slice_oos(nav, "2014-04-01", "2023-12-31") or {}
    results.append({
        "config": name, "hold_Q": hQ, "n_pos": n, "tier": "+".join(tier), "incl": sub, "mode": refresh,
        "CAGR": full["CAGR"], "Sharpe": full["Sharpe"], "MaxDD": full["MaxDD"], "Calmar": full["Calmar"],
        "n_trades": full["n_trades"], "avg_n_pos": full["avg_n_pos"],
        "CAGR_pre24": pre2024.get("CAGR", np.nan), "MaxDD_pre24": pre2024.get("MaxDD", np.nan),
        "CAGR_oos24": oos2024.get("CAGR", np.nan), "MaxDD_oos24": oos2024.get("MaxDD", np.nan),
    })

# Benchmarks
bh = run_vnindex_bh(start="2014-04-01")
bh_oos = run_vnindex_bh(start="2024-01-01")
bh_pre = run_vnindex_bh(start="2014-04-01", end="2023-12-31")
results.append({"config":"VNINDEX_BH","hold_Q":"-","n_pos":"-","tier":"-","incl":"-","mode":"-",
    "CAGR":bh["metrics"]["CAGR"], "Sharpe":bh["metrics"]["Sharpe"],
    "MaxDD":bh["metrics"]["MaxDD"], "Calmar":bh["metrics"]["Calmar"],
    "n_trades":0,"avg_n_pos":0,
    "CAGR_pre24":bh_pre["metrics"]["CAGR"], "MaxDD_pre24":bh_pre["metrics"]["MaxDD"],
    "CAGR_oos24":bh_oos["metrics"]["CAGR"], "MaxDD_oos24":bh_oos["metrics"]["MaxDD"]})

df = pd.DataFrame(results)
df.to_csv("lh_matrix_results.csv", index=False)

# Pretty print
print("\n" + "="*120)
print("LONG-HOLD MATRIX RESULTS (50B init, 0.10/0.15% slip, 0.1% tax, 20%ADV cap, 1% cash deposit)")
print("="*120)
fmt = "%.4f"
cols_show = ["config","hold_Q","n_pos","tier","incl","mode","CAGR","Sharpe","MaxDD","Calmar","CAGR_pre24","MaxDD_pre24","CAGR_oos24","MaxDD_oos24","n_trades","avg_n_pos"]
print(df[cols_show].to_string(index=False, float_format=lambda x: f"{x:+.4f}" if isinstance(x,(int,float,np.floating)) and abs(x)<10 else str(x)))

# Save nav series for top performers
nav_df = pd.DataFrame(nav_store)
nav_df.to_csv("lh_nav_series.csv")
print("\nSaved lh_matrix_results.csv and lh_nav_series.csv")
