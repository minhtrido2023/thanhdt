# -*- coding: utf-8 -*-
"""
So sánh H_System với 4 mức lãi tiền mặt:
  - 6%/năm   : giả định gốc (term deposit)
  - 0.1%/năm : thực tế VN (tiền gửi không kỳ hạn)
  - 0%/năm   : không lãi tiền mặt
  - B&H      : buy and hold benchmark
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
from collections import Counter

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Load & build states (identical to backtest_workflow.py) ───────────────
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
    br = pd.read_csv(WORKDIR+"/data/breadth_data.csv")
    br["time"] = pd.to_datetime(br["time"])
    vni = vni.merge(br, on="time", how="left")
else:
    vni["breadth"] = np.nan

close=vni["Close"].values.copy(); high=vni["High"].values.copy()
low=vni["Low"].values.copy(); vol=vni["Volume"].values.copy(); n=len(close)
cal_days=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY=n/(cal_days/365.25)

def _ema(arr, k):
    out=np.full(len(arr),np.nan)
    for i in range(len(arr)):
        out[i]=arr[i] if (i==0 or np.isnan(out[i-1])) else out[i-1]*(1-k)+arr[i]*k
    return out

def _rank(arr, min_lb=252):
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

gate_active=False; gate_start=-1; gate_flag=np.zeros(n,dtype=int)
st_dvg=st.copy()
for i in range(n):
    if bear_mask[i]: gate_active=True; gate_start=i
    if gate_active:
        gate_flag[i]=1
        if st_dvg[i]>1: st_dvg[i]=1
        if i-gate_start>=60:
            p3_ok=(not np.isnan(p3m_rank[i])) and p3m_rank[i]>0.45
            pe_ok=(not np.isnan(pe_rank[i])) and pe_rank[i]<0.80
            if bull_mask[i] or (p3_ok and pe_ok) or bool(streak[i]):
                gate_active=False

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

# ── Simulation voi deposit_rate tuy chon ─────────────────────────────────
def simulate(deposit_annual):
    DR = deposit_annual / SPY
    BR = 0.10 / SPY
    TC = 0.001
    pv = np.zeros(n); pv[0] = 1e9
    w = TARGET_W[3]
    for t in range(1, n):
        target = TARGET_W[st_smooth[t-1]]
        diff = target - w
        w_new = target if abs(diff) < 0.03 else w + diff/3
        w_new = float(np.clip(w_new, 0.0, 1.30))
        rm = close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t] = pv[t-1] * (1.0 + w_new*rm
                            + max(0.0, 1.0-w_new)*DR
                            - max(0.0, w_new-1.0)*BR
                            - abs(w_new-w)*TC)
        w = w_new
    return pv

pv_6  = simulate(0.06)    # baseline: 6%/nam
pv_01 = simulate(0.001)   # 0.1%/nam - tien gui khong ky han VN (thuc te)
pv_0  = simulate(0.00)    # khong lai tien mat

# B&H benchmark
pv_bh = np.zeros(n); pv_bh[0] = 1e9
for t in range(1,n): pv_bh[t] = pv_bh[t-1]*(close[t]/close[t-1] if close[t-1]>0 else 1.0)

# ── Metrics ───────────────────────────────────────────────────────────────
def metrics(pv_arr, i0=0, i1=None):
    sl = pv_arr[i0:] if i1 is None else pv_arr[i0:i1]
    ds = vni["time"].reset_index(drop=True).iloc[i0:] if i1 is None else vni["time"].reset_index(drop=True).iloc[i0:i1]
    pv_arr2=np.asarray(sl,dtype=float)
    valid=np.where(pv_arr2>0)[0]
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
    under=dd2<0; mx=0; cu=0
    for u in under:
        cu=cu+1 if u else 0; mx=max(mx,cu)
    return {"cagr":cagr,"sharpe":sharpe,"sortino":sortino,"mdd":mdd,"calmar":calmar,"ddur":mx}

dates_all = vni["time"].reset_index(drop=True)
idx11=vni[vni["time"]>="2011-01-01"].index[0]
idx21=vni[vni["time"]>="2021-01-01"].index[0]

# ── Print helpers ─────────────────────────────────────────────────────────
p  = lambda v: f"{v:+.1%}"  if not np.isnan(v) else "N/A"
f2 = lambda v: f"{v:.2f}"   if not np.isnan(v) else "N/A"
fi = lambda v: f"{int(v)}"  if not np.isnan(v) else "N/A"

print()
print("="*78)
print("  SO SANH: 4 KICH BAN LAI TIEN MAT (H_System)")
print("  - HT 6%  : gia dinh goc (term deposit ko thuc te)")
print("  - HT 0.1%: tien gui khong ky han VN (thuc te ~0.1%/nam)")
print("  - HT 0%  : khong co lai tien mat")
print("  - B&H    : buy and hold VNINDEX")
print("="*78)

periods=[
    ("Toan ky (2000-nay)", 0,     None),
    ("Tu 2011",            idx11, None),
    ("OOS (2021-nay)",     idx21, None),
]

for lbl, i0, i1 in periods:
    m6  = metrics(pv_6,  i0, i1)
    m01 = metrics(pv_01, i0, i1)
    m0  = metrics(pv_0,  i0, i1)
    mb  = metrics(pv_bh, i0, i1)
    print(f"\n  {'─'*74}")
    print(f"  {lbl}")
    print(f"  {'─'*74}")
    print(f"  {'Chi so':<18} {'HT 6%':>10} {'HT 0.1%':>10} {'HT 0%':>10} {'B&H':>9}  {'0.1%-6%':>9}")
    print(f"  {'─'*74}")
    rows=[
        ("CAGR",         "cagr",   p,   True),
        ("Sharpe",       "sharpe", f2,  True),
        ("Sortino",      "sortino",f2,  True),
        ("MaxDD",        "mdd",    p,   False),
        ("Calmar",       "calmar", f2,  True),
        ("DDdur(phien)", "ddur",   fi,  False),
    ]
    for name,ks,fmt,hb in rows:
        v6  = m6.get(ks,np.nan)
        v01 = m01.get(ks,np.nan)
        v0  = m0.get(ks,np.nan)
        vb  = mb.get(ks,np.nan)
        if ks=="cagr":   diff=f"{(v01-v6)*100:+.2f}pp"
        elif ks=="mdd":  diff=f"{(v01-v6)*100:+.2f}pp"
        elif ks=="ddur": diff=f"{int(v01-v6):+d}p" if not(np.isnan(v01) or np.isnan(v6)) else "—"
        else:            diff=f"{v01-v6:+.3f}"
        # does HT(0.1%) beat B&H?
        beat01 = ("ok" if (hb and v01>vb) or (not hb and v01<vb) else "  ") if not np.isnan(v01) and not np.isnan(vb) else "  "
        print(f"  {name:<18} {fmt(v6):>10} {fmt(v01):>10} {fmt(v0):>10} {fmt(vb):>9}  {diff:>9}  0.1%>BH:{beat01}")

# ── Phan tich dong gop lai tien mat ──────────────────────────────────────
print(f"\n\n{'='*78}")
print(f"  PHAN TICH: Tien gui khong ky han 0.1%/nam dong gop bao nhieu?")
print(f"{'='*78}")

st11=st_smooth[idx11:]; cnt11=Counter(st11.tolist()); total11=len(st11)
avg_cash=(cnt11[1]*1.00 + cnt11[2]*0.80 + cnt11[3]*0.30) / total11
contrib_6   = avg_cash * 6.0
contrib_01  = avg_cash * 0.1

m6_11  = metrics(pv_6,  idx11)
m01_11 = metrics(pv_01, idx11)
m0_11  = metrics(pv_0,  idx11)
mb_11  = metrics(pv_bh, idx11)

actual_diff_6_to_01 = (m01_11.get("cagr",0) - m0_11.get("cagr",0)) * 100
actual_diff_6_to_0  = (m6_11.get("cagr",0)  - m0_11.get("cagr",0)) * 100

print(f"""
  Phan bo thoi gian tu 2011 ({total11} phien = {total11/SPY:.1f} nam):
  ─────────────────────────────────────────────────────────
  CRISIS  (0%  von => 100% tien mat): {cnt11[1]:5d} phien ({cnt11[1]/total11*100:5.1f}%)
  BEAR    (20% von =>  80% tien mat): {cnt11[2]:5d} phien ({cnt11[2]/total11*100:5.1f}%)
  NEUTRAL (70% von =>  30% tien mat): {cnt11[3]:5d} phien ({cnt11[3]/total11*100:5.1f}%)
  BULL    (100% von =>  0% tien mat): {cnt11[4]:5d} phien ({cnt11[4]/total11*100:5.1f}%)
  EX-BULL (130% von => vay margin):   {cnt11[5]:5d} phien ({cnt11[5]/total11*100:5.1f}%)

  Ty le tien mat binh quan (tu 2011): {avg_cash:.1%}

  Dong gop uoc tinh:
    Tien gui 6%/nam   : {avg_cash:.3f} x 6.0% = {contrib_6:+.3f}pp/nam
    Tien gui 0.1%/nam : {avg_cash:.3f} x 0.1% = {contrib_01:+.4f}pp/nam  (= {contrib_01*10:.4f}pp ~ gan 0)

  CAGR thuc te (tu 2011):
    HT(6%)  - HT(0%) = {actual_diff_6_to_0:+.2f}pp/nam  (kiem tra: ≈ {contrib_6:.2f}pp)
    HT(0.1%)- HT(0%) = {actual_diff_6_to_01:+.3f}pp/nam  (thuc te: ≈ {contrib_01:.4f}pp, can bang voi sai so lam tron)
