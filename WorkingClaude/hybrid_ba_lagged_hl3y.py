#!/usr/bin/env python3
"""
hybrid_ba_lagged_hl3y.py — Final hybrid test

Uses:
  - BA v11 PRODUCTION NAV (from ba_v11_production_12y_nav.csv)
  - LAGGED HL_3y NAV (from compare_lagged_vs_ba_navs.csv)

Test 8 weight ratios + find sweet spot for Sharpe / Calmar.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)

print("="*100)
print("  HYBRID BA v11 + LAGGED HL_3y — Final Test")
print("="*100)

# Load aligned NAVs
df = pd.read_csv("compare_lagged_vs_ba_navs.csv", index_col=0, parse_dates=True)
print(f"NAVs loaded: {len(df)} days  ({df.index.min().date()} → {df.index.max().date()})")
print(f"  BA v11 final: {df['BA_v11'].iloc[-1]:.3f}x")
print(f"  LAGGED HL_3y final: {df['LAGGED_HL3y'].iloc[-1]:.3f}x")

# VNI baseline
vni = pd.read_csv("VNINDEX.csv", parse_dates=["time"])
vni = vni.set_index("time").sort_index()
vni_n = vni["Close"].reindex(df.index).ffill()
vni_n = vni_n / vni_n.iloc[0]

# Hybrid at multiple weights
weights = [(1.0, 0.0), (0.9, 0.1), (0.8, 0.2), (0.7, 0.3),
           (0.6, 0.4), (0.5, 0.5), (0.4, 0.6), (0.3, 0.7),
           (0.2, 0.8), (0.0, 1.0)]
hybrids = {}
for wb, wl in weights:
    label = f"BA{int(wb*100)}_L{int(wl*100)}"
    hybrids[label] = wb * df["BA_v11"] + wl * df["LAGGED_HL3y"]

def metrics_period(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    rets = s.pct_change().dropna()
    spy = len(rets) / yrs if yrs > 0 else 252
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = (s - s.cummax()) / s.cummax()
    mdd = dd.min()
    cal = cagr/abs(mdd) if mdd<0 else 0
    return {"CAGR":cagr*100, "Sharpe":sh, "DD":mdd*100, "Calmar":cal, "wealth":s.iloc[-1]/s.iloc[0]}

periods = [
    ("FULL 2014-26",     df.index.min(), df.index.max()),
    ("OOS 2024-26",      pd.Timestamp("2024-01-01"), df.index.max()),
    ("Pre-OOS 14-19",    pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-23",      pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2022",            pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1 2026",          pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]

print("\n" + "="*125)
print("  RESULTS by weight ratio")
print("="*125)
for label, st, en in periods:
    print(f"\n  --- {label} ---")
    print(f"  {'Mix':<14}{'CAGR%':>10}{'Sharpe':>10}{'DD%':>10}{'Calmar':>10}{'Wealth':>10}")
    for name, nav in hybrids.items():
        m = metrics_period(nav, st, en)
        if m is None: continue
        print(f"  {name:<14}{m['CAGR']:>+9.2f}{m['Sharpe']:>+10.2f}{m['DD']:>+9.2f}{m['Calmar']:>+10.2f}{m['wealth']:>+10.2f}")
    vm = metrics_period(vni_n, st, en)
    if vm:
        print(f"  {'VNI':<14}{vm['CAGR']:>+9.2f}{vm['Sharpe']:>+10.2f}{vm['DD']:>+9.2f}{vm['Calmar']:>+10.2f}{vm['wealth']:>+10.2f}")

# Sweet spot analysis on FULL
print("\n" + "="*100)
print("  SWEET SPOT ANALYSIS (FULL 12y)")
print("="*100)
full_metrics = {name: metrics_period(nav, df.index.min(), df.index.max()) for name, nav in hybrids.items()}
fm_df = pd.DataFrame(full_metrics).T
print(fm_df[["CAGR","Sharpe","DD","Calmar"]].sort_values("Sharpe", ascending=False).to_string(float_format="%.2f"))

# Find best Sharpe + Calmar
best_sh = fm_df["Sharpe"].idxmax()
best_cal = fm_df["Calmar"].idxmax()
print(f"\n  🏆 Best Sharpe: {best_sh} → Sh {fm_df.loc[best_sh,'Sharpe']:.2f}, CAGR {fm_df.loc[best_sh,'CAGR']:.2f}%, DD {fm_df.loc[best_sh,'DD']:.2f}%")
print(f"  🏆 Best Calmar: {best_cal} → Cal {fm_df.loc[best_cal,'Calmar']:.2f}, CAGR {fm_df.loc[best_cal,'CAGR']:.2f}%, DD {fm_df.loc[best_cal,'DD']:.2f}%")

# Save
pd.DataFrame(hybrids).to_csv("hybrid_ba_lagged_hl3y_nav.csv")
fm_df.to_csv("hybrid_ba_lagged_hl3y_metrics.csv")
print("\nSaved: hybrid_ba_lagged_hl3y_nav.csv, hybrid_ba_lagged_hl3y_metrics.csv")
