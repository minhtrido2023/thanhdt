# -*- coding: utf-8 -*-
"""route_v3latest_arm.py — the MISSING attribution arm (job Taylor_20260714_121717).

Every number quoted so far (v3route +7.63pp, v3route3 +6.17pp) is measured against the PRODUCTION
baseline `yieldcombo`. But v3route3 differs from yieldcombo in TWO independent ways:

  (a) the whole valuation axis: rank(1/PE)+rank(1/PCF)  ->  the v3latest 8L composite
      (route-weighted ey/cfy/ps, coverage-aware percentiles, golden-cell floor) for EVERY route;
  (b) the financial route fix: BANK/INSURANCE/SECURITIES -> value_score_v2 (pb_z, no 1/PCF lens).

The user's premise — "a bank's PCF is not a manufacturer's PCF" — is a claim about (b) ONLY.
`v3latest` is the arm that separates them, and it was never built:

    v3route3 - yieldcombo  = (a) + (b)   <- what has been quoted as "route-aware repricing"
    v3latest - yieldcombo  = (a)          <- the 8L composite axis, nothing to do with routes
    v3route3 - v3latest    = (b)          <- the ACTUAL route-aware repricing edge

If (a) carries most of the spread, the route claim is misattributed regardless of how the scale
fix or the placebo come out.

Run: $DNA_PYEXE mike/agents/Taylor/route_exp/route_v3latest_arm.py
"""
import os, sys
import numpy as np, pandas as pd

WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import bq  # noqa: E402
import custom_basket as cb  # noqa: E402

START, END = "2014-01-02", "2026-06-19"
OUT = os.path.dirname(os.path.abspath(__file__))
FIN = {"BANK", "INSURANCE", "SECURITIES"}

PANEL = pd.read_csv(os.path.join(WORKDIR, "data", "value_panel_2014.csv"), parse_dates=["time"])
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
    return out


def finw(mem):
    m = mem.copy(); m["route"] = m.ticker.map(ROUTE).fillna("?")
    return m.groupby("rebal_date").apply(lambda g: g.route.isin(FIN).sum()).mean()


print("building v3latest (the missing attribution arm) ...")
lvl, mem = build("v3latest")
lvl.to_csv(os.path.join(OUT, "vehicle_level_v3latest.csv"), index=False)
mem.to_csv(os.path.join(OUT, "members_v3latest.csv"), index=False)

rows = []
for a in ("yieldcombo", "v3latest", "v3route", "v3route2", "v3route3"):
    p = os.path.join(OUT, f"vehicle_level_{a}.csv")
    if not os.path.exists(p):
        continue
    L = pd.read_csv(p, parse_dates=["time"])
    m = vmetrics(L, a)
    mp = os.path.join(OUT, f"members_{a}.csv")
    m["fin_per30"] = finw(pd.read_csv(mp, parse_dates=["rebal_date"])) if os.path.exists(mp) else np.nan
    rows.append(m)

R = pd.DataFrame(rows).set_index("label")
R.to_csv(os.path.join(OUT, "attribution_metrics.csv"))
print("\n" + "=" * 100)
print("ATTRIBUTION — where does the spread actually come from?")
print("=" * 100)
print(R[["CAGR", "Sharpe", "MaxDD", "Calmar", "CAGR_IS", "CAGR_OOS", "fin_per30"]].round(2).to_string())

B, Lt, R3 = R.loc["yieldcombo", "CAGR"], R.loc["v3latest", "CAGR"], R.loc["v3route3", "CAGR"]
print("\n" + "-" * 100)
print(f"  (a) 8L composite axis   v3latest - yieldcombo = {Lt-B:+6.2f}pp   <- NOT route-aware; "
      f"pure valuation-axis upgrade")
print(f"  (b) route-aware fix     v3route3 - v3latest   = {R3-Lt:+6.2f}pp   <- the user's premise, isolated")
print(f"      total quoted so far v3route3 - yieldcombo = {R3-B:+6.2f}pp")
print("-" * 100)
share = 100 * (R3 - Lt) / (R3 - B) if abs(R3 - B) > 1e-9 else float("nan")
print(f"  the route fix is {share:.0f}% of the quoted spread; the other {100-share:.0f}% is the "
      f"composite axis, which was never the thing under debate.")
for tag in ("CAGR_IS", "CAGR_OOS"):
    print(f"    {tag:9s}: (a) {R.loc['v3latest',tag]-R.loc['yieldcombo',tag]:+6.2f}pp | "
          f"(b) {R.loc['v3route3',tag]-R.loc['v3latest',tag]:+6.2f}pp")
print("\nDONE — artifacts in", OUT)
