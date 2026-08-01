# -*- coding: utf-8 -*-
"""analyze_engine.py — FULL-ENGINE-TIER (portfolio NAV) analysis of the FSCORE enhancer legs.
Job Taylor_20260801_131833.

Tier 2 of the two-tier requirement (quant-research skill §6). Reads each leg's audit CSV
(the same artifact extract_peryear.py reads, so the numbers here are reproducible by that
independent script) and reports, per leg:
   Full / IS(2014-01-02..2019-12-31) / OOS(2020-01-01..end) CAGR, Sharpe, MaxDD, Calmar
   + per-year return, + per-year leave-one-out on the OOS delta vs ctrl.

OOS is the tiebreaker (skill §5 — the v3latest lesson), never Full.
"""
import os, sys, glob
import numpy as np, pandas as pd

WORK = "/home/trido/thanhdt/WorkingClaude"
EXPDIR = os.path.join(WORK, "data", "fscore_c30v_20260801")
PREFIX = os.path.join(
    WORK, "data",
    "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_")
IS_END = pd.Timestamp("2019-12-31")
OOS_BEG = pd.Timestamp("2020-01-01")

LEGS = ["fsctrl", "fsctrl2",
        "tieb_k05", "tieb_k10", "tieb_k20",
        "blend_w010", "blend_w020", "blend_w040", "blend_w080", "blend_w200",
        "wtilt_t030", "wtilt_t060", "wtilt_t090",
        "plac_k10_s1", "plac_k10_s2", "plac_k10_s3", "plac_k10_s4"]


def nav_series(tag):
    p = f"{PREFIX}{tag}_univpit_exp_{tag}.csv"
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p, low_memory=False)
    d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
    d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
    d = d.dropna(subset=["ymd"]).sort_values("ymd")
    return d.groupby("ymd")["combined_nav"].last().astype(float)


def met(s):
    s = s.dropna()
    if len(s) < 30:
        return dict(CAGR=np.nan, Sharpe=np.nan, MaxDD=np.nan, Calmar=np.nan)
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    r = s.pct_change().dropna()
    sh = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    dd = (s / s.cummax() - 1).min()
    return dict(CAGR=100 * cagr, Sharpe=sh, MaxDD=100 * dd,
                Calmar=(cagr / abs(dd) if dd < 0 else np.nan))


def peryear(s):
    out = {}
    for y in range(int(s.index[0].year), int(s.index[-1].year) + 1):
        ny = s[s.index.year == y]
        if len(ny) < 5:
            continue
        out[y] = 100 * (ny.iloc[-1] / ny.iloc[0] - 1)
    return out


rows, py = [], {}
navs = {}
for tag in LEGS:
    s = nav_series(tag)
    if s is None:
        print(f"  [skip] {tag}: audit CSV not written yet")
        continue
    navs[tag] = s
    f = met(s); i = met(s[s.index <= IS_END]); o = met(s[s.index >= OOS_BEG])
    py[tag] = peryear(s)
    rows.append(dict(leg=tag, n_days=len(s),
                     CAGR=f["CAGR"], Sharpe=f["Sharpe"], MaxDD=f["MaxDD"], Calmar=f["Calmar"],
                     IS_CAGR=i["CAGR"], IS_Sharpe=i["Sharpe"], IS_Calmar=i["Calmar"],
                     OOS_CAGR=o["CAGR"], OOS_Sharpe=o["Sharpe"], OOS_MaxDD=o["MaxDD"],
                     OOS_Calmar=o["Calmar"]))

t = pd.DataFrame(rows).set_index("leg")
if "fsctrl" in t.index:
    c = t.loc["fsctrl"]
    for k in ("CAGR", "IS_CAGR", "OOS_CAGR", "Sharpe", "IS_Sharpe", "OOS_Sharpe", "Calmar",
              "OOS_Calmar", "MaxDD"):
        t["d_" + k] = t[k] - c[k]

t.to_csv(os.path.join(EXPDIR, "tier2_engine_metrics.csv"))
pd.set_option("display.width", 250, "display.max_columns", 40)
print("\n== TIER 2 (full engine, combined NAV) ==")
print(t[["CAGR", "Sharpe", "MaxDD", "Calmar", "IS_CAGR", "OOS_CAGR", "OOS_Sharpe",
         "OOS_Calmar"]].round(3).to_string())
print("\n== deltas vs ctrl (pp / units) — OOS is the tiebreaker ==")
print(t[["d_CAGR", "d_IS_CAGR", "d_OOS_CAGR", "d_Sharpe", "d_OOS_Sharpe", "d_OOS_Calmar",
         "d_MaxDD"]].round(3).to_string())

# ---- per-year table + leave-one-year-out on the OOS delta -------------------------------
pyt = pd.DataFrame(py).T
pyt.to_csv(os.path.join(EXPDIR, "tier2_peryear.csv"))
print("\n== per-year total return (%) ==")
print(pyt.round(1).to_string())

if "fsctrl" in navs:
    print("\n== per-year OOS delta vs ctrl (pp) + leave-one-year-out mean ==")
    oos_years = [y for y in pyt.columns if y >= 2020]
    lo = []
    for leg in t.index:
        if leg == "fsctrl":
            continue
        d = {y: pyt.loc[leg, y] - pyt.loc["fsctrl", y] for y in oos_years}
        vals = np.array(list(d.values()), dtype=float)
        worst = min(oos_years, key=lambda y: -abs(d[y]))  # placeholder, replaced below
        # LOO: drop the single year that contributes most to the mean
        loo = {y: float(np.mean([v for yy, v in d.items() if yy != y])) for y in oos_years}
        drv = max(oos_years, key=lambda y: abs(float(np.mean(vals)) - loo[y]))
        lo.append(dict(leg=leg, oos_mean_pp=float(np.mean(vals)),
                       n_pos=int((vals > 0).sum()), n_yrs=len(vals),
                       worst_yr=int(min(d, key=d.get)), worst_pp=float(min(d.values())),
                       driver_yr=int(drv), loo_drop_driver=loo[drv],
                       **{f"y{y}": d[y] for y in oos_years}))
    lot = pd.DataFrame(lo).set_index("leg")
    lot.to_csv(os.path.join(EXPDIR, "tier2_loo.csv"))
    print(lot.round(2).to_string())
print("\nwrote tier2_engine_metrics.csv / tier2_peryear.csv / tier2_loo.csv")
