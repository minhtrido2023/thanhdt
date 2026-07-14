# -*- coding: utf-8 -*-
"""route_fix_compare.py — the decision run for the v3route scale fix (job Taylor_20260714_121717).

quant-skeptic REFUTED v3route: its financial value_score_v2 carries an ABSOLUTE pb_z term while every
other route is scored on pure within-route percentiles, and the top-30 cut is CROSS-route. So the
+7.63pp vehicle edge may be nothing but "financials are systematically under-scored" — a blind sector
underweight wearing a repricing costume.

Four arms, identical in every other respect:
  yieldcombo  production baseline (rank(1/PE)+rank(1/PCF), one metric for banks and manufacturers)
  v3route     the REFUTED original           — financial P90 sits 0.107 BELOW non-financial
  v3route2    naive percentile-norm          — over-corrects, financial P90 0.064 ABOVE
  v3route3    quantile-matched (reference)   — financial P90 gap ~0.000, the only comparable one

v3route/2/3 share IDENTICAL within-route financial ordering (monotone transforms of one v2 score) and
byte-identical non-financial scores. The ONLY thing that varies across the three is how much financial
weight the cross-route cut grants. So:
  edge monotone in financial weight  -> it is a sector bet, not a value mechanism
  edge survives at v3route3          -> the repricing is real

Run: $DNA_PYEXE mike/agents/Taylor/route_exp/route_fix_compare.py
"""
import os, sys
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq  # noqa: E402
import custom_basket as cb  # noqa: E402

START, END = "2014-01-02", "2026-06-19"
FOCUS = pd.Timestamp("2026-05-05")
OUT = os.path.dirname(os.path.abspath(__file__))
ARMS = ["yieldcombo", "v3route", "v3route2", "v3route3"]
FIN = {"BANK", "INSURANCE", "SECURITIES"}

PANEL = pd.read_csv(os.path.join(WORKDIR, "data", "value_panel_2014.csv"), parse_dates=["time"])
PANEL["qstart"] = PANEL["time"].dt.to_period("Q").dt.start_time
ROUTE = PANEL.sort_values("time").groupby("ticker")["route"].last().to_dict()


def build(mode):
    _prev = os.environ.get("BASKET_SELECT")
    os.environ["BASKET_SELECT"] = mode
    try:
        lvl, adv, mem, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                         gate_rating=3, weight_scheme="namecap",
                                         top_n=30, name_cap=0.10, qtilt=None)
    finally:
        if _prev is None: os.environ.pop("BASKET_SELECT", None)
        else: os.environ["BASKET_SELECT"] = _prev
    s = pd.Series(lvl); s.index = pd.to_datetime(s.index)
    lvl = s.sort_index().rename("level").reset_index().rename(columns={"index": "time"})
    mem = mem.copy(); mem["rebal_date"] = pd.to_datetime(mem["rebal_date"])
    return lvl, mem


def vmetrics(lvl, label):
    s = lvl.sort_values("time")
    v = s["level"].astype(float).values; t = s["time"].values
    yrs = (t[-1] - t[0]) / np.timedelta64(365, "D")
    cagr = (v[-1] / v[0]) ** (1 / yrs) - 1
    r = pd.Series(v).pct_change().dropna()
    dd = (pd.Series(v) / pd.Series(v).cummax() - 1).min()
    out = dict(label=label, CAGR=100 * cagr, Sharpe=r.mean() / r.std() * np.sqrt(252),
               MaxDD=100 * dd, Calmar=cagr / abs(dd))
    for tag, a, b in (("IS", "2014-01-01", "2019-12-31"), ("OOS", "2020-01-01", "2026-12-31")):
        m = (s["time"] >= a) & (s["time"] <= b)
        vv = s.loc[m, "level"].astype(float).values; tt = s.loc[m, "time"].values
        if len(vv) > 20:
            yy = (tt[-1] - tt[0]) / np.timedelta64(365, "D")
            out[f"CAGR_{tag}"] = 100 * ((vv[-1] / vv[0]) ** (1 / yy) - 1)
            out[f"MaxDD_{tag}"] = 100 * (pd.Series(vv) / pd.Series(vv).cummax() - 1).min()
    return out


