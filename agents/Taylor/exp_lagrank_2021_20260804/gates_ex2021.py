# -*- coding: utf-8 -*-
"""Re-run EVERY gate of job Taylor_20260804_051145 with 2021 excised (job Taylor_20260804_061252).

Reports BOTH versions side by side for every leg and every gate — never one "prettier" version.
Excising a year is a REAL extra degree of freedom; whether it is legitimate depends on the ex-ante
regime evidence in dispersion_by_year.py, not on the numbers below. That is why both columns print.

Gates (identical formulas to the original job, so numbers are directly comparable):
  Delta CAGR   — annualised mean of the daily log-return difference (treatment - baseline)
  t-stat       — mean/se of that same difference series (the "is the ADD distinguishable from 0" test)
  DSR          — Deflated Sharpe of the difference series, N_trials=10 (the family actually searched)
  PBO          — CSCV over the full 11-config family (10 variants + FIFO)
  LOO          — OOS per-year leave-one-out, drop-2-worst core test, run on the remaining years
Usage: python gates_ex2021.py [1B|50B]
"""
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from dsr_pbo_annex import moments, expected_max_sr, dsr, cscv_pbo

ANN = 252.0
N_TRIALS = 10
SCALE = sys.argv[1] if len(sys.argv) > 1 else "1B"
PRE = ("/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_"
       "edge_etfliqcustompitg_wtnamecap_advprice_exp_")
SUF = "_1B_univpit_nav1B.csv" if SCALE == "1B" else "_50B_univpit.csv"
BASE = ("L0_ctrl1B_univpit_nav1B.csv" if SCALE == "1B" else "L0_ctrl50B_univpit.csv")
LEGS = ["A_dnpr_w0", "A_surprise_w0", "A_pahl3_w0", "A_fill_w0", "A_blend_w0",
        "B_surprise_w5", "B_pahl3_w5", "B_blend_w5", "B_dnpr_w5", "B_fill_w5"]
OOS_START = pd.Timestamp("2020-01-01")


def nav(path):
    df = pd.read_csv(path, low_memory=False)
    d = df[df["record_type"] == "DAILY"].copy()
    d["date"] = pd.to_datetime(d["ymd"])
    return d.sort_values("date").set_index("date")["combined_nav"].astype(float)


base = nav(PRE + BASE)
legs = {lab: nav(PRE + lab + SUF) for lab in LEGS}
idx = base.index
for s in legs.values():
    idx = idx.intersection(s.index)
base, legs = base.loc[idx], {k: v.loc[idx] for k, v in legs.items()}
print(f"scale NAV {SCALE} | {idx[0].date()} -> {idx[-1].date()} | {len(idx)} sessions "
      f"({(idx.year == 2021).sum()} of them in 2021)\n")


def diff_series(lab, drop2021):
    lr_b = np.diff(np.log(base.values))
    lr_t = np.diff(np.log(legs[lab].values))
    d = pd.Series(lr_t - lr_b, index=idx[1:])
    return d[d.index.year != 2021] if drop2021 else d


def gates(lab, drop2021):
    d = diff_series(lab, drop2021)
    dcagr = (np.exp(d.mean() * ANN) - 1) * 100
    t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
    return dcagr, t, d


# ---- var(SR) across the family is itself computed on the same sample, both versions ----
def dsr_family(drop2021):
    ds = {lab: gates(lab, drop2021)[2] for lab in LEGS}
    srs = np.array([moments(v.values)[0] for v in ds.values()])
    sr0 = expected_max_sr(float(np.var(srs, ddof=1)), N_TRIALS)
    out = {}
    for lab, v in ds.items():
        sr, g3, g4 = moments(v.values)
        out[lab] = dsr(sr, sr0, g3, g4, len(v))[0]
    return out, sr0


d_in, sr0_in = dsr_family(False)
d_ex, sr0_ex = dsr_family(True)
print(f"DSR SR_0 (expected max under null, N_trials={N_TRIALS}): "
      f"with-2021 {sr0_in:.5f} | ex-2021 {sr0_ex:.5f}\n")

