#!/usr/bin/env python3
"""power_lifecycle_ic.py — VALIDATE the debt-paydown lifecycle thesis before building the lens.
Hypothesis: PRE-INFLECTION power plants (meaningful debt BUT falling + CFO-covering + cheap) outperform
forward (earnings surge + re-rating as debt retires) vs debt-free-mature (already re-rated) vs distress."""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
fin=pd.read_csv(os.path.join(W,"data","power_fin_panel.csv")); px=pd.read_csv(os.path.join(W,"data","power_price_panel.csv"))
fin["time"]=pd.to_datetime(fin["time"]); px["time"]=pd.to_datetime(px["time"]); px=px.sort_values("time")
def asof(tk,dt):
    s=px[(px.ticker==tk)&(px.time>=dt)]; return s.iloc[0]["Close"] if len(s) else np.nan
rows=[]
for _,r in fin.iterrows():
    tk=r["ticker"]; d0=r["time"]+pd.Timedelta(days=45)   # point-in-time (report lag)
    p0=asof(tk,d0)
    if not np.isfinite(p0): continue
    p1=asof(tk,d0+pd.Timedelta(days=365)); p2=asof(tk,d0+pd.Timedelta(days=730))
    deq=r["deq"]; deq4=r["deq4"]; cfo=r["cfo_ttm"]; pb=r["pb"]
    falling=(pd.notna(deq4) and deq<deq4); cfo_pos=(pd.notna(cfo) and cfo>0)
    # lifecycle stage
    if deq<0.3: stage="4_debtfree_mature"
    elif deq>=0.7 and falling and cfo_pos: stage="1_PRE_INFLECTION"   # the thesis buy
    elif deq>=0.7 and not (falling and cfo_pos): stage="0_early_risky" # debt rising or CFO not covering
    else: stage="3_mid"
    rows.append(dict(ticker=tk,time=r["time"],deq=deq,falling=falling,cfo_pos=cfo_pos,pb=pb,stage=stage,
        f1=(p1/p0-1) if np.isfinite(p1) else np.nan, f2=(p2/p0-1) if np.isfinite(p2) else np.nan))
d=pd.DataFrame(rows)
print(f"power panel: {len(d)} obs, {d.ticker.nunique()} tickers {d.time.dt.year.min()}-{d.time.dt.year.max()}\n")
print("=== forward returns by lifecycle stage ===")
print(f"{'stage':<20}{'n':>5}{'1Y med':>9}{'1Y mean':>9}{'1Y win':>8}{'2Y med':>9}{'2Y mean':>9}{'2Y win':>8}")
for s in sorted(d.stage.unique()):
    g=d[d.stage==s]; f1=g["f1"].dropna(); f2=g["f2"].dropna()
    print(f"{s:<20}{len(g):>5}{f1.median()*100:>8.1f}%{f1.mean()*100:>8.1f}%{(f1>0).mean()*100:>7.0f}%{f2.median()*100:>8.1f}%{f2.mean()*100:>8.1f}%{(f2>0).mean()*100:>7.0f}%")
print()
print("=== PRE-INFLECTION × cheap PB (the full thesis: debt falling + CFO + cheap) ===")
pre=d[d.stage=='1_PRE_INFLECTION']
for lab,sub in [("PB<1.0 (cheap)",pre[pre.pb<1.0]),("PB 1.0-1.5",pre[(pre.pb>=1.0)&(pre.pb<1.5)]),("PB>=1.5",pre[pre.pb>=1.5])]:
    f2=sub["f2"].dropna()
    if len(f2)>=5: print(f"  {lab:<16} n={len(sub):>3}  2Y med {f2.median()*100:+.1f}%  mean {f2.mean()*100:+.1f}%  win {(f2>0).mean()*100:.0f}%")
print()
print("=== distress check: early_risky (debt NOT falling or CFO<=0) should be WORST ===")
er=d[d.stage=='0_early_risky']; f2=er["f2"].dropna()
print(f"  early_risky 2Y med {f2.median()*100:+.1f}% / mean {f2.mean()*100:+.1f}% / win {(f2>0).mean()*100:.0f}%  (vs PRE-INFLECTION above)")
