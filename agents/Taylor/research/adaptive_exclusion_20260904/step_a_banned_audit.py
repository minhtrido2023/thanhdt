# -*- coding: utf-8 -*-
"""step_a_banned_audit.py — Viec 1/3 scenario (i) vs (ii): does the 16-name BANNED list bind on
custom30V (yieldcombo) selection at all, and what is the pure-selection NAV delta?
Mirrors custom30v_exclude_audit.py (job Taylor_20260630_102153) methodology, full 16-name list.
"""
import os, sys, numpy as np, pandas as pd
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

START, END = "2014-01-01", "2026-06-15"
BANNED16 = "PC1,VVS,KSF,NKG,HSG,HVN,VJC,NVL,GEG,SBA,DMC,IMP,TRA,TOS,VTP,BAF"

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

CACHE = os.path.join(WORKDIR, "mike/agents/Taylor/research/adaptive_exclusion_20260904/cache")
os.makedirs(CACHE, exist_ok=True)
RES, MEM = {}, {}
for tag, exc in [("baseline_nobanned", ""), ("banned16_excluded", BANNED16)]:
    navp = os.path.join(CACHE, f"nav_{tag}.csv"); memp = os.path.join(CACHE, f"mem_{tag}.csv")
    if os.path.exists(navp) and os.path.exists(memp):
        print(f"[load cached] {tag}")
        sv = pd.read_csv(navp, parse_dates=["date"]).set_index("date")["nav"]
        RES[tag] = sv; MEM[tag] = pd.read_csv(memp, parse_dates=["rebal_date"])
        continue
    os.environ["BASKET_SELECT"] = "yieldcombo"
    os.environ["BASKET_EXCLUDE"] = exc
    print(f"[build] {tag} BASKET_EXCLUDE='{exc or '(none)'}'")
    lvl, adv, memdf, bx = cb.build_pit(bq, START, END, quality="none", rebal="q2m5",
                                       gate_rating=3, weight_scheme="namecap")
    RES[tag] = lvl; MEM[tag] = memdf
    s = pd.Series(lvl); s.index = pd.to_datetime(s.index)
    s.sort_index().rename("nav").rename_axis("date").to_csv(navp)
    memdf.to_csv(memp, index=False)
os.environ["BASKET_EXCLUDE"] = ""

exl = BANNED16.split(",")
mb = MEM["baseline_nobanned"]
n_rebal = mb["rebal_date"].nunique()
print(f"\n### Q1 — BANNED-16 names in BASELINE custom30V selection (no exclude applied), {n_rebal} rebals ###")
rows = []
for t in exl:
    g = mb[mb["ticker"] == t]
    nr = g["rebal_date"].nunique()
    first = g["rebal_date"].min() if len(g) else None
    last = g["rebal_date"].max() if len(g) else None
    rows.append(dict(ticker=t, n_rebals=nr, pct_rebals=100*nr/n_rebal,
                      avg_liq_rank=g["liq_rank"].mean() if len(g) else np.nan,
                      avg_rating=g["rating"].mean() if len(g) else np.nan,
                      first_selected=first, last_selected=last))
q1 = pd.DataFrame(rows).sort_values("pct_rebals", ascending=False)
print(q1.to_string(index=False))
q1.to_csv("q1_selection_frequency_16names.csv", index=False)

print(f"\n### Q2 — pure-selection NAV: baseline vs banned16-excluded (walk-forward) ###")
WINS = [("FULL 2014->now", None, None), ("IS 2014-2019", None, pd.Timestamp("2019-12-31")),
        ("OOS 2020->now", pd.Timestamp("2020-01-01"), None)]
metrics_rows = []
for tag in ["baseline_nobanned", "banned16_excluded"]:
    for wt, a, b in WINS:
        x = window(RES[tag], a, b)
        x.update(tag=tag, window=wt)
        metrics_rows.append(x)
mdf = pd.DataFrame(metrics_rows)
print(mdf.to_string(index=False))
mdf.to_csv("q2_nav_metrics.csv", index=False)

print(f"\n### DELTA (banned16 - baseline) ###")
for wt, a, b in WINS:
    xb = window(RES["baseline_nobanned"], a, b); xe = window(RES["banned16_excluded"], a, b)
    print(f"  {wt:<16}dCAGR {xe['CAGR']-xb['CAGR']:+.2f}pp  dSharpe {xe['Sharpe']-xb['Sharpe']:+.2f}  "
          f"dMaxDD {xe['MaxDD']-xb['MaxDD']:+.1f}pp  dCalmar {xe['Calmar']-xb['Calmar']:+.2f}")

print(f"\n### by-year basket return (%) ###")
yb = by_year(RES["baseline_nobanned"]); ye = by_year(RES["banned16_excluded"])
yrs = sorted(set(yb) | set(ye))
byyr = []
for y in yrs:
    a, b = yb.get(y, float('nan')), ye.get(y, float('nan'))
    byyr.append(dict(year=y, baseline=a, banned16=b, delta=b-a))
    print(f"  {y:<6}{a:>8.1f}{b:>8.1f}{(b-a):>+9.1f}")
pd.DataFrame(byyr).to_csv("q3_by_year.csv", index=False)
print("\n[done step_a]")
