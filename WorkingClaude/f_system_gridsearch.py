# -*- coding: utf-8 -*-
"""
F_System Grid Search: Tim position map toi uu.
Grid: CRISIS, BEAR, NEUTRAL, BULL, EX-BULL positions + smoothing variant.
Metric toi uu: Calmar (CAGR/MaxDD) tu 2011, kiem tra OOS tu 2021.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
from itertools import product

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Full pipeline (copy tu f_system_backtest.py) ─────────────────────────────
vni = pd.read_csv(WORKDIR + "/data/VNINDEX.csv", low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close",
            "D_RSI_Max3M_Close","D_RSI_Max3M_MACD","D_RSI_Max1W_MACD",
            "D_RSI_Min1W_Close","D_RSI_MinT3","D_MACDdiff","D_CMF","C_L1M","C_L1W","VN30"]:
    if col in vni.columns: vni[col] = pd.to_numeric(vni[col], errors="coerce")
if "breadth" not in vni.columns: vni["breadth"] = np.nan

# Underlying: VN30 tu 2012, VNINDEX truoc
vn30_raw  = vni["VN30"].values if "VN30" in vni.columns else np.full(len(vni), np.nan)
vnidx_raw = vni["Close"].values.copy()
vn30_start = np.where(~np.isnan(vn30_raw))[0]
underlying = vnidx_raw.copy()
if len(vn30_start):
    s = vn30_start[0]; scale = vnidx_raw[s] / vn30_raw[s]
    for i in range(s, len(vni)):
        if not np.isnan(vn30_raw[i]): underlying[i] = vn30_raw[i] * scale

close=vni["Close"].values.copy(); high=vni["High"].values.copy()
low=vni["Low"].values.copy(); vol=vni["Volume"].values.copy(); n=len(close)
cal_days=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY=n/(cal_days/365.25)

def _ema(arr,k):
    out=np.full(len(arr),np.nan)
    for i in range(len(arr)):
        out[i]=arr[i] if(i==0 or np.isnan(out[i-1])) else out[i-1]*(1-k)+arr[i]*k
    return out
def _rank(arr,min_lb=252):
    out=np.full(len(arr),np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        v=arr[:t+1]; v=v[~np.isnan(v)]
        if len(v)>=min_lb: out[t]=np.sum(v<=arr[t])/len(v)
    return out

p3m=np.full(n,np.nan)
for i in range(60,n):
    if close[i-60]>0: p3m[i]=close[i]/close[i-60]-1
p1m=np.full(n,np.nan)
for i in range(20,n):
    if close[i-20]>0: p1m[i]=close[i]/close[i-20]-1
ma200=pd.Series(close).rolling(200,min_periods=200).mean().values
ma200_dev=np.where((ma200>0)&~np.isnan(ma200),close/ma200-1,np.nan)
rsi=np.full(n,np.nan); au=ad=np.nan
for i in range(1,n):
    d=close[i]-close[i-1]; u=max(d,0); dn=max(-d,0)
    if np.isnan(au):
        if i>=14:
            au=np.mean([max(close[j]-close[j-1],0) for j in range(1,15)])
            ad=np.mean([max(close[j-1]-close[j],0) for j in range(1,15)])
            if au+ad>0: rsi[i]=au/(au+ad)
    else:
        au=(au*13+u)/14; ad=(ad*13+dn)/14
        if au+ad>0: rsi[i]=au/(au+ad)
e12=_ema(close,2/13); e26=_ema(close,2/27)
macd_l=e12-e26; sig9=_ema(macd_l,2/10)
macd_hist=np.where(np.arange(n)>=33,macd_l-sig9,np.nan)
hl=high-low; mfm=np.where(hl>0,((close-low)-(high-close))/hl,0.0)
cmf=np.full(n,np.nan)
for i in range(14,n):
    vs=np.sum(vol[i-14:i])
    if vs>0: cmf[i]=np.sum(mfm[i-14:i]*vol[i-14:i])/vs
br_arr=vni["breadth"].values
W={"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
raw={"P3M":p3m,"P1M":p1m,"MA200":ma200_dev,"RSI":rsi,"MACD":macd_hist,"CMF":cmf,"Breadth":br_arr}
ranks={k:_rank(v) for k,v in raw.items()}
score=np.full(n,np.nan)
for t in range(n):
    av={k:ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(av)>=3:
        ws=sum(W[k] for k in av); score[t]=sum(av[k]*W[k] for k in av)/ws
r_score=_rank(score)
r_ema_arr=np.full(n,np.nan)
for t in range(n):
    v=r_score[t]; p=r_ema_arr[t-1] if t>0 else np.nan
    r_ema_arr[t]=v if np.isnan(p) else (p if np.isnan(v) else 0.40*v+0.60*p)
pe_arr=vni["VNINDEX_PE"].values.copy()
pe_p90=np.full(n,np.nan)
for t in range(n):
    h=pe_arr[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: pe_p90[t]=np.nanpercentile(h,90)
rm_c=np.maximum.accumulate(np.where(np.isnan(close),0,close))
dd_raw=np.where(rm_c>0,close/rm_c-1,0.0)
dr=np.full(n,np.nan)
for i in range(1,n):
    if close[i-1]>0: dr[i]=close[i]/close[i-1]-1
v20_a=np.full(n,np.nan)
for i in range(20,n):
    w2=dr[i-20:i]; w2=w2[~np.isnan(w2)]
    if len(w2)>=15: v20_a[i]=np.std(w2)*np.sqrt(SPY)
avg_vol_a=np.full(n,np.nan)
for t in range(n):
    h=v20_a[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: avg_vol_a[t]=np.mean(h)
def classify(rs):
    if np.isnan(rs): return 3
    if rs<0.10: return 1
    elif rs<0.20: return 2
    elif rs<0.70: return 3
    elif rs<0.90: return 4
    else: return 5
st=np.array([classify(r) for r in r_ema_arr])
for i in range(n):
    s=st[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s==5: s=4
    if dd_raw[i]<-0.25 and s>=4: s=3
    if not np.isnan(avg_vol_a[i]) and not np.isnan(v20_a[i]) and v20_a[i]>1.5*avg_vol_a[i] and s==5: s=4
    st[i]=s
def _s(c): return vni[c] if c in vni.columns else pd.Series(np.nan,index=vni.index)
_mask=vni["time"]>="2011-01-01"
_DR=_s("D_RSI");_DRT=_s("D_RSI_T1W");_DM1W=_s("D_RSI_Max1W");_DM3M=_s("D_RSI_Max3M")
_DN1W=_s("D_RSI_Min1W");_DN3M=_s("D_RSI_Min3M");_DM1WC=_s("D_RSI_Max1W_Close")
_DM3MC=_s("D_RSI_Max3M_Close");_DM3MM=_s("D_RSI_Max3M_MACD");_DM1WM=_s("D_RSI_Max1W_MACD")
_DN1WC=_s("D_RSI_Min1W_Close");_DMT3=_s("D_RSI_MinT3");_DMACD=_s("D_MACDdiff")
_DCMF=_s("D_CMF");_CL1M=_s("C_L1M");_CL1W=_s("C_L1W")
bear_mask=(
 ((_DM1W/_DR>1.044)&(_DM3M>0.74)&(_DM1W<0.72)&(_DM1W>0.61)&
  (_DM1WC/_DM3MC>1.028)&(_DM3MM/_DM1WM>1.11)&(_DMACD<0)&
  (vni["Close"]/_DM3MC>0.96)&(_DMT3>0.43)&(_DCMF<0.13)&_mask)
 |((_DM1W/_DR>1.016)&(_DM3M>0.77)&(_DM1W<0.79)&(_DM1W>0.60)&
  (_DM1WC/_DM3MC>1.008)&(_DM3MM/_DM1WM>1.10)&(_DMACD<0)&
  (vni["Close"]/_DM3MC>0.97)&(_DMT3>0.50)&(_DCMF<0.15)&_mask)
).values.astype(bool)
bull_mask=(
 ((_DN1W/_DN3M>0.90)&(_DN1W<0.60)&(_DN3M<0.40)&(_DN1WC/_DM3MC<1.15)&
  (_DMACD>0)&(_DMT3<0.50)&(_DM1W<0.48)&(_DR/_DRT>1.12)&(_DCMF>0)&
  (_CL1M<1.21)&(_CL1W<1.05)&_mask)
 |((_DN1W/_DN3M>0.92)&(_DN1W<0.52)&(_DN3M<0.38)&(_DN1WC/_DM3MC<1.10)&
  (_DMACD>0)&(_DMT3<0.56)&(_DM1W<0.64)&(_DR/_DRT>1.10)&(_DCMF>0)&
  (_CL1M<1.20)&(_CL1W<1.025)&_mask)
).values.astype(bool)
pe_rank=np.full(n,np.nan)
for t in range(n):
    if np.isnan(pe_arr[t]): continue
    h=pe_arr[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: pe_rank[t]=np.sum(h<=pe_arr[t])/len(h)
p3m_rank=ranks["P3M"]
streak=np.zeros(n,dtype=bool); _k=0
for i in range(n):
    if not np.isnan(r_ema_arr[i]) and r_ema_arr[i]>0.65: _k+=1
    else: _k=0
    if _k>=10: streak[i]=True
gate_active=False; gate_start=-1; st_dvg=st.copy()
for i in range(n):
    if bear_mask[i]: gate_active=True; gate_start=i
    if gate_active:
        if st_dvg[i]>1: st_dvg[i]=1
        if i-gate_start>=60:
            p3_ok=(not np.isnan(p3m_rank[i])) and p3m_rank[i]>0.45
            pe_ok=(not np.isnan(pe_rank[i])) and pe_rank[i]<0.80
            if bull_mask[i] or (p3_ok and pe_ok) or bool(streak[i]): gate_active=False

def rolling_mode(states,w=15):
    out=states.copy()
    for t in range(w-1,len(states)):
        ww=states[t-w+1:t+1]; vs,cs=np.unique(ww,return_counts=True)
        cands=vs[cs==cs.max()]
        for v in reversed(ww):
            if v in cands: out[t]=v; break
    return out
def min_stay_filter(states,m=7):
    out=states.copy(); changed=True
    while changed:
        changed=False; i=0
        while i<len(out):
            j=i+1
            while j<len(out) and out[j]==out[i]: j+=1
            if j-i<m:
                fill=out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j]=fill; changed=True
            i=j
    return out

# Pre-build smoothed state arrays (2 variants)
st_H = min_stay_filter(rolling_mode(st_dvg, 15), 7)  # H-System canonical
st_F = min_stay_filter(rolling_mode(st_dvg,  5), 3)  # F-System lighter

SMOOTH_VARIANTS = {"H": st_H, "F": st_F}

# ── Simulate (ultra-fast, pure numpy) ────────────────────────────────────────
TC_F   = 0.0003   # 0.03% per unit |Δpos|
ROLL_C = 0.012 / SPY  # 1.2%/yr on |pos|, per session

def simulate_fast(pos_map_arr, st_arr):
    """
    pos_map_arr: array of length 6, index = state (1-5), pos_map_arr[s] = position
    st_arr: smoothed state array length n
    Returns: (pv array, n_trades)
    """
    pv  = np.empty(n); pv[0]  = 1e9
    pos = pos_map_arr[3]
    trades = 0
    for t in range(1, n):
        target = pos_map_arr[st_arr[t-1]]
        diff   = target - pos
        pos_new= target  # T+0 snap
        if abs(diff) > 0.01: trades += 1
        rm = (underlying[t]/underlying[t-1]-1) if underlying[t-1]>0 else 0.0
        pv[t] = pv[t-1] * (1.0 + pos_new*rm
                            - abs(diff)*TC_F
                            - abs(pos_new)*ROLL_C)
        pos = pos_new
    return pv, trades

def metrics_fast(pv, i0, i1=None):
    sl = pv[i0:] if i1 is None else pv[i0:i1]
    ds = vni["time"].iloc[i0:] if i1 is None else vni["time"].iloc[i0:i1]
    a  = sl.astype(float); v = np.where(a>0)[0]
    if len(v)<10: return None
    i0_,i1_ = v[0],v[-1]; v0,v1=a[i0_],a[i1_]
    yrs = (ds.reset_index(drop=True).iloc[i1_]-ds.reset_index(drop=True).iloc[i0_]).days/365.25
    if yrs<=0: return None
    cagr = (v1/v0)**(1/yrs)-1
    sub  = a[i0_:i1_+1]; rets=np.diff(sub)/sub[:-1]; spy_s=len(rets)/yrs
    mr=np.mean(rets); sr=np.std(rets)
    sharpe = mr*spy_s/(sr*np.sqrt(spy_s)) if sr>0 else 0.0
    rm2  = np.maximum.accumulate(sub)
    dd2  = np.where(rm2>0, sub/rm2-1, 0.0)
    mdd  = dd2.min()
    calmar = cagr/abs(mdd) if mdd!=0 else 0.0
    return {"cagr":cagr, "sharpe":sharpe, "mdd":mdd, "calmar":calmar}

idx11 = int(vni[vni["time"]>="2011-01-01"].index[0])
idx21 = int(vni[vni["time"]>="2021-01-01"].index[0])

# B&H reference
pv_bh = np.empty(n); pv_bh[0]=1e9
for t in range(1,n):
    pv_bh[t]=pv_bh[t-1]*(underlying[t]/underlying[t-1] if underlying[t-1]>0 else 1.0)
m_bh_11  = metrics_fast(pv_bh, idx11)
m_bh_oos = metrics_fast(pv_bh, idx21)

# ── Grid definition ────────────────────────────────────────────────────────────
CRISIS_GRID  = [-0.30, -0.50, -0.75, -1.00]
BEAR_GRID    = [-0.10, -0.20, -0.30, -0.50]
NEUTRAL_GRID = [ 0.50]
BULL_GRID    = [ 0.80,  1.00]
EXBULL_GRID  = [ 1.20,  1.30,  1.50]
SMOOTH_GRID  = ["F"]

total = (len(CRISIS_GRID)*len(BEAR_GRID)*len(NEUTRAL_GRID)*
         len(BULL_GRID)*len(EXBULL_GRID)*len(SMOOTH_GRID))
print(f"Grid search: {total} combinations")
print(f"Optimizing: Calmar IS (2011-2020), checking OOS (2021+)")
print()

# ── Run grid search ──────────────────────────────────────────────────────────
IS_END = idx21  # 2011-2020 = in-sample
results = []

done = 0
for cr, be, ne, bu, ex, sm in product(
        CRISIS_GRID, BEAR_GRID, NEUTRAL_GRID,
        BULL_GRID, EXBULL_GRID, SMOOTH_GRID):

    # pos_map_arr: index 0 unused, 1=CRISIS,2=BEAR,3=NEUTRAL,4=BULL,5=EXBULL
    pm = np.array([0.0, cr, be, ne, bu, ex])
    st_arr = SMOOTH_VARIANTS[sm]
    pv, n_trades = simulate_fast(pm, st_arr)

    m_is  = metrics_fast(pv, idx11, IS_END)   # IS: 2011-2020
    m_full= metrics_fast(pv, idx11)            # Full: 2011+
    m_oos = metrics_fast(pv, idx21)            # OOS: 2021+

    if m_is is None or m_full is None or m_oos is None:
        done += 1; continue

    results.append({
        "cr":cr, "be":be, "ne":ne, "bu":bu, "ex":ex, "sm":sm,
        "is_cagr":   m_is["cagr"],
        "is_calmar": m_is["calmar"],
        "is_mdd":    m_is["mdd"],
        "is_sharpe": m_is["sharpe"],
        "full_cagr":  m_full["cagr"],
        "full_calmar":m_full["calmar"],
        "full_mdd":   m_full["mdd"],
        "full_sharpe":m_full["sharpe"],
        "oos_cagr":  m_oos["cagr"],
        "oos_calmar":m_oos["calmar"],
        "oos_mdd":   m_oos["mdd"],
        "oos_sharpe":m_oos["sharpe"],
        "trades":    n_trades,
    })
    done += 1

print(f"Completed {done} runs ({len(results)} valid)")
df = pd.DataFrame(results)

# ── Analysis ──────────────────────────────────────────────────────────────────
# Sort by IS Calmar (2011-2020)
df_s = df.sort_values("is_calmar", ascending=False).reset_index(drop=True)

print()
print("=" * 110)
print("  TOP 20 by IS Calmar (2011–2020) — sorted")
print("=" * 110)
print(f"  {'#':>3}  {'Pos map (C/Be/Ne/Bu/Ex)':>28}  {'Sm':>3}  "
      f"{'IS CAGR':>8}  {'IS Calmar':>9}  {'IS MaxDD':>8}  "
      f"{'Full CAGR':>9}  {'OOS CAGR':>9}  {'OOS Calmar':>10}  {'Trades':>7}")
print(f"  {'-'*3}  {'-'*28}  {'-'*3}  {'-'*8}  {'-'*9}  {'-'*8}  {'-'*9}  {'-'*9}  {'-'*10}  {'-'*7}")
for i, row in df_s.head(20).iterrows():
    pm_str = f"{float(row["cr"]):+.2f}/{float(row["be"]):+.2f}/{float(row["ne"]):+.2f}/{float(row["bu"]):+.2f}/{float(row["ex"]):+.2f}"
    print(f"  {i+1:>3}  {pm_str:>28}  {str(row["sm"]):>3}  "
          f"{float(row["is_cagr"])*100:>+7.1f}%  {float(row["is_calmar"]):>9.2f}  {float(row["is_mdd"])*100:>+7.1f}%  "
          f"{float(row["full_cagr"])*100:>+8.1f}%  {float(row["oos_cagr"])*100:>+8.1f}%  {float(row["oos_calmar"]):>10.2f}  {int(row["trades"]):>7}")

# Reference: B&H and H_System
print()
print(f"  {'REF':<3}  {'B&H':>28}  {'—':>3}  "
      f"{'':>8}  {m_bh_11['calmar']:>9.2f}  {m_bh_11['mdd']*100:>+7.1f}%  "
      f"{'':>9}  {m_bh_oos['cagr']*100:>+8.1f}%  {m_bh_oos['calmar']:>10.2f}")

# ── NEUTRAL sweep: show impact of NEUTRAL position ───────────────────────────
print()
print("=" * 80)
print("  NEUTRAL sweep: IS Calmar by NEUTRAL position (median of all other combos)")
print("=" * 80)
for ne in NEUTRAL_GRID:
    sub = df[df["ne"] == ne]
    print(f"  NEUTRAL={ne:+.2f}:  "
          f"IS Calmar {sub.is_calmar.median():.3f} (max {sub.is_calmar.max():.3f})  |  "
          f"IS CAGR {sub.is_cagr.median()*100:+.1f}%  |  "
          f"IS MaxDD {sub.is_mdd.median()*100:+.1f}%  |  "
          f"OOS Calmar {sub.oos_calmar.median():.3f}")

print()
print("=" * 80)
print("  CRISIS sweep: IS Calmar by CRISIS position")
print("=" * 80)
for cr in CRISIS_GRID:
    sub = df[df["cr"] == cr]
    print(f"  CRISIS={cr:+.2f}:  "
          f"IS Calmar {sub.is_calmar.median():.3f} (max {sub.is_calmar.max():.3f})  |  "
          f"IS CAGR {sub.is_cagr.median()*100:+.1f}%  |  "
          f"IS MaxDD {sub.is_mdd.median()*100:+.1f}%  |  "
          f"OOS Calmar {sub.oos_calmar.median():.3f}")

print()
print("=" * 80)
print("  BEAR sweep: IS Calmar by BEAR position")
print("=" * 80)
for be in BEAR_GRID:
    sub = df[df["be"] == be]
    print(f"  BEAR={be:+.2f}:    "
          f"IS Calmar {sub.is_calmar.median():.3f} (max {sub.is_calmar.max():.3f})  |  "
          f"IS CAGR {sub.is_cagr.median()*100:+.1f}%  |  "
          f"IS MaxDD {sub.is_mdd.median()*100:+.1f}%  |  "
          f"OOS Calmar {sub.oos_calmar.median():.3f}")

print()
print("=" * 80)
print("  SMOOTHING: IS vs OOS")
print("=" * 80)
for sm in SMOOTH_GRID:
    sub = df[df["sm"] == sm]
    lbl = "H-canonical (rm=15,ms=7)" if sm=="H" else "F-lighter   (rm= 5,ms=3)"
    print(f"  {sm} [{lbl}]:  "
          f"IS Calmar {sub.is_calmar.median():.3f}  |  OOS Calmar {sub.oos_calmar.median():.3f}  |  "
          f"Trades (median) {sub.trades.median():.0f}")

# ── Best combo: full annual breakdown ─────────────────────────────────────────
best = df_s.iloc[0]
pm_best = np.array([0.0, best["cr"], best["be"], best["ne"], best["bu"], best["ex"]])
st_best = SMOOTH_VARIANTS[best["sm"]]
pv_best, _ = simulate_fast(pm_best, st_best)

# Also run H_System for comparison
# H_System HT+Rec
H_WEIGHT = {1:0.00, 2:0.20, 3:0.70, 4:1.00, 5:1.30}
rec_map = {}
i = 0
while i < n-1:
    if st_H[i] == 1:
        start = i
        while i < n-1 and st_H[i] == 1: i += 1
        end = i
        if end-start>=2 and end<n:
            for t in range(end, min(end+20,n)):
                if st_H[t]!=1: rec_map[t]=1.30
    else: i += 1

pv_H = np.empty(n); pv_H[0]=1e9; w=0.70; DR=0.001/SPY; BR=0.10/SPY; TC=0.001
for t in range(1,n):
    base=H_WEIGHT[st_H[t-1]]
    target=max(base, rec_map[t-1]) if (t-1) in rec_map else base
    diff=target-w
    w_new=target if abs(diff)<0.03 else w+diff/3
    w_new=float(np.clip(w_new,0.0,1.50))
    rm=underlying[t]/underlying[t-1]-1 if underlying[t-1]>0 else 0.0
    pv_H[t]=pv_H[t-1]*(1.0+w_new*rm+max(0.0,1.0-w_new)*DR
                        -max(0.0,w_new-1.0)*BR-abs(w_new-w)*TC)
    w=w_new

print()
print("=" * 80)
print(f"  BEST COMBO: CRISIS={float(best["cr"]):+.2f} / BEAR={float(best["be"]):+.2f} / NEUTRAL={float(best["ne"]):+.2f} / "
      f"BULL={float(best["bu"]):+.2f} / EX-BULL={float(best["ex"]):+.2f} / Smooth={best["sm"]}")
print("=" * 80)
print(f"  IS  Calmar={best["is_calmar"]:.2f}  CAGR={best["is_cagr"]*100:+.1f}%  MaxDD={best["is_mdd"]*100:.1f}%")
print(f"  OOS Calmar={best["oos_calmar"]:.2f}  CAGR={best["oos_cagr"]*100:+.1f}%  MaxDD={best["oos_mdd"]*100:.1f}%")
print(f"  Full(11+) Calmar={best["full_calmar"]:.2f}  CAGR={best["full_cagr"]*100:+.1f}%  MaxDD={best["full_mdd"]*100:.1f}%")

print()
print(f"  {'Year':<6}  {'F_Best':>9}  {'HT+Rec':>9}  {'B&H':>9}")
print(f"  {'-'*6}  {'-'*9}  {'-'*9}  {'-'*9}")
for yr in sorted(vni["time"].dt.year.unique()):
    mask=vni["time"].dt.year==yr; idx=vni[mask].index
    if len(idx)<10: continue
    i0,i1=idx[0],idx[-1]
    if pv_best[i0]<=0 or yr<2011: continue
    rb=pv_best[i1]/pv_best[i0]-1
    rh=pv_H[i1]/pv_H[i0]-1
    rBH=pv_bh[i1]/pv_bh[i0]-1
    oos=" *" if yr>=2021 else "  "
    def p(v): return f"{v*100:>+8.1f}%"
    beat_h  = ">" if rb>rh  else "<"
    beat_bh = ">" if rb>rBH else "<"
    print(f"  {yr:>4}{oos}  {p(rb)}  {p(rh)}  {p(rBH)}  F{beat_h}H  F{beat_bh}BH")

# ── Save results CSV ──────────────────────────────────────────────────────────
csv_out = WORKDIR + "/data/f_system_gridsearch.csv"
df_s.to_csv(csv_out, index=False)
print(f"\nGrid search results saved: {csv_out}")
print(f"Total combos: {len(df_s)}")
