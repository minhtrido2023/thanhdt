# -*- coding: utf-8 -*-
"""Phase-0 0b — ATTRIBUTION LADDER cho drop-in fail (job Taylor_20260711_114557).

Tach degradation cua drop-in tier8l (27.15% vs control 28.82%) thanh 2 hieu ung:
  control  = legacy scale + legacy coverage  (PIN R3)
  maskleg  = 8L scale     + legacy coverage  -> delta = HIEU UNG DOI THANG DO (scale)
  legcov8l = legacy scale + 8L coverage (COALESCE fill NULL) -> delta = HIEU UNG COVERAGE
  tier8l   = 8L scale     + 8L coverage      (drop-in da bac) -> check additivity
Read-only. Conventions y het fa8l_compare_20260711.py (registry: daily combined_nav, ANN=252).
"""
import os, sys, math
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from dsr_pbo_annex import load_nav, daily_logret, ANN

EXP = "data/fa8l_exp"
CSVS = {
    "control_legacy":  f"{EXP}/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_falegacy_control.csv",
    "diag_maskleg":    f"{EXP}/v23_fa8l_diag_maskleg_20260711.csv",
    "diag_legcov8l":   f"{EXP}/v23_fa8l_diag_legcov8l_20260711.csv",
    "tier8l_dropin":   f"{EXP}/v23_fatier8l_exp_20260711.csv",
}

def metrics(nav):
    r = daily_logret(nav)
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    sh = r.mean() / r.std(ddof=1) * math.sqrt(ANN)
    mdd = (nav / nav.cummax() - 1).min()
    return cagr * 100, sh, mdd * 100, (cagr / abs(mdd) if mdd else np.nan)

def window(nav, lo=None, hi=None):
    s = nav
    if lo: s = s[s.index >= lo]
    if hi: s = s[s.index <= hi]
    return s

navs = {}
for k, p in CSVS.items():
    navs[k] = load_nav(p)
    print(f"loaded {k}: {len(navs[k])} daily obs ({navs[k].index[0].date()} -> {navs[k].index[-1].date()})")

print("\n" + "=" * 110)
print("[0b] ATTRIBUTION LADDER — FULL + IS(2014-19) + OOS(2020+)")
print("=" * 110)
rows = {}
for k, nav in navs.items():
    f = metrics(nav); i = metrics(window(nav, hi="2019-12-31")); o = metrics(window(nav, lo="2020-01-01"))
    rows[k] = (f, i, o)
    print(f"{k:16s} FULL: CAGR {f[0]:6.2f}%  Sh {f[1]:.2f}  MaxDD {f[2]:6.1f}%  Calmar {f[3]:.2f}"
          f"  | IS: {i[0]:6.2f}%/{i[3]:.2f}  | OOS: {o[0]:6.2f}%/{o[3]:.2f}")

c = rows["control_legacy"]
print("\n--- DELTA vs control (FULL CAGR pp | OOS CAGR pp | OOS Calmar) ---")
for k in ["diag_maskleg", "diag_legcov8l", "tier8l_dropin"]:
    d = rows[k]
    print(f"{k:16s}  dFULL {d[0][0]-c[0][0]:+6.2f}pp   dOOS {d[2][0]-c[2][0]:+6.2f}pp   dOOSCalmar {d[2][3]-c[2][3]:+.2f}")
scale_eff = rows["diag_maskleg"][0][0] - c[0][0]
cov_eff = rows["diag_legcov8l"][0][0] - c[0][0]
both = rows["tier8l_dropin"][0][0] - c[0][0]
print(f"\nAdditivity check (FULL): scale {scale_eff:+.2f}pp + coverage {cov_eff:+.2f}pp = {scale_eff+cov_eff:+.2f}pp"
      f"  vs drop-in thuc do {both:+.2f}pp  (interaction {both-scale_eff-cov_eff:+.2f}pp)")

print("\n--- PER-YEAR ---")
yr_tbl = {}
for k, nav in navs.items():
    out = {}
    for y in range(nav.index[0].year, nav.index[-1].year + 1):
        ny = nav[nav.index.year == y]
        if len(ny) >= 5: out[y] = (ny.iloc[-1] / ny.iloc[0] - 1) * 100
    yr_tbl[k] = out
ydf = pd.DataFrame(yr_tbl).round(2)
ydf["d_maskleg"] = (ydf["diag_maskleg"] - ydf["control_legacy"]).round(2)
ydf["d_legcov8l"] = (ydf["diag_legcov8l"] - ydf["control_legacy"]).round(2)
ydf["d_dropin"] = (ydf["tier8l_dropin"] - ydf["control_legacy"]).round(2)
print(ydf.to_string())
print("\nDONE 0b compare.")