print(f"{'leg':<16} {'dCAGR in':>9} {'dCAGR ex':>9} | {'t in':>6} {'t ex':>6} | "
      f"{'DSR in':>7} {'DSR ex':>7}   verdict(ex-2021)")
rows = []
for lab in LEGS:
    ci, ti, _ = gates(lab, False)
    ce, te, _ = gates(lab, True)
    v = "PASS" if (te >= 2.0 and d_ex[lab] >= 0.95) else "FAIL"
    print(f"{lab:<16} {ci:+8.2f}% {ce:+8.2f}% | {ti:6.2f} {te:6.2f} | "
          f"{d_in[lab]:7.4f} {d_ex[lab]:7.4f}   {v}")
    rows.append({"leg": lab, "dCAGR_in": ci, "dCAGR_ex": ce, "t_in": ti, "t_ex": te,
                 "DSR_in": d_in[lab], "DSR_ex": d_ex[lab]})
pd.DataFrame(rows).to_csv(f"gates_ex2021_{SCALE}.csv", index=False)

# ---------------------------------------------------------------- PBO both ways
for tag, drop in (("with 2021", False), ("ex 2021 ", True)):
    m = np.ones(len(idx) - 1, dtype=bool) if not drop else (idx[1:].year != 2021)
    lr_b = np.diff(np.log(base.values))[m]
    M = np.column_stack([lr_b] + [np.diff(np.log(legs[l].values))[m] for l in LEGS])
    out = cscv_pbo(M, S=16)
    pbo = out[0] if isinstance(out, tuple) else out
    print(f"\nCSCV PBO (S=16, 11 configs incl FIFO), {tag}: {pbo:.4f} "
          f"{'PASS <0.5' if pbo < 0.5 else 'FAIL >=0.5'}")

# ---------------------------------------------------------------- LOO both ways
print("\n=== OOS per-year leave-one-out, drop-2-worst core test ===")
b_oos = base[base.index >= OOS_START]
years_all = sorted(set(b_oos.index.year))
spy = (len(b_oos) - 1) / ((b_oos.index[-1] - b_oos.index[0]).days / 365.25)


def cagr_of(r):
    n = (1 + r).cumprod()
    return (n.iloc[-1] ** (spy / len(r)) - 1) * 100


def loo(lab, pre_drop):
    """pre_drop = years removed from the sample BEFORE the LOO test (e.g. [2021])."""
    br = base[base.index >= OOS_START].pct_change().dropna()
    tr = legs[lab][legs[lab].index >= OOS_START].pct_change().dropna()
    ri = br.index.intersection(tr.index)
    br, tr = br.loc[ri], tr.loc[ri]
    keep0 = ~br.index.year.isin(pre_drop)
    br, tr = br[keep0], tr[keep0]
    yrs = sorted(set(br.index.year))
    full = cagr_of(tr) - cagr_of(br)
    dd = {}
    for y in yrs:
        m = br.index.year != y
        dd[y] = cagr_of(tr[m]) - cagr_of(br[m])
    top2 = sorted(dd, key=lambda y: dd[y])[:2]
    m2 = ~br.index.year.isin(top2)
    d2 = cagr_of(tr[m2]) - cagr_of(br[m2])
    npos = sum(1 for v in dd.values() if v > 0)
    return full, top2, d2, npos, len(yrs)


print(f"{'leg':<16} | {'with 2021: full  drop2  ->':<40} | ex-2021: full  drop2  ->")
for lab in LEGS:
    f1, t1, d1, p1, n1 = loo(lab, [])
    f2, t2, d2, p2, n2 = loo(lab, [2021])
    print(f"{lab:<16} | {f1:+6.2f}pp  drop{t1[0]}+{t1[1]} {d1:+6.2f}pp  {p1}/{n1}yr pos"
          f"     | {f2:+6.2f}pp  drop{t2[0]}+{t2[1]} {d2:+6.2f}pp  {p2}/{n2}yr pos"
          f"   {'ROBUST' if d2 > 0 else 'LUMPY'}")
