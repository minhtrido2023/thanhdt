# -*- coding: utf-8 -*-
"""
custom30v_exclude_audit.py — does the sector-sweep Permanent Exclude List change custom30V?
custom30V = yieldcombo (rank(1/PE)+rank(1/PCF), top-30 of liquid pool, HARD 8L gate_rating<=3,
namecap0.10, q2m5). Q1: how often do exclude-list names actually appear in the basket (gate may
already drop them)? Q2: filter them out (BASKET_EXCLUDE) -> re-run -> parking-basket NAV delta,
walk-forward IS(2014-19)/OOS(2020+). Faithful: same build_pit machinery, only the gated pool differs.
"""
import os, sys, numpy as np, pandas as pd
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb
START, END = "2014-01-01", "2026-06-15"
EXCLUDE = "HVN,VJC,NVL,KDC,VHC,HPG,HSG"   # sector-sweep Permanent Exclude List (structural value-traps)

def metrics(lvl):
    s = pd.Series(lvl).sort_index(); s.index = pd.to_datetime(s.index)
    r = s.pct_change().dropna()
    return _m(s, r)

def _m(s, r):
    yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    spd = len(r)/yrs
    sharpe = r.mean()/r.std()*np.sqrt(spd) if r.std()>0 else 0
    dd = (s/s.cummax()-1).min()
    return dict(CAGR=cagr*100, Sharpe=sharpe, MaxDD=dd*100, Calmar=(cagr*100)/abs(dd*100) if dd<0 else 0)

def window(lvl, a, b):
    s = pd.Series(lvl).sort_index(); s.index = pd.to_datetime(s.index)
    if a is not None: s = s[s.index >= a]
    if b is not None: s = s[s.index <= b]
    s = s / s.iloc[0]
    return _m(s, s.pct_change().dropna())

def by_year(lvl):
    s = pd.Series(lvl).sort_index(); s.index = pd.to_datetime(s.index)
    return {y: (g.iloc[-1]/g.iloc[0]-1)*100 for y, g in s.groupby(s.index.year) if len(g) > 1}

CACHE = os.path.join(WORKDIR, "data", "c30v_exclude_cache")
os.makedirs(CACHE, exist_ok=True)
RES = {}; MEM = {}
for tag, exc in [("baseline", ""), ("exclude", EXCLUDE)]:
    navp = os.path.join(CACHE, f"nav_{tag}.csv"); memp = os.path.join(CACHE, f"mem_{tag}.csv")
    if os.path.exists(navp) and os.path.exists(memp):
        print(f"\n===== load cached: yieldcombo  BASKET_EXCLUDE='{exc or '(none)'}' =====")
        sv = pd.read_csv(navp, parse_dates=["date"]).set_index("date")["nav"]
        RES[tag] = sv; MEM[tag] = pd.read_csv(memp, parse_dates=["rebal_date"])
        continue
    os.environ["BASKET_SELECT"] = "yieldcombo"
    os.environ["BASKET_EXCLUDE"] = exc
    print(f"\n===== build basket: yieldcombo  BASKET_EXCLUDE='{exc or '(none)'}' =====")
    lvl, adv, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                       gate_rating=3, weight_scheme="namecap")
    RES[tag] = lvl; MEM[tag] = memdf
    s = pd.Series(lvl); s.index = pd.to_datetime(s.index); s.sort_index().rename("nav").rename_axis("date").to_csv(navp)
    memdf.to_csv(memp, index=False)
os.environ["BASKET_EXCLUDE"] = ""   # restore prod default

# ---- Q1: overlap frequency in the BASELINE (un-excluded) yieldcombo membership ----
exl = [x.strip() for x in EXCLUDE.split(",")]
mb = MEM["baseline"]
n_rebal = mb["rebal_date"].nunique()
print(f"\n############ Q1 — exclude-list names in BASELINE custom30V (yieldcombo), {n_rebal} rebals ############")
print(f"{'ticker':<8}{'#rebals':>9}{'% of rebals':>13}{'avg liq_rank':>14}{'avg rating':>12}")
tot_rows = len(mb)
flagged_rows = 0
for t in exl:
    g = mb[mb["ticker"] == t]
    nr = g["rebal_date"].nunique(); flagged_rows += len(g)
    if len(g):
        print(f"{t:<8}{nr:>9}{100*nr/n_rebal:>12.1f}%{g['liq_rank'].mean():>14.1f}{g['rating'].mean():>12.2f}")
    else:
        print(f"{t:<8}{0:>9}{0.0:>12.1f}%{'-':>14}{'-':>12}")
print(f"\nflagged member-rows = {flagged_rows}/{tot_rows} ({100*flagged_rows/tot_rows:.1f}% of all basket slots ever)")

# ---- Q2: parking-basket NAV delta (faithful own-NAV, no DT5G overlay = pure selection effect) ----
print(f"\n############ Q2 — parking-basket NAV: baseline vs exclude (walk-forward) ############")
WINS = [("FULL 2014->now", None, None), ("IS 2014-2019", None, pd.Timestamp("2019-12-31")),
        ("OOS 2020->now", pd.Timestamp("2020-01-01"), None)]
for tag in ["baseline", "exclude"]:
    print(f"\n--- {tag} ---")
    for wt, a, b in WINS:
        x = window(RES[tag], a, b)
        print(f"  {wt:<16}CAGR {x['CAGR']:6.2f}%  Sharpe {x['Sharpe']:.2f}  MaxDD {x['MaxDD']:6.1f}%  Calmar {x['Calmar']:.2f}")
print(f"\n--- DELTA (exclude - baseline) ---")
for wt, a, b in WINS:
    xb = window(RES["baseline"], a, b); xe = window(RES["exclude"], a, b)
    print(f"  {wt:<16}dCAGR {xe['CAGR']-xb['CAGR']:+.2f}pp  dSharpe {xe['Sharpe']-xb['Sharpe']:+.2f}  dMaxDD {xe['MaxDD']-xb['MaxDD']:+.1f}pp  dCalmar {xe['Calmar']-xb['Calmar']:+.2f}")

print(f"\n--- by-year basket return (%) ---")
yb = by_year(RES["baseline"]); ye = by_year(RES["exclude"])
yrs = sorted(set(yb) | set(ye))
print(f"  {'year':<6}{'base':>8}{'excl':>8}{'excl-base':>11}")
for y in yrs:
    a, b = yb.get(y, float('nan')), ye.get(y, float('nan'))
    print(f"  {y:<6}{a:>8.1f}{b:>8.1f}{(b-a):>+11.1f}")
print("\n[done]")
