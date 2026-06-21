# -*- coding: utf-8 -*-
"""
Backtest: Recovery Boost sau CRISIS
- Gia thuyet: giam cang sau + cang nhanh -> phuc hoi cang manh
- Thu nghiem: sau CRISIS, neu do sau / toc do giam du nguong -> tang weight
- Grid search: depth_thresh x speed_thresh x rec_weight x rec_dur
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
from itertools import product

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Rebuild states (giong backtest_workflow.py) ────────────────────────────
vni = pd.read_csv(WORKDIR + "/VNINDEX.csv", low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close","D_RSI_Max3M_Close",
            "D_RSI_Max3M_MACD","D_RSI_Max1W_MACD","D_RSI_MinT3",
            "D_MACDdiff","D_CMF","C_L1M","C_L1W"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")

if os.path.exists(WORKDIR+"/breadth_data.csv"):
    br = pd.read_csv(WORKDIR+"/breadth_data.csv"); br["time"]=pd.to_datetime(br["time"])
    vni = vni.merge(br, on="time", how="left")
else:
    vni["breadth"] = np.nan

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
if "Change_3M" in vni.columns:
    cv=pd.to_numeric(vni["Change_3M"],errors="coerce").values
    for i in range(n):
        p3m[i]=cv[i] if not np.isnan(cv[i]) else (close[i]/close[i-60]-1 if i>=60 and close[i-60]>0 else np.nan)
else:
    for i in range(60,n):
        if close[i-60]>0: p3m[i]=close[i]/close[i-60]-1
p1m=np.full(n,np.nan)
if "Change_1M" in vni.columns:
    cv=pd.to_numeric(vni["Change_1M"],errors="coerce").values
    for i in range(n):
        p1m[i]=cv[i] if not np.isnan(cv[i]) else (close[i]/close[i-20]-1 if i>=20 and close[i-20]>0 else np.nan)
else:
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
br_arr=vni["breadth"].values if "breadth" in vni.columns else np.full(n,np.nan)
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
v20=np.full(n,np.nan)
for i in range(20,n):
    w2=dr[i-20:i]; w2=w2[~np.isnan(w2)]
    if len(w2)>=15: v20[i]=np.std(w2)*np.sqrt(SPY)
avg_vol=np.full(n,np.nan)
for t in range(n):
    h=v20[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: avg_vol[t]=np.mean(h)
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
    if not np.isnan(avg_vol[i]) and not np.isnan(v20[i]) and v20[i]>1.5*avg_vol[i] and s==5: s=4
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
STATE_NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

# ── Tinh dac trung tung giai doan CRISIS ─────────────────────────────────
# crisis_info[i] = {"depth": dd_min, "speed": dd/dur, "vol": std_daily}
# cho moi phien i, neu dang trong recovery mode, tra ve weight tung ung
crisis_episodes = []
i = 0
while i < n - 1:
    if st_smooth[i] == 1:
        start = i
        while i < n - 1 and st_smooth[i] == 1:
            i += 1
        end = i  # phien dau tien KHONG con CRISIS
        dur = end - start
        if dur < 2 or end >= n: continue
        seg = close[start:end]
        daily_rets = np.diff(seg)/seg[:-1]
        peak_in = close[start]  # gia khi vao CRISIS
        bot_val = np.min(seg)
        depth = bot_val/peak_in - 1            # % giam tu dinh (tinh tu khi bat dau CRISIS)
        # depth tu dinh toan ky (dd_raw tai diem exit)
        depth_peak = dd_raw[end]               # DD tu dinh lich su khi thoat
        speed = depth / dur                    # % giam moi phien (am)
        vol_c = np.std(daily_rets) if len(daily_rets) > 1 else 0.0
        to_state = st_smooth[end]
        crisis_episodes.append({
            "start": start, "end": end, "dur": dur,
            "depth_local": depth,
            "depth_peak": depth_peak,
            "speed": speed,
            "vol_crisis": vol_c,
            "to_state": to_state,
            "date_exit": vni["time"].iloc[end],
        })
    else:
        i += 1

# ── Phan 1: Kiem tra gia thuyet depth/speed → forward return ─────────────
print()
print("="*78)
print("  PHAN 1: MOI QUAN HE GIAM SAU/NHANH → PHUC HOI MANH?")
print("="*78)
print(f"\n  {'Lan':>3}  {'Ngay':>12}  {'Depth':>7}  {'Speed/p':>8}  {'Vol/p':>7}  {'T+20':>7}  {'T+40':>7}  {'T+60':>7}")
print(f"  {'─'*72}")

fwd_data = []
for ep in crisis_episodes:
    idx = ep["end"]
    fwds = {}
    for h in [20, 40, 60, 120]:
        fwds[h] = close[idx+h]/close[idx]-1 if idx+h < n and close[idx]>0 else np.nan
    fwd_data.append({**ep, **{f"fwd_{h}": fwds[h] for h in [20,40,60,120]}})
    print(f"  {len(fwd_data):>3}  {ep['date_exit'].strftime('%Y-%m-%d'):>12}"
          f"  {ep['depth_peak']*100:>+6.1f}%"
          f"  {ep['speed']*100:>+7.3f}%"
          f"  {ep['vol_crisis']*100:>+6.2f}%"
          f"  {fwds[20]*100 if not np.isnan(fwds[20]) else 0:>+6.1f}%"
          f"  {fwds[40]*100 if not np.isnan(fwds[40]) else 0:>+6.1f}%"
          f"  {fwds[60]*100 if not np.isnan(fwds[60]) else 0:>+6.1f}%")

# Phan nhom theo do sau
print(f"\n  PHAN NHOM THEO DO SAU (depth_peak khi thoat CRISIS):")
print(f"  {'Nhom':>20}  {'N':>3}  {'T+20 TB':>8}  {'T+40 TB':>8}  {'T+60 TB':>8}  {'%>0 T20':>8}")
print(f"  {'─'*60}")
groups = [
    ("Nhe (<-20%)",       lambda e: e["depth_peak"] > -0.20),
    ("Vua (-20~-35%)",    lambda e: -0.35 < e["depth_peak"] <= -0.20),
    ("Sau (-35~-50%)",    lambda e: -0.50 < e["depth_peak"] <= -0.35),
    ("Rat sau (>-50%)",   lambda e: e["depth_peak"] <= -0.50),
]
for name, fn in groups:
    sub = [e for e in fwd_data if fn(e)]
    if not sub: continue
    v20 = [e["fwd_20"] for e in sub if not np.isnan(e.get("fwd_20",np.nan))]
    v40 = [e["fwd_40"] for e in sub if not np.isnan(e.get("fwd_40",np.nan))]
    v60 = [e["fwd_60"] for e in sub if not np.isnan(e.get("fwd_60",np.nan))]
    pct = sum(1 for x in v20 if x>0)/len(v20) if v20 else 0
    print(f"  {name:>20}  {len(sub):>3}  {np.mean(v20)*100:>+7.1f}%  {np.mean(v40)*100:>+7.1f}%  {np.mean(v60)*100:>+7.1f}%  {pct*100:>7.0f}%")

# Phan nhom theo toc do giam
print(f"\n  PHAN NHOM THEO TOC DO GIAM (speed = depth/duration, %/phien):")
print(f"  {'Nhom':>22}  {'N':>3}  {'T+20 TB':>8}  {'T+40 TB':>8}  {'T+60 TB':>8}  {'%>0 T20':>8}")
print(f"  {'─'*62}")
speed_groups = [
    ("Cham  (>-0.2%/p)",   lambda e: e["speed"] > -0.002),
    ("TB    (-0.2~-0.5%/p)",lambda e: -0.005 < e["speed"] <= -0.002),
    ("Nhanh (-0.5~-1.0%/p)",lambda e: -0.010 < e["speed"] <= -0.005),
    ("Rat nhanh (<-1%/p)", lambda e: e["speed"] <= -0.010),
]
for name, fn in speed_groups:
    sub = [e for e in fwd_data if fn(e)]
    if not sub: continue
    v20 = [e["fwd_20"] for e in sub if not np.isnan(e.get("fwd_20",np.nan))]
    v40 = [e["fwd_40"] for e in sub if not np.isnan(e.get("fwd_40",np.nan))]
    v60 = [e["fwd_60"] for e in sub if not np.isnan(e.get("fwd_60",np.nan))]
    pct = sum(1 for x in v20 if x>0)/len(v20) if v20 else 0
    print(f"  {name:>22}  {len(sub):>3}  {np.mean(v20)*100:>+7.1f}%  {np.mean(v40)*100:>+7.1f}%  {np.mean(v60)*100:>+7.1f}%  {pct*100:>7.0f}%")

# ── Phan 2: Tao weight array voi recovery boost ───────────────────────────
def build_recovery_map(depth_thresh, speed_thresh, rec_weight, rec_dur):
    """
    Tra ve dict: {phien_idx: recovery_weight_target}
    Kich hoat neu: depth_peak < depth_thresh AND speed < speed_thresh
    """
    rec_map = {}
    for ep in crisis_episodes:
        ok_depth = ep["depth_peak"] < depth_thresh    # giam du sau
        ok_speed = ep["speed"] < speed_thresh         # giam du nhanh
        if ok_depth and ok_speed:
            exit_idx = ep["end"]
            for t in range(exit_idx, min(exit_idx + rec_dur, n)):
                # Chi override neu state hien tai khong phai CRISIS
                if st_smooth[t] != 1:
                    rec_map[t] = rec_weight
    return rec_map

def simulate_with_recovery(rec_map, deposit_annual=0.001):
    """NAV simulation giong backtest_workflow nhung co the override target_w."""
    DR = deposit_annual / SPY
    BR = 0.10 / SPY
    TC = 0.001
    pv = np.zeros(n); pv[0] = 1e9
    w = TARGET_W[3]
    for t in range(1, n):
        # Target weight: uu tien recovery_map neu co
        base_target = TARGET_W[st_smooth[t-1]]
        if (t-1) in rec_map:
            # Recovery: lay max cua base va rec_weight (khong giam xuong)
            target = max(base_target, rec_map[t-1])
        else:
            target = base_target
        diff = target - w
        w_new = target if abs(diff) < 0.03 else w + diff/3
        w_new = float(np.clip(w_new, 0.0, 1.50))
        rm = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t] = pv[t-1] * (1.0 + w_new*rm
                            + max(0.0, 1.0-w_new)*DR
                            - max(0.0, w_new-1.0)*BR
                            - abs(w_new-w)*TC)
        w = w_new
    return pv

def metrics(pv_arr, i0=0, i1=None):
    sl = pv_arr[i0:] if i1 is None else pv_arr[i0:i1]
    ds = vni["time"].reset_index(drop=True).iloc[i0:] if i1 is None else vni["time"].reset_index(drop=True).iloc[i0:i1]
    pv_arr2=np.asarray(sl,dtype=float); valid=np.where(pv_arr2>0)[0]
    if len(valid)<10: return {}
    i0_,i1_=valid[0],valid[-1]; v0,v1=pv_arr2[i0_],pv_arr2[i1_]
    ds2=ds.reset_index(drop=True)
    yrs=(ds2.iloc[i1_]-ds2.iloc[i0_]).days/365.25
    if yrs<=0: return {}
    cagr=(v1/v0)**(1/yrs)-1
    sub=pv_arr2[i0_:i1_+1]; rets=np.diff(sub)/sub[:-1]
    spy_sub=len(rets)/yrs
    mr=np.mean(rets); sr=np.std(rets)
    sharpe=mr*spy_sub/(sr*np.sqrt(spy_sub)) if sr>0 else 0
    down=rets[rets<0]; ds3=np.sqrt(np.mean(down**2)) if len(down)>0 else 0
    sortino=mr*spy_sub/(ds3*np.sqrt(spy_sub)) if ds3>0 else 0
    rm2=np.maximum.accumulate(sub); dd2=np.where(rm2>0,sub/rm2-1,0)
    mdd=dd2.min(); calmar=cagr/abs(mdd) if mdd!=0 else 0
    return {"cagr":cagr,"sharpe":sharpe,"sortino":sortino,"mdd":mdd,"calmar":calmar}

idx11=vni[vni["time"]>="2011-01-01"].index[0]
idx21=vni[vni["time"]>="2021-01-01"].index[0]

# Baseline (deposit 0.1%, khong co recovery boost)
pv_base = simulate_with_recovery({}, deposit_annual=0.001)
mb11 = metrics(pv_base, idx11)

# B&H
pv_bh = np.zeros(n); pv_bh[0] = 1e9
for t in range(1,n): pv_bh[t] = pv_bh[t-1]*(close[t]/close[t-1] if close[t-1]>0 else 1.0)
mb_bh11 = metrics(pv_bh, idx11)

# ── Phan 2: Grid search ───────────────────────────────────────────────────
print(f"\n\n{'='*78}")
print(f"  PHAN 2: GRID SEARCH - Recovery Boost Parameters")
print(f"  Baseline (0.1% dep, khong boost): CAGR={mb11['cagr']*100:+.1f}%  Calmar={mb11['calmar']:.2f}  MaxDD={mb11['mdd']*100:+.1f}%")
print(f"  B&H                             : CAGR={mb_bh11['cagr']*100:+.1f}%  Calmar={mb_bh11['calmar']:.2f}  MaxDD={mb_bh11['mdd']*100:+.1f}%")
print(f"{'='*78}")

DEPTH_THRESHS  = [-0.15, -0.20, -0.25, -0.30, -0.35]   # depth_peak < X moi kich hoat
SPEED_THRESHS  = [-0.001, -0.002, -0.003, -0.005]        # speed < X moi kich hoat
REC_WEIGHTS    = [0.90, 1.00, 1.10, 1.20, 1.30]          # weight trong recovery
REC_DURS       = [20, 40, 60]                             # phien recovery

print(f"\n  Dang chay {len(DEPTH_THRESHS)*len(SPEED_THRESHS)*len(REC_WEIGHTS)*len(REC_DURS)} kich ban...\n")

results = []
for dt, st_, rw, rd in product(DEPTH_THRESHS, SPEED_THRESHS, REC_WEIGHTS, REC_DURS):
    rmap = build_recovery_map(dt, st_, rw, rd)
    n_activated = len(set(rmap.keys()))
    if n_activated == 0: continue
    pv = simulate_with_recovery(rmap, deposit_annual=0.001)
    m11 = metrics(pv, idx11)
    m21 = metrics(pv, idx21)
    if not m11: continue
    results.append({
        "depth": dt, "speed": st_, "rw": rw, "dur": rd,
        "cagr11": m11["cagr"], "calmar11": m11["calmar"], "mdd11": m11["mdd"],
        "sharpe11": m11["sharpe"],
        "cagr21": m21.get("cagr", np.nan), "calmar21": m21.get("calmar", np.nan),
        "n_sess": n_activated,
    })

results.sort(key=lambda x: x["calmar11"], reverse=True)

print(f"  TOP 20 theo Calmar (2011-nay), dep=0.1%/nam:")
print(f"  {'Depth':>7}  {'Speed/p':>8}  {'RecW':>6}  {'Dur':>4}  {'CAGR':>7}  {'Calmar':>7}  {'MaxDD':>8}  {'Sharpe':>7}  {'CAGR21':>7}  {'Cal21':>6}  {'Sess':>5}")
print(f"  {'─'*90}")
for r in results[:20]:
    print(f"  {r['depth']*100:>+6.0f}%  {r['speed']*100:>+7.3f}%  {r['rw']*100:>5.0f}%  {r['dur']:>4}"
          f"  {r['cagr11']*100:>+6.1f}%  {r['calmar11']:>7.2f}  {r['mdd11']*100:>+7.1f}%"
          f"  {r['sharpe11']:>7.2f}  {r['cagr21']*100:>+6.1f}%  {r['calmar21']:>6.2f}"
          f"  {r['n_sess']:>5}")

# ── Phan 3: Phan tich best scenario chi tiet ─────────────────────────────
best = results[0]
print(f"\n\n{'='*78}")
print(f"  PHAN 3: CHI TIET BEST SCENARIO")
print(f"  depth<{best['depth']*100:.0f}%  speed<{best['speed']*100:.3f}%/p  recW={best['rw']*100:.0f}%  dur={best['dur']}p")
print(f"{'='*78}")

rmap_best = build_recovery_map(best["depth"], best["speed"], best["rw"], best["dur"])
pv_best = simulate_with_recovery(rmap_best, deposit_annual=0.001)

# Hien thi nhung phien nao duoc kich hoat recovery
print(f"\n  Cac giai doan recovery duoc kich hoat ({len([ep for ep in crisis_episodes if ep['depth_peak']<best['depth'] and ep['speed']<best['speed']])} lan):")
print(f"  {'Ngay thoat':>12}  {'Depth':>7}  {'Speed':>8}  {'Dur':>5}  {'T+20 VNINDEX':>13}  {'T+20 HT':>10}  {'T+20 BEST':>10}")
print(f"  {'─'*74}")
for ep in fwd_data:
    ok = ep["depth_peak"] < best["depth"] and ep["speed"] < best["speed"]
    if not ok: continue
    idx = ep["end"]
    # HT baseline trong 20p
    pv_b20 = pv_base[idx+20]/pv_base[idx]-1 if idx+20 < n else np.nan
    pv_bst20 = pv_best[idx+20]/pv_best[idx]-1 if idx+20 < n else np.nan
    fv = ep.get("fwd_20", np.nan)
    print(f"  {ep['date_exit'].strftime('%Y-%m-%d'):>12}"
          f"  {ep['depth_peak']*100:>+6.1f}%  {ep['speed']*100:>+7.3f}%"
          f"  {ep['dur']:>5}"
          f"  {fv*100:>+12.1f}%"
          f"  {pv_b20*100:>+9.1f}%"
          f"  {pv_bst20*100:>+9.1f}%")

# So sanh tong the
print(f"\n  {'─'*74}")
print(f"  SO SANH TONG THE:")
print(f"  {'Kich ban':<30}  {'CAGR 2011':>10}  {'Calmar':>7}  {'MaxDD':>8}  {'Sharpe':>7}  {'CAGR OOS':>9}")
print(f"  {'─'*74}")

for lbl, pv_arr in [("Baseline (khong boost)", pv_base),
                     (f"Best recovery boost", pv_best),
                     ("B&H", pv_bh)]:
    m11 = metrics(pv_arr, idx11)
    m21 = metrics(pv_arr, idx21)
    print(f"  {lbl:<30}  {m11.get('cagr',0)*100:>+9.1f}%  {m11.get('calmar',0):>7.2f}"
          f"  {m11.get('mdd',0)*100:>+7.1f}%  {m11.get('sharpe',0):>7.2f}"
          f"  {m21.get('cagr',0)*100:>+8.1f}%")

# ── Phan 4: Annual breakdown ──────────────────────────────────────────────
print(f"\n  ANNUAL BREAKDOWN (tu 2011):")
print(f"  {'Nam':>4}  {'Baseline':>9}  {'BestBoost':>10}  {'B&H':>8}  {'Diff':>7}  {'Boost>BH':>9}")
print(f"  {'─'*62}")
for yr in sorted(vni["time"].dt.year.unique()):
    if yr < 2011: continue
    mask=vni["time"].dt.year==yr; idx=vni[mask].index
    if len(idx)<20: continue
    i0,i1=idx[0],idx[-1]
    if pv_base[i0]<=0: continue
    rb  = pv_base[i1]/pv_base[i0]-1
    rbt = pv_best[i1]/pv_best[i0]-1
    rbh = pv_bh[i1]/pv_bh[i0]-1
    diff = rbt - rb
    oos = " <OOS" if yr>=2021 else ""
    beat = "ok" if rbt>rbh else "  "
    print(f"  {yr:>4}  {rb:>+8.1f}%  {rbt:>+9.1f}%  {rbh:>+7.1f}%  {diff*100:>+6.2f}pp  {beat:>9}{oos}")

# ── Phan 5: Sensitivity vs baseline ──────────────────────────────────────
print(f"\n\n{'='*78}")
print(f"  PHAN 5: HEATMAP CALMAR - depth vs rec_weight (speed={best['speed']*100:.3f}%, dur={best['dur']}p)")
print(f"{'='*78}")
print(f"\n  {'Depth\\RecW':>12}", end="")
for rw in REC_WEIGHTS: print(f"  {rw*100:.0f}%", end="")
print()
print(f"  {'─'*50}")
for dt in DEPTH_THRESHS:
    print(f"  {dt*100:>+10.0f}%  ", end="")
    for rw in REC_WEIGHTS:
        # Lay best speed va best dur cho combo nay
        matches = [r for r in results if r["depth"]==dt and r["rw"]==rw and r["speed"]==best["speed"] and r["dur"]==best["dur"]]
        if matches:
            cal = matches[0]["calmar11"]
            marker = "*" if (dt==best["depth"] and rw==best["rw"]) else " "
            print(f"  {cal:.2f}{marker}", end="")
        else:
            print(f"   N/A", end="")
    print()

print(f"\n  * = best combination\n  Baseline Calmar = {mb11['calmar']:.2f}")
print()
