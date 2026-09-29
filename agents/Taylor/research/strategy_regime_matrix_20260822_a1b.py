#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A1b — doi chuan THU HAI cho parking: TIEN NHAN ROI 0%/nam (CLAUDE.md §Backtest quy uoc chi phi).
Parking custom30V trong NEUTRAL thay the TIEN NHAN ROI trong so BAL (ETF_PARK={3:0.8}), KHONG
thay the VNINDEX. Nen excess-vs-VNI o a1 la goc doc TUONG DOI; goc doc DUNG voi production la
CAGR tuyet doi cua ro (vs 0%). Bang nay bo sung CI cho CAGR tuyet doi + phan ra 2 goc doc."""
import os, sys
import numpy as np, pandas as pd
W = "/home/trido/thanhdt/WorkingClaude"
OUT = os.path.join(W, "mike", "agents", "Taylor", "research", "strategy_regime_matrix_20260822")
SPY = 249.2785102175346
d = pd.read_csv(os.path.join(OUT, "a1_daily.csv"), parse_dates=["time"]).set_index("time")

def cagr(r):
    r = r.dropna()
    return np.nan if len(r) < 20 else (1 + r).prod() ** (SPY / len(r)) - 1

def boot_level(x, L=20, B=4000, seed=11):
    x = x.dropna().values; n = len(x)
    if n < 3 * L: return (np.nan,) * 3
    rng = np.random.default_rng(seed); nb = int(np.ceil(n / L)); o = np.empty(B)
    for b in range(B):
        st = rng.integers(0, n - L + 1, nb)
        ix = np.concatenate([np.arange(s, s + L) for s in st])[:n]
        o[b] = (1 + x[ix]).prod() ** (SPY / n) - 1
    return tuple(float(np.percentile(o, p)) for p in (5, 50, 95))

rows = []
for scope, sel in [("ALL/LOW", d.bucket == "LOW"), ("ALL/MID", d.bucket == "MID"),
                   ("ALL/HIGH", d.bucket == "HIGH"), ("ALL/*", d.bucket.notna()),
                   ("NEUTRAL/LOW", (d.bucket == "LOW") & (d.state == 3)),
                   ("NEUTRAL/MID", (d.bucket == "MID") & (d.state == 3)),
                   ("NEUTRAL/HIGH", (d.bucket == "HIGH") & (d.state == 3)),
                   ("NEUTRAL/*", d.state == 3)]:
    r = {"scope": scope, "n_days": int(sel.sum())}
    for k in ["base", "cap40", "cap50", "bank", "nonbank"]:
        lo, md, hi = boot_level(d.loc[sel, f"r_{k}"])
        r[f"{k}_cagr"] = cagr(d.loc[sel, f"r_{k}"]); r[f"{k}_p5"] = lo; r[f"{k}_p95"] = hi
    r["VNI_cagr"] = cagr(d.loc[sel, "r_vni"])
    rows.append(r)
T = pd.DataFrame(rows)
T.to_csv(os.path.join(OUT, "a1_vs_cash.csv"), index=False)
pd.set_option("display.width", 240, "display.max_columns", 40)
show = T[["scope", "n_days", "VNI_cagr", "base_cagr", "base_p5", "base_p95",
          "cap40_cagr", "cap50_cagr", "bank_cagr", "nonbank_cagr"]].copy()
for c in show.columns[2:]:
    show[c] = (show[c] * 100).round(2)
print("=== A1b — CAGR TUYET DOI cua ro parking (doi chuan that = tien nhan roi 0%/nam) ===")
print("    P(CAGR>0) doc truc tiep tu CI: base_p5 > 0 => an toan hon tien mat o muc 5%")
print(show.to_string(index=False))
