#!/usr/bin/env python3
"""Stage 1 — Q1 LAG equity decomposition + Q2 IC-by-regime. Run with $DNA_PYEXE."""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
import pandas as pd, numpy as np
os.chdir("/home/trido/thanhdt/WorkingClaude")
sys.path.insert(0, "research/lag_regime_gate")
from lag_common import build_events, simulate_nav, metrics

E, prices = build_events()

def spearman_ic(x, y):
    d = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(d) < 15: return np.nan, np.nan, len(d)
    ic = d["x"].rank().corr(d["y"].rank())
    n = len(d)
    t = ic * np.sqrt((n - 2) / max(1e-9, 1 - ic**2))
    return ic, t, n

print("="*94)
print("  Q1 — LAG-only performance decomposition (2014-2026)")
print("="*94)
nav, trades = simulate_nav(E, prices)
print("Full-period LAG-only:", {k: round(v, 3) for k, v in metrics(nav).items()}, "| trades", len(trades))

# per-year trade stats
trades["year"] = pd.to_datetime(trades["dt"]).dt.year
print("\nPer-YEAR realized-trade stats (exit year):")
print(f"  {'yr':<6}{'N':>5}{'WR':>8}{'avg%':>9}{'med%':>9}")
for y, g in trades.groupby("year"):
    print(f"  {y:<6}{len(g):>5}{(g.ret_pct>0).mean()*100:>7.1f}%{g.ret_pct.mean():>+8.2f}%{g.ret_pct.median():>+8.2f}%")

# per-year event-level stats (all admitted signals, entry year) — decouples from fill/capacity
print("\nPer-YEAR event-level post_ret (entry year, ALL admitted LAG signals):")
print(f"  {'yr':<6}{'N':>5}{'WR':>8}{'avg%':>9}{'IC_sur':>9}{'IC_npr':>9}")
for y, g in E.groupby("year"):
    if len(g) < 10: continue
    ic_s, _, _ = spearman_ic(g["surprise"], g["post_ret"])
    ic_n, _, _ = spearman_ic(g["NP_R"], g["post_ret"])
    print(f"  {y:<6}{len(g):>5}{(g.post_ret>0).mean()*100:>7.1f}%{g.post_ret.mean():>+8.2f}%{ic_s:>+9.3f}{ic_n:>+9.3f}")

# rolling 1y Sharpe of NAV
r = nav.pct_change().dropna()
roll = r.rolling(252)
rsharpe = (roll.mean() / roll.std()) * np.sqrt(252)
rsharpe = rsharpe.dropna()
print("\nRolling-252d Sharpe — half-year snapshots:")
for dt in pd.date_range("2015-06-30", nav.index[-1], freq="2QS"):
    idx = rsharpe.index.searchsorted(dt)
    if idx >= len(rsharpe): continue
    print(f"  {rsharpe.index[idx].date()}  {rsharpe.iloc[idx]:+.2f}")

print("\n" + "="*94)
print("  Q2 — IC of surprise & NP_R vs post_ret, SPLIT BY REGIME (measured at entry)")
print("="*94)

def report_buckets(label, colfn):
    print(f"\n--- {label} ---")
    print(f"  {'bucket':<20}{'N':>6}{'avgPost%':>10}{'WR':>7}{'IC_sur':>9}{'t_sur':>8}{'IC_npr':>9}{'t_npr':>8}")
    buckets = colfn(E)
    for bname, mask in buckets:
        g = E[mask]
        if len(g) < 20:
            print(f"  {bname:<20}{len(g):>6}   (n<20 skip)")
            continue
        ic_s, t_s, _ = spearman_ic(g["surprise"], g["post_ret"])
        ic_n, t_n, _ = spearman_ic(g["NP_R"], g["post_ret"])
        print(f"  {bname:<20}{len(g):>6}{g.post_ret.mean():>+9.2f}%{(g.post_ret>0).mean()*100:>6.0f}%"
              f"{ic_s:>+9.3f}{t_s:>+8.2f}{ic_n:>+9.3f}{t_n:>+8.2f}")

