# -*- coding: utf-8 -*-
"""
f_system_van_gatespeed_test.py
==============================
Hai cau hoi:
 (1) Gate-speed: future giao dich intraday -> co can smooth nang 10-25-25 khong?
     Test thang: raw(no smooth) -> 5_15_15 -> 7_20_20 -> 10_25_25 -> 15_25_30 -> dt5g_live(+macro)
 (2) Vol-target van: scale position theo realized vol VN30F de chan deep-DD do don bay.
     Van-A de-risk-only: pos*min(1, tgt/rv) ; Van-B full: pos*clip(tgt/rv,0,1.5)
Underlying = VN30F1M actual (roll embedded). Map = F_HAdapted (live).
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
WD = r"/home/trido/thanhdt/WorkingClaude"

# ---- VN30F1M returns + realized vol (master index = futures dates) ----
f1 = pd.read_csv(WD+"/data/vn30f1m_raw.csv"); f1["time"]=pd.to_datetime(f1["time"])
f1 = f1.sort_values("time").reset_index(drop=True)
f1["lr"] = np.log(f1["close"]/f1["close"].shift(1))
f1["ret"] = f1["close"].pct_change()
N = len(f1); SPY = N/((f1["time"].iloc[-1]-f1["time"].iloc[0]).days/365.25)
f1["rv"] = f1["lr"].rolling(20).std()*np.sqrt(SPY)        # 20d annualized realized vol
TGT = float(np.nanmedian(f1["rv"].values))                # neutral target = historical median
print(f"VN30F1M: {N} days {f1.time.min().date()}->{f1.time.max().date()} | SPY~{SPY:.0f} | median realized vol={TGT:.1%}")

# ---- state series (align to futures dates) ----
def load_state(fname, col="state"):
    d=pd.read_csv(WD+"/"+fname+".csv"); d["time"]=pd.to_datetime(d["time"])
    return dict(zip(d["time"], d[col]))
STATES = {
 "raw (no smooth, 497tr)"   : load_state("vnindex_5state_dt_5_15_15","state_raw"),
 "DT 5-15-15  (157tr)"      : load_state("vnindex_5state_dt_5_15_15"),
 "DT 7-20-20  (124tr)"      : load_state("vnindex_5state_dt_7_20_20"),
 "DT 10-25-25 (93tr,nomac)" : load_state("vnindex_5state_dt_10_25_25"),
 "DT 15-25-30 (62tr)"       : load_state("vnindex_5state_dt_15_25_30"),
 "DT5G live (49tr,+macro)"  : load_state("vnindex_5state_dt5g_live"),
}
def state_arr(mp): return np.array([int(mp.get(t,0)) for t in f1["time"]])

M_LIVE = {1:-1.00,2:-0.20,3:0.70,4:1.00,5:1.30}
TC=0.0003
ret = f1["ret"].values; rv = f1["rv"].values

def sim(st_arr, van=None, tgt=TGT):
    pv=np.zeros(N); pv[0]=1e9; pos=0.0; tr=0
    for t in range(1,N):
        s_=int(st_arr[t-1])
        base = M_LIVE.get(s_,0.0) if s_!=0 else 0.0
        # vol-target van uses realized vol known at t-1 (causal)
        if van and not np.isnan(rv[t-1]) and rv[t-1]>0:
            sc = tgt/rv[t-1]
            if van=="A": sc=min(1.0, sc)        # de-risk only
            elif van=="B": sc=min(1.5, max(0.0, sc))  # full vol-target
            target = base*sc
        else:
            target = base
        diff=target-pos
        if abs(diff)>0.01: tr+=1
        rm = ret[t] if not np.isnan(ret[t]) else 0.0
        pv[t]=pv[t-1]*(1.0+target*rm-abs(diff)*TC)
        pos=target
    return pv,tr

def metrics(pv,i0):
    a=pv[i0:]; ds=f1["time"].iloc[i0:].reset_index(drop=True)
    v=np.where(a>0)[0]; a0,a1=v[0],v[-1]
    yrs=(ds.iloc[a1]-ds.iloc[a0]).days/365.25
    sub=a[a0:a1+1]; cagr=(sub[-1]/sub[0])**(1/yrs)-1
    r=np.diff(sub)/sub[:-1]; sp=len(r)/yrs
    sh=np.mean(r)*sp/(np.std(r)*np.sqrt(sp)) if np.std(r)>0 else 0
    rm=np.maximum.accumulate(sub); dd=np.where(rm>0,sub/rm-1,0); mdd=dd.min()
    return dict(cagr=cagr,sharpe=sh,mdd=mdd,calmar=cagr/abs(mdd) if mdd else 0)

i18=f1[f1["time"]>="2018-01-01"].index[0]
i21=f1[f1["time"]>="2021-01-01"].index[0]

def block(title, van):
    print("\n"+"="*94); print(f"  {title}"); print("="*94)
    for plabel,i0 in [("2018+",i18),("OOS 2021+",i21)]:
        print(f"\n  [{plabel}]  (van={van or 'NONE'})")
        print(f"  {'State':<28}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}{'Trades':>8}")
        print("  "+"-"*78)
        for name,mp in STATES.items():
            pv,tr=sim(state_arr(mp),van=van)
            m=metrics(pv,i0)
            print(f"  {name:<28}{m['cagr']*100:>+7.1f}%{m['sharpe']:>8.2f}{m['mdd']*100:>+8.1f}%{m['calmar']:>8.2f}{tr:>8d}")

block("Q1 — GATE SPEED, no van (underlying VN30F1M, map F_HAdapted)", None)
block("Q2 — + Vol-target van A (de-risk only: pos*min(1, tgt/rv))", "A")
block("Q2 — + Vol-target van B (full vol-target: pos*clip(tgt/rv,0,1.5))", "B")
print("\nDone.")
