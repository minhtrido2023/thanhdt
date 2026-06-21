# -*- coding: utf-8 -*-
"""
f_system_van_banding_test.py
============================
Giam churn cua vol-target Van B (full: pos*clip(tgt/rv,0,1.5)) bang BANDING.
Co che:
  none      : re-scale moi ngay (baseline van B, ~900 trades)
  deadband d: chi cap nhat applied_scale khi |desired-applied|>=d
  bucket    : lam tron scale ve buoc roi rac [0.25..1.5], doi khi flip bucket
  weekly    : cap nhat scale moi 5 phien
Map F_HAdapted, underlying VN30F1M. So sanh trades + Sharpe/DD/Calmar.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
WD = r"/home/trido/thanhdt/WorkingClaude"

f1=pd.read_csv(WD+"/vn30f1m_raw.csv"); f1["time"]=pd.to_datetime(f1["time"])
f1=f1.sort_values("time").reset_index(drop=True)
f1["lr"]=np.log(f1["close"]/f1["close"].shift(1)); f1["ret"]=f1["close"].pct_change()
N=len(f1); SPY=N/((f1.time.iloc[-1]-f1.time.iloc[0]).days/365.25)
f1["rv"]=f1["lr"].rolling(20).std()*np.sqrt(SPY)
TGT=float(np.nanmedian(f1["rv"].values))
ret=f1["ret"].values; rv=f1["rv"].values

def load_state(fname,col="state"):
    d=pd.read_csv(WD+"/"+fname+".csv"); d["time"]=pd.to_datetime(d["time"])
    mp=dict(zip(d["time"],d[col])); return np.array([int(mp.get(t,0)) for t in f1["time"]])
ST={"DT5G live (49tr)":load_state("vnindex_5state_dt5g_live"),
    "DT 15-25-30 (62tr)":load_state("vnindex_5state_dt_15_25_30")}

M_LIVE={1:-1.00,2:-0.20,3:0.70,4:1.00,5:1.30}; TC=0.0003
BUCKETS=np.array([0.0,0.25,0.5,0.75,1.0,1.25,1.5])

def desired_scale(t):
    if t<1 or np.isnan(rv[t-1]) or rv[t-1]<=0: return 1.0
    return min(1.5,max(0.0,TGT/rv[t-1]))

def sim(st_arr, mode="none", d=0.15):
    pv=np.zeros(N); pv[0]=1e9; pos=0.0; tr=0; applied=1.0; last_wk=-99
    for t in range(1,N):
        s_=int(st_arr[t-1]); base=M_LIVE.get(s_,0.0) if s_!=0 else 0.0
        des=desired_scale(t)
        if mode=="none":      applied=des
        elif mode=="deadband":
            if abs(des-applied)>=d: applied=des
        elif mode=="bucket":  applied=BUCKETS[np.argmin(np.abs(BUCKETS-des))]
        elif mode=="weekly":
            if t-last_wk>=5: applied=des; last_wk=t
        target=base*applied
        diff=target-pos
        if abs(diff)>0.01: tr+=1
        rm=ret[t] if not np.isnan(ret[t]) else 0.0
        pv[t]=pv[t-1]*(1.0+target*rm-abs(diff)*TC); pos=target
    return pv,tr

def metrics(pv,i0):
    a=pv[i0:]; ds=f1["time"].iloc[i0:].reset_index(drop=True)
    v=np.where(a>0)[0]; a0,a1=v[0],v[-1]; yrs=(ds.iloc[a1]-ds.iloc[a0]).days/365.25
    sub=a[a0:a1+1]; cagr=(sub[-1]/sub[0])**(1/yrs)-1
    r=np.diff(sub)/sub[:-1]; sp=len(r)/yrs
    sh=np.mean(r)*sp/(np.std(r)*np.sqrt(sp)) if np.std(r)>0 else 0
    rm=np.maximum.accumulate(sub); dd=np.where(rm>0,sub/rm-1,0); mdd=dd.min()
    return dict(cagr=cagr,sharpe=sh,mdd=mdd,calmar=cagr/abs(mdd) if mdd else 0)

i18=f1[f1.time>="2018-01-01"].index[0]; i21=f1[f1.time>="2021-01-01"].index[0]
VARS=[("no van","none_NOVAN",0),("Van B (no band)","none",0),
      ("Van B + deadband .10","deadband",.10),("Van B + deadband .15","deadband",.15),
      ("Van B + deadband .25","deadband",.25),("Van B + bucket .25","bucket",0),
      ("Van B + weekly","weekly",0)]

print(f"VN30F1M N={N} SPY~{SPY:.0f} median vol={TGT:.1%} | map F_HAdapted")
for sname,st in ST.items():
    print("\n"+"="*92); print(f"  {sname}"); print("="*92)
    for plabel,i0 in [("2018+",i18),("OOS 2021+",i21)]:
        print(f"\n  [{plabel}]")
        print(f"  {'Variant':<24}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}{'Trades':>8}{'tr/yr':>7}")
        print("  "+"-"*78)
        yrs=(f1.time.iloc[-1]-f1.time.iloc[i0]).days/365.25
        for label,mode,d in VARS:
            if mode=="none_NOVAN":
                # no van at all: position = base only
                pv=np.zeros(N); pv[0]=1e9; pos=0.0; tr=0
                for t in range(1,N):
                    s_=int(st[t-1]); base=M_LIVE.get(s_,0.0) if s_!=0 else 0.0
                    diff=base-pos
                    if abs(diff)>0.01: tr+=1
                    rm=ret[t] if not np.isnan(ret[t]) else 0.0
                    pv[t]=pv[t-1]*(1.0+base*rm-abs(diff)*TC); pos=base
            else:
                pv,tr=sim(st,mode,d)
            m=metrics(pv,i0)
            print(f"  {label:<24}{m['cagr']*100:>+7.1f}%{m['sharpe']:>8.2f}{m['mdd']*100:>+8.1f}%"
                  f"{m['calmar']:>8.2f}{tr:>8d}{tr/yrs:>7.0f}")
print("\nDone.")
