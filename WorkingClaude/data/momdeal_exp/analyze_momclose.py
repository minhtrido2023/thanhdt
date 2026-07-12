# -*- coding: utf-8 -*-
"""Phân tích 3 run đóng kênh MOM (job Taylor_20260712_012515).
Đọc 3 CSV cache-vintage, tính FULL/IS/OOS CAGR-Sharpe-MaxDD-Calmar, per-year, LOO delta,
DSR (N=2 trials pre-registered) cho từng treatment. Deterministic, read-only.
"""
import sys, os, math
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from dsr_pbo_annex import moments, expected_max_sr, dsr as dsr_fn

BASE = ("data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap"
        "{tag}.csv")
RUNS = {
    "control(dropnone)": BASE.format(tag="_exp_dropnone"),
    "ScopeA(-MOM_N,-MOM_S)": BASE.format(tag="_exp_dropMOMN-MOMS"),
    "ScopeB(-family)": BASE.format(tag="_exp_dropMEGA-MOM-MOMN-MOMS"),
}
ANN = 252.0

def load_nav(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby("ymd")["combined_nav"].last().astype(float)

def metrics(nav):
    if len(nav) < 5:
        return dict(cagr=np.nan, sharpe=np.nan, maxdd=np.nan, calmar=np.nan)
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = nav.pct_change().dropna()
    sharpe = r.mean() / r.std(ddof=1) * math.sqrt(ANN)
    dd = (nav / nav.cummax() - 1).min()
    return dict(cagr=cagr * 100, sharpe=sharpe, maxdd=dd * 100,
                calmar=(cagr / abs(dd)) if dd < 0 else np.nan)

def peryear(nav):
    out = {}
    for y in range(nav.index[0].year, nav.index[-1].year + 1):
        ny = nav[nav.index.year == y]
        if len(ny) >= 5:
            out[y] = (ny.iloc[-1] / ny.iloc[0] - 1) * 100
    return out

navs = {k: load_nav(p) for k, p in RUNS.items()}
print("=" * 100)
print("HEADLINE (recompute độc lập từ CSV — đối chiếu với print của engine)")
print(f"{'run':<26}{'FULL CAGR':>10}{'Sharpe':>8}{'MaxDD':>8}{'Calmar':>8}"
      f"{'IS CAGR':>9}{'OOS CAGR':>9}{'OOS Calmar':>11}")
for k, nav in navs.items():
    m = metrics(nav)
    mi = metrics(nav[nav.index <= "2019-12-31"])
    mo = metrics(nav[nav.index >= "2020-01-01"])
    print(f"{k:<26}{m['cagr']:>9.2f}%{m['sharpe']:>8.2f}{m['maxdd']:>7.1f}%{m['calmar']:>8.2f}"
          f"{mi['cagr']:>8.2f}%{mo['cagr']:>8.2f}%{mo['calmar']:>11.2f}")

print("\nPER-YEAR (%):")
py = {k: peryear(nav) for k, nav in navs.items()}
years = sorted(py["control(dropnone)"].keys())
print(f"{'year':<6}" + "".join(f"{k:>24}" for k in navs))
for y in years:
    print(f"{y:<6}" + "".join(f"{py[k].get(y, float('nan')):>+23.2f}%" for k in navs))

print("\nDELTA vs control per-year (pp) + LOO full-CAGR khi bỏ từng năm:")
ctrl = navs["control(dropnone)"]
for k in list(navs)[1:]:
    d = {y: py[k][y] - py["control(dropnone)"][y] for y in years if y in py[k]}
    print(f"  {k}: " + "  ".join(f"{y}:{v:+.1f}" for y, v in d.items()))
    # LOO: replace year-y daily returns of treatment with control's → recompute full CAGR delta
    rT = navs[k].pct_change().dropna()
    rC = ctrl.pct_change().dropna()
    idx = rT.index.intersection(rC.index)
    rT, rC = rT[idx], rC[idx]
    yrs_span = (idx[-1] - idx[0]).days / 365.25
    full_T = ((1 + rT).prod()) ** (1 / yrs_span) - 1
    full_C = ((1 + rC).prod()) ** (1 / yrs_span) - 1
    loo = {}
    for y in years:
        mask = idx.year == y
        rmix = rT.copy(); rmix[mask] = rC[mask]  # bỏ đóng-góp năm y của treatment
        loo[y] = (((1 + rmix).prod()) ** (1 / yrs_span) - 1 - full_C) * 100
    base_delta = (full_T - full_C) * 100
    print(f"    full-delta {base_delta:+.2f}pp | LOO delta khi trung-hòa từng năm: "
          + "  ".join(f"{y}:{v:+.2f}" for y, v in loo.items()))

print("\nDSR (BLdP 2014, N=2 trials pre-registered — 2 scope, không tune):")
for k in list(navs)[1:]:
    r = navs[k].pct_change().dropna().values
    sr_hat, g3, g4 = moments(pd.Series(r))
    # var of SR across the trial family (2 treatments)
    srs = []
    for kk in list(navs)[1:]:
        rr = navs[kk].pct_change().dropna().values
        srs.append(pd.Series(rr).mean() / pd.Series(rr).std(ddof=1))
    var_sr = np.var(srs, ddof=1) if len(srs) > 1 else 1e-8
    sr0 = expected_max_sr(max(var_sr, 1e-12), 2)
    p, stat = dsr_fn(sr_hat, sr0, g3, g4, len(r))
    print(f"  {k}: SR_daily={sr_hat:.4f} SR0={sr0:.5f} DSR={p:.4f} (z={stat:.2f})")
print("\nDone.")
