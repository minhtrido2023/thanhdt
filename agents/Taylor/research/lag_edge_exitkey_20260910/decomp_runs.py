# -*- coding: utf-8 -*-
"""decomp_runs.py — is the +0.02pp net delta 'small everywhere' or 'large but cancelling'?

Splits the exitkey-vs-ctrl log-NAV delta over the 15 contiguous gate-disagreement runs
(N = independent events, per PREREG) plus the residual outside them. A near-zero net that
is the sum of large opposite-signed run effects is a DIFFERENT (weaker) claim than a
near-zero net that is small in every run — this separates the two.
"""
import os, sys, io
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR)
B = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_%s_univpit.csv"

def load(leg):
    d = pd.read_csv(B % leg, low_memory=False)
    dl = d[d.record_type == "DAILY"].copy(); dl.index = pd.to_datetime(dl["ymd"])
    nav = pd.to_numeric(dl["combined_nav"], errors="coerce").dropna().sort_index()
    w = pd.to_numeric(dl["w_lag_tgt"], errors="coerce").reindex(nav.index)
    return nav, w

n0, w0 = load("ekctrl"); n1, w1 = load("ekexit")
l0 = np.log(n0).diff().fillna(0.0); l1 = np.log(n1).diff().fillna(0.0)
dlt = (l1 - l0)
diff = (w0 - w1).abs() > 1e-9
blk = (diff != diff.shift()).cumsum()

rows = []
for k, g in diff[diff].groupby(blk[diff]):
    # attribute the run window PLUS the 25 sessions after it (the tilt's effect persists
    # until the allocator band re-rebalances; a pure in-window cut would understate it)
    i0 = n0.index.get_loc(g.index[0]); i1 = n0.index.get_loc(g.index[-1])
    win = n0.index[i0:min(i1 + 26, len(n0))]
    rows.append(dict(start=g.index[0].date(), end=g.index[-1].date(), n_sess=len(g),
                     ctrl_tilts=bool(w0.loc[g.index[0]] > 0.55),
                     d_in_window=round(float(dlt.loc[g.index].sum()) * 100, 3),
                     d_window_plus25=round(float(dlt.loc[win].sum()) * 100, 3)))
r = pd.DataFrame(rows)
print("PER-RUN contribution to the log-NAV delta (exitkey - ctrl), in log-% points")
print(r.to_string(index=False))
tot = float(dlt.sum()) * 100
inw = r["d_in_window"].sum()
print(f"\nsum over the 15 runs (in-window)   = {inw:+.3f} log-%")
print(f"gross movement sum|run|            = {r['d_in_window'].abs().sum():+.3f} log-%")
print(f"largest single run                 = {r['d_in_window'].abs().max():+.3f} log-%")
print(f"residual OUTSIDE every run         = {tot - inw:+.3f} log-%   (pure path divergence)")
print(f"TOTAL 2014-2026                    = {tot:+.3f} log-%")
pos = (r["d_in_window"] > 0).sum(); neg = (r["d_in_window"] < 0).sum()
print(f"\nsign split across N=15 runs: {pos} positive / {neg} negative"
      f"   -> two-sided sign test p = {2*min(pos,neg)/15:.2f} (informal; runs are not iid)")
yrs = (n0.index[-1] - n0.index[0]).days / 365.25
print(f"\nannualised: total {tot/100:.5f} log over {yrs:.2f}y = {(np.exp(tot/100/yrs)-1)*100:+.3f}pp CAGR")
