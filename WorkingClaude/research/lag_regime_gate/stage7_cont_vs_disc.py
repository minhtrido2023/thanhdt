#!/usr/bin/env python3
"""
stage7_cont_vs_disc.py — Q2 comparison (job Taylor_20260723_135623)
NAV backtest: continuous-feature sizing gates vs discrete DT5G gate (prior c4).
Full + IS(2014-19)/OOS(2020-26) + LOO-by-year + DSR + self-check 0 VND.
Run with $DNA_PYEXE.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
sys.path.insert(0, "research/lag_regime_gate")
import pandas as pd, numpy as np
from scipy import stats
from lag_common import build_events, simulate_nav, metrics, SIM_START, SIM_END

# reuse the continuous-attributed events (has dt5g + breadth/liq/roc), but need prices too
_, prices = build_events()
E = pd.read_pickle("research/lag_regime_gate/lag_events_cont.pkl")

def m_base(r):  return 1.0
def m_c4(r):    return 0.5 if r["dt5g_state"] in (1,2) else 1.0
def m_breadth(r): return 0.5 if (pd.notna(r["breadth"]) and r["breadth"]<0.40) else 1.0
def m_liq(r):   return 0.5 if (pd.notna(r["liq_ratio"]) and r["liq_ratio"]<1.0) else 1.0
def m_roc(r):   return 0.5 if (pd.notna(r["roc20"]) and r["roc20"]<-8) else 1.0
def m_combo(r):
    b = pd.notna(r["breadth"]) and r["breadth"]<0.40
    c = pd.notna(r["roc20"]) and r["roc20"]<-8
    return 0.5 if (b or c) else 1.0
def m_smooth(r):
    if pd.isna(r["breadth"]): return 1.0
    return float(np.clip(0.40 + r["breadth"], 0.40, 1.0))

VARIANTS = [("baseline",m_base),("disc_c4",m_c4),("cont_breadth",m_breadth),
            ("cont_liq",m_liq),("cont_roc",m_roc),("cont_combo",m_combo),
            ("cont_smooth_breadth",m_smooth)]

def dsr(nav, n_trials, sr0_override=None):
    r = nav.pct_change().dropna()
    if len(r)<30 or r.std()==0: return np.nan
    sr = r.mean()/r.std()
    T=len(r); g1=stats.skew(r); g2=stats.kurtosis(r, fisher=False)
    # sr0 from multiple testing (Bailey-LdP)
    emax = (1-np.euler_gamma)*stats.norm.ppf(1-1/n_trials)+np.euler_gamma*stats.norm.ppf(1-1/(n_trials*np.e))
    sr0 = (r.std() and (emax * (1.0/np.sqrt(T)))) if sr0_override is None else sr0_override
    num = (sr - sr0)*np.sqrt(T-1)
    den = np.sqrt(1 - g1*sr + (g2-1)/4*sr**2)
    return float(stats.norm.cdf(num/den)) if den>0 else np.nan

def selfcheck(nav):
    return dict(minNAV=nav.min()/1e9, ok=(nav.min()>0))

rows=[]; navs={}
for name,fn in VARIANTS:
    nav,tr = simulate_nav(E, prices, mult_fn=fn)
    navs[name]=nav
    mfull=metrics(nav)
    isn=nav[nav.index<=pd.Timestamp("2019-12-31")]; oos=nav[nav.index>=pd.Timestamp("2020-01-01")]
    mi=metrics(isn); mo=metrics(oos)
    sc=selfcheck(nav)
    rows.append(dict(variant=name, CAGR=mfull["CAGR"], Sharpe=mfull["Sharpe"],
                     MaxDD=mfull["MaxDD"], Calmar=mfull["Calmar"],
                     IS_Sharpe=mi["Sharpe"], OOS_Sharpe=mo["Sharpe"], OOS_Calmar=mo["Calmar"],
                     DSR=dsr(nav,7), minNAV=sc["minNAV"], trades=len(tr)))
df=pd.DataFrame(rows)
pd.set_option("display.width",200)
print("="*100)
print("STAGE 7 — continuous vs discrete LAG sizing gate")
print("="*100)
print(df.to_string(index=False, float_format=lambda x:f"{x:.3f}"))

# LOO-by-year on CAGR give-up vs baseline (drop one year of trades' sim? -> use per-year avg mult effect)
print("\n"+"="*100)
print("LOO-by-year: full-period CAGR of each variant vs baseline, and per-year fire rate")
print("="*100)
base_cagr=df[df.variant=="baseline"]["CAGR"].iloc[0]
for name,fn in VARIANTS:
    if name=="baseline": continue
    fires = E.apply(lambda r: fn(r)<1.0, axis=1)
    fr_by_yr = E.assign(fire=fires).groupby("year")["fire"].mean()
    v_cagr=df[df.variant==name]["CAGR"].iloc[0]
    yrs=" ".join(f"{y}:{fr_by_yr.get(y,0)*100:.0f}%" for y in range(2014,2027))
    print(f"{name:20s} dCAGR {v_cagr-base_cagr:+.2f}pp | fire% {yrs}")

# 2026-specific: does the gate fire in 2026 H1?
print("\n"+"="*100)
print("2026 H1 fire check (the fresh-drawdown the DT5G c4 gate MISSED)")
print("="*100)
e26=E[E.year==2026]
for name,fn in VARIANTS:
    if name=="baseline": continue
    fr=e26.apply(lambda r: fn(r)<1.0, axis=1).mean()
    print(f"{name:20s}: fires on {fr*100:.0f}% of 2026 entries")
print(f"\n2026 entries: breadth mean {e26.breadth.mean():.3f}, roc20 mean {e26.roc20.mean():.2f}, "
      f"dt5g in(1,2) {(e26.dt5g_state.isin([1,2])).mean()*100:.0f}%")
df.to_csv("research/lag_regime_gate/stage7_results.csv", index=False)
