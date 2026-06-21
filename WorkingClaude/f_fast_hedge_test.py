# -*- coding: utf-8 -*-
"""
f_fast_hedge_test.py
====================
Co-sung-NHANH doc lap DT5G (vol-spike / drawdown / MA-break tren VN30F1M) de bat
phan drawdown ma DT5G bo lo (vd grind 2025-26: VN30F intra-DD -16.7% nhung DT5G van NEU).
Hedge sleeve_ret[t] = -short_sig[t-1] * vn30f_ret[t]   (short khi trigger ON)
Combined V5 = V5_ret + lambda * sleeve_ret  (overlay margin, notional = lambda x NAV)
Bao cao: full-period CAGR/Sharpe/MaxDD + MaxDD theo 3 episode + so cost o bull.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
WD=r"/home/trido/thanhdt/WorkingClaude"

v=pd.read_csv(WD+"/data/5sys_prodspec_201401_202605_dt5g.csv"); v["time"]=pd.to_datetime(v["time"])
f=pd.read_csv(WD+"/data/vn30f1m_raw.csv"); f["time"]=pd.to_datetime(f["time"]); f=f.sort_values("time").reset_index(drop=True)
ds=pd.read_csv(WD+"/data/vnindex_5state_dt5g_live.csv"); ds["time"]=pd.to_datetime(ds["time"])
f=f.merge(ds[["time","state"]],on="time",how="left")
c=f["close"].values; n=len(f)
f["ret"]=f["close"].pct_change()
f["ma20"]=f["close"].rolling(20).mean(); f["ma50"]=f["close"].rolling(50).mean()
f["rmax20"]=f["close"].rolling(20).max()
f["lr"]=np.log(f["close"]/f["close"].shift(1))
SPYf=n/((f.time.iloc[-1]-f.time.iloc[0]).days/365.25)
f["rv10"]=f["lr"].rolling(10).std()*np.sqrt(SPYf)
MEDV=float(np.nanmedian(f["rv10"]))
f["ddfromhi"]=f["close"]/f["rmax20"]-1

# ---- fast short triggers (causal: use values at t-1) ----
def sig_ma20(): return (f["close"]<f["ma20"]).astype(int).values
def sig_ma50(): return (f["close"]<f["ma50"]).astype(int).values
def sig_dd5():  return (f["ddfromhi"]<-0.05).astype(int).values
def sig_dd8():  return (f["ddfromhi"]<-0.08).astype(int).values
def sig_vol():  return (f["rv10"]>1.3*MEDV).astype(int).values
def sig_ma20_vol(): return ((f["close"]<f["ma20"])&(f["rv10"]>1.1*MEDV)).astype(int).values
def sig_ma50_dd5(): return ((f["close"]<f["ma50"])&(f["ddfromhi"]<-0.05)).astype(int).values
# DT5G F_hedge for reference (short only when CRISIS/BEAR)
def sig_dt5g(): return f["state"].isin([1,2]).astype(int).values

TRIGS={"MA20-break":sig_ma20(),"MA50-break":sig_ma50(),"DD>5%":sig_dd5(),"DD>8%":sig_dd8(),
       "Vol-spike":sig_vol(),"MA20&Vol":sig_ma20_vol(),"MA50&DD5":sig_ma50_dd5(),
       "[DT5G C/B ref]":sig_dt5g()}

ret=f["ret"].values
def sleeve(sig):
    out=np.zeros(n)
    for t in range(1,n):
        if sig[t-1]==1 and not np.isnan(ret[t]): out[t]=-ret[t]   # short
    return out

m=v[["time","V5_V4_KellyQ2","V4_V121_ENS_TQ34b"]].merge(f[["time"]],on="time")
sl={k:sleeve(sg) for k,sg in TRIGS.items()}
# align sleeve to merged dates
fmap_idx={t:i for i,t in enumerate(f["time"])}
m["V5r"]=m["V5_V4_KellyQ2"].pct_change()
for k in TRIGS: m[k]=[sl[k][fmap_idx[t]] for t in m["time"]]
m=m.dropna(subset=["V5r"]).reset_index(drop=True)
SPY=len(m)/((m.time.iloc[-1]-m.time.iloc[0]).days/365.25)

def met(r):
    r=np.asarray(r); nav=np.cumprod(1+r); yrs=len(r)/SPY
    cagr=nav[-1]**(1/yrs)-1
    sh=np.mean(r)*SPY/(np.std(r)*np.sqrt(SPY)) if np.std(r)>0 else 0
    mdd=np.min(nav/np.maximum.accumulate(nav)-1)
    return cagr,sh,mdd
def dd_window(r_series,a,b):
    s=m[(m.time>=a)&(m.time<=b)]; r=s.values
    nav=np.cumprod(1+r_series[s.index]); return np.min(nav/np.maximum.accumulate(nav)-1)

EP=[("COVID20","2020-01-15","2020-05-01"),("Bear22","2022-04-01","2022-12-01"),
    ("Grind25","2025-09-04","2026-03-23")]
LAM=0.4  # hedge notional ~ V5 beta 0.42

print(f"V5 + {LAM} x fast-hedge sleeve | aligned {len(m)} days {m.time.min().date()}->{m.time.max().date()}")
base_c,base_s,base_d=met(m["V5r"].values)
print(f"\n  BASELINE V5 (no hedge): CAGR {base_c*100:+.1f}%  Sharpe {base_s:.2f}  MaxDD {base_d*100:+.1f}%")
print(f"\n  {'Trigger':<16}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>9}{'on%':>6}  {'DD_COVID':>9}{'DD_Bear22':>10}{'DD_Grind':>9}")
print("  "+"-"*86)
# baseline episode DDs
bd={lbl:dd_window(m['V5r'].values,a,b) for lbl,a,b in EP}
print(f"  {'(baseline V5)':<16}{'':>8}{'':>8}{'':>9}{'':>6}  {bd['COVID20']*100:>+8.1f}%{bd['Bear22']*100:>+9.1f}%{bd['Grind25']*100:>+8.1f}%")
for k in TRIGS:
    comb=m["V5r"].values+LAM*m[k].values
    cg,sh,dd=met(comb)
    on=m[k].astype(bool).mean()*100  # frac days sleeve active (nonzero ret proxy)
    on=(np.array(TRIGS[k])==1).mean()*100
    e={lbl:dd_window(comb,a,b) for lbl,a,b in EP}
    print(f"  {k:<16}{cg*100:>+7.1f}%{sh:>8.2f}{dd*100:>+8.1f}%{on:>5.0f}%  "
          f"{e['COVID20']*100:>+8.1f}%{e['Bear22']*100:>+9.1f}%{e['Grind25']*100:>+8.1f}%")
print("\nDone.")
