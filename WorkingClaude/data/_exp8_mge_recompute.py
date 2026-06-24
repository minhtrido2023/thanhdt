#!/usr/bin/env python
"""Exp-8 MGE sensitivity: recompute FULL/IS/OOS metrics from audit CSVs.
IS = 2014-01-01..2019-12-31, OOS = 2020-01-01..end. calc_metrics == pt_v23_audit_2014.py."""
import pandas as pd, numpy as np, sys, glob

def calc_metrics(s):
    s = s.dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    r = s.pct_change().dropna()
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    sh252 = r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0
    peak = s.cummax(); dds = s / peak - 1
    maxdd = dds.min()
    calmar = cagr / abs(maxdd) if maxdd < 0 else float('nan')
    return dict(cagr=cagr*100, sharpe=sh252, maxdd=maxdd*100, calmar=calmar, years=yrs)

def fmt(m): return f"{m['cagr']:.2f}% / Sh {m['sharpe']:.2f} / DD {m['maxdd']:.1f}% / Cal {m['calmar']:.2f}"

# args: pairs of mge=csvpath
specs=[a.split("=",1) for a in sys.argv[1:]]
print(f"{'MGE':>5} | {'window':<8} | {'CAGR':>7} | {'Sharpe':>6} | {'MaxDD':>7} | {'Calmar':>6} | selfcheck")
print("-"*78)
for mge,fn in specs:
    df=pd.read_csv(fn,low_memory=False)
    d=df[df.record_type=="DAILY"].copy()
    d["ymd"]=pd.to_datetime(d["ymd"])
    s=pd.Series(d.combined_nav.astype(float).values,index=d.ymd).sort_index()
    m=df[df.record_type=="METRIC"].set_index("key")["value"]
    sc=max(abs(float(m.get(f"{k}",0))) for k in
           ["cash_flow_identity_max_err_vnd_BAL","final_nav_identity_err_vnd_BAL",
            "cash_flow_identity_max_err_vnd_LAG","final_nav_identity_err_vnd_LAG",
            "combination_replay_err_vnd"])
    sc_str=f"{sc:.0f} VND"
    full=calc_metrics(s)
    isw =calc_metrics(s[(s.index>="2014-01-01")&(s.index<="2019-12-31")])
    oos =calc_metrics(s[ s.index>="2020-01-01"])
    for lbl,mm in [("FULL",full),("IS14-19",isw),("OOS20+",oos)]:
        print(f"{mge:>5} | {lbl:<8} | {mm['cagr']:>6.2f}% | {mm['sharpe']:>6.2f} | {mm['maxdd']:>6.1f}% | {mm['calmar']:>6.2f} | {sc_str if lbl=='FULL' else ''}")
    print("-"*78)
