# -*- coding: utf-8 -*-
"""analyze_legs.py — exit-keyed A/B analysis (job Taylor_20260910_142406).

Recomputes headline metrics INDEPENDENTLY from each leg's DAILY combined-NAV column
(quant-research: verify the artifact, not the self-report), then decomposes the
control-vs-treatment delta by year and over the 16 gate-disagreement runs.
"""
import os, sys, io
import numpy as np, pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR)
EDGE = "data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_exp_%s_univpit.csv"
NOEDGE = "data/v23_golive_audit_2014_now_matpostbull_shrink0_etfliqcustompitg_wtnamecap_advprice_exp_%s_univpit.csv"
LEGS = [("ekctrl", EDGE, "ctrl  = pin R3, entry-keyed gate"),
        ("ekinert", EDGE, "inert = research engine copy, switch OFF"),
        ("ekexit", EDGE, "exitkey = gate reads mean12_av on exit axis"),
        ("eknoedge", NOEDGE, "noedge = allocator WITHOUT the edge gate")]


def load(leg, pat):
    f = pat % leg
    if not os.path.exists(f): return None
    d = pd.read_csv(f, low_memory=False)
    m = d[d.record_type == "METRIC"].set_index("key")["value"]
    dl = d[d.record_type == "DAILY"].copy()
    navcol = [c for c in dl.columns if "combined" in c.lower() and "nav" in c.lower()][0]
    dl.index = pd.to_datetime(dl["ymd"])
    nav = pd.to_numeric(dl[navcol], errors="coerce").dropna().sort_index()
    w = pd.to_numeric(dl.get("w_lag_tgt"), errors="coerce") if "w_lag_tgt" in dl.columns else None
    return m, nav, w, f


def metrics(nav):
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1
    r = nav.pct_change().dropna()
    sh = r.mean() / r.std(ddof=1) * np.sqrt(len(r) / yrs) if r.std(ddof=1) > 0 else np.nan
    dd = (nav / nav.cummax() - 1).min()
    return cagr * 100, sh, dd * 100, cagr / abs(dd), nav.iloc[-1] / 1e9


data = {}
for leg, pat, _ in LEGS:
    g = load(leg, pat)
    if g is None: print(f"  (MISSING: {leg} -> {pat % leg})"); continue
    data[leg] = g

print("=" * 112)
print("HEADLINE — independent recompute from DAILY.combined_nav (harness METRIC rows in brackets)")
print("=" * 112)
print(f"{'leg':46s} {'CAGR%':>8s} {'Sharpe':>7s} {'MaxDD%':>8s} {'Calmar':>7s} {'FinalNAV_B':>11s}")
print("-" * 112)
for leg, _, lab in LEGS:
    if leg not in data: continue
    m, nav, w, f = data[leg]
    c, s, dd, cal, fn = metrics(nav)
    print(f"{lab:46s} {c:8.2f} {s:7.2f} {dd:8.2f} {cal:7.2f} {fn:11.2f}")
    hm = {k: m.get(k) for k in ("cagr_pct", "sharpe", "maxdd_pct", "calmar", "final_nav_vnd")}
    print(f"{'    harness METRIC rows':46s} {hm}")

if "ekctrl" in data and "ekexit" in data:
    c0 = metrics(data["ekctrl"][1]); c1 = metrics(data["ekexit"][1])
    print("\n" + "=" * 112)
    print(f"TREATMENT DELTA (exitkey - ctrl):  CAGR {c1[0]-c0[0]:+.3f}pp   Sharpe {c1[1]-c0[1]:+.3f}"
          f"   MaxDD {c1[2]-c0[2]:+.3f}pp   Calmar {c1[3]-c0[3]:+.3f}   FinalNAV {c1[4]-c0[4]:+.2f}B")
    if "eknoedge" in data:
        cb = metrics(data["eknoedge"][1])
        print(f"\nEDGE PREMIUM in this harness (vs the SAME allocator with the gate off):")
        print(f"  entry-keyed (as published) : {c0[0]-cb[0]:+.3f}pp   ({c0[0]:.2f}% vs {cb[0]:.2f}%)")
        print(f"  exit-keyed  (causal)       : {c1[0]-cb[0]:+.3f}pp   ({c1[0]:.2f}% vs {cb[0]:.2f}%)")
        print(f"  SURVIVING SHARE            : {(c1[0]-cb[0])/(c0[0]-cb[0])*100:.1f}%")

    # --- where the two legs' gate decisions differ, and what it cost -----------
    w0, w1 = data["ekctrl"][2], data["ekexit"][2]
    if w0 is not None and w1 is not None:
        w0 = w0.dropna(); w1 = w1.reindex(w0.index)
        diff = (w0 - w1).abs() > 1e-9
        print(f"\nw_lag_tgt differs on {int(diff.sum()):,} of {len(w0):,} sessions "
              f"({diff.mean()*100:.1f}%)")
        blk = (diff != diff.shift()).cumsum()
        runs = [(g.index[0].date(), g.index[-1].date(), len(g))
                for _, g in diff[diff].groupby(blk[diff])]
        print(f"  contiguous disagreement runs (N as independent events) = {len(runs)}")
        for a, b, n in runs: print(f"    {a} -> {b}  ({n} sessions)")

    # --- per-year log-return decomposition -------------------------------------
    n0, n1 = data["ekctrl"][1], data["ekexit"][1]
    l0 = np.log(n0).diff().dropna(); l1 = np.log(n1).diff().dropna()
    yr = pd.DataFrame({"ctrl": l0.groupby(l0.index.year).sum(),
                       "exitkey": l1.groupby(l1.index.year).sum()})
    yr["delta_log"] = yr["exitkey"] - yr["ctrl"]
    print("\nPER-YEAR log-return delta (exitkey - ctrl):")
    print(yr.round(4).to_string())
    print(f"  total delta_log = {yr['delta_log'].sum():+.5f}")
    top = yr["delta_log"].abs().sort_values(ascending=False)
    print(f"  largest single year = {top.index[0]} ({yr.loc[top.index[0],'delta_log']:+.4f}), "
          f"share of |total| = {top.iloc[0]/yr['delta_log'].abs().sum()*100:.0f}% of gross movement")