# DT5G 5-state: 0=CRISIS 1=BEAR 2=? actually {0:CRISIS,1:BEAR,3:NEUTRAL,4:BULL,5?}. Inspect codes.
print("\nDT5G state codes present:", sorted(E["dt5g_state"].dropna().unique()))
STATE_NAME = {0: "0-CRISIS", 1: "1-BEAR", 2: "2-NEUTRAL", 3: "3-NEUTRAL", 4: "4-BULL", 5: "5-EXBULL"}
def by_dt5g(E):
    return [(STATE_NAME.get(int(s), f"s{int(s)}"), E["dt5g_state"] == s)
            for s in sorted(E["dt5g_state"].dropna().unique())]
report_buckets("DT5G state at entry", by_dt5g)

# collapse to GOOD (BULL/EXBULL >=4) vs NEUTRAL(3) vs BAD (<=1 CRISIS/BEAR)
def by_dt5g_coarse(E):
    return [("BAD (CRISIS/BEAR)", E["dt5g_state"] <= 1),
            ("NEUTRAL (2/3)", (E["dt5g_state"] >= 2) & (E["dt5g_state"] <= 3)),
            ("GOOD (BULL+)", E["dt5g_state"] >= 4)]
report_buckets("DT5G coarse", by_dt5g_coarse)

def by_dd(E):
    return [("dd<=-20 (deep)", E["vni_dd"] <= -20),
            ("-20<dd<=-10", (E["vni_dd"] > -20) & (E["vni_dd"] <= -10)),
            ("-10<dd<=-5", (E["vni_dd"] > -10) & (E["vni_dd"] <= -5)),
            ("dd>-5 (near high)", E["vni_dd"] > -5)]
report_buckets("VNINDEX drawdown-from-1y-peak", by_dd)

def by_6m(E):
    return [("6m<=-10 (bear)", E["vni_6m"] <= -10),
            ("-10<6m<=0", (E["vni_6m"] > -10) & (E["vni_6m"] <= 0)),
            ("0<6m<=15", (E["vni_6m"] > 0) & (E["vni_6m"] <= 15)),
            ("6m>15 (strong)", E["vni_6m"] > 15)]
report_buckets("VNINDEX 6M return", by_6m)

def by_ma200(E):
    return [("below MA200", E["vni_vs_ma200"] < 0),
            ("above MA200", E["vni_vs_ma200"] >= 0)]
report_buckets("VNINDEX vs MA200", by_ma200)

# magnitude question: within each coarse regime, top-surprise vs bottom-surprise spread
print("\n--- Magnitude: avg post_ret of TOP-tercile surprise minus BOTTOM-tercile, per regime ---")
print(f"  {'regime':<20}{'N':>6}{'topSurAvg%':>12}{'botSurAvg%':>12}{'spread pp':>11}")
for bname, mask in [("BAD(CRISIS/BEAR)", E["dt5g_state"] <= 1),
                    ("NEUTRAL(2/3)", (E["dt5g_state"] >= 2) & (E["dt5g_state"] <= 3)),
                    ("GOOD(BULL+)", E["dt5g_state"] >= 4)]:
    g = E[mask].dropna(subset=["surprise", "post_ret"])
    if len(g) < 30: continue
    q1, q2 = g["surprise"].quantile([1/3, 2/3])
    top = g[g["surprise"] >= q2]["post_ret"].mean()
    bot = g[g["surprise"] <= q1]["post_ret"].mean()
    print(f"  {bname:<20}{len(g):>6}{top:>+11.2f}%{bot:>+11.2f}%{top-bot:>+10.2f}pp")

E.to_pickle("research/lag_regime_gate/lag_events_attributed.pkl")
print("\n[saved lag_events_attributed.pkl]")
