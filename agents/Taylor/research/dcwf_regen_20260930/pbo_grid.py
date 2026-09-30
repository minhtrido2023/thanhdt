# -*- coding: utf-8 -*-
"""pbo_grid.py (job Taylor_20260930_122400) — CSCV/PBO over the 8-trial park-fraction grid
(2 targets x 4 park levels), reusing dsr_pbo_annex.cscv_pbo (Bailey et al 2017), S=16 blocks.
Tests: if you picked the IS-best config among these 8, how often is it below-OOS-median?
"""
import os, sys
import numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from dsr_pbo_annex import cscv_pbo

AUDITS = {
    0.0: "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-0_advprice_exp_dcwf_grid_00_20260930_univpit.csv",
    0.3: "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-30_advprice_exp_dcwf_r3_20260930_univpit.csv",
    0.5: "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_park3-50_advprice_exp_dcwf_grid_05_20260930_univpit.csv",
    0.7: "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_advprice_exp_dcwf_grid_07_20260930_univpit.csv",
}
SLEEVE = "data/converge_portfolio_backtest_nav_dcwf_r3_20260930.csv"


def load_audit(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["ymd"] = pd.to_datetime(d["ymd"])
    for c in ["bal_etf_ref", "lag_etf_ref", "combined_nav"]:
        d[c] = pd.to_numeric(d[c])
    return d.set_index("ymd").sort_index()


def overlay(r_base, w_park_prev, delta_vehicle):
    dv = delta_vehicle.reindex(r_base.index).fillna(0.0)
    return r_base + w_park_prev.reindex(r_base.index).fillna(0.0) * dv


slv = pd.read_csv(SLEEVE, parse_dates=["date"]).set_index("date")
r_c30v = slv["baseline_ret"]; r_wf = slv["ConvergePort (equal-weight)"]

series = {}
common_idx = None
for p, path in AUDITS.items():
    aud = load_audit(path)
    nav = aud["combined_nav"]
    r_base = nav.pct_change().dropna()
    w_park = (aud["bal_etf_ref"] + aud["lag_etf_ref"]) / aud["combined_nav"]
    w_park_prev = w_park.shift(1).reindex(r_base.index).fillna(0.0)
    r_wfall = overlay(r_base, w_park_prev, (r_wf - r_c30v))
    series[f"p{p:.1f}_c30v"] = r_base
    series[f"p{p:.1f}_wf"] = r_wfall
    common_idx = r_base.index if common_idx is None else common_idx.intersection(r_base.index)

M = pd.DataFrame({k: v.reindex(common_idx) for k, v in series.items()}).dropna()
print(f"Config matrix: T={len(M)} days, Ncfg={M.shape[1]}")
print("Configs:", list(M.columns))
pbo, logits, n_combos, ncfg, T2 = cscv_pbo(M.values, S=16)
print(f"\nPBO (CSCV, S=16, {n_combos} combos, Ncfg={ncfg}, T={T2}) = {pbo:.3f}")
print(f"  logit mean={np.mean(logits):.3f}  median={np.median(logits):.3f}  frac<0={np.mean(logits<0):.3f}")
