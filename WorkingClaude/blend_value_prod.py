# -*- coding: utf-8 -*-
"""blend_value_prod.py — does adding the VALUE book to the production book (BAL+LAG+capit+parking) help?
The decisive test is correlation/diversification vs the PRODUCTION book (not the index). Carve w% of
capital to the value leg, daily-rebalanced blend of returns. Report corr + blended CAGR/Sharpe/DD/Calmar
full + IS/OOS. (Returns-based -> NAV scale irrelevant.)"""
import sys, os, glob
import numpy as np, pandas as pd
os.chdir(r"/home/trido/thanhdt/WorkingClaude")

val = pd.read_csv("data/value_book_nav.csv", index_col=0)
val.index = pd.to_datetime(val.index); val = val.iloc[:,0].astype(float)
prodf = "data/v23_golive_audit_2014_now_etfliqcustompitg_wtnamecap.csv"
df = pd.read_csv(prodf, low_memory=False)
d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce"); d = d.dropna(subset=["ymd"]).sort_values("ymd")
prod = d.groupby("ymd")["combined_nav"].last().astype(float)

idx = val.index.intersection(prod.index)
vr = val.reindex(idx).pct_change(); pr = prod.reindex(idx).pct_change()
both = pd.concat([pr, vr], axis=1).dropna(); both.columns = ["prod","val"]
print(f"common {idx[0].date()} -> {idx[-1].date()}  ({len(both)} days)")
print(f"daily-return corr(prod,value) = {both['prod'].corr(both['val']):+.2f}")
mp = prod.reindex(idx).resample('ME').last().pct_change(); mv = val.reindex(idx).resample('ME').last().pct_change()
mm = pd.concat([mp,mv],axis=1).dropna()
print(f"monthly-return corr(prod,value) = {mm.iloc[:,0].corr(mm.iloc[:,1]):+.2f}\n")

def met(r):
    r = r.dropna()
    if len(r) < 20: return None
    nav = (1+r).cumprod(); yrs = (r.index[-1]-r.index[0]).days/365.25
    cg = nav.iloc[-1]**(1/yrs)-1; dd = (nav/nav.cummax()-1).min()
    return dict(cagr=cg*100, sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else 0, dd=dd*100, cal=cg/abs(dd) if dd<0 else 0)
def win(r,lo,hi): return r[(r.index>=lo)&(r.index<=hi)]
def line(lbl,r):
    f=met(r); i=met(win(r,'2014-01-01','2019-12-31')); o=met(win(r,'2020-01-01','2026-12-31'))
    if not f: print(f"  {lbl:22s} n/a"); return
    print(f"  {lbl:22s} FULL {f['cagr']:5.1f}%/Sh{f['sh']:.2f}/DD{f['dd']:5.1f}/Cal{f['cal']:.2f}   "
          f"IS {i['cagr']:5.1f}%/Cal{i['cal']:.2f}   OOS {o['cagr']:5.1f}%/Cal{o['cal']:.2f}")

print("blends (carve w to value, daily rebal):")
line("prod only (w=0)", both["prod"])
for w in (0.2, 0.3, 0.5):
    line(f"prod{1-w:.0%}+value{w:.0%}", (1-w)*both["prod"] + w*both["val"])
line("value only (w=1)", both["val"])
