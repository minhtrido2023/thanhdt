# -*- coding: utf-8 -*-
"""
backtest_vol_target.py
======================
Backtest Hybrid: H-system state cap + Volatility Targeting
  w_final = min(sigma_target / sigma_realized_20d, state_cap[state])
So sanh voi Original system va B&H.
"""
import os, sys
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Parameters (khong doi) ────────────────────────────────────────────
W_BASE = {"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
MIN_LB=252; MIN_FACTORS=3; MODE_WIN=15; MIN_STAY=7; EMA_ALPHA=0.40
RAMP_DAYS=3; SNAP_THR=0.03; TC=0.001; DEPOSIT_R=0.06/252; BORROW_R=0.10/252

# ── Vol target sweep ──────────────────────────────────────────────────
VOL_WINDOW   = 20                           # realized vol lookback (sessions)
SIGMA_TARGETS = [0.08, 0.10, 0.12, 0.14, 0.16]   # sweep

# ── State caps (gioi han tren theo trang thai) ────────────────────────
STATE_CAP = {1: 0.05, 2: 0.60, 3: 1.00, 4: 1.15, 5: 1.30}
# CRISIS=5%: ngay ca vol thap (crisis gia), van bao ve
# BEAR=60%: cho phep vol target voi ceiling 60%
# NEUTRAL=100%: vol target tu do, toi da 100%
# BULL=115%, EX-BULL=130%: cho phep dung margin khi vol thap

# Original system (de so sanh)
ALLOC_ORIG = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}

