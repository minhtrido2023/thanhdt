# -*- coding: utf-8 -*-
"""route_abstain_sens.py — §3 ABSTAIN isolation + §4 sensitivity plateau (job Taylor_20260714_121717).

§3 ABSTAIN. v3route* drops a financial with no pb_z (rating_8l's own abstain rule). In 2014-19 that is
~20% of all financial exclusions, and pb_z coverage GROWS over time (a name needs 5y of PB history).
So part of the "edge" may be a DATA-COVERAGE artifact: early years hold fewer banks because the panel
did not know their PB yet, not because they were judged expensive. V3R_ABSTAIN_IMPUTE=1 gives a
no-pb_z financial the route-median pb_z instead of dropping it, so it competes on its real ey.
  edge(v3route3) - edge(v3route3_abstimp) = the abstain/coverage contribution.

§4 SENSITIVITY. W_ABS_V2 / cfo nudge / track bonus were tuned inside rating_8l's WITHIN-route problem.
Nothing says they survive a CROSS-route cut. A plateau = mechanism; a spike at the default = fragile
point. This is EVIDENCE, not a tuning opportunity: the reference arm stays the rating_8l-verbatim
default no matter which cell scores best. N declared up front = 8 runs (1 abstain + 7 sens).

Run: $DNA_PYEXE mike/agents/Taylor/route_exp/route_abstain_sens.py
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

# (label, env overrides on top of v3route3). Defaults = rating_8l verbatim: W_ABS .65, cfo +.05/-.08,
# track +.03/+.03. The reference arm v3route3 is read from disk (already built by route_fix_compare).
RUNS = [
    ("v3route3_abstimp", {"V3R_ABSTAIN_IMPUTE": "1"}),                       # §3
    ("sens_wabs055",     {"V3R_W_ABS": "0.55"}),                             # §4 W_ABS_V2
    ("sens_wabs075",     {"V3R_W_ABS": "0.75"}),
    ("sens_cfo_off",     {"V3R_CFO_UP": "0.0",  "V3R_CFO_DN": "0.0"}),       # §4 cfo nudge
    ("sens_cfo_x2",      {"V3R_CFO_UP": "0.10", "V3R_CFO_DN": "-0.16"}),
    ("sens_trk_off",     {"V3R_TRK_CF": "0.0",  "V3R_TRK_ROE": "0.0"}),      # §4 track bonus
    ("sens_trk_x2",      {"V3R_TRK_CF": "0.06", "V3R_TRK_ROE": "0.06"}),
]


def build(mode, env=None):
    keys = ["BASKET_SELECT"] + list((env or {}).keys())
    save = {k: os.environ.get(k) for k in keys}
    os.environ["BASKET_SELECT"] = mode
    for k, v in (env or {}).items():
        os.environ[k] = v
    try:
        lvl, adv, mem, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                         gate_rating=3, weight_scheme="namecap",
                                         top_n=30, name_cap=0.10, qtilt=None)
    finally:
        for k, v in save.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v
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


# ---- reference arms already on disk ----
ref = {}
for a in ("yieldcombo", "v3route3"):
    ref[a] = pd.read_csv(os.path.join(OUT, f"vehicle_level_{a}.csv"), parse_dates=["time"])
rows = [vmetrics(ref["yieldcombo"], "yieldcombo"), vmetrics(ref["v3route3"], "v3route3")]
rows[0]["fin_per30"] = finw(pd.read_csv(os.path.join(OUT, "members_yieldcombo.csv"), parse_dates=["rebal_date"]))
rows[1]["fin_per30"] = finw(pd.read_csv(os.path.join(OUT, "members_v3route3.csv"), parse_dates=["rebal_date"]))
BASE = rows[0]["CAGR"]; REF = rows[1]["CAGR"]
print(f"reference: yieldcombo {BASE:.2f}%  |  v3route3 {REF:.2f}%  |  real edge {REF-BASE:+.2f}pp\n")

print("=" * 100)
print(f"Building {len(RUNS)} arms (§3 abstain + §4 sensitivity) — several minutes each")
print("=" * 100)
for label, env in RUNS:
    lvl, mem = build("v3route3", env)
    lvl.to_csv(os.path.join(OUT, f"vehicle_level_{label}.csv"), index=False)
    mem.to_csv(os.path.join(OUT, f"members_{label}.csv"), index=False)
    m = vmetrics(lvl, label); m["fin_per30"] = finw(mem)
    rows.append(m)
    print(f"  {label:18s}: CAGR {m['CAGR']:6.2f}%  edge {m['CAGR']-BASE:+6.2f}pp  "
          f"(vs v3route3 {m['CAGR']-REF:+6.2f}pp)  fin {m['fin_per30']:.2f}/30  "
          f"IS {m.get('CAGR_IS', float('nan')):.2f} OOS {m.get('CAGR_OOS', float('nan')):.2f}")

R = pd.DataFrame(rows).set_index("label")
R["edge_vs_base"] = R.CAGR - BASE
R.to_csv(os.path.join(OUT, "abstain_sens_metrics.csv"))

print("\n" + "=" * 100)
print("§3 ABSTAIN CONTRIBUTION")
print("=" * 100)
ab = R.loc["v3route3_abstimp"]
print(f"  v3route3          edge {REF-BASE:+.2f}pp  (fin {R.loc['v3route3','fin_per30']:.2f}/30)")
print(f"  v3route3_abstimp  edge {ab.edge_vs_base:+.2f}pp  (fin {ab.fin_per30:.2f}/30)  "
      f"<- no-pb_z financials kept, judged on real ey")
print(f"  => abstain/coverage contribution = {(REF-BASE) - ab.edge_vs_base:+.2f}pp "
      f"({100*((REF-BASE)-ab.edge_vs_base)/(REF-BASE):.0f}% of the edge)")
print(f"  => valuation-judgement residual  = {ab.edge_vs_base:+.2f}pp")

print("\n" + "=" * 100)
print("§4 SENSITIVITY PLATEAU (evidence only — reference arm stays rating_8l-verbatim regardless)")
print("=" * 100)
S = R.loc[[l for l, _ in RUNS if l.startswith("sens_")]]
print(pd.concat([R.loc[["v3route3"]], S])[["CAGR", "edge_vs_base", "CAGR_IS", "CAGR_OOS", "fin_per30"]]
      .round(2).to_string())
sp = pd.concat([R.loc[["v3route3"]], S]).edge_vs_base
print(f"\n  edge across the 8 sensitivity cells: min {sp.min():+.2f}pp  max {sp.max():+.2f}pp  "
      f"sd {sp.std():.2f}  (all positive: {bool((sp > 0).all())})")
print("  PLATEAU if the default is NOT a lone spike; FRAGILE if edge collapses off-default.")
print("\nDONE — artifacts in", OUT)
