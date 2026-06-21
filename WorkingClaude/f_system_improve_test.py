# -*- coding: utf-8 -*-
"""
f_system_improve_test.py
========================
Thi nghiem cai tien F-system overlay. Reuse pipeline cua f_system_backtest.py
(Co Dien VNINDEX state) lam BASELINE, roi test cac don bay:
  L1  DT5G state source  (production regime, it whipsaw)  thay Co Dien VNINDEX
  L2  Signal-on-VN30      (regime tinh tren VN30 thay vi VNINDEX)  -- de sau
  L3  Short-only hedge    (CRISIS-100/BEAR-30, con lai FLAT) = co lap gia tri rieng cua futures
  L4  Asymmetric no-lev-long (cap long +100, bo +150 EX-BULL leveraged)
Underlying = VN30 (scale ve VNINDEX o ngay dau co VN30), TC=0.03%, roll=1.2%/yr.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
vni = pd.read_csv(WORKDIR + "/VNINDEX.csv", low_memory=False)
vni["time"] = pd.to_datetime(vni["time"]); vni = vni.sort_values("time").reset_index(drop=True)
for c in ["Open","High","Low","Close","Volume","VNINDEX_PE","D_RSI","D_RSI_T1W","D_RSI_Max1W",
          "D_RSI_Max3M","D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close","D_RSI_Max3M_Close",
          "D_RSI_Max3M_MACD","D_RSI_Max1W_MACD","D_RSI_Min1W_Close","D_RSI_MinT3","D_MACDdiff",
          "D_CMF","C_L1M","C_L1W","VN30"]:
    if c in vni.columns: vni[c] = pd.to_numeric(vni[c], errors="coerce")
if "breadth" not in vni.columns: vni["breadth"] = np.nan

vn30_raw = vni["VN30"].values; vnidx = vni["Close"].values.copy()
s_idx = np.where(~np.isnan(vn30_raw))[0]
s = s_idx[0]; scale = vnidx[s]/vn30_raw[s]
underlying = vnidx.copy()
for i in range(s, len(vni)):
    if not np.isnan(vn30_raw[i]): underlying[i] = vn30_raw[i]*scale
close=vni["Close"].values.copy(); high=vni["High"].values.copy()
low=vni["Low"].values.copy(); vol=vni["Volume"].values.copy(); n=len(close)
cal=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days; SPY=n/(cal/365.25)

# ---- Co Dien VNINDEX pipeline (identical to f_system_backtest.py) ----
def _ema(a,k):
    o=np.full(len(a),np.nan)
    for i in range(len(a)): o[i]=a[i] if (i==0 or np.isnan(o[i-1])) else o[i-1]*(1-k)+a[i]*k
    return o
def _rank(a,mlb=252):
    o=np.full(len(a),np.nan)
    for t in range(len(a)):
        if np.isnan(a[t]): continue
        v=a[:t+1]; v=v[~np.isnan(v)]
        if len(v)>=mlb: o[t]=np.sum(v<=a[t])/len(v)
    return o
p3m=np.full(n,np.nan); p1m=np.full(n,np.nan)
for i in range(60,n):
    if close[i-60]>0: p3m[i]=close[i]/close[i-60]-1
for i in range(20,n):
    if close[i-20]>0: p1m[i]=close[i]/close[i-20]-1
ma200=pd.Series(close).rolling(200,min_periods=200).mean().values
ma200d=np.where((ma200>0)&~np.isnan(ma200),close/ma200-1,np.nan)
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
e12=_ema(close,2/13); e26=_ema(close,2/27); macd_l=e12-e26; sig9=_ema(macd_l,2/10)
macd_h=np.where(np.arange(n)>=33,macd_l-sig9,np.nan)
hl=high-low; mfm=np.where(hl>0,((close-low)-(high-close))/hl,0.0)
cmf=np.full(n,np.nan)
for i in range(14,n):
    vs=np.sum(vol[i-14:i])
    if vs>0: cmf[i]=np.sum(mfm[i-14:i]*vol[i-14:i])/vs
W={"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
raw={"P3M":p3m,"P1M":p1m,"MA200":ma200d,"RSI":rsi,"MACD":macd_h,"CMF":cmf,"Breadth":vni["breadth"].values}
ranks={k:_rank(v) for k,v in raw.items()}
score=np.full(n,np.nan)
for t in range(n):
    av={k:ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(av)>=3:
        ws=sum(W[k] for k in av); score[t]=sum(av[k]*W[k] for k in av)/ws
r_score=_rank(score); r_ema=np.full(n,np.nan)
for t in range(n):
    v=r_score[t]; p=r_ema[t-1] if t>0 else np.nan
    r_ema[t]=v if np.isnan(p) else (p if np.isnan(v) else 0.40*v+0.60*p)
pe=vni["VNINDEX_PE"].values.copy(); pe90=np.full(n,np.nan)
for t in range(n):
    h=pe[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: pe90[t]=np.nanpercentile(h,90)
rmc=np.maximum.accumulate(np.where(np.isnan(close),0,close)); ddr=np.where(rmc>0,close/rmc-1,0.0)
dr=np.full(n,np.nan)
for i in range(1,n):
    if close[i-1]>0: dr[i]=close[i]/close[i-1]-1
v20=np.full(n,np.nan)
for i in range(20,n):
    w2=dr[i-20:i]; w2=w2[~np.isnan(w2)]
    if len(w2)>=15: v20[i]=np.std(w2)*np.sqrt(SPY)
av20=np.full(n,np.nan)
for t in range(n):
    h=v20[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: av20[t]=np.mean(h)
def classify(rs):
    if np.isnan(rs): return 3
    return 1 if rs<0.10 else 2 if rs<0.20 else 3 if rs<0.70 else 4 if rs<0.90 else 5
st=np.array([classify(r) for r in r_ema])
for i in range(n):
    sc=st[i]
    if not np.isnan(pe90[i]) and not np.isnan(pe[i]) and pe[i]>pe90[i] and sc==5: sc=4
    if ddr[i]<-0.25 and sc>=4: sc=3
    if not np.isnan(av20[i]) and not np.isnan(v20[i]) and v20[i]>1.5*av20[i] and sc==5: sc=4
    st[i]=sc
def _s(c): return vni[c] if c in vni.columns else pd.Series(np.nan,index=vni.index)
_mask=vni["time"]>="2011-01-01"
_DR=_s("D_RSI");_DRT=_s("D_RSI_T1W");_DM1W=_s("D_RSI_Max1W");_DM3M=_s("D_RSI_Max3M")
_DN1W=_s("D_RSI_Min1W");_DN3M=_s("D_RSI_Min3M");_DM1WC=_s("D_RSI_Max1W_Close")
_DM3MC=_s("D_RSI_Max3M_Close");_DM3MM=_s("D_RSI_Max3M_MACD");_DM1WM=_s("D_RSI_Max1W_MACD")
_DN1WC=_s("D_RSI_Min1W_Close");_DMT3=_s("D_RSI_MinT3");_DMACD=_s("D_MACDdiff")
_DCMF=_s("D_CMF");_CL1M=_s("C_L1M");_CL1W=_s("C_L1W")
bear_mask=(((_DM1W/_DR>1.044)&(_DM3M>0.74)&(_DM1W<0.72)&(_DM1W>0.61)&(_DM1WC/_DM3MC>1.028)&
  (_DM3MM/_DM1WM>1.11)&(_DMACD<0)&(vni["Close"]/_DM3MC>0.96)&(_DMT3>0.43)&(_DCMF<0.13)&_mask)
 |((_DM1W/_DR>1.016)&(_DM3M>0.77)&(_DM1W<0.79)&(_DM1W>0.60)&(_DM1WC/_DM3MC>1.008)&
  (_DM3MM/_DM1WM>1.10)&(_DMACD<0)&(vni["Close"]/_DM3MC>0.97)&(_DMT3>0.50)&(_DCMF<0.15)&_mask)).values.astype(bool)
bull_mask=(((_DN1W/_DN3M>0.90)&(_DN1W<0.60)&(_DN3M<0.40)&(_DN1WC/_DM3MC<1.15)&(_DMACD>0)&
  (_DMT3<0.50)&(_DM1W<0.48)&(_DR/_DRT>1.12)&(_DCMF>0)&(_CL1M<1.21)&(_CL1W<1.05)&_mask)
 |((_DN1W/_DN3M>0.92)&(_DN1W<0.52)&(_DN3M<0.38)&(_DN1WC/_DM3MC<1.10)&(_DMACD>0)&
  (_DMT3<0.56)&(_DM1W<0.64)&(_DR/_DRT>1.10)&(_DCMF>0)&(_CL1M<1.20)&(_CL1W<1.025)&_mask)).values.astype(bool)
pe_rank=np.full(n,np.nan)
for t in range(n):
    if np.isnan(pe[t]): continue
    h=pe[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: pe_rank[t]=np.sum(h<=pe[t])/len(h)
p3m_rank=ranks["P3M"]; streak=np.zeros(n,bool); _k=0
for i in range(n):
    if not np.isnan(r_ema[i]) and r_ema[i]>0.65: _k+=1
    else: _k=0
    if _k>=10: streak[i]=True
ga=False; gs=-1; st_dvg=st.copy()
for i in range(n):
    if bear_mask[i]: ga=True; gs=i
    if ga:
        if st_dvg[i]>1: st_dvg[i]=1
        if i-gs>=60:
            p3_ok=(not np.isnan(p3m_rank[i])) and p3m_rank[i]>0.45
            pe_ok=(not np.isnan(pe_rank[i])) and pe_rank[i]<0.80
            if bull_mask[i] or (p3_ok and pe_ok) or bool(streak[i]): ga=False
def rmode(s_,w=15):
    o=s_.copy()
    for t in range(w-1,len(s_)):
        ww=s_[t-w+1:t+1]; vs,cs=np.unique(ww,return_counts=True); cands=vs[cs==cs.max()]
        for v in reversed(ww):
            if v in cands: o[t]=v; break
    return o
def msf(s_,m=7):
    o=s_.copy(); ch=True
    while ch:
        ch=False; i=0
        while i<len(o):
            j=i+1
            while j<len(o) and o[j]==o[i]: j+=1
            if j-i<m:
                fill=o[i-1] if i>0 else (o[j] if j<len(o) else o[i]); o[i:j]=fill; ch=True
            i=j
    return o
st_codien = msf(rmode(st_dvg,15),7)   # BASELINE Co Dien state

# ---- DT5G live state (merge by time) ----
dt=pd.read_csv(WORKDIR+"/vnindex_5state_dt5g_live.csv"); dt["time"]=pd.to_datetime(dt["time"])
mp=dict(zip(dt["time"],dt["state"]))
st_dt5g=np.array([int(mp.get(t, 0)) for t in vni["time"]])  # 0 = no DT5G data (pre-2014)

# ---- Underlyings: SPOT (VN30 index, scaled) vs FUTURES (VN30F1M actual) ----
ret_spot=np.full(n,np.nan)
for t in range(1,n):
    if underlying[t-1]>0: ret_spot[t]=underlying[t]/underlying[t-1]-1
# VN30F1M actual close-to-close return (roll embedded in continuous series)
f1=pd.read_csv(WORKDIR+"/vn30f1m_raw.csv"); f1["time"]=pd.to_datetime(f1["time"])
fmap=dict(zip(f1["time"],f1["close"]))
f1c=np.array([fmap.get(t, np.nan) for t in vni["time"]])
ret_fut=np.full(n,np.nan)
for t in range(1,n):
    if not np.isnan(f1c[t]) and not np.isnan(f1c[t-1]) and f1c[t-1]>0:
        ret_fut[t]=f1c[t]/f1c[t-1]-1

# ---- Simulator (generic on a return array; no artificial roll for FUT) ----
TC_F=0.0003; ROLL_SPOT=0.012
def sim(pos_map, st_arr, ret_arr, roll=0.0):
    RC=roll/SPY; pv=np.zeros(n); pv[0]=1e9; pos=0.0; tr=0
    for t in range(1,n):
        s_=int(st_arr[t-1])
        target = pos_map.get(s_, pos) if s_ in pos_map else 0.0
        if s_==0: target=0.0
        diff=target-pos; pos_new=target
        if abs(diff)>0.01: tr+=1
        rm=ret_arr[t] if not np.isnan(ret_arr[t]) else 0.0
        pv[t]=pv[t-1]*(1.0+pos_new*rm-abs(diff)*TC_F-abs(pos_new)*RC)
        pos=pos_new
    return pv,tr
pv_bh=np.zeros(n); pv_bh[0]=1e9
for t in range(1,n):
    r=ret_fut[t] if not np.isnan(ret_fut[t]) else (ret_spot[t] if not np.isnan(ret_spot[t]) else 0.0)
    pv_bh[t]=pv_bh[t-1]*(1.0+r)

# Position maps
M_LIVE  = {1:-1.00,2:-0.20,3:0.70,4:1.00,5:1.30}   # F_HAdapted (live)
M_SHORT = {1:-1.00,2:-0.30,3:0.00,4:0.00,5:0.00}   # short-only hedge
M_ASYM  = {1:-1.00,2:-0.20,3:0.70,4:1.00,5:1.00}   # no leveraged long (cap +100)
M_ASYM2 = {1:-1.00,2:-0.30,3:0.50,4:1.00,5:1.00}   # asym + deeper bear short + lighter neutral

VARIANTS = [
    ("LIVE  / CoDien  (baseline)", M_LIVE,  st_codien),
    ("LIVE  / DT5G",               M_LIVE,  st_dt5g),
    ("SHORT-only / CoDien",        M_SHORT, st_codien),
    ("SHORT-only / DT5G",          M_SHORT, st_dt5g),
    ("ASYM  / CoDien",             M_ASYM,  st_codien),
    ("ASYM  / DT5G",               M_ASYM,  st_dt5g),
    ("ASYM2 / DT5G",               M_ASYM2, st_dt5g),
]

def metrics(pv,i0,i1=None):
    sl=pv[i0:] if i1 is None else pv[i0:i1]
    ds=vni["time"].iloc[i0:] if i1 is None else vni["time"].iloc[i0:i1]
    a=np.asarray(sl,float); v=np.where(a>0)[0]
    if len(v)<10: return {}
    a0,a1=v[0],v[-1]; ds2=ds.reset_index(drop=True)
    yrs=(ds2.iloc[a1]-ds2.iloc[a0]).days/365.25
    if yrs<=0: return {}
    sub=a[a0:a1+1]; cagr=(sub[-1]/sub[0])**(1/yrs)-1
    rets=np.diff(sub)/sub[:-1]; sp=len(rets)/yrs
    mr=np.mean(rets); sr=np.std(rets)
    sh=mr*sp/(sr*np.sqrt(sp)) if sr>0 else 0
    rm=np.maximum.accumulate(sub); dd=np.where(rm>0,sub/rm-1,0); mdd=dd.min()
    cal=cagr/abs(mdd) if mdd!=0 else 0
    return {"cagr":cagr,"sharpe":sh,"mdd":mdd,"calmar":cal,"final":sub[-1]/1e9}

# VN30F starts 2017-08, DT5G 2014. Compare on VN30F-era windows only.
i18=vni[vni["time"]>="2018-01-01"].index[0]
i21=vni[vni["time"]>="2021-01-01"].index[0]
PER=[("2018+",i18),("OOS 2021+",i21)]

for ulabel, ret_arr, rollc in [("SPOT (VN30 index proxy + 1.2%/yr roll)", ret_spot, ROLL_SPOT),
                                ("FUTURES (VN30F1M actual, roll embedded)", ret_fut, 0.0)]:
    print("\n"+"="*104)
    print(f"  F-SYSTEM RE-VALIDATION — underlying = {ulabel}")
    print("="*104)
    sims={name:sim(m,s,ret_arr,roll=rollc) for name,m,s in VARIANTS}
    for plabel,i0 in PER:
        print(f"\n  [{plabel}]")
        print(f"  {'Variant':<30}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}{'Trades':>8}")
        print("  "+"-"*80)
        for name,m,s_ in VARIANTS:
            pv,tr=sims[name]; mm=metrics(pv,i0)
            if not mm: continue
            print(f"  {name:<30}{mm['cagr']*100:>+7.1f}%{mm['sharpe']:>8.2f}{mm['mdd']*100:>+8.1f}%"
                  f"{mm['calmar']:>8.2f}{tr:>8d}")
        mb=metrics(pv_bh,i0)
        print(f"  {'B&H (VN30F1M)':<30}{mb['cagr']*100:>+7.1f}%{mb['sharpe']:>8.2f}{mb['mdd']*100:>+8.1f}%"
              f"{mb['calmar']:>8.2f}{0:>8d}")
print("\nDone.")