STATE_NAMES = {1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ══════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════
print("Loading data...")
vni = pd.read_csv(os.path.join(WORKDIR,"VNINDEX.csv"), low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Close","D_RSI","D_MACDdiff","D_CMF","VNINDEX_PE"]:
    if col in vni.columns: vni[col]=pd.to_numeric(vni[col],errors="coerce")

b_path = os.path.join(WORKDIR,"breadth_data.csv")
if os.path.exists(b_path):
    b=pd.read_csv(b_path); b["time"]=pd.to_datetime(b["time"])
    b["breadth"]=pd.to_numeric(b["breadth"],errors="coerce")
    vni=vni.merge(b,on="time",how="left")
else:
    vni["breadth"]=np.nan

n=len(vni); close=vni["Close"].values.copy()
cal_days=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY=n/(cal_days/365.25)
print(f"  {n} sessions | {vni['time'].min().date()} -> {vni['time'].max().date()} | SPY={SPY:.1f}")

# ══════════════════════════════════════════════════════════════════════
# COMPUTE H-STATE (copy tu vnindex_5state_system.py)
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
        window=arr[max(0,i-3000):i+1]; valid=window[~np.isnan(window)]
        if len(valid)<10 or np.isnan(arr[i]): continue
        out[i]=np.searchsorted(np.sort(valid),arr[i])/len(valid)
    return out

p3m=rolling_ret(close,63); p1m=rolling_ret(close,21)
ma200=np.full(n,np.nan)
for i in range(199,n): ma200[i]=np.mean(close[i-199:i+1])
ma200_dev=np.where(ma200>0,close/ma200-1,np.nan)
rsi    = vni["D_RSI"].values.copy()     if "D_RSI"      in vni.columns else np.full(n,np.nan)
macd_h = vni["D_MACDdiff"].values.copy() if "D_MACDdiff" in vni.columns else np.full(n,np.nan)
cmf    = vni["D_CMF"].values.copy()     if "D_CMF"      in vni.columns else np.full(n,np.nan)
brdt   = vni["breadth"].values.copy()   if "breadth"    in vni.columns else np.full(n,np.nan)

ranks={
    "P3M":expanding_rank(p3m),"P1M":expanding_rank(p1m),
    "MA200":expanding_rank(ma200_dev),"RSI":expanding_rank(rsi),
    "MACD":expanding_rank(macd_h),"CMF":expanding_rank(cmf),
    "Breadth":expanding_rank(brdt),
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
    if   rs<0.10: return 1
    elif rs<0.30: return 2
    elif rs<0.55: return 3
    elif rs<0.75: return 3
    elif rs<0.90: return 4
    else:         return 5

state_raw=np.array([classify(v) if not np.isnan(v) else 3 for v in r_score])

pe_arr = vni["VNINDEX_PE"].values.copy() if "VNINDEX_PE" in vni.columns else np.full(n,np.nan)
pe_p90=np.full(n,np.nan)
for i in range(252,n):
    w2=pe_arr[max(0,i-3000):i+1]; v2=w2[~np.isnan(w2)]
    if len(v2)>=50: pe_p90[i]=np.percentile(v2,90)
dd=np.zeros(n); pk=close[0]
for i in range(n):
    if close[i]>pk: pk=close[i]; dd[i]=close[i]/pk-1
log_r=np.concatenate([[np.nan],np.diff(np.log(np.where(close>0,close,np.nan)))])
vol20=np.full(n,np.nan)
for i in range(VOL_WINDOW,n):
    vol20[i]=np.nanstd(log_r[i-VOL_WINDOW+1:i+1])*np.sqrt(SPY)
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

ss=rolling_mode(so,MODE_WIN)
ss=min_stay_filter(ss,MIN_STAY)
print(f"  Done. States: {dict(zip(*np.unique(ss,return_counts=True)))}")

# ══════════════════════════════════════════════════════════════════════
# BUILD TARGET WEIGHT ARRAYS
# ══════════════════════════════════════════════════════════════════════

# Original (discrete)
target_orig = np.array([ALLOC_ORIG[s] for s in ss])

# Vol-target arrays per sigma_target
def build_vol_target(sigma_target):
    target=np.zeros(n)
    for i in range(n):
        s=int(ss[i])
        cap=STATE_CAP[s]
        if np.isnan(vol20[i]) or vol20[i]<=0:
            # Chua du du lieu vol: dung state cap lam default
            w_vol=cap
        else:
            w_vol=sigma_target/vol20[i]
        target[i]=min(w_vol, cap)
    return target

# ══════════════════════════════════════════════════════════════════════
# NAV SIMULATION
# ══════════════════════════════════════════════════════════════════════
def run_nav(target_arr):
    pv=np.zeros(n); pv[0]=1e9
    w=target_arr[0]; wa=np.zeros(n); wa[0]=w
    for t in range(1,n):
        tgt=target_arr[t-1]    # T+1 delay
        diff=tgt-w
        wn=tgt if abs(diff)<SNAP_THR else w+diff/RAMP_DAYS
        wn=float(np.clip(wn,0.0,1.30))
        r=close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        cash_r = max(0.0,1.0-wn)*DEPOSIT_R
        marg_c = max(0.0,wn-1.0)*BORROW_R
        trd_c  = abs(wn-w)*TC
        pv[t]=pv[t-1]*(1.0+wn*r+cash_r-marg_c-trd_c)
        wa[t]=wn; w=wn
    return pv, wa

# ══════════════════════════════════════════════════════════════════════
# METRICS
# ══════════════════════════════════════════════════════════════════════
def metrics(pv, wa, start_date=None):
    dates=vni["time"]
    if start_date:
        idx=np.where((dates>=pd.Timestamp(start_date)).values)[0]
        if len(idx)==0: return None
        i0=idx[0]
        pv=pv[i0:].copy(); wa=wa[i0:].copy()
        pv=pv/pv[0]*1e9
        dates2=dates.iloc[i0:]
    else:
        dates2=dates
    cal=(dates2.iloc[-1]-dates2.iloc[0]).days/365.25
    cagr=(pv[-1]/pv[0])**(1/cal)-1
    dr=np.diff(pv)/pv[:-1]
    ann_r=np.mean(dr)*SPY
    ann_s=np.std(dr)*np.sqrt(SPY)
    sharpe=ann_r/ann_s if ann_s>0 else 0
    neg=dr[dr<0]
    sortino_d=np.std(neg)*np.sqrt(SPY) if len(neg)>0 else 0
    sortino=ann_r/sortino_d if sortino_d>0 else 0
    peak2=np.maximum.accumulate(pv); mdd=np.min(pv/peak2-1)
    calmar=cagr/abs(mdd) if mdd<0 else 0
    # Max DD duration (sessions)
    under=(pv<peak2); cur=dd_dur=0
    for x in under:
        if x: cur+=1
        else:
            dd_dur=max(dd_dur,cur); cur=0
    dd_dur=max(dd_dur,cur)
    avg_dep=wa.mean()
    ann_tc=np.abs(np.diff(wa)).mean()*TC*SPY
    return dict(cagr=cagr,sharpe=sharpe,sortino=sortino,mdd=mdd,
                calmar=calmar,dd_dur=dd_dur,avg_dep=avg_dep,ann_tc=ann_tc)

# ══════════════════════════════════════════════════════════════════════
# RUN ALL SYSTEMS
# ══════════════════════════════════════════════════════════════════════
print("Running simulations...")
results={}

# Original
pv_orig, wa_orig = run_nav(target_orig)
results["Orig(0/20/70/100/130)"] = (pv_orig, wa_orig)

# Vol-target sweep
for sig in SIGMA_TARGETS:
    t=build_vol_target(sig)
    pv,wa=run_nav(t)
    results[f"VolTgt σ={sig:.0%}"] = (pv,wa)

# B&H
target_bh=np.ones(n)
pv_bh,wa_bh=run_nav(target_bh)
results["Buy & Hold"] = (pv_bh,wa_bh)

# ══════════════════════════════════════════════════════════════════════
# PRINT RESULTS
# ══════════════════════════════════════════════════════════════════════
def print_table(start_date, title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")
    print(f"{'System':<28} {'CAGR':>7} {'Sharpe':>7} {'Sortino':>8} {'MaxDD':>8} {'Calmar':>7} {'DDdur':>6} {'AvgDep':>8} {'AnnTC':>7}")
    print("-"*90)
    for name,(pv,wa) in results.items():
        m=metrics(pv,wa,start_date)
        if m is None: continue
        print(f"{name:<28} {m['cagr']*100:>6.1f}% {m['sharpe']:>7.2f} {m['sortino']:>8.2f} "
              f"{m['mdd']*100:>7.1f}% {m['calmar']:>7.2f} {m['dd_dur']:>5}s "
              f"{m['avg_dep']*100:>7.1f}% {m['ann_tc']*100:>6.3f}%")

print_table(None,       "FULL PERIOD (2001+)")
print_table("2011-01-01","SINCE 2011")

# ── Annual breakdown (2011+) ──────────────────────────────────────────
print(f"\n{'='*80}")
print("  ANNUAL RETURNS (since 2011)")
print(f"{'='*80}")
keys=list(results.keys())
header="Year  " + "".join(f"{k[:12]:>14}" for k in keys)
print(header); print("-"*len(header))
dates=vni["time"]
for yr in range(2011,2027):
    mask=dates.dt.year==yr; idx=np.where(mask.values)[0]
    if len(idx)<5: continue
    i0,i1=idx[0],idx[-1]
    row=f"{yr}  "
    for name,(pv,wa) in results.items():
        if pv[i0]>0: r=(pv[i1]/pv[i0]-1)*100; row+=f"{r:>+13.1f}%"
        else: row+=f"{'N/A':>14}"
    print(row)

# ── Vol-target dynamics: vol profile ────────────────────────────────
print(f"\n{'='*80}")
print("  VOL-TARGET DYNAMICS: allocation vs realized vol")
print(f"{'='*80}")
# Show allocation for sigma=0.12 at key vol levels
sig=0.12
print(f"\n  sigma_target = {sig:.0%}")
print(f"  {'State':<10} {'Cap':>6} | {'vol=8%':>8} {'vol=12%':>8} {'vol=18%':>8} {'vol=25%':>8} {'vol=35%':>8}")
print("  "+"-"*65)
for s,name in STATE_NAMES.items():
    cap=STATE_CAP[s]
    row=f"  {name:<10} {cap*100:>5.0f}% |"
    for vol in [0.08,0.12,0.18,0.25,0.35]:
        w=min(sig/vol,cap)*100
        row+=f"   {w:>5.0f}%  "
    print(row)

# ── CRISIS episodes comparison ────────────────────────────────────────
print(f"\n{'='*80}")
print("  CRISIS EPISODES: allocation per system")
print(f"{'='*80}")
# Build vol-target 0.12 target array for detail
t12=build_vol_target(0.12)
print(f"{'Date':<12} {'State':>8} {'vol20':>7} {'Orig%':>7} {'VT12%':>7} {'1M_fwd':>8} {'3M_fwd':>8}")
print("-"*62)
for i in range(1,n):
    if ss[i]==1 and ss[i-1]!=1:
        r1m=close[i+20]/close[i]-1 if i+20<n and close[i]>0 else np.nan
        r3m=close[i+60]/close[i]-1 if i+60<n and close[i]>0 else np.nan
        v=vol20[i] if not np.isnan(vol20[i]) else 0
        orig_a=ALLOC_ORIG[1]*100
        vt12_a=t12[i]*100
        r1ms=f"{r1m*100:+.1f}%" if not np.isnan(r1m) else "  N/A"
        r3ms=f"{r3m*100:+.1f}%" if not np.isnan(r3m) else "  N/A"
        print(f"{str(vni['time'].iloc[i].date()):<12} {'CRISIS':>8} {v*100:>6.1f}% {orig_a:>6.0f}% {vt12_a:>6.1f}% {r1ms:>8} {r3ms:>8}")

# ── Sensitivity: CAGR & MaxDD grid (sigma x vol_window) ──────────────
print(f"\n{'='*80}")
print("  SENSITIVITY: sigma_target sweep — Since 2011")
print(f"{'='*80}")
print(f"  {'sigma':>7} {'CAGR':>7} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} {'AvgDep':>8}")
print("  "+"-"*50)
for sig in [0.07,0.08,0.09,0.10,0.11,0.12,0.13,0.14,0.15,0.16,0.18,0.20]:
    t=build_vol_target(sig)
    pv,wa=run_nav(t)
    m=metrics(pv,wa,"2011-01-01")
    print(f"  {sig*100:>6.0f}%  {m['cagr']*100:>6.1f}% {m['sharpe']:>7.2f} {m['mdd']*100:>7.1f}% {m['calmar']:>7.2f} {m['avg_dep']*100:>7.1f}%")

# ── Reference: Original ──
m_orig=metrics(pv_orig,wa_orig,"2011-01-01")
print(f"\n  Original:  CAGR={m_orig['cagr']*100:.1f}%  Sharpe={m_orig['sharpe']:.2f}  MaxDD={m_orig['mdd']*100:.1f}%  Calmar={m_orig['calmar']:.2f}  AvgDep={m_orig['avg_dep']*100:.1f}%")
m_bh=metrics(pv_bh,wa_bh,"2011-01-01")
print(f"  B&H:       CAGR={m_bh['cagr']*100:.1f}%  Sharpe={m_bh['sharpe']:.2f}  MaxDD={m_bh['mdd']*100:.1f}%  Calmar={m_bh['calmar']:.2f}  AvgDep=100.0%")

print("\nDone.")
