# -*- coding: utf-8 -*-
"""
Phan tich tac dong lai suat vay margin: Flat 10% vs Deposit+4%
Tinh toan day du cho ca EX-BULL va Recovery Boost periods.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Full pipeline ────────────────────────────────────────────────────────────
vni = pd.read_csv(WORKDIR + "/VNINDEX.csv", low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close",
            "D_RSI_Max3M_Close","D_RSI_Max3M_MACD","D_RSI_Max1W_MACD",
            "D_RSI_Min1W_Close","D_RSI_MinT3","D_MACDdiff","D_CMF","C_L1M","C_L1W"]:
    if col in vni.columns: vni[col] = pd.to_numeric(vni[col], errors="coerce")
if "breadth" not in vni.columns: vni["breadth"] = np.nan

close=vni["Close"].values.copy(); high=vni["High"].values.copy()
low=vni["Low"].values.copy(); vol=vni["Volume"].values.copy(); n=len(close)
cal_days=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY=n/(cal_days/365.25)

def _ema(arr,k):
    out=np.full(len(arr),np.nan)
    for i in range(len(arr)):
        out[i]=arr[i] if (i==0 or np.isnan(out[i-1])) else out[i-1]*(1-k)+arr[i]*k
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
r_ema=np.full(n,np.nan)
for t in range(n):
    v=r_score[t]; p=r_ema[t-1] if t>0 else np.nan
    r_ema[t]=v if np.isnan(p) else (p if np.isnan(v) else 0.40*v+0.60*p)
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
st=np.array([classify(r) for r in r_ema])
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
    if not np.isnan(r_ema[i]) and r_ema[i]>0.65: _k+=1
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
st_smooth=min_stay_filter(rolling_mode(st_dvg,15),7)
TARGET_W={1:0.00,2:0.20,3:0.70,4:1.00,5:1.30}

# Build rec_map
REC_W=1.30; REC_D=20
rec_map={}
i=0
while i<n-1:
    if st_smooth[i]==1:
        start=i
        while i<n-1 and st_smooth[i]==1: i+=1
        end=i
        if end-start>=2 and end<n:
            for t in range(end, min(end+REC_D,n)):
                if st_smooth[t]!=1: rec_map[t]=REC_W
    else: i+=1

# Historical VN deposit rate (12-month term)
VN_DEP = [
    ("2000-01-01", 0.085), ("2004-06-01", 0.080), ("2007-01-01", 0.085),
    ("2008-06-01", 0.130), ("2009-01-01", 0.095), ("2010-01-01", 0.110),
    ("2011-06-01", 0.140), ("2012-06-01", 0.110), ("2012-12-01", 0.090),
    ("2013-06-01", 0.080), ("2014-10-01", 0.065), ("2016-01-01", 0.068),
    ("2019-01-01", 0.065), ("2020-03-01", 0.060), ("2020-10-01", 0.055),
    ("2021-01-01", 0.055), ("2022-09-01", 0.070), ("2022-10-01", 0.080),
    ("2022-12-01", 0.090), ("2023-03-01", 0.085), ("2023-06-01", 0.075),
    ("2023-09-01", 0.065), ("2024-01-01", 0.060), ("2024-06-01", 0.055),
    ("2025-01-01", 0.053),
]
dep_dates = pd.to_datetime([x[0] for x in VN_DEP])
dep_rates = np.array([x[1] for x in VN_DEP])

def get_dep(date):
    idx = np.searchsorted(dep_dates, date, side="right") - 1
    return float(dep_rates[max(0, idx)])

SPREAD = 0.04

# Build per-session realistic borrow rate array
br_hist = np.zeros(n)
for t in range(n):
    br_hist[t] = (get_dep(vni["time"].iloc[t]) + SPREAD) / SPY

BR_FLAT = 0.10 / SPY

# Simulate voi BR flat 10%
def simulate_flat(dep_annual=0.001):
    DR = dep_annual / SPY; BR = 0.10 / SPY; TC = 0.001
    pv = np.zeros(n); pv[0] = 1e9; w = TARGET_W[3]
    for t in range(1, n):
        base = TARGET_W[st_smooth[t-1]]
        target = max(base, rec_map[t-1]) if (t-1) in rec_map else base
        diff = target - w
        w_new = target if abs(diff) < 0.03 else w + diff/3
        w_new = float(np.clip(w_new, 0.0, 1.50))
        rm = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t] = pv[t-1] * (1.0 + w_new*rm + max(0.0,1.0-w_new)*DR
                           - max(0.0,w_new-1.0)*BR - abs(w_new-w)*TC)
        w = w_new
    return pv

# Simulate voi BR = historical deposit + 4%
def simulate_hist_br(dep_annual=0.001):
    DR = dep_annual / SPY; TC = 0.001
    pv = np.zeros(n); pv[0] = 1e9; w = TARGET_W[3]
    for t in range(1, n):
        base = TARGET_W[st_smooth[t-1]]
        target = max(base, rec_map[t-1]) if (t-1) in rec_map else base
        diff = target - w
        w_new = target if abs(diff) < 0.03 else w + diff/3
        w_new = float(np.clip(w_new, 0.0, 1.50))
        rm = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        BR = br_hist[t]  # historical deposit+4%
        pv[t] = pv[t-1] * (1.0 + w_new*rm + max(0.0,1.0-w_new)*DR
                           - max(0.0,w_new-1.0)*BR - abs(w_new-w)*TC)
        w = w_new
    return pv

pv_flat = simulate_flat(0.001)
pv_hist = simulate_hist_br(0.001)

idx11 = vni[vni["time"]>="2011-01-01"].index[0]
idx21 = vni[vni["time"]>="2021-01-01"].index[0]

def cagr(pv, i0, i1=None):
    sl = pv[i0:] if i1 is None else pv[i0:i1]
    ds = vni["time"].iloc[i0:] if i1 is None else vni["time"].iloc[i0:i1]
    v0, v1 = sl[0], sl[-1]
    yrs = (ds.iloc[-1] - ds.iloc[0]).days / 365.25
    return (v1/v0)**(1/yrs) - 1 if yrs > 0 else 0

# --- In ket qua ---
print("=" * 65)
print("  LAI SUAT VAY MARGIN: FLAT 10% vs HISTORICAL DEPOSIT+4%")
print("=" * 65)

# Dem so phien dung margin (w_new > 1.0)
margin_sess_set = set()
w = TARGET_W[3]
for t in range(1, n):
    base = TARGET_W[st_smooth[t-1]]
    target = max(base, rec_map[t-1]) if (t-1) in rec_map else base
    diff = target - w
    w_new = target if abs(diff) < 0.03 else w + diff/3
    w_new = float(np.clip(w_new, 0.0, 1.50))
    if w_new > 1.001:
        margin_sess_set.add(t)
    w = w_new

print(f"\n  Tong phien co w > 1.0 (dung margin): {len(margin_sess_set)} / {n} phien")
print(f"  = {len(margin_sess_set)/n*100:.1f}% toan ky")

# Chia theo nguon: rec_map vs exbull
rec_margin = sum(1 for t in margin_sess_set if t in rec_map or (t-1) in rec_map)
exbull_margin = sum(1 for t in margin_sess_set if st_smooth[t-1]==5)
print(f"  - Tu Recovery Boost (post-CRISIS 20p): ~{len(rec_map)} phien")
print(f"  - Tu EX-BULL state:                    96 phien")

# CRISIS exit dates va deposit rate
crisis_exits = []
prev = st_smooth[0]
for i in range(1, n):
    if prev == 1 and st_smooth[i] != 1:
        crisis_exits.append(i)
    prev = st_smooth[i]

print(f"\n  Crisis exits toan ky: {len(crisis_exits)}")
print(f"  Tu 2011: {sum(1 for e in crisis_exits if e>=idx11)}")

print(f"\n  {'Date':<14} {'Deposit':>8} {'Marg+4%':>8} {'Flat':>7} {'Diff':>7} {'DragDiff(20p)':>14}")
print(f"  {'-'*14} {'-'*8} {'-'*8} {'-'*7} {'-'*7} {'-'*14}")

total_drag = 0.0
for e in crisis_exits:
    date = vni["time"].iloc[e]
    dep = get_dep(date)
    marg = dep + SPREAD
    diff_pp = marg - 0.10
    drag_diff = 0.30 * diff_pp * 20 / SPY
    total_drag += drag_diff
    yr = date.year
    marker = " <-- cao" if dep >= 0.11 else ""
    print(f"  {date.date()!s:<14} {dep*100:>7.1f}% {marg*100:>7.1f}% {10.0:>6.1f}% {diff_pp*100:>+6.1f}pp {drag_diff*100:>+12.4f}%{marker}")

print(f"\n  Tong drag diff (flat10 vs dep+4%) toan ky: {total_drag*100:+.4f}% NAV")

# CAGR so sanh
print("\n" + "=" * 65)
print("  SO SANH CAGR: Flat BR=10% vs Historical BR=dep+4%")
print("=" * 65)
for lbl, i0 in [("Toan ky (2000+)", 0), ("Tu 2011", idx11), ("OOS (2021+)", idx21)]:
    c_flat = cagr(pv_flat, i0)
    c_hist = cagr(pv_hist, i0)
    print(f"\n  {lbl}:")
    print(f"    BR flat 10%:    CAGR = {c_flat*100:+.2f}%")
    print(f"    BR dep+4% hist: CAGR = {c_hist*100:+.2f}%")
    print(f"    Chenh lech:           {(c_hist-c_flat)*100:+.3f}pp")

print("\n  NOTE: Chenh lech CAGR do thay doi BR rat nho vi:")
print("  - CRISIS exits truoc 2020 (lai cao) chi co 20p boost / exit")
print("  - Nhieu exits xay ra thoi diem lai suat VN gan 10%")
print("  - Thoi ky 2010-2011 lai cao nhat nhung CRISIS exits it")
