#!/usr/bin/env python3
"""analyze_rating_BC.py — per-year + per-crisis breakdown of the B/C overlay NAVs.

A distress gate / regime-sizing overlay earns its keep in TAIL years, not on full-period
CAGR. This reads data/rating_8l_BC_prodspec_navs.csv and reports, per system:
  - annual return: base vs exclude5 (B) vs regime_size (C)
  - crisis-window total return + maxDD (2018 derisk, 2020 COVID, 2022 bear, 2025 selloff)
"""
import warnings; warnings.filterwarnings("ignore")
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

nav = pd.read_csv("data/rating_8l_BC_prodspec_navs.csv", index_col=0, parse_dates=True)
MODES = ["base","exclude5","regime_size"]; SYS = ["V1","V2","V3","V4","V5"]

def ann_ret(s):
    s = s.dropna()
    return (s.iloc[-1]/s.iloc[0]-1)*100 if len(s)>1 else np.nan
def maxdd(s):
    s = s.dropna()
    return ((s-s.cummax())/s.cummax()).min()*100 if len(s)>1 else np.nan

print("="*100); print("  ANNUAL RETURN by system — base / B(excl5) / C(regime_sz)   [Δ vs base]"); print("="*100)
years = sorted(set(nav.index.year))
for sysn in SYS:
    print(f"\n  {sysn}")
    print(f"    {'year':<6}{'base':>9}{'B':>9}{'ΔB':>8}{'C':>9}{'ΔC':>8}")
    for y in years:
        sl = nav[nav.index.year==y]
        b = ann_ret(sl[f"base_{sysn}"]); e = ann_ret(sl[f"exclude5_{sysn}"]); r = ann_ret(sl[f"regime_size_{sysn}"])
        if np.isnan(b): continue
        print(f"    {y:<6}{b:>+8.1f}%{e:>+8.1f}%{e-b:>+7.1f}{r:>+8.1f}%{r-b:>+7.1f}")

print("\n"+"="*100); print("  CRISIS WINDOWS — total return / maxDD   (gate should help here if anywhere)"); print("="*100)
WINDOWS = {"2018 derisk":("2018-01-01","2018-12-31"),
           "2020 COVID":("2020-01-15","2020-08-01"),
           "2022 bear":("2022-04-01","2022-12-31"),
           "2025 selloff":("2025-03-01","2025-06-30")}
for sysn in SYS:
    print(f"\n  {sysn}")
    print(f"    {'window':<14}{'base ret/DD':>20}{'B ret/DD':>20}{'C ret/DD':>20}")
    for wn,(a,z) in WINDOWS.items():
        sl = nav[(nav.index>=a)&(nav.index<=z)]
        if len(sl)<5: continue
        def cell(m): return f"{ann_ret(sl[f'{m}_{sysn}']):+.1f}% / {maxdd(sl[f'{m}_{sysn}']):.1f}%"
        print(f"    {wn:<14}{cell('base'):>20}{cell('exclude5'):>20}{cell('regime_size'):>20}")
print("\nDONE.")
