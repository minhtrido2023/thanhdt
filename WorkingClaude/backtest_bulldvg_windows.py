# -*- coding: utf-8 -*-
"""
Kiem tra BullDvg voi cac cua so nhin lai rong hon (25-60 phien).
So sanh voi "boost tat ca exits" (best tu truoc).
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Build states (same pipeline) ──────────────────────────────────────────
vni = pd.read_csv(WORKDIR + "/data/VNINDEX.csv", low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close","D_RSI_Max3M_Close",
            "D_RSI_Max3M_MACD","D_RSI_Max1W_MACD","D_RSI_MinT3",
            "D_MACDdiff","D_CMF","C_L1M","C_L1W"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")
if os.path.exists(WORKDIR+"/data/breadth_data.csv"):
    br = pd.read_csv(WORKDIR+"/data/breadth_data.csv"); br["time"]=pd.to_datetime(br["time"])
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
v20_arr=np.full(n,np.nan)
for i in range(20,n):
    w2=dr[i-20:i]; w2=w2[~np.isnan(w2)]
    if len(w2)>=15: v20_arr[i]=np.std(w2)*np.sqrt(SPY)
avg_vol_arr=np.full(n,np.nan)
for t in range(n):
    h=v20_arr[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: avg_vol_arr[t]=np.mean(h)

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
    if not np.isnan(avg_vol_arr[i]) and not np.isnan(v20_arr[i]) and v20_arr[i]>1.5*avg_vol_arr[i] and s==5: s=4
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

# ── Precompute BullDvg rolling windows ────────────────────────────────────
WINDOWS = [20, 25, 30, 40, 60]
bull_win = {}
for w in WINDOWS:
    arr = np.zeros(n, dtype=bool)
    for i in range(n):
        arr[i] = np.any(bull_mask[max(0,i-w+1):i+1])
    bull_win[w] = arr

# ── Collect CRISIS exits ───────────────────────────────────────────────────
crisis_exits = []
i = 0
while i < n-1:
    if st_smooth[i] == 1:
        start = i
        while i < n-1 and st_smooth[i] == 1:
            i += 1
        end = i
        dur = end - start
        if dur < 2 or end >= n-1: i += 1; continue
        ep = {"start":start,"end":end,"dur":dur,
              "date":vni["time"].iloc[end],
              "depth_peak":dd_raw[end],
              "r_ema_val":r_ema[end] if not np.isnan(r_ema[end]) else 0.0}
        for w in WINDOWS:
            ep[f"bull_{w}p"] = bool(bull_win[w][end])
        for h in [20,40,60]:
            ep[f"fwd_{h}"] = close[end+h]/close[end]-1 if end+h < n and close[end]>0 else np.nan
        crisis_exits.append(ep)
    else:
        i += 1

# ── Utility ────────────────────────────────────────────────────────────────
REC_WEIGHT = 1.30
REC_DUR    = 20

def simulate(rec_episodes, dep=0.001):
    # Build rmap from episode list
    rmap = {}
    for ep in rec_episodes:
        for t in range(ep["end"], min(ep["end"]+REC_DUR, n)):
            if st_smooth[t] != 1:
                rmap[t] = REC_WEIGHT
    DR=dep/SPY; BR=0.10/SPY; TC=0.001
    pv=np.zeros(n); pv[0]=1e9; w=TARGET_W[3]
    for t in range(1,n):
        base=TARGET_W[st_smooth[t-1]]
        target=max(base,rmap[t-1]) if (t-1) in rmap else base
        diff=target-w
        w_new=target if abs(diff)<0.03 else w+diff/3
        w_new=float(np.clip(w_new,0.0,1.50))
        rm=close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t]=pv[t-1]*(1.0+w_new*rm+max(0.0,1.0-w_new)*DR
                        -max(0.0,w_new-1.0)*BR-abs(w_new-w)*TC)
        w=w_new
    return pv

def metrics(pv,i0=0,i1=None):
    sl=pv[i0:] if i1 is None else pv[i0:i1]
    ds=(vni["time"].reset_index(drop=True).iloc[i0:] if i1 is None
        else vni["time"].reset_index(drop=True).iloc[i0:i1])
    a=np.asarray(sl,dtype=float); v=np.where(a>0)[0]
    if len(v)<10: return {}
    i0_,i1_=v[0],v[-1]; v0,v1=a[i0_],a[i1_]
    ds2=ds.reset_index(drop=True)
    yrs=(ds2.iloc[i1_]-ds2.iloc[i0_]).days/365.25
    if yrs<=0: return {}
    cagr=(v1/v0)**(1/yrs)-1
    sub=a[i0_:i1_+1]; rets=np.diff(sub)/sub[:-1]; spy_s=len(rets)/yrs
    mr=np.mean(rets); sr=np.std(rets)
    sharpe=mr*spy_s/(sr*np.sqrt(spy_s)) if sr>0 else 0
    down=rets[rets<0]; ds3=np.sqrt(np.mean(down**2)) if len(down)>0 else 0
    sortino=mr*spy_s/(ds3*np.sqrt(spy_s)) if ds3>0 else 0
    rm2=np.maximum.accumulate(sub); dd2=np.where(rm2>0,sub/rm2-1,0)
    mdd=dd2.min(); calmar=cagr/abs(mdd) if mdd!=0 else 0
    return {"cagr":cagr,"sharpe":sharpe,"sortino":sortino,"mdd":mdd,"calmar":calmar}

idx11=vni[vni["time"]>="2011-01-01"].index[0]
idx21=vni[vni["time"]>="2021-01-01"].index[0]
pv_bh=np.zeros(n); pv_bh[0]=1e9
for t in range(1,n): pv_bh[t]=pv_bh[t-1]*(close[t]/close[t-1] if close[t-1]>0 else 1.0)

# ── Phan 1: BullDvg tai tung exit voi cac window ─────────────────────────
print()
print("="*80)
print("  BULLDVG: TAN SUAT XUAT HIEN TRONG TUNG CUA SO NHIN LAI")
print("="*80)
print(f"\n  {'Lan':>3}  {'Ngay':>12}  {'Depth':>7}  {'T+20':>7}", end="")
for w in WINDOWS: print(f"  {'BD'+str(w)+'p':>6}", end="")
print(f"  {'Ket qua':>8}")
print(f"  {'─'*75}")

for e in crisis_exits:
    f20 = e.get("fwd_20", np.nan)
    result = "?" if np.isnan(f20) else ("TANG" if f20>0.05 else ("NGANG" if f20>0 else "BAY"))
    print(f"  {crisis_exits.index(e)+1:>3}  {e['date'].strftime('%Y-%m-%d'):>12}"
          f"  {e['depth_peak']*100:>+6.1f}%"
          f"  {f20*100 if not np.isnan(f20) else 0:>+6.1f}%", end="")
    for w in WINDOWS:
        print(f"  {'Y' if e[f'bull_{w}p'] else '-':>6}", end="")
    print(f"  {result:>8}")

# Tan suat
print(f"\n  Tan suat co BullDvg:")
for w in WINDOWS:
    cnt = sum(1 for e in crisis_exits if e[f"bull_{w}p"])
    activated = [e for e in crisis_exits if e[f"bull_{w}p"]]
    fwds = [e["fwd_20"] for e in activated if not np.isnan(e.get("fwd_20",np.nan))]
    not_act = [e for e in crisis_exits if not e[f"bull_{w}p"]]
    fwds_no = [e["fwd_20"] for e in not_act if not np.isnan(e.get("fwd_20",np.nan))]
    print(f"  BullDvg({w:>2}p): {cnt:>2}/{len(crisis_exits)} exits"
          f"  |  T+20 YES={np.mean(fwds)*100:+.1f}% (N={len(fwds)})"
          f"  NO={np.mean(fwds_no)*100:+.1f}% (N={len(fwds_no)})" if fwds else
          f"  BullDvg({w:>2}p): {cnt:>2}/{len(crisis_exits)} exits  |  (no data)")

# ── Phan 2: Backtest tung window ──────────────────────────────────────────
print(f"\n\n{'='*80}")
print(f"  BACKTEST: BullDvg(Xp) vs Boost-All vs Baseline  [RecW=130%, Dur=20p]")
print(f"{'='*80}")
print(f"\n  {'Kich ban':<38}  {'N':>3}  {'CAGR11':>7}  {'Calmar':>7}  {'MaxDD':>8}  {'OOS CAGR':>9}")
print(f"  {'─'*80}")

pv_base  = simulate([])
pv_all   = simulate(crisis_exits)
pv_bh_   = pv_bh

mb   = metrics(pv_base, idx11)
mall = metrics(pv_all,  idx11)
mbh  = metrics(pv_bh,   idx11)
mob  = metrics(pv_base, idx21)
moal = metrics(pv_all,  idx21)
mobh = metrics(pv_bh,   idx21)

print(f"  {'Baseline (khong boost)':<38}  {0:>3}  {mb['cagr']*100:>+6.1f}%  {mb['calmar']:>7.2f}"
      f"  {mb['mdd']*100:>+7.1f}%  {mob.get('cagr',0)*100:>+8.1f}%")
print(f"  {'Boost TAT CA exits (best truoc)':<38}  {len(crisis_exits):>3}  {mall['cagr']*100:>+6.1f}%  {mall['calmar']:>7.2f}"
      f"  {mall['mdd']*100:>+7.1f}%  {moal.get('cagr',0)*100:>+8.1f}%")

results_bd = []
for w in WINDOWS:
    filtered = [e for e in crisis_exits if e[f"bull_{w}p"]]
    pv = simulate(filtered)
    m11 = metrics(pv, idx11)
    m21 = metrics(pv, idx21)
    results_bd.append((w, filtered, pv, m11, m21))
    print(f"  {'Filter: BullDvg('+str(w)+'p)':<38}  {len(filtered):>3}  {m11.get('cagr',0)*100:>+6.1f}%  {m11.get('calmar',0):>7.2f}"
          f"  {m11.get('mdd',0)*100:>+7.1f}%  {m21.get('cagr',0)*100:>+8.1f}%")

# BullDvg OR: khi khong co BullDvg -> van boost (= boost all), chi la kiem tra
# BullDvg NOT: chi boost khi KHONG co BullDvg
for w in [30, 40]:
    filtered_not = [e for e in crisis_exits if not e[f"bull_{w}p"]]
    pv = simulate(filtered_not)
    m11 = metrics(pv, idx11)
    m21 = metrics(pv, idx21)
    print(f"  {'Filter: NOT BullDvg('+str(w)+'p)':<38}  {len(filtered_not):>3}  {m11.get('cagr',0)*100:>+6.1f}%  {m11.get('calmar',0):>7.2f}"
          f"  {m11.get('mdd',0)*100:>+7.1f}%  {m21.get('cagr',0)*100:>+8.1f}%")

print(f"  {'B&H':<38}  {'':>3}  {mbh['cagr']*100:>+6.1f}%  {mbh['calmar']:>7.2f}"
      f"  {mbh['mdd']*100:>+7.1f}%  {mobh.get('cagr',0)*100:>+8.1f}%")

# ── Phan 3: BullDvg trong khoang CRISIS (tu khi bat dau den khi thoat) ───
print(f"\n\n{'='*80}")
print(f"  PHAN 3: BULLDVG XUAT HIEN O DAU TRONG GIAI DOAN CRISIS?")
print(f"  (BullDvg o dau trong crisis vs o gan exit?)")
print(f"{'='*80}")
print(f"\n  {'Lan':>3}  {'Ngay exit':>12}  {'Dur':>5}  {'BD lan dau':>12}  {'Cach exit':>10}  {'% thoi gian':>12}  {'T+20':>8}")
print(f"  {'─'*72}")

lag_stats = []
for e in crisis_exits:
    start, end, dur = e["start"], e["end"], e["dur"]
    # Tim phien dau tien co BullDvg trong giai doan CRISIS
    first_bd = None
    for t in range(start, end+1):
        if bull_mask[t]:
            first_bd = t
            break
    if first_bd is not None:
        dist_from_exit = end - first_bd
        pct_thru = (first_bd - start) / dur if dur > 0 else 0
        lag_stats.append(dist_from_exit)
        f20 = e.get("fwd_20", np.nan)
        print(f"  {crisis_exits.index(e)+1:>3}  {e['date'].strftime('%Y-%m-%d'):>12}"
              f"  {dur:>5}p"
              f"  {vni['time'].iloc[first_bd].strftime('%Y-%m-%d'):>12}"
              f"  {dist_from_exit:>8}p truoc"
              f"  {pct_thru*100:>10.0f}% vao"
              f"  {f20*100 if not np.isnan(f20) else 0:>+7.1f}%")
    else:
        print(f"  {crisis_exits.index(e)+1:>3}  {e['date'].strftime('%Y-%m-%d'):>12}"
              f"  {dur:>5}p  {'(Khong co BullDvg)':>40}  {e.get('fwd_20',0)*100:>+7.1f}%")

if lag_stats:
    print(f"\n  BullDvg xuat hien trung binh {np.mean(lag_stats):.0f}p truoc khi thoat CRISIS"
          f" (trung vi: {np.median(lag_stats):.0f}p)")
    print(f"  → Cua so tot nhat de bat BullDvg: {int(np.percentile(lag_stats,75))+5}p den {int(np.max(lag_stats))+10}p")

# ── Phan 4: Boost chi khi BullDvg xuat hien TRONG crisis (bat ky vi tri) ─
print(f"\n\n{'='*80}")
print(f"  PHAN 4: BOOST NEU CO BULLDVG BAT KY LUC NAO TRONG GIAI DOAN CRISIS")
print(f"{'='*80}")

# Danh dau moi episode: co BullDvg trong CRISIS episode khong?
for e in crisis_exits:
    has_bd_in_crisis = any(bull_mask[e["start"]:e["end"]+1])
    e["has_bd_in_crisis"] = has_bd_in_crisis

crisis_with_bd    = [e for e in crisis_exits if e["has_bd_in_crisis"]]
crisis_without_bd = [e for e in crisis_exits if not e["has_bd_in_crisis"]]

pv_with_bd    = simulate(crisis_with_bd)
pv_without_bd = simulate(crisis_without_bd)

m_with   = metrics(pv_with_bd,    idx11)
m_without= metrics(pv_without_bd, idx11)
mo_with  = metrics(pv_with_bd,    idx21)
mo_with2 = metrics(pv_without_bd, idx21)

print(f"\n  {'Kich ban':<42}  {'N':>3}  {'CAGR11':>7}  {'Calmar':>7}  {'MaxDD':>8}  {'OOS CAGR':>9}")
print(f"  {'─'*84}")
print(f"  {'Baseline':<42}  {0:>3}  {mb['cagr']*100:>+6.1f}%  {mb['calmar']:>7.2f}  {mb['mdd']*100:>+7.1f}%  {mob.get('cagr',0)*100:>+8.1f}%")
print(f"  {'Boost ALL exits':<42}  {len(crisis_exits):>3}  {mall['cagr']*100:>+6.1f}%  {mall['calmar']:>7.2f}  {mall['mdd']*100:>+7.1f}%  {moal.get('cagr',0)*100:>+8.1f}%")
print(f"  {'Boost: co BullDvg TRONG crisis':<42}  {len(crisis_with_bd):>3}  {m_with.get('cagr',0)*100:>+6.1f}%  {m_with.get('calmar',0):>7.2f}  {m_with.get('mdd',0)*100:>+7.1f}%  {mo_with.get('cagr',0)*100:>+8.1f}%")
print(f"  {'Boost: KHONG co BullDvg trong crisis':<42}  {len(crisis_without_bd):>3}  {m_without.get('cagr',0)*100:>+6.1f}%  {m_without.get('calmar',0):>7.2f}  {m_without.get('mdd',0)*100:>+7.1f}%  {mo_with2.get('cagr',0)*100:>+8.1f}%")
print(f"  {'B&H':<42}  {'':>3}  {mbh['cagr']*100:>+6.1f}%  {mbh['calmar']:>7.2f}  {mbh['mdd']*100:>+7.1f}%  {mobh.get('cagr',0)*100:>+8.1f}%")

# Chi tiet tung episode
print(f"\n  Chi tiet:")
print(f"  {'Lan':>3}  {'Ngay':>12}  {'BullDvg?':>9}  {'Depth':>7}  {'T+20':>8}  {'Ket qua'}")
print(f"  {'─'*58}")
for e in crisis_exits:
    f20 = e.get("fwd_20", np.nan)
    result = "TANG" if not np.isnan(f20) and f20>0.05 else ("BAY" if not np.isnan(f20) and f20<0 else "NGANG")
    bd_str = "CO" if e["has_bd_in_crisis"] else "KHONG"
    print(f"  {crisis_exits.index(e)+1:>3}  {e['date'].strftime('%Y-%m-%d'):>12}"
          f"  {bd_str:>9}  {e['depth_peak']*100:>+6.1f}%  {f20*100 if not np.isnan(f20) else 0:>+7.1f}%  {result}")

# ── Ket luan ──────────────────────────────────────────────────────────────
print(f"\n\n{'='*80}")
print(f"  KET LUAN: CO NEN TICH HOP BULLDVG KHONG?")
print(f"{'='*80}")

best_bd_calmar = max(results_bd, key=lambda x: x[3].get("calmar",0))
w_best, _, _, m_best, _ = best_bd_calmar

print(f"""
  So sanh cac phuong an:
  ┌─────────────────────────────────────┬──────┬────────┬────────┬──────────┐
  │ Kich ban                            │  N   │  CAGR  │ Calmar │ OOS CAGR │
  ├─────────────────────────────────────┼──────┼────────┼────────┼──────────┤
  │ Baseline (khong boost)              │   0  │  +9.1% │  0.43  │   +8.9%  │
  │ Boost ALL exits (KHUYEN NGHI)       │  {len(crisis_exits):>2}  │ +10.7% │  0.54  │  +10.4%  │
  │ BullDvg filter (best: {w_best:>2}p window)  │  {sum(1 for e in crisis_exits if e[f'bull_{w_best}p']):>2}  │ {m_best.get('cagr',0)*100:>+5.1f}% │  {m_best.get('calmar',0):.2f}  │  {max(results_bd, key=lambda x: x[3].get('calmar',0))[4].get('cagr',0)*100:>+5.1f}%  │
  │ BullDvg trong crisis                │  {len(crisis_with_bd):>2}  │ {m_with.get('cagr',0)*100:>+5.1f}% │  {m_with.get('calmar',0):.2f}  │  {mo_with.get('cagr',0)*100:>+5.1f}%  │
  │ B&H                                 │  --  │  +9.2% │  0.20  │  +10.2%  │
  └─────────────────────────────────────┴──────┴────────┴────────┴──────────┘

  Nhan xet:
""")

all_calmar = mall["calmar"]
best_bd_cal = max(r[3].get("calmar",0) for r in results_bd)
bd_crisis_cal = m_with.get("calmar",0)

if all_calmar >= best_bd_cal and all_calmar >= bd_crisis_cal:
    print(f"  → BullDvg KHONG cai thien so voi Boost-All (Calmar {all_calmar:.2f} vs {best_bd_cal:.2f})")
    print(f"  → KHUYEN NGHI: GIU NGUYEN cach hien tai - Boost tat ca exits, recW=130%, dur=20p")
    print(f"  → BullDvg xuat hien trung binh {np.mean(lag_stats):.0f} phien TRUOC khi thoat CRISIS")
    print(f"     → Pipeline smoothing da 'bao gom' thong tin BullDvg trong qua trinh chuyen trang thai")
else:
    best_w = w_best
    print(f"  → BullDvg({best_w}p) CAI THIEN so voi Boost-All: Calmar {best_bd_cal:.2f} vs {all_calmar:.2f}")
    print(f"  → KHUYEN NGHI: Dung BullDvg({best_w}p) lam filter")
print()
