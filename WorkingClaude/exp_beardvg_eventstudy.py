# -*- coding: utf-8 -*-
"""Event study of the BearDvg pattern (production formula from dual_v3.py), 2000-now.
Measures: per-fire forward VNINDEX returns T+20/60/120, hit-rate (% the index actually
fell), false-positive rate, vs all-day baseline. Research-only — answers 'is the pattern
worth tuning / does it lead?' before touching it. Factor calc replicated verbatim."""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR)

vni = pd.read_pickle("_cache_vnindex_2000_now.pkl"); vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
close = vni["Close"].values.astype(float); n = len(close)
cmf = vni["D_CMF"].values.astype(float)

# RSI (Wilder 14, 0-1) — verbatim
rsi = np.full(n, np.nan); avg_u = avg_d = np.nan; period = 14
for i in range(1, n):
    diff = close[i]-close[i-1]
    if np.isnan(diff): continue
    u = max(diff,0.0); d = max(-diff,0.0)
    if np.isnan(avg_u):
        if i >= period:
            g=[max(close[j]-close[j-1],0) for j in range(1,period+1)]; l=[max(close[j-1]-close[j],0) for j in range(1,period+1)]
            avg_u=np.mean(g); avg_d=np.mean(l)
            if (avg_u+avg_d)>0: rsi[i]=avg_u/(avg_u+avg_d)
    else:
        avg_u=(avg_u*(period-1)+u)/period; avg_d=(avg_d*(period-1)+d)/period
        if (avg_u+avg_d)>0: rsi[i]=avg_u/(avg_u+avg_d)
# MACD hist — verbatim
ema12=np.full(n,np.nan); ema26=np.full(n,np.nan); signal=np.full(n,np.nan); macd_hist=np.full(n,np.nan)
k12,k26,k9=2/13,2/27,2/10
for i in range(n):
    if np.isnan(close[i]): continue
    if i==0 or np.isnan(ema12[i-1]): ema12[i]=close[i]; ema26[i]=close[i]
    else: ema12[i]=ema12[i-1]*(1-k12)+close[i]*k12; ema26[i]=ema26[i-1]*(1-k26)+close[i]*k26
    ml=ema12[i]-ema26[i]
    if i==0 or np.isnan(signal[i-1]): signal[i]=ml
    else: signal[i]=signal[i-1]*(1-k9)+ml*k9
    if i>=33: macd_hist[i]=ml-signal[i]

def rmax(a,w): return pd.Series(a).rolling(w,min_periods=1).max().values
def rmin(a,w): return pd.Series(a).rolling(w,min_periods=1).min().values
def argc_max(r,c,w):
    o=np.full(len(r),np.nan)
    for i in range(len(r)):
        s=r[max(0,i-w+1):i+1]
        if np.all(np.isnan(s)): continue
        o[i]=c[max(0,i-w+1)+int(np.nanargmax(s))]
    return o
def argm_max(r,m,w):
    o=np.full(len(r),np.nan)
    for i in range(len(r)):
        s=r[max(0,i-w+1):i+1]
        if np.all(np.isnan(s)): continue
        o[i]=m[max(0,i-w+1)+int(np.nanargmax(s))]
    return o
D_RSI=rsi; Mx1W=rmax(D_RSI,5); Mx3M=rmax(D_RSI,60); MnT3=rmin(D_RSI,3)
Mx1W_C=argc_max(D_RSI,close,5); Mx3M_C=argc_max(D_RSI,close,60)
Mx1W_M=argm_max(D_RSI,macd_hist,5); Mx3M_M=argm_max(D_RSI,macd_hist,60)
mask_d=(vni["time"]>="2007-01-01").values
with np.errstate(divide='ignore',invalid='ignore'):
    bear1=((Mx1W/np.where(D_RSI>0,D_RSI,np.nan)>1.044)&(Mx3M>0.74)&(Mx1W<0.72)&(Mx1W>0.61)&
           (Mx1W_C/np.where(Mx3M_C>0,Mx3M_C,np.nan)>1.028)&(Mx3M_M/np.where(Mx1W_M!=0,Mx1W_M,np.nan)>1.11)&
           (macd_hist<0)&(close/np.where(Mx3M_C>0,Mx3M_C,np.nan)>0.96)&(MnT3>0.43)&(cmf<0.13)&mask_d)
    bear2=((Mx1W/np.where(D_RSI>0,D_RSI,np.nan)>1.016)&(Mx3M>0.77)&(Mx1W<0.79)&(Mx1W>0.60)&
           (Mx1W_C/np.where(Mx3M_C>0,Mx3M_C,np.nan)>1.008)&(Mx3M_M/np.where(Mx1W_M!=0,Mx1W_M,np.nan)>1.10)&
           (macd_hist<0)&(close/np.where(Mx3M_C>0,Mx3M_C,np.nan)>0.97)&(MnT3>0.50)&(cmf<0.15)&mask_d)
