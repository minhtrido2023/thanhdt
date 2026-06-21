# -*- coding: utf-8 -*-
"""
backtest_dynamic_crisis.py
==========================
Vol-target voi CRISIS cap dong theo realized vol:
  - vol < threshold (crisis gia): cap = cap_lo  (giu nhieu, khong miss recovery)
  - vol >= threshold (crisis that): cap = cap_hi (bao ve manh)
Sweep: vol_threshold x cap_lo de tim to hop toi uu.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import os
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

W_BASE = {"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
MIN_LB=252; MIN_FACTORS=3; MODE_WIN=15; MIN_STAY=7; EMA_ALPHA=0.40
RAMP_DAYS=3; SNAP_THR=0.03; TC=0.001; DEPOSIT_R=0.06/252; BORROW_R=0.10/252
VOL_WINDOW = 20
SIGMA_TARGET = 0.10          # fixed, dung ket qua tot nhat tu backtest truoc
STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
ALLOC_ORIG  = {1:0.00, 2:0.20, 3:0.70, 4:1.00, 5:1.30}

# State caps cho non-CRISIS states
BASE_CAP = {2: 0.60, 3: 1.00, 4: 1.15, 5: 1.30}

# ══════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════
print("Loading data...")
vni = pd.read_csv(os.path.join(WORKDIR,"VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Close","D_RSI","D_MACDdiff","D_CMF","VNINDEX_PE"]:
    if col in vni.columns: vni[col] = pd.to_numeric(vni[col], errors="coerce")
b_path = os.path.join(WORKDIR,"breadth_data.csv")
if os.path.exists(b_path):
    b = pd.read_csv(b_path); b["time"] = pd.to_datetime(b["time"])
    b["breadth"] = pd.to_numeric(b["breadth"], errors="coerce")
    vni = vni.merge(b, on="time", how="left")
else:
    vni["breadth"] = np.nan

n = len(vni); close = vni["Close"].values.copy()
cal_days = (vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY = n / (cal_days/365.25)
print(f"  {n} sessions | {vni['time'].min().date()} -> {vni['time'].max().date()}")

# ══════════════════════════════════════════════════════════════════════
# COMPUTE H-STATE
# ══════════════════════════════════════════════════════════════════════
print("Computing H-state...")
def rolling_ret(arr,w):
    out=np.full(len(arr),np.nan)
    for i in range(w,len(arr)):
        if arr[i-w]>0: out[i]=arr[i]/arr[i-w]-1
    return out
def expanding_rank(arr):
    out=np.full(len(arr),np.nan)
    for i in range(MIN_LB,len(arr)):
        win=arr[max(0,i-3000):i+1]; valid=win[~np.isnan(win)]
        if len(valid)<10 or np.isnan(arr[i]): continue
        out[i]=np.searchsorted(np.sort(valid),arr[i])/len(valid)
    return out

p3m=rolling_ret(close,63); p1m=rolling_ret(close,21)
ma200=np.full(n,np.nan)
for i in range(199,n): ma200[i]=np.mean(close[i-199:i+1])
ma200_dev=np.where(ma200>0,close/ma200-1,np.nan)
rsi  =vni["D_RSI"].values.copy()     if "D_RSI"      in vni.columns else np.full(n,np.nan)
macd =vni["D_MACDdiff"].values.copy() if "D_MACDdiff" in vni.columns else np.full(n,np.nan)
cmf  =vni["D_CMF"].values.copy()     if "D_CMF"      in vni.columns else np.full(n,np.nan)
brdt =vni["breadth"].values.copy()   if "breadth"    in vni.columns else np.full(n,np.nan)

ranks={"P3M":expanding_rank(p3m),"P1M":expanding_rank(p1m),"MA200":expanding_rank(ma200_dev),
       "RSI":expanding_rank(rsi),"MACD":expanding_rank(macd),"CMF":expanding_rank(cmf),"Breadth":expanding_rank(brdt)}
score=np.full(n,np.nan)
for i in range(n):
    vals=[(w,ranks[k][i]) for k,w in W_BASE.items() if not np.isnan(ranks[k][i])]
    if len(vals)>=MIN_FACTORS:
        tw=sum(x[0] for x in vals); score[i]=sum(x[0]*x[1] for x in vals)/tw
r_score=np.full(n,np.nan); last=None
for i in range(n):
    if np.isnan(score[i]): r_score[i]=last
    else:
        r_score[i]=EMA_ALPHA*score[i]+(1-EMA_ALPHA)*last if last is not None else score[i]
        last=r_score[i]

def classify(rs):
    if rs<0.10: return 1
    elif rs<0.30: return 2
    elif rs<0.55: return 3
    elif rs<0.75: return 3
    elif rs<0.90: return 4
    else:         return 5

state_raw=np.array([classify(v) if not np.isnan(v) else 3 for v in r_score])
pe_arr=vni["VNINDEX_PE"].values.copy() if "VNINDEX_PE" in vni.columns else np.full(n,np.nan)
pe_p90=np.full(n,np.nan)
for i in range(252,n):
    w2=pe_arr[max(0,i-3000):i+1]; v2=w2[~np.isnan(w2)]
    if len(v2)>=50: pe_p90[i]=np.percentile(v2,90)
dd_arr=np.zeros(n); pk=close[0]
for i in range(n):
    if close[i]>pk: pk=close[i]; dd_arr[i]=close[i]/pk-1
log_r=np.concatenate([[np.nan],np.diff(np.log(np.where(close>0,close,np.nan)))])
vol20=np.full(n,np.nan)
for i in range(VOL_WINDOW,n): vol20[i]=np.nanstd(log_r[i-VOL_WINDOW+1:i+1])*np.sqrt(SPY)
vol20_ma=np.full(n,np.nan)
for i in range(60,n): vol20_ma[i]=np.nanmean(vol20[i-59:i+1])

so=state_raw.copy()
for i in range(n):
    s=so[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s>=4: so[i]=min(s,4)
    if dd_arr[i]<-0.25 and s>=3: so[i]=min(s,3)
    if (not np.isnan(vol20[i]) and not np.isnan(vol20_ma[i])
        and vol20_ma[i]>0 and vol20[i]>1.5*vol20_ma[i] and s>=4): so[i]=min(s,4)

def rolling_mode(arr,w):
    out=arr.copy()
    for i in range(w-1,len(arr)):
        window=arr[i-w+1:i+1]; counts=np.bincount(window,minlength=6); out[i]=np.argmax(counts)
    return out
def min_stay_filter(arr,ms):
    out=arr.copy(); i=0
    while i<len(arr):
        j=i+1
        while j<len(arr) and arr[j]==arr[i]: j+=1
        if j-i<ms:
            prev=out[i-1] if i>0 else arr[i]; out[i:j]=prev
        i=j
    return out

ss=rolling_mode(so,MODE_WIN); ss=min_stay_filter(ss,MIN_STAY)
print(f"  Done.")

# ══════════════════════════════════════════════════════════════════════
# NAV SIMULATION
# ══════════════════════════════════════════════════════════════════════
def run_nav(target_arr):
    pv=np.zeros(n); pv[0]=1e9
    w=target_arr[0]; wa=np.zeros(n); wa[0]=w
    for t in range(1,n):
        tgt=target_arr[t-1]; diff=tgt-w
        wn=tgt if abs(diff)<SNAP_THR else w+diff/RAMP_DAYS
        wn=float(np.clip(wn,0.0,1.30))
        r=close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t]=pv[t-1]*(1.0+wn*r+max(0.0,1.0-wn)*DEPOSIT_R-max(0.0,wn-1.0)*BORROW_R-abs(wn-w)*TC)
        wa[t]=wn; w=wn
    return pv, wa

def metrics(pv, wa, start=None):
    dates=vni["time"]
    if start:
        idx=np.where((dates>=pd.Timestamp(start)).values)[0]
        if len(idx)==0: return None
        i0=idx[0]
    else:
        i0=0
    p=pv[i0:].copy()/pv[i0]*1e9; w2=wa[i0:]
    cal=(dates.iloc[-1]-dates.iloc[i0]).days/365.25
    cagr=(p[-1]/p[0])**(1/cal)-1
    dr=np.diff(p)/p[:-1]
    sh=np.mean(dr)*SPY/(np.std(dr)*np.sqrt(SPY)+1e-12)
    neg=dr[dr<0]; so=np.mean(dr)*SPY/(np.std(neg)*np.sqrt(SPY)+1e-12) if len(neg)>0 else 0
    pk2=np.maximum.accumulate(p); mdd=np.min(p/pk2-1)
    calmar=cagr/abs(mdd) if mdd<0 else 0
    under=(p<pk2); cur=dd_dur=0
    for x in under:
        if x: cur+=1
        else: dd_dur=max(dd_dur,cur); cur=0
    dd_dur=max(dd_dur,cur)
    ann_tc=np.abs(np.diff(w2)).mean()*TC*SPY
    return dict(cagr=cagr,sh=sh,so=so,mdd=mdd,calmar=calmar,
                dd_dur=dd_dur,avg_dep=w2.mean(),ann_tc=ann_tc)

# ══════════════════════════════════════════════════════════════════════
# BUILD TARGET: dynamic crisis cap
# ══════════════════════════════════════════════════════════════════════
def build_target(sig, vol_thr, cap_lo, cap_hi=0.05):
    target=np.zeros(n)
    for i in range(n):
        s=int(ss[i])
        v=vol20[i] if not np.isnan(vol20[i]) else 0.20
        if s==1:  # CRISIS
            cap = cap_lo if v < vol_thr else cap_hi
        else:
            cap = BASE_CAP[s]
        w_vol = sig/v if v>0 else cap
        target[i] = min(w_vol, cap)
    return target

# ══════════════════════════════════════════════════════════════════════
# BENCHMARKS
# ══════════════════════════════════════════════════════════════════════
print("Computing benchmarks...")
pv_orig, wa_orig = run_nav(np.array([ALLOC_ORIG[s] for s in ss]))
pv_bh,   wa_bh   = run_nav(np.ones(n))
# Best from previous backtest: sig=10%, flat cap=5%
pv_vt10, wa_vt10 = run_nav(build_target(0.10, 999, 0.05, 0.05))

m_orig      = metrics(pv_orig, wa_orig, "2011-01-01")
m_bh        = metrics(pv_bh,   wa_bh,   "2011-01-01")
m_vt10      = metrics(pv_vt10, wa_vt10, "2011-01-01")
m_orig_full = metrics(pv_orig, wa_orig)
m_bh_full   = metrics(pv_bh,   wa_bh)
m_vt10_full = metrics(pv_vt10, wa_vt10)

# ══════════════════════════════════════════════════════════════════════
# SWEEP: vol_threshold x cap_lo
# ══════════════════════════════════════════════════════════════════════
print("Sweeping dynamic crisis cap...")
VOL_THRESHOLDS = [0.12, 0.15, 0.18, 0.20, 0.25]
CAP_LO_VALUES  = [0.20, 0.30, 0.40, 0.50, 0.60]
SIG = 0.10

sweep_results = []
for vthr in VOL_THRESHOLDS:
    for cap_lo in CAP_LO_VALUES:
        t = build_target(SIG, vthr, cap_lo, cap_hi=0.05)
        pv, wa = run_nav(t)
        m_full = metrics(pv, wa, start=None)
        m_2011 = metrics(pv, wa, start="2011-01-01")
        sweep_results.append(dict(vthr=vthr, cap_lo=cap_lo,
                                  cagr=m_2011["cagr"], sh=m_2011["sh"],
                                  mdd=m_2011["mdd"], calmar=m_2011["calmar"],
                                  avg_dep=m_2011["avg_dep"], ann_tc=m_2011["ann_tc"],
                                  cagr_f=m_full["cagr"], calmar_f=m_full["calmar"],
                                  mdd_f=m_full["mdd"]))

df = pd.DataFrame(sweep_results)

# ── Print sweep table (Calmar heatmap style) ─────────────────────────
print("\n" + "="*80)
print("  SWEEP: vol_threshold x cap_lo — CALMAR (Since 2011)")
print("  sigma_target=10%, cap_hi(vol>=thr)=5%")
print("="*80)
hdr = f"{'vol_thr\\cap_lo':>16}" + "".join(f"{c*100:>8.0f}%" for c in CAP_LO_VALUES)
print(hdr); print("-"*(len(hdr)))
for vthr in VOL_THRESHOLDS:
    row = f"{vthr*100:>14.0f}%  "
    for cap_lo in CAP_LO_VALUES:
        v = df[(df.vthr==vthr)&(df.cap_lo==cap_lo)]["calmar"].values[0]
        flag = " *" if v == df["calmar"].max() else "  "
        row += f"{v:>7.2f}{flag}"
    print(row)

print(f"\n  Original:      Calmar={m_orig['calmar']:.2f}")
print(f"  VolTgt10%(flat): Calmar={m_vt10['calmar']:.2f}")
print(f"  B&H:           Calmar={m_bh['calmar']:.2f}")

print("\n" + "="*80)
print("  SWEEP: vol_threshold x cap_lo — CAGR (Since 2011)")
print("="*80)
print(hdr); print("-"*(len(hdr)))
for vthr in VOL_THRESHOLDS:
    row = f"{vthr*100:>14.0f}%  "
    for cap_lo in CAP_LO_VALUES:
        v = df[(df.vthr==vthr)&(df.cap_lo==cap_lo)]["cagr"].values[0]*100
        row += f"{v:>8.1f}%"
    print(row)

print(f"\n  Original: CAGR={m_orig['cagr']*100:.1f}%  |  B&H: CAGR={m_bh['cagr']*100:.1f}%")

print("\n" + "="*80)
print("  SWEEP: vol_threshold x cap_lo — MaxDD (Since 2011)")
print("="*80)
print(hdr); print("-"*(len(hdr)))
for vthr in VOL_THRESHOLDS:
    row = f"{vthr*100:>14.0f}%  "
    for cap_lo in CAP_LO_VALUES:
        v = df[(df.vthr==vthr)&(df.cap_lo==cap_lo)]["mdd"].values[0]*100
        row += f"{v:>8.1f}%"
    print(row)
print(f"\n  Original: MaxDD={m_orig['mdd']*100:.1f}%  |  B&H: MaxDD={m_bh['mdd']*100:.1f}%")

# ── Best configurations ───────────────────────────────────────────────
print("\n" + "="*80)
print("  TOP 5 by CALMAR (Since 2011)")
print("="*80)
top5 = df.nlargest(5, "calmar")
print(f"{'Config':<28} {'CAGR':>7} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} {'AvgDep':>8} {'AnnTC':>7}")
print("-"*75)
for _,r in top5.iterrows():
    name = f"vthr={r.vthr*100:.0f}% cap_lo={r.cap_lo*100:.0f}%"
    print(f"{name:<28} {r.cagr*100:>6.1f}% {r.sh:>7.2f} {r.mdd*100:>7.1f}% {r.calmar:>7.2f} {r.avg_dep*100:>7.1f}% {r.ann_tc*100:>6.3f}%")

print(f"\n  {'--- Reference ---':<28}")
print(f"  {'Original':<26} {m_orig['cagr']*100:>6.1f}% {m_orig['sh']:>7.2f} {m_orig['mdd']*100:>7.1f}% {m_orig['calmar']:>7.2f} {m_orig['avg_dep']*100:>7.1f}% {m_orig['ann_tc']*100:>6.3f}%")
print(f"  {'VolTgt10%(flat cap5%)':<26} {m_vt10['cagr']*100:>6.1f}% {m_vt10['sh']:>7.2f} {m_vt10['mdd']*100:>7.1f}% {m_vt10['calmar']:>7.2f} {m_vt10['avg_dep']*100:>7.1f}% {m_vt10['ann_tc']*100:>6.3f}%")
print(f"  {'B&H':<26} {m_bh['cagr']*100:>6.1f}% {m_bh['sh']:>7.2f} {m_bh['mdd']*100:>7.1f}% {m_bh['calmar']:>7.2f} {m_bh['avg_dep']*100:>7.1f}% {m_bh['ann_tc']*100:>6.3f}%")

# ── Detail for best config ────────────────────────────────────────────
best = df.nlargest(1,"calmar").iloc[0]
vthr_b, cap_lo_b = best["vthr"], best["cap_lo"]
print(f"\n{'='*80}")
print(f"  DETAIL: best config vthr={vthr_b*100:.0f}%, cap_lo={cap_lo_b*100:.0f}%")
print(f"{'='*80}")

t_best = build_target(SIG, vthr_b, cap_lo_b)
pv_best, wa_best = run_nav(t_best)

# Annual breakdown
print(f"\n  Annual returns vs Original vs B&H (since 2011):")
print(f"  {'Year':<6} {'Best':>8} {'Orig':>8} {'BH':>8}  {'Beat_orig':>10}")
print("  "+"-"*48)
for yr in range(2001,2027):
    mask=vni["time"].dt.year==yr; idx=np.where(mask.values)[0]
    if len(idx)<5: continue
    i0,i1=idx[0],idx[-1]
    def yr_ret(pv,a,b): return (pv[b]/pv[a]-1)*100 if pv[a]>0 else float("nan")
    rb=yr_ret(pv_best,i0,i1); ro=yr_ret(pv_orig,i0,i1); rh=yr_ret(pv_bh,i0,i1)
    diff=rb-ro
    print(f"  {yr:<6} {rb:>+7.1f}% {ro:>+7.1f}% {rh:>+7.1f}%  {diff:>+9.1f}%")

# CRISIS episode detail for best config
print(f"\n  CRISIS episodes (allocation with best config):")
print(f"  {'Date':<12} {'vol20':>7} {'cap_dyn':>9} {'w_final':>9} {'1M':>8} {'3M':>8}  verdict")
print("  "+"-"*72)
for i in range(1,n):
    if ss[i]==1 and ss[i-1]!=1:
        v=vol20[i] if not np.isnan(vol20[i]) else 0
        cap = cap_lo_b if v < vthr_b else 0.05
        wf  = t_best[i]
        r1m=close[i+20]/close[i]-1 if i+20<n and close[i]>0 else np.nan
        r3m=close[i+60]/close[i]-1 if i+60<n and close[i]>0 else np.nan
        verdict = "OK-protect" if (not np.isnan(r1m) and r1m < -0.05) else "false-alarm"
        r1s=f"{r1m*100:+.1f}%" if not np.isnan(r1m) else " N/A"
        r3s=f"{r3m*100:+.1f}%" if not np.isnan(r3m) else " N/A"
        print(f"  {str(vni['time'].iloc[i].date()):<12} {v*100:>6.1f}% {cap*100:>8.0f}% {wf*100:>8.1f}% {r1s:>8} {r3s:>8}  {verdict}")

# ── Full period comparison for top configs ────────────────────────────
print(f"\n{'='*80}")
print("  FULL PERIOD (2001+): top configs vs benchmarks")
print(f"{'='*80}")
print(f"  {'Config':<28} {'CAGR':>7} {'MaxDD':>8} {'Calmar':>7}")
print("  "+"-"*50)
top3 = df.nlargest(3,"calmar_f")
for _,r in top3.iterrows():
    name=f"vthr={r.vthr*100:.0f}% cap_lo={r.cap_lo*100:.0f}%"
    print(f"  {name:<28} {r.cagr_f*100:>6.1f}% {r.mdd_f*100:>7.1f}% {r.calmar_f:>7.2f}")
print(f"  {'Original':<28} {m_orig_full['cagr']*100:>6.1f}% {m_orig_full['mdd']*100:>7.1f}% {m_orig_full['calmar']:>7.2f}")
print(f"  {'VolTgt10%(flat cap5%)':<28} {m_vt10_full['cagr']*100:>6.1f}% {m_vt10_full['mdd']*100:>7.1f}% {m_vt10_full['calmar']:>7.2f}")
print(f"  {'B&H':<28} {m_bh_full['cagr']*100:>6.1f}% {m_bh_full['mdd']*100:>7.1f}% {m_bh_full['calmar']:>7.2f}")

print("\nDone.")
