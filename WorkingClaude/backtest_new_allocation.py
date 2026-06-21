# -*- coding: utf-8 -*-
"""
backtest_new_allocation.py
===========================
So sanh 3 he thong allocation tren VNINDEX:
  A) Original  : CRISIS=0%, BEAR=20%, NEUTRAL=70%, BULL=100%, EX-BULL=130%
  B) New        : CRISIS(deep)=0%, CRISIS(border)=30%, BEAR=50%, NEUTRAL=85%, BULL=100%, EX-BULL=120%
  C) Buy & Hold : 100% moi luc
Methodology: giong vnindex_5state_system.py (T+1, ramp 3 ngay, TC=0.1%, deposit=6%/yr, borrow=10%/yr)
"""
import os, sys
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Parameters (khong doi) ────────────────────────────────────────────
W_BASE = {"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
MIN_LB=252; MIN_FACTORS=3; MODE_WIN=15; MIN_STAY=7; EMA_ALPHA=0.40
RAMP_DAYS=3; SNAP_THR=0.03; TC=0.001; DEPOSIT_R=0.06/252; BORROW_R=0.10/252
STATE_NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ── r_score threshold phan chia CRISIS ───────────────────────────────
CRISIS_DEEP_THR = 0.06   # < threshold: deep crisis -> 0%
                          # >= threshold: borderline -> 30%

# ── Allocation tables ─────────────────────────────────────────────────
# Original system
ALLOC_ORIG = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}

# New system (state=1 phan lam 2 muc, xu ly rieng trong backtest)
ALLOC_NEW_DEEP   = 0.00   # CRISIS r_score < 0.06
ALLOC_NEW_BORDER = 0.30   # CRISIS r_score 0.06-0.10
ALLOC_NEW = {2: 0.50, 3: 0.85, 4: 1.00, 5: 1.20}