bear_mask=np.nan_to_num(bear1,nan=0).astype(bool)|np.nan_to_num(bear2,nan=0).astype(bool)

# forward returns + forward max-drawdown (next H sessions)
def fwd_ret(h):
    o=np.full(n,np.nan); o[:n-h]=close[h:]/close[:n-h]-1; return o
def fwd_mdd(h):
    o=np.full(n,np.nan)
    for i in range(n-1):
        seg=close[i:min(i+h+1,n)]
        if len(seg)<2: continue
        o[i]=(seg/np.maximum.accumulate(seg)-1).min()
    return o
f20,f60,f120=fwd_ret(20),fwd_ret(60),fwd_ret(120); mdd60=fwd_mdd(60)

# episode onsets: a fire that is the first bear day after >=20 calm days
onset=np.zeros(n,bool)
for i in range(n):
    if bear_mask[i] and not bear_mask[max(0,i-20):i].any(): onset[i]=True
idx=np.where(onset)[0]
print("="*92); print("BearDvg EVENT STUDY (production pattern), 2000-now"); print("="*92)
print(f"bear_mask fire-days: {int(bear_mask.sum())} | distinct episodes (onset, 20d-gap): {len(idx)}")
print(f"\n{'metric':28s}{'fwd20':>12s}{'fwd60':>12s}{'fwd120':>12s}")
def stat(arr_idx, name):
    a20=f20[arr_idx]; a60=f60[arr_idx]; a120=f120[arr_idx]
    def f(a): a=a[~np.isnan(a)]; return f"{np.mean(a)*100:+.1f}/{np.median(a)*100:+.1f}" if len(a) else "n/a"
    print(f"{name:28s}{f(a20):>12s}{f(a60):>12s}{f(a120):>12s}")
stat(idx, "onset mean/median %")
# baseline all-days
allidx=np.arange(n)
stat(allidx, "ALL-DAYS baseline %")
# hit rate (index fell) at each horizon
print(f"\n{'hit-rate (fwd ret < 0)':28s}", end="")
for fa in (f20,f60,f120):
    a=fa[idx]; a=a[~np.isnan(a)]; print(f"{np.mean(a<0)*100:>11.0f}%", end="")
print()
print(f"{'  baseline P(ret<0)':28s}", end="")
for fa in (f20,f60,f120):
    a=fa[~np.isnan(fa)]; print(f"{np.mean(a<0)*100:>11.0f}%", end="")
print("\n")
# false-positive: fire NOT followed by a real drawdown (fwd60 mdd > -10%)
m=mdd60[idx]; m=m[~np.isnan(m)]
real=np.mean(m<=-0.10); fp=np.mean(m>-0.10)
print(f"Of {len(m)} episodes w/ fwd60 data:")
print(f"  followed by REAL drawdown (fwd60 MDD <= -10%): {real*100:.0f}%")
print(f"  FALSE POSITIVE (fwd60 MDD > -10%, benign):     {fp*100:.0f}%")
print(f"  median fwd60 MDD after fire: {np.median(m)*100:.1f}%  (all-days median: {np.median(mdd60[~np.isnan(mdd60)])*100:.1f}%)")
# list episodes
print(f"\n--- episodes (onset date, fwd20/60/120, fwd60 MDD) ---")
for i in idx:
    print(f"  {vni['time'].iloc[i].date()}  f20 {f20[i]*100:+6.1f}  f60 {f60[i]*100:+6.1f}  f120 {f120[i]*100:+6.1f}  mdd60 {mdd60[i]*100:+6.1f}")
print("DONE.")