print("=" * 100)
print("Building 4 arms (BQ/local cache; several minutes)")
LVL, MEM = {}, {}
for a in ARMS:
    LVL[a], MEM[a] = build(a)
    MEM[a].to_csv(os.path.join(OUT, f"members_{a}.csv"), index=False)
    LVL[a].to_csv(os.path.join(OUT, f"vehicle_level_{a}.csv"), index=False)
    print(f"  {a:11s}: {len(MEM[a])} member-rows, {MEM[a].ticker.nunique()} union names")

# ---- financial weight actually granted by each arm's cut (the axis under suspicion) ----
print("\n" + "=" * 100)
print("FINANCIAL WEIGHT PER ARM — mean names/30 per rebal (this is what the three arms vary)")
print("=" * 100)
finw = {}
for a in ARMS:
    m = MEM[a].copy(); m["route"] = m.ticker.map(ROUTE).fillna("?")
    per = m.groupby("rebal_date").apply(lambda g: g.route.isin(FIN).sum())
    bank = m.groupby("rebal_date").apply(lambda g: (g.route == "BANK").sum())
    finw[a] = dict(fin_mean=per.mean(), fin_med=per.median(), bank_mean=bank.mean())
    print(f"  {a:11s}: financial {per.mean():5.2f}/30 (med {per.median():.0f})   BANK {bank.mean():5.2f}/30")

print("\n" + "=" * 100)
print("VEHICLE-LEVEL custom30V standalone (the mechanism, undiluted)")
print("=" * 100)
R = pd.DataFrame([vmetrics(LVL[a], a) for a in ARMS]).set_index("label")
print(R.round(2).to_string())
print("\ndelta vs yieldcombo baseline:")
D = (R - R.loc["yieldcombo"]).drop(index="yieldcombo")
print(D.round(2).to_string())
R.to_csv(os.path.join(OUT, "vehicle_metrics_fix.csv"))

print("\n" + "=" * 100)
print("THE TEST: is the edge monotone in financial weight? (-> sector bet, not repricing)")
print("=" * 100)
tab = pd.DataFrame({"fin_names_per30": [finw[a]["fin_mean"] for a in ARMS],
                    "CAGR": [R.loc[a, "CAGR"] for a in ARMS],
                    "edge_vs_base": [R.loc[a, "CAGR"] - R.loc["yieldcombo", "CAGR"] for a in ARMS]},
                   index=ARMS)
print(tab.round(2).to_string())
_c = np.corrcoef(tab.fin_names_per30.values, tab.CAGR.values)[0, 1]
print(f"\n  corr(financial weight, CAGR) across the 4 arms = {_c:+.3f}")
print("  (strongly negative => the 'edge' is just underweighting financials)")
tab.to_csv(os.path.join(OUT, "finweight_vs_edge.csv"))

# ---- basket at the focus rebal ----
print("\n" + "=" * 100)
print(f"BASKET at rebal nearest {FOCUS.date()} — HPG / LPB standing per arm")
print("=" * 100)
for a in ARMS:
    m = MEM[a]; ds = sorted(m.rebal_date.unique())
    pick = max([x for x in ds if x <= FOCUS], default=ds[0])
    b = m[m.rebal_date == pick]
    b_r = b.ticker.map(ROUTE).fillna("?")
    hp = "IN " if "HPG" in set(b.ticker) else "OUT"
    lp = "IN " if "LPB" in set(b.ticker) else "OUT"
    print(f"  {a:11s} @ {pd.Timestamp(pick).date()}: HPG {hp} | LPB {lp} | "
          f"financial {b_r.isin(FIN).sum()}/30 | BANK {(b_r=='BANK').sum()}/30")

print("\nDONE — artifacts in", OUT)