# ══════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════
print("Loading data...")
vni = pd.read_csv(os.path.join(WORKDIR,"VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Close","D_RSI","D_MACDdiff","D_CMF","VNINDEX_PE"]:
    if col in vni.columns: vni[col]=pd.to_numeric(vni[col],errors="coerce")

breadth_path = os.path.join(WORKDIR,"breadth_data.csv")
if os.path.exists(breadth_path):
    b=pd.read_csv(breadth_path); b["time"]=pd.to_datetime(b["time"])
    b["breadth"]=pd.to_numeric(b["breadth"],errors="coerce")
    vni=vni.merge(b,on="time",how="left")
else:
    vni["breadth"]=np.nan

n=len(vni); close=vni["Close"].values.copy()
cal_days=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY=n/(cal_days/365.25)
print(f"  {n} sessions | {vni['time'].min().date()} -> {vni['time'].max().date()} | SPY={SPY:.1f}/yr")

# ══════════════════════════════════════════════════════════════════════
# COMPUTE STATE (copy logic tu vnindex_5state_system.py)
# ══════════════════════════════════════════════════════════════════════
print("Computing state classification...")

def rolling_ret(arr,w):
    out=np.full(len(arr),np.nan)
    for i in range(w,len(arr)):
        if arr[i-w]>0: out[i]=arr[i]/arr[i-w]-1
    return out

def expanding_rank(arr,min_lb=MIN_LB):
    out=np.full(len(arr),np.nan)
    for i in range(min_lb,len(arr)):
        window=arr[max(0,i-3000):i+1]; valid=window[~np.isnan(window)]
        if len(valid)<10 or np.isnan(arr[i]): continue
        out[i]=np.searchsorted(np.sort(valid),arr[i])/len(valid)
    return out

p3m=rolling_ret(close,63); p1m=rolling_ret(close,21)
ma200=np.full(n,np.nan)
for i in range(199,n): ma200[i]=np.mean(close[i-199:i+1])
ma200_dev=np.where(ma200>0,close/ma200-1,np.nan)
rsi=vni["D_RSI"].values.copy() if "D_RSI" in vni.columns else np.full(n,np.nan)
macd_hist=vni["D_MACDdiff"].values.copy() if "D_MACDdiff" in vni.columns else np.full(n,np.nan)
cmf_raw=vni["D_CMF"].values.copy() if "D_CMF" in vni.columns else np.full(n,np.nan)
breadth_arr=vni["breadth"].values.copy() if "breadth" in vni.columns else np.full(n,np.nan)

ranks={
    "P3M":expanding_rank(p3m),"P1M":expanding_rank(p1m),
    "MA200":expanding_rank(ma200_dev),"RSI":expanding_rank(rsi),
    "MACD":expanding_rank(macd_hist),"CMF":expanding_rank(cmf_raw),
    "Breadth":expanding_rank(breadth_arr),
}

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
    else: return 5

state_raw=np.array([classify(v) if not np.isnan(v) else 3 for v in r_score])

# Overrides
pe_arr=vni["VNINDEX_PE"].values.copy() if "VNINDEX_PE" in vni.columns else np.full(n,np.nan)
pe_p90=np.full(n,np.nan)
for i in range(252,n):
    w2=pe_arr[max(0,i-3000):i+1]; v2=w2[~np.isnan(w2)]
    if len(v2)>=50: pe_p90[i]=np.percentile(v2,90)
dd=np.zeros(n); pk=close[0]
for i in range(n):
    if close[i]>pk: pk=close[i]; dd[i]=close[i]/pk-1
rets=np.concatenate([[np.nan],np.diff(np.log(np.where(close>0,close,np.nan)))])
vol20=np.full(n,np.nan)
for i in range(20,n): vol20[i]=np.nanstd(rets[i-19:i+1])*np.sqrt(252)
vol20_ma=np.full(n,np.nan)
for i in range(60,n): vol20_ma[i]=np.nanmean(vol20[i-59:i+1])

so=state_raw.copy()
for i in range(n):
    s=so[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s>=4: so[i]=min(s,4)
    if dd[i]<-0.25 and s>=3: so[i]=min(s,3)
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

state_smooth=rolling_mode(so,MODE_WIN)
state_smooth=min_stay_filter(state_smooth,MIN_STAY)
print(f"  States computed. CRISIS sessions: {(state_smooth==1).sum()}")

# ══════════════════════════════════════════════════════════════════════
# TARGET WEIGHT ARRAYS
# ══════════════════════════════════════════════════════════════════════
target_orig=np.array([ALLOC_ORIG[s] for s in state_smooth])

# New: CRISIS split by r_score
target_new=np.zeros(n)
for i in range(n):
    s=state_smooth[i]
    if s==1:
        rs=r_score[i-1] if i>0 and not np.isnan(r_score[i-1]) else r_score[i]
        target_new[i]=ALLOC_NEW_DEEP if (np.isnan(rs) or rs<CRISIS_DEEP_THR) else ALLOC_NEW_BORDER
    else:
        target_new[i]=ALLOC_NEW[s]

# ══════════════════════════════════════════════════════════════════════
# NAV SIMULATION
# ══════════════════════════════════════════════════════════════════════
def run_nav(target_w_arr, label):
    pv=np.zeros(n); pv[0]=1e9
    w=target_w_arr[0]
    w_arr=np.zeros(n); w_arr[0]=w
    for t in range(1,n):
        target=target_w_arr[t-1]   # T+1 delay
        diff=target-w
        w_new=target if abs(diff)<SNAP_THR else w+diff/RAMP_DAYS
        w_new=float(np.clip(w_new,0.0,1.30))
        r=close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        cash_r=max(0.0,1.0-w_new)*DEPOSIT_R
        marg_c=max(0.0,w_new-1.0)*BORROW_R
        trd_c=abs(w_new-w)*TC
        pv[t]=pv[t-1]*(1.0+w_new*r+cash_r-marg_c-trd_c)
        w_arr[t]=w_new
        w=w_new
    return pv, w_arr

print("Running NAV simulations...")
pv_orig,w_orig=run_nav(target_orig,"Original")
pv_new,w_new=run_nav(target_new,"New")
pv_bh=np.zeros(n); pv_bh[0]=1e9
for t in range(1,n):
    r=close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
    pv_bh[t]=pv_bh[t-1]*(1.0+r)

# ══════════════════════════════════════════════════════════════════════
# METRICS
# ══════════════════════════════════════════════════════════════════════
def metrics(pv,dates,label,start_date=None):
    if start_date:
        mask=dates>=pd.Timestamp(start_date)
        # find first valid index
        idx=np.where(mask)[0]
        if len(idx)==0: return
        i0=idx[0]
        pv2=pv[i0:].copy(); pv2=pv2/pv2[0]*1e9
        dates2=dates[i0:]
    else:
        pv2=pv; dates2=dates

    n2=len(pv2)
    cal=(dates2.iloc[-1]-dates2.iloc[0]).days/365.25
    cagr=(pv2[-1]/pv2[0])**(1/cal)-1

    # daily returns
    dr=np.diff(pv2)/pv2[:-1]
    ann_ret=np.mean(dr)*SPY
    ann_std=np.std(dr)*np.sqrt(SPY)
    sharpe=ann_ret/ann_std if ann_std>0 else 0

    neg=dr[dr<0]
    sortino_d=np.std(neg)*np.sqrt(SPY) if len(neg)>0 else 0
    sortino=ann_ret/sortino_d if sortino_d>0 else 0

    # MaxDD
    peak2=np.maximum.accumulate(pv2)
    mdd=np.min(pv2/peak2-1)
    calmar=cagr/abs(mdd) if mdd<0 else 0

    # DD duration (calendar days)
    under=(pv2<peak2)
    dd_dur=0
    cur=0
    for x in under:
        if x: cur+=1
        else:
            if cur>dd_dur: dd_dur=cur
            cur=0
    if cur>dd_dur: dd_dur=cur

    return {"label":label,"cagr":cagr,"sharpe":sharpe,"sortino":sortino,
            "mdd":mdd,"calmar":calmar,"dd_dur_s":dd_dur}

dates=vni["time"]

print("\n" + "="*72)
print("BACKTEST RESULTS — VNINDEX NAV SIMULATION")
print("="*72)

for period,start in [("Full (2001+)",None),("Since 2011","2011-01-01")]:
    print(f"\n--- {period} ---")
    print(f"{'System':<22} {'CAGR':>7} {'Sharpe':>7} {'Sortino':>8} {'MaxDD':>8} {'Calmar':>7} {'DDdur':>6}")
    print("-"*70)
    for label,pv in [("Original (0/20/70/100/130)",pv_orig),
                     ("New (0|30/50/85/100/120)",pv_new),
                     ("Buy & Hold",pv_bh)]:
        m=metrics(pv,dates,label,start)
        if m:
            print(f"{m['label']:<22} {m['cagr']*100:>6.1f}% {m['sharpe']:>7.2f} {m['sortino']:>8.2f} {m['mdd']*100:>7.1f}% {m['calmar']:>7.2f} {m['dd_dur_s']:>5}s")

# ── Average deployment ────────────────────────────────────────────────
print()
print("--- Average deployment (2011+) ---")
mask11=(dates>="2011-01-01").values
print(f"  Original : {w_orig[mask11].mean()*100:.1f}%")
print(f"  New      : {w_new[mask11].mean()*100:.1f}%")
print(f"  B&H      : 100.0%")

# ── Annual breakdown ──────────────────────────────────────────────────
print()
print("--- Annual returns (2011+) ---")
print(f"{'Year':<6} {'Orig':>7} {'New':>7} {'BH':>7}")
print("-"*28)
vni2=vni[vni["time"]>="2011-01-01"].copy()
idx_start=vni2.index[0]
for yr in range(2011,2027):
    mask_yr=vni["time"].dt.year==yr
    idx_yr=np.where(mask_yr.values)[0]
    if len(idx_yr)<5: continue
    i0,i1=idx_yr[0],idx_yr[-1]
    def yr_ret(pv):
        if pv[i0]<=0: return float("nan")
        return pv[i1]/pv[i0]-1
    ro=yr_ret(pv_orig); rn=yr_ret(pv_new); rb=yr_ret(pv_bh)
    win_o="*" if ro>rb else " "
    win_n="*" if rn>rb else " "
    print(f"{yr:<6} {ro*100:>+6.1f}%{win_o} {rn*100:>+6.1f}%{win_n} {rb*100:>+6.1f}%")

# ── CRISIS episode detail ─────────────────────────────────────────────
print()
print("--- CRISIS episodes: allocation comparison ---")
print(f"{'Date':<12} {'r_score':>8} {'Orig%':>7} {'New%':>7} {'1M_fwd':>8} {'3M_fwd':>8}")
print("-"*55)
in_crisis=False
for i in range(1,n):
    if state_smooth[i]==1 and state_smooth[i-1]!=1:
        r1m=close[i+20]/close[i]-1 if i+20<n and close[i]>0 else float("nan")
        r3m=close[i+60]/close[i]-1 if i+60<n and close[i]>0 else float("nan")
        rs=r_score[i-1] if not np.isnan(r_score[i-1]) else r_score[i]
        orig_a=ALLOC_ORIG[1]*100
        new_a=ALLOC_NEW_DEEP*100 if (np.isnan(rs) or rs<CRISIS_DEEP_THR) else ALLOC_NEW_BORDER*100
        r1ms=f"{r1m*100:+.1f}%" if not np.isnan(r1m) else " N/A"
        r3ms=f"{r3m*100:+.1f}%" if not np.isnan(r3m) else " N/A"
        flag="DEEP" if new_a==0 else "BORDER"
        print(f"{str(vni['time'].iloc[i].date()):<12} {rs:>8.3f} {orig_a:>6.0f}% {new_a:>6.0f}% {r1ms:>8} {r3ms:>8}  [{flag}]")

print("\nDone.")
