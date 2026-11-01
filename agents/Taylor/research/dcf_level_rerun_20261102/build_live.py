# -*- coding: utf-8 -*-
"""Việc 1: OShares 'live' PIT cho mọi (t, mã) của panel — oshares_pit (production) + luật R10. Một lần BQ."""
import os, sys, time
import numpy as np, pandas as pd
WC = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WC)
OLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dcf_vn_calibration_20261101", "data")
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ["DCF_RATE_FRAME"] = "domestic_v2"
import oshares_pit as OP
import oshares_live as OL
LIVE_BELOW_FIN_TOL = 0.005   # = dcf_valuation.LIVE_BELOW_FIN_TOL (assert bên dưới)
pan = pd.read_parquet(os.path.join(OLD, "panel_monthly.parquet"))[["t", "ticker", "OShares"]]
tks = sorted(pan.ticker.unique())
until = str(pan.t.max().date())
t0 = time.time()
cache = OL._fetch(tks, until)
print("BQ fetch", round(time.time() - t0), "s; quarters", len(cache[0]), "corp", len(cache[1]))
out = []
for t, g in pan.groupby("t"):
    asof = str(t.date())
    fb = dict(zip(g.ticker, g.OShares))
    recs = OP.oshares_pit(list(g.ticker), asof, fb, cache=cache)
    for tk in g.ticker:
        r = recs[tk]
        out.append((t, tk, r["value"], r["source"], r.get("method"), r.get("live_value")))
L = pd.DataFrame(out, columns=["t", "ticker", "os_pit", "source", "method", "live_value"])
L = L.merge(pan, on=["t", "ticker"])
# R10: live < quý*(1-tol) => số quý (như dcf_valuation._live_oshares (e))
below = (L.source == "oshares_live") & (L.os_pit < L.OShares * (1 - LIVE_BELOW_FIN_TOL))
L["os_live"] = np.where(below, L.OShares, L.os_pit)
L["r10_fallback"] = below
L.to_parquet(os.path.join(HERE, "data", "os_live.parquet"))
print("rows", len(L), "| source", L.source.value_counts().to_dict(), "| R10 fallback", int(below.sum()))
d = (L.os_live / L.OShares - 1)
print("os_live != fin:", int((d.abs() > 1e-9).sum()), "rows; |diff|>10%:", int((d.abs() > .1).sum()))
import dcf_valuation as D
assert D.LIVE_BELOW_FIN_TOL == LIVE_BELOW_FIN_TOL