""")

# ── Annual breakdown ──────────────────────────────────────────────────────
print(f"{'='*78}")
print(f"  ANNUAL BREAKDOWN (tu 2011)")
print(f"{'='*78}")
print(f"  {'Nam':>4} {'HT 6%':>8} {'HT 0.1%':>9} {'HT 0%':>8} {'B&H':>8}  {'0.1%>BH':>7}  {'0%>BH':>6}")
print(f"  {'─'*72}")

for yr in sorted(vni["time"].dt.year.unique()):
    if yr < 2011: continue
    mask=vni["time"].dt.year==yr; idx=vni[mask].index
    if len(idx)<20: continue
    i0,i1=idx[0],idx[-1]
    if pv_6[i0]<=0: continue
    r6  = pv_6[i1]  / pv_6[i0]  - 1
    r01 = pv_01[i1] / pv_01[i0] - 1
    r0  = pv_0[i1]  / pv_0[i0]  - 1
    rb  = pv_bh[i1] / pv_bh[i0] - 1
    b01 = "ok" if r01>rb else "  "
    b0  = "ok" if r0 >rb else "  "
    oos_mark = " <OOS" if yr>=2021 else ""
    print(f"  {yr:>4} {r6:>+8.1%} {r01:>+9.1%} {r0:>+8.1%} {rb:>+8.1%}  {b01:>7}  {b0:>6}{oos_mark}")

# ── Conclusion ────────────────────────────────────────────────────────────
m6_21  = metrics(pv_6,  idx21)
m01_21 = metrics(pv_01, idx21)
m0_21  = metrics(pv_0,  idx21)
mb_21  = metrics(pv_bh, idx21)

print(f"""
{'='*78}
  KET LUAN
{'='*78}

  Tu 2011:
    HT deposit 6%/nam   : CAGR={p(m6_11.get("cagr",np.nan))}  Calmar={f2(m6_11.get("calmar",np.nan))}  MaxDD={p(m6_11.get("mdd",np.nan))}
    HT deposit 0.1%/nam : CAGR={p(m01_11.get("cagr",np.nan))}  Calmar={f2(m01_11.get("calmar",np.nan))}  MaxDD={p(m01_11.get("mdd",np.nan))}
    HT deposit 0%/nam   : CAGR={p(m0_11.get("cagr",np.nan))}  Calmar={f2(m0_11.get("calmar",np.nan))}  MaxDD={p(m0_11.get("mdd",np.nan))}
    B&H                 : CAGR={p(mb_11.get("cagr",np.nan))}  Calmar={f2(mb_11.get("calmar",np.nan))}  MaxDD={p(mb_11.get("mdd",np.nan))}

  OOS (2021-nay):
    HT deposit 6%/nam   : CAGR={p(m6_21.get("cagr",np.nan))}  Calmar={f2(m6_21.get("calmar",np.nan))}  MaxDD={p(m6_21.get("mdd",np.nan))}
    HT deposit 0.1%/nam : CAGR={p(m01_21.get("cagr",np.nan))}  Calmar={f2(m01_21.get("calmar",np.nan))}  MaxDD={p(m01_21.get("mdd",np.nan))}
    HT deposit 0%/nam   : CAGR={p(m0_21.get("cagr",np.nan))}  Calmar={f2(m0_21.get("calmar",np.nan))}  MaxDD={p(m0_21.get("mdd",np.nan))}
    B&H                 : CAGR={p(mb_21.get("cagr",np.nan))}  Calmar={f2(mb_21.get("calmar",np.nan))}  MaxDD={p(mb_21.get("mdd",np.nan))}

  Nhan xet:
    1. Tien gui khong ky han 0.1%/nam dong gop chi ~{contrib_01:.4f}pp/nam (= {avg_cash:.1%} x 0.1%)
       => Gan nhu BANG KHONG, khong anh huong dang ke den ket qua.
    2. HT(0.1%) ≈ HT(0%) — 2 kich ban nay thuc te dong nhat.
    3. Gia dinh 6%/nam la KHONG THUC TE cho tien mat giu linh hoat:
       => Da thoi phong CAGR len {actual_diff_6_to_0:+.2f}pp/nam.
    4. Voi lai suat thuc te (0.1%/nam), HT CAGR tu 2011:
       => {p(m01_11.get("cagr",np.nan))} vs B&H {p(mb_11.get("cagr",np.nan))} — {'TREN' if m01_11.get("cagr",0)>mb_11.get("cagr",0) else 'DUOI'} B&H ve CAGR
       => Calmar {f2(m01_11.get("calmar",np.nan))} vs B&H {f2(mb_11.get("calmar",np.nan))} — {'TOT HON' if m01_11.get("calmar",0)>mb_11.get("calmar",0) else 'THUA'} ve Calmar
       => MaxDD {p(m01_11.get("mdd",np.nan))} vs B&H {p(mb_11.get("mdd",np.nan))} — bao ve von tot hon nhieu
    5. GIA TRI THAT SU cua he thong: quan ly rui ro, khong phai alpha tuyet doi.
       MaxDD {p(m01_11.get("mdd",np.nan))} vs B&H {p(mb_11.get("mdd",np.nan))} = bao ve rui ro tot hon {abs(m01_11.get("mdd",0)-mb_11.get("mdd",0))*100:.1f}pp.
""")
