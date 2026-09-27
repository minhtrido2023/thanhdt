#!/usr/bin/env python3
"""FAIL-D dividend-tax haircut applied ARITHMETICALLY to one park-grid leg.

Same formula as measurement_integrity_audit_20260927/part2 (nav_drag.txt):
  k = tax 5% + fee 0.1%*(1-tax) = 5.095% on every dividend dong
  drag = 1 - PROD_p(1 - k*DY_p*park_share_p)^(1/yrs)
DY_p comes verbatim from part2/dy_by_rebal.csv (49 custom30V rebal periods, measured from
tav2_bq.corporate_action cash-dividend events / raw price at rebal).
park_share_p is MEASURED on THIS leg's own audit CSV ((bal_etf_ref+lag_etf_ref)/combined_nav,
daily mean inside the period window) -- NOT assumed proportional to the park knob.
Usage: park_haircut.py <audit_csv> <cagr_gross_pct>
"""
import sys, pandas as pd, numpy as np

DY = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/measurement_integrity_audit_20260927/part2/dy_by_rebal.csv"
TAX, FEE = 0.05, 0.001
k = TAX + (1 - TAX) * FEE

csv_path, cagr_gross = sys.argv[1], float(sys.argv[2]) / 100.0
df = pd.read_csv(csv_path, low_memory=False)
d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
d = d.dropna(subset=["ymd"]).sort_values("ymd")
g = d.groupby(d["ymd"].dt.normalize()).last()
park = (g["bal_etf_ref"].fillna(0) + g["lag_etf_ref"].fillna(0)) / g["combined_nav"].astype(float)
nav = g["combined_nav"].astype(float)
yrs = (nav.index[-1] - nav.index[0]).days / 365.25

dy = pd.read_csv(DY)
prod, rows = 1.0, []
for _, r in dy.iterrows():
    s, e = pd.Timestamp(r["start"]), pd.Timestamp(r["end"])
    m = park[(park.index >= s) & (park.index < e)]
    ps = float(m.mean()) if len(m) else 0.0
    f = 1 - k * float(r["dy_period"]) * ps
    prod *= f
    rows.append((r["rebal"], float(r["dy_period"]), ps, f))

drag = (1 - prod ** (1 / yrs))
print(f"csv={csv_path.split('_exp_')[1]}")
print(f"  window {nav.index[0].date()}..{nav.index[-1].date()} = {yrs:.3f} yrs; k={k:.5f}")
print(f"  park share NAV mean full period = {park.mean():.4f}")
print(f"  PROD(1-k*DY*park) over {len(rows)} periods = {prod:.6f}")
print(f"  drag on CAGR = {drag*100*(1+cagr_gross):.4f} pp/yr  =>  CAGR {cagr_gross*100:.4f}% -> {((1+cagr_gross)*prod**(1/yrs)-1)*100:.4f}%")
