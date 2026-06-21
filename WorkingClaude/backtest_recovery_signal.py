# -*- coding: utf-8 -*-
"""
Tim tin hieu phan biet "phuc hoi that" vs "bay" khi thoat CRISIS.
Test: P3M momentum + BullDvg pattern + combinations.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
from itertools import product

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Rebuild states (identical to other scripts) ────────────────────────────
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
avg_vol=np.full(n,np.nan)
for t in range(n):
    h=v20_arr[:t+1]; h=h[~np.isnan(h)]
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
    if not np.isnan(avg_vol[i]) and not np.isnan(v20_arr[i]) and v20_arr[i]>1.5*avg_vol[i] and s==5: s=4
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

# ── Precompute BullDvg rolling window signals ─────────────────────────────
# bull_recent_5: co BullDvg trong 5 phien truoc va tai diem exit
# bull_recent_20: co BullDvg trong 20 phien truoc va tai diem exit
bull_recent_5  = np.zeros(n, dtype=bool)
bull_recent_20 = np.zeros(n, dtype=bool)
for i in range(n):
    bull_recent_5[i]  = np.any(bull_mask[max(0,i-4):i+1])
    bull_recent_20[i] = np.any(bull_mask[max(0,i-19):i+1])

# P3M improving: p3m tang so voi 10 phien truoc
p3m_delta10 = np.full(n, np.nan)
for i in range(10, n):
    if not np.isnan(p3m[i]) and not np.isnan(p3m[i-10]):
        p3m_delta10[i] = p3m[i] - p3m[i-10]

# RSI improving
rsi_delta10 = np.full(n, np.nan)
for i in range(10, n):
    if not np.isnan(rsi[i]) and not np.isnan(rsi[i-10]):
        rsi_delta10[i] = rsi[i] - rsi[i-10]

# ── Tim tat ca CRISIS exits ────────────────────────────────────────────────
crisis_exits = []
i = 0
while i < n-1:
    if st_smooth[i] == 1:
        start = i
        while i < n-1 and st_smooth[i] == 1:
            i += 1
        end = i
        dur = end - start
        if dur < 2 or end >= n-1: i+=1; continue
        # Dac trung tai diem exit
        seg = close[start:end]
        daily_rets = np.diff(seg)/seg[:-1] if len(seg)>1 else np.array([0.0])
        bot_offset = np.argmin(seg)
        bot_idx = start + bot_offset
        gain_from_bot = close[end]/close[bot_idx]-1 if close[bot_idx]>0 else 0.0
        ep = {
            "start": start, "end": end, "dur": dur,
            "depth_peak": dd_raw[end],
            "speed": (close[end]/close[start]-1)/dur if dur>0 else 0,
            "date": vni["time"].iloc[end],
            # === TIN HIEU TAI DIEM EXIT ===
            # P3M
            "p3m_val":       p3m[end] if not np.isnan(p3m[end]) else 0.0,
            "p3m_rank_val":  p3m_rank[end] if not np.isnan(p3m_rank[end]) else 0.0,
            "p3m_delta10":   p3m_delta10[end] if not np.isnan(p3m_delta10[end]) else 0.0,
            "p3m_positive":  p3m[end] > 0 if not np.isnan(p3m[end]) else False,
            "p3m_rank_30":   p3m_rank[end] > 0.30 if not np.isnan(p3m_rank[end]) else False,
            "p3m_rank_40":   p3m_rank[end] > 0.40 if not np.isnan(p3m_rank[end]) else False,
            "p3m_improving": p3m_delta10[end] > 0 if not np.isnan(p3m_delta10[end]) else False,
            # BullDvg
            "bull_exact":    bool(bull_mask[end]),
            "bull_5p":       bool(bull_recent_5[end]),
            "bull_20p":      bool(bull_recent_20[end]),
            # RSI
            "rsi_val":       rsi[end] if not np.isnan(rsi[end]) else 0.5,
            "rsi_improving": rsi_delta10[end] > 0 if not np.isnan(rsi_delta10[end]) else False,
            # Composite
            "r_ema_val":     r_ema[end] if not np.isnan(r_ema[end]) else 0.0,
            "r_ema_rising":  (r_ema[end]>r_ema[end-5]) if end>=5 and not np.isnan(r_ema[end]) and not np.isnan(r_ema[end-5]) else False,
            # Recovery da xay ra
            "gain_from_bot": gain_from_bot,
        }
        # Forward returns
        for h in [10, 20, 40, 60]:
            ep[f"fwd_{h}"] = close[end+h]/close[end]-1 if end+h < n and close[end]>0 else np.nan
        crisis_exits.append(ep)
    else:
        i += 1

print()
print("="*82)
print("  PHAN TICH TIN HIEU TAI DIEM THOAT CRISIS:")
print("  P3M momentum + BullDvg pattern → phan biet phuc hoi that vs bay")
print("="*82)

# ── Phan 1: Hien thi tin hieu tai moi exit ────────────────────────────────
print(f"\n  {'Lan':>3}  {'Ngay':>12}  {'P3M':>7}  {'P3Mrk':>7}  {'P3Mdlt':>7}  {'BullDvg':>8}  {'BullDvg':>8}  {'rEMA':>6}  {'T+20':>7}  {'T+60':>7}  Ket qua")
print(f"  {'':>3}  {'':>12}  {'(val)':>7}  {'(rank)':>7}  {'(10p)':>7}  {'(5p win)':>8}  {'(20p win)':>9}  {'':>6}  {'':>7}  {'':>7}")
print(f"  {'─'*100}")
for e in crisis_exits:
    good = "?" if np.isnan(e.get("fwd_20",np.nan)) else ("TANG" if e["fwd_20"]>0.05 else ("NGANG" if e["fwd_20"]>0 else "BAY"))
    bd5  = "Y" if e["bull_5p"] else "-"
    bd20 = "Y" if e["bull_20p"] else "-"
    print(f"  {crisis_exits.index(e)+1:>3}  {e['date'].strftime('%Y-%m-%d'):>12}"
          f"  {e['p3m_val']*100:>+6.1f}%"
          f"  {e['p3m_rank_val']:.2f}   "
          f"  {e['p3m_delta10']*100:>+6.2f}%"
          f"  {bd5:>8}  {bd20:>9}"
          f"  {e['r_ema_val']:.3f}"
          f"  {e.get('fwd_20',np.nan)*100:>+6.1f}%"
          f"  {e.get('fwd_60',np.nan)*100:>+6.1f}%"
          f"  {good}")

# ── Phan 2: Phan tich tung tin hieu ──────────────────────────────────────
print(f"\n\n{'='*82}")
print(f"  PHAN 2: TUNG TIN HIEU → T+20 FORWARD RETURN")
print(f"{'='*82}")

def compare_signal(signal_key, label, exits=crisis_exits):
    yes = [e for e in exits if e.get(signal_key, False) and not np.isnan(e.get("fwd_20",np.nan))]
    no  = [e for e in exits if not e.get(signal_key, False) and not np.isnan(e.get("fwd_20",np.nan))]
    def stats(lst):
        v = [e["fwd_20"] for e in lst]
        if not v: return "N/A", "N/A", "N/A", 0
        return f"{np.mean(v)*100:+.1f}%", f"{np.median(v)*100:+.1f}%", f"{sum(1 for x in v if x>0)/len(v)*100:.0f}%", len(v)
    ym,ymd,yp,yn = stats(yes)
    nm,nmd,np_,nn = stats(no)
    print(f"  {label:<30}  YES(N={yn}): TB={ym} Med={ymd} Pos={yp}  |  NO(N={nn}): TB={nm} Med={nmd} Pos={np_}")

print()
compare_signal("p3m_positive",   "P3M > 0  (momentum duong)")
compare_signal("p3m_rank_30",    "P3M rank > 0.30")
compare_signal("p3m_rank_40",    "P3M rank > 0.40")
compare_signal("p3m_improving",  "P3M tang trong 10p qua")
compare_signal("bull_exact",     "BullDvg chinh xac hom nay")
compare_signal("bull_5p",        "BullDvg trong 5p gan nhat")
compare_signal("bull_20p",       "BullDvg trong 20p gan nhat")
compare_signal("rsi_improving",  "RSI dang tang trong 10p")
compare_signal("r_ema_rising",   "r_ema dang tang trong 5p")

# Combinations
print(f"\n  --- Ket hop ---")
for e in crisis_exits:
    e["combo_p3m_bull5"]   = e["p3m_rank_30"] and e["bull_5p"]
    e["combo_p3m_bull20"]  = e["p3m_rank_30"] and e["bull_20p"]
    e["combo_p3m_or_bull"] = e["p3m_rank_30"] or  e["bull_20p"]
    e["combo_p3m_rema"]    = e["p3m_rank_30"] and e["r_ema_rising"]
    e["combo_all3"]        = e["p3m_rank_30"] and e["bull_20p"] and e["r_ema_rising"]

compare_signal("combo_p3m_bull5",   "P3M>30% AND BullDvg(5p)")
compare_signal("combo_p3m_bull20",  "P3M>30% AND BullDvg(20p)")
compare_signal("combo_p3m_or_bull", "P3M>30% OR  BullDvg(20p)")
compare_signal("combo_p3m_rema",    "P3M>30% AND r_ema rising")
compare_signal("combo_all3",        "P3M>30% AND BullDvg(20p) AND r_ema↑")

# ── Phan 3: Chi tiet - signal nao dung/sai trong tung truong hop ──────────
print(f"\n\n{'='*82}")
print(f"  PHAN 3: CHI TIET - P3M rank + BullDvg(20p) voi tung exit")
print(f"{'='*82}")
print(f"\n  {'Lan':>3}  {'Ngay':>12}  {'P3Mrk':>6}  {'Bul20':>5}  {'OR':>4}  {'AND':>4}  {'T+20':>8}  {'T+60':>8}  {'OR dung?':>9}  {'AND dung?':>10}")
print(f"  {'─'*85}")
for e in crisis_exits:
    f20 = e.get("fwd_20", np.nan)
    f60 = e.get("fwd_60", np.nan)
    or_sig  = e["combo_p3m_or_bull"]
    and_sig = e["combo_p3m_bull20"]
    good20 = f20 > 0.03 if not np.isnan(f20) else None  # "phuc hoi that" = T+20 > 3%
    or_correct  = ("ok" if (or_sig  and good20) or (not or_sig  and not good20) else "MISS") if good20 is not None else "?"
    and_correct = ("ok" if (and_sig and good20) or (not and_sig and not good20) else "MISS") if good20 is not None else "?"
    print(f"  {crisis_exits.index(e)+1:>3}  {e['date'].strftime('%Y-%m-%d'):>12}"
          f"  {e['p3m_rank_val']:.2f}  "
          f"  {'Y' if e['bull_20p'] else '-':>5}"
          f"  {'Y' if or_sig else '-':>4}"
          f"  {'Y' if and_sig else '-':>4}"
          f"  {f20*100 if not np.isnan(f20) else 0:>+7.1f}%"
          f"  {f60*100 if not np.isnan(f60) else 0:>+7.1f}%"
          f"  {or_correct:>9}  {and_correct:>10}")

# ── Phan 4: Backtest so sanh cac filter ──────────────────────────────────
print(f"\n\n{'='*82}")
print(f"  PHAN 4: BACKTEST RECOVERY BOOST voi FILTER TIN HIEU")
print(f"  RecW = 130%, Dur = 20 phien  (best params tu grid search truoc)")
print(f"{'='*82}")

REC_WEIGHT = 1.30
REC_DUR    = 20

def build_rmap_filtered(exits_filtered):
    """Chi kich hoat recovery cho nhung episode da loc."""
    rmap = {}
    for ep in exits_filtered:
        exit_idx = ep["end"]
        for t in range(exit_idx, min(exit_idx + REC_DUR, n)):
            if st_smooth[t] != 1:
                rmap[t] = REC_WEIGHT
    return rmap

def simulate_rmap(rmap, dep=0.001):
    DR=dep/SPY; BR=0.10/SPY; TC=0.001
    pv=np.zeros(n); pv[0]=1e9; w=TARGET_W[3]
    for t in range(1,n):
        base = TARGET_W[st_smooth[t-1]]
        target = max(base, rmap[t-1]) if (t-1) in rmap else base
        diff=target-w
        w_new=target if abs(diff)<0.03 else w+diff/3
        w_new=float(np.clip(w_new,0.0,1.50))
        rm=close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t]=pv[t-1]*(1.0+w_new*rm+max(0.0,1.0-w_new)*DR-max(0.0,w_new-1.0)*BR-abs(w_new-w)*TC)
        w=w_new
    return pv

def metrics(pv_arr,i0=0,i1=None):
    sl=pv_arr[i0:] if i1 is None else pv_arr[i0:i1]
    ds=vni["time"].reset_index(drop=True).iloc[i0:] if i1 is None else vni["time"].reset_index(drop=True).iloc[i0:i1]
    pv2=np.asarray(sl,dtype=float); valid=np.where(pv2>0)[0]
    if len(valid)<10: return {}
    i0_,i1_=valid[0],valid[-1]; v0,v1=pv2[i0_],pv2[i1_]
    ds2=ds.reset_index(drop=True)
    yrs=(ds2.iloc[i1_]-ds2.iloc[i0_]).days/365.25
    if yrs<=0: return {}
    cagr=(v1/v0)**(1/yrs)-1
    sub=pv2[i0_:i1_+1]; rets=np.diff(sub)/sub[:-1]
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

# B&H
pv_bh=np.zeros(n); pv_bh[0]=1e9
for t in range(1,n): pv_bh[t]=pv_bh[t-1]*(close[t]/close[t-1] if close[t-1]>0 else 1.0)

# Baseline (no boost)
pv_base=simulate_rmap({})
mb=metrics(pv_base,idx11); mb_bh=metrics(pv_bh,idx11)

# Cac kich ban filter
scenarios = [
    ("Baseline (khong boost)",       []),
    ("Boost tat ca exits (no filter)",crisis_exits),
    ("Filter: P3M > 0",              [e for e in crisis_exits if e["p3m_positive"]]),
    ("Filter: P3M rank > 0.30",      [e for e in crisis_exits if e["p3m_rank_30"]]),
    ("Filter: P3M rank > 0.40",      [e for e in crisis_exits if e["p3m_rank_40"]]),
    ("Filter: BullDvg(5p)",          [e for e in crisis_exits if e["bull_5p"]]),
    ("Filter: BullDvg(20p)",         [e for e in crisis_exits if e["bull_20p"]]),
    ("Filter: P3M>30% OR BullDvg20", [e for e in crisis_exits if e["combo_p3m_or_bull"]]),
    ("Filter: P3M>30% AND BullDvg20",[e for e in crisis_exits if e["combo_p3m_bull20"]]),
    ("Filter: P3M>30% AND rEMA up",  [e for e in crisis_exits if e["combo_p3m_rema"]]),
    ("Filter: All 3 (P3M+BDvg+rEMA)",[e for e in crisis_exits if e["combo_all3"]]),
    ("Filter: BullDvg20 OR rEMA up", [e for e in crisis_exits if e["bull_20p"] or e["r_ema_rising"]]),
]

print(f"\n  {'Kich ban':<38}  {'N':>3}  {'CAGR11':>7}  {'Calmar':>7}  {'MaxDD':>8}  {'Sharpe':>7}  {'CAGR OOS':>9}")
print(f"  {'─'*90}")
results_bt = []
for lbl, exits_f in scenarios:
    rmap = {} if lbl.startswith("Baseline") else build_rmap_filtered(exits_f)
    pv = simulate_rmap(rmap)
    m11 = metrics(pv, idx11)
    m21 = metrics(pv, idx21)
    n_ep = len(exits_f)
    results_bt.append((lbl, n_ep, m11, m21, pv))
    print(f"  {lbl:<38}  {n_ep:>3}  {m11.get('cagr',0)*100:>+6.1f}%  {m11.get('calmar',0):>7.2f}"
          f"  {m11.get('mdd',0)*100:>+7.1f}%  {m11.get('sharpe',0):>7.2f}"
          f"  {m21.get('cagr',0)*100:>+6.1f}%")

# B&H
print(f"  {'B&H':<38}  {'':>3}  {mb_bh.get('cagr',0)*100:>+6.1f}%  {mb_bh.get('calmar',0):>7.2f}"
      f"  {mb_bh.get('mdd',0)*100:>+7.1f}%  {mb_bh.get('sharpe',0):>7.2f}"
      f"  {metrics(pv_bh,idx21).get('cagr',0)*100:>+6.1f}%")

# ── Phan 5: Chi tiet best filtered scenario ───────────────────────────────
# Tim best theo Calmar
best_bt = max(results_bt[1:], key=lambda x: x[2].get("calmar",0))
lbl_best, n_best, m11_best, m21_best, pv_best = best_bt

print(f"\n\n{'='*82}")
print(f"  PHAN 5: ANNUAL BREAKDOWN - Best Filter: [{lbl_best}]")
print(f"{'='*82}")
print(f"  {'Nam':>4}  {'Baseline':>9}  {'BestFilter':>11}  {'B&H':>8}  {'Diff':>8}  {'Beat B&H':>9}")
print(f"  {'─'*65}")
for yr in sorted(vni["time"].dt.year.unique()):
    if yr < 2011: continue
    mask=vni["time"].dt.year==yr; idx=vni[mask].index
    if len(idx)<20: continue
    i0,i1=idx[0],idx[-1]
    if pv_base[i0]<=0: continue
    rb  = pv_base[i1]/pv_base[i0]-1
    rbst= pv_best[i1]/pv_best[i0]-1
    rbh = pv_bh[i1]/pv_bh[i0]-1
    diff= rbst - rb
    beat= "ok" if rbst > rbh else "  "
    oos = " <OOS" if yr>=2021 else ""
    print(f"  {yr:>4}  {rb:>+8.1%}  {rbst:>+10.1%}  {rbh:>+7.1%}  {diff*100:>+7.2f}pp  {beat:>9}{oos}")

print(f"\n  Summary:")
print(f"  Baseline     : CAGR={mb.get('cagr',0)*100:+.1f}%  Calmar={mb.get('calmar',0):.2f}  MaxDD={mb.get('mdd',0)*100:+.1f}%")
print(f"  [{lbl_best}]: CAGR={m11_best.get('cagr',0)*100:+.1f}%  Calmar={m11_best.get('calmar',0):.2f}  MaxDD={m11_best.get('mdd',0)*100:+.1f}%  (N episodes={n_best})")
print(f"  B&H          : CAGR={mb_bh.get('cagr',0)*100:+.1f}%  Calmar={mb_bh.get('calmar',0):.2f}  MaxDD={mb_bh.get('mdd',0)*100:+.1f}%")
print()

# ── Phan 6: Phan tich chinh xac cua tung filter ──────────────────────────
print(f"\n{'='*82}")
print(f"  PHAN 6: DO CHINH XAC CUA TIN HIEU (threshold T+20 > 3% = 'phuc hoi that')")
print(f"{'='*82}\n")
print(f"  {'Tin hieu':<35}  {'N':>3}  {'Prec':>6}  {'Recall':>7}  {'F1':>6}  {'TB T+20 khi Y':>14}  {'TB T+20 khi N':>14}")
print(f"  {'─'*90}")

all_exits_valid = [e for e in crisis_exits if not np.isnan(e.get("fwd_20",np.nan))]
true_pos_set = {i for i,e in enumerate(all_exits_valid) if e["fwd_20"] > 0.03}

def precision_recall(signal_key):
    y_pred = [e.get(signal_key, False) for e in all_exits_valid]
    y_true = [e["fwd_20"] > 0.03 for e in all_exits_valid]
    tp = sum(1 for p,t in zip(y_pred,y_true) if p and t)
    fp = sum(1 for p,t in zip(y_pred,y_true) if p and not t)
    fn = sum(1 for p,t in zip(y_pred,y_true) if not p and t)
    prec   = tp/(tp+fp) if (tp+fp)>0 else 0
    recall = tp/(tp+fn) if (tp+fn)>0 else 0
    f1     = 2*prec*recall/(prec+recall) if (prec+recall)>0 else 0
    yes_ret = np.mean([e["fwd_20"] for e in all_exits_valid if e.get(signal_key,False)])
    no_ret  = np.mean([e["fwd_20"] for e in all_exits_valid if not e.get(signal_key,False)])
    n_yes = sum(y_pred)
    return prec, recall, f1, n_yes, yes_ret, no_ret

signals_to_eval = [
    ("p3m_positive",      "P3M > 0"),
    ("p3m_rank_30",       "P3M rank > 0.30"),
    ("p3m_rank_40",       "P3M rank > 0.40"),
    ("p3m_improving",     "P3M improving (10p)"),
    ("bull_5p",           "BullDvg (5p window)"),
    ("bull_20p",          "BullDvg (20p window)"),
    ("r_ema_rising",      "r_ema rising (5p)"),
    ("combo_p3m_or_bull", "P3M>30% OR BullDvg20"),
    ("combo_p3m_bull20",  "P3M>30% AND BullDvg20"),
    ("combo_all3",        "All 3 (P3M+BDvg+rEMA)"),
]
for key, lbl in signals_to_eval:
    pr, rc, f1, ny, yr_mean, no_mean = precision_recall(key)
    print(f"  {lbl:<35}  {ny:>3}  {pr*100:>5.0f}%  {rc*100:>6.0f}%  {f1:.2f}  {yr_mean*100:>+13.1f}%  {no_mean*100:>+13.1f}%")

print(f"\n  Base rate: {len(true_pos_set)}/{len(all_exits_valid)} exits co T+20>3% = {len(true_pos_set)/len(all_exits_valid)*100:.0f}%")
print(f"\n  Precision = khi signal=Y, bao nhieu % la phuc hoi that (T+20>3%)")
print(f"  Recall    = bao nhieu % phuc hoi that duoc signal bat duoc")
print(f"  F1        = trung hoa precision va recall (cao = tot toan dien)")
print()
