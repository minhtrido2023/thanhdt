# -*- coding: utf-8 -*-
"""Research-only (NO deploy). Test the ASYMMETRY principle: keep defensive CAP (de-risk),
but DISABLE the monetary easing FLOOR (re-risk only via the price-based DT base).
DT base fixed = canonical DT_10_25_25. Macro overlay identical except easing_mode.
Reuses sim_dt4g_macro_overlay logic. Compares full-history + crisis windows + 2012."""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
from sbv_macro_overlay import SBV_REFI_EVENTS

STATE_ALLOC = {1:0.00,2:0.20,3:0.70,4:1.00,5:1.30}
TC,TAX,BORROW,INIT = 0.001,0.001,0.10,1_000_000_000
NEUTRAL,CRISIS,BEAR,EXBULL = 3,1,2,5; RF=0.001
VGB_1Y={2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,2008:.14,2009:.09,
        2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,2016:.05,2017:.045,2018:.04,2019:.036,
        2020:.025,2021:.012,2022:.035,2023:.025,2024:.02,2025:.025,2026:.027}
US_REFI_LAG=5; T_DOM_MILD,T_DOM_STRONG,T_DOM_EXTREME=0.5,1.5,3.0; REFI_CUT_FROM_PEAK=0.5
BREADTH_FILE=r"/home/trido/thanhdt/WorkingClaude/data/preprocess_others_market_indicators_all_tickers.csv"
BREADTH_TH,BREADTH_MIN_UNIVERSE=0.50,100; CAP_COMMIT=7
DT=dict(default=10,enter_crisis=25,exit_crisis=10,enter_exbull=25,exit_exbull=10)

def asym(states,default,enter_crisis,exit_crisis,enter_exbull,exit_exbull):
    states=np.asarray(states,int); out=states.copy(); committed=states[0]; ps,pr=states[0],1
    for t in range(1,len(states)):
        s=states[t]
        if s==ps: pr+=1
        else: ps,pr=s,1
        if ps==committed: out[t]=committed; continue
        need=enter_crisis if ps==CRISIS else enter_exbull if ps==EXBULL else exit_crisis if committed==CRISIS else exit_exbull if committed==EXBULL else default
        if pr>=need: committed=ps
        out[t]=committed
    return out

px=bq("""SELECT p.time,p.Close,p.MA200,p.D_RSI FROM tav2_bq.ticker AS p WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"]=pd.to_datetime(px["time"]); px=px.dropna(subset=["Close"]).sort_values("time").reset_index(drop=True)
base=pd.read_csv("data/vnindex_5state_tam_quan_v3_4b_full_history.csv"); base["time"]=pd.to_datetime(base["time"])
px=px.merge(base[["time","state"]].rename(columns={"state":"base_state"}),on="time",how="inner").dropna(subset=["base_state"]).reset_index(drop=True)
px["base_state"]=px["base_state"].astype(int)
us=pd.read_csv("data/us_market_history.csv",parse_dates=["time"]).sort_values("time")
key=px[["time"]].copy(); key["jt"]=key["time"]-pd.Timedelta(days=1)
um=pd.merge_asof(key.sort_values("jt"),us.rename(columns={"time":"us_time"}),left_on="jt",right_on="us_time",direction="backward").sort_values("time").reset_index(drop=True)
px=px.merge(um[["time","vix","spx_dd_1y","vix_ma252"]],on="time",how="left")
ev=pd.DataFrame(SBV_REFI_EVENTS,columns=["time","refi"]); ev["time"]=pd.to_datetime(ev["time"])
dr=pd.DataFrame({"time":pd.date_range(px["time"].min(),px["time"].max(),freq="D")}).merge(ev,on="time",how="left"); dr["refi"]=dr["refi"].ffill().bfill()
px=px.merge(dr,on="time",how="left"); px["refi"]=px["refi"].ffill().bfill()
px["refi_chg6m"]=(px["refi"]-px["refi"].shift(126)).shift(US_REFI_LAG)
px["refi_peak6m"]=px["refi"].rolling(126,min_periods=20).max()
px["refi_cut"]=((px["refi_peak6m"]-px["refi"])>=REFI_CUT_FROM_PEAK).shift(US_REFI_LAG).fillna(False)
px["vni_r6m"]=px["Close"]/px["Close"].shift(126)-1
px["bull"]=((px["vni_r6m"]>0.15)&(px["Close"]>px["MA200"])).shift(1).fillna(False)
px["us_decoupled"]=False
try:
    bd=pd.read_csv(BREADTH_FILE); bd["time"]=pd.to_datetime(bd["time"]); bd=bd[["time","Breadth_MA200","Breadth_Total_MA200"]].sort_values("time")
    px=pd.merge_asof(px.sort_values("time"),bd,on="time",direction="backward").sort_values("time").reset_index(drop=True)
    px["us_decoupled"]=((px["Breadth_Total_MA200"].fillna(0)>=BREADTH_MIN_UNIVERSE)&(px["Breadth_MA200"]>=BREADTH_TH)).shift(1).fillna(False)
except Exception as e: print(f"  [breadth guard inactive: {e}]")

def macro_signal(d):
    n=len(d); vix=d["vix"].values; sdd=d["spx_dd_1y"].values; vixma=d["vix_ma252"].values
    rc6=d["refi_chg6m"].values; cut=d["refi_cut"].values.astype(bool); bull=d["bull"].values.astype(bool); decoup=d["us_decoupled"].values.astype(bool)
    cap=np.full(n,9); easing=np.zeros(n,bool)
    for t in range(n):
        v,dd,vm,rr=vix[t],sdd[t],vixma[t],rc6[t]
        if bull[t] or decoup[t]: uc=ub=um_=False
        else:
            uc=(not np.isnan(dd) and dd<-0.25) or (not np.isnan(v) and v>35); ub=(not np.isnan(dd) and dd<-0.15) and (not np.isnan(v) and v>25); um_=(not np.isnan(dd) and dd<-0.10) and (not np.isnan(v) and v>20)
        de=(not np.isnan(rr) and rr>=T_DOM_EXTREME); ds=(not np.isnan(rr) and rr>=T_DOM_STRONG); dm=(not np.isnan(rr) and rr>=T_DOM_MILD)
        if uc or de: cap[t]=CRISIS
        elif ub or ds: cap[t]=BEAR
        elif um_ or dm: cap[t]=NEUTRAL
        calm=(not np.isnan(v) and not np.isnan(vm) and v<vm) and (not np.isnan(dd) and dd>-0.05)
        if cap[t]==9 and cut[t] and calm: easing[t]=True
    close=d["Close"].values; persist=np.zeros(n,int)
    for t in range(n): persist[t]=persist[t-1]+1 if (t>0 and easing[t]) else (1 if easing[t] else 0)
    pu=np.zeros(n,bool); pu[10:]=close[10:]>close[:-10]; ezc=easing&(persist>=10)&pu
    return cap,easing,ezc
def commit(arr,K):
    out=arr.copy(); c=arr[0]; ps,pr=arr[0],1
    for t in range(1,len(arr)):
        if arr[t]==ps: pr+=1
        else: ps,pr=arr[t],1
        if pr>=K: c=ps
        out[t]=c
    return out
px["state"]=asym(px["base_state"].values,**DT)
cap,easing,ezc=macro_signal(px); cap=commit(cap,CAP_COMMIT)

def build_weight(d):
    n=len(d); st=d["state"].values.astype(int); close=d["Close"].values; ma200=d["MA200"].values; rsi=d["D_RSI"].values
    w=np.array([STATE_ALLOC[s] for s in st],float)
    up_raw=(close>ma200)&(~np.isnan(ma200))&(np.nan_to_num(rsi,nan=0.0)<=0.72); up=np.zeros(n,bool); cf=False; ru=rd=0
    for t in range(n):
        if up_raw[t]: ru+=1; rd=0
        else: rd+=1; ru=0
        if not cf and ru>=10: cf=True
        elif cf and rd>=10: cf=False
        up[t]=cf
    w[(st==NEUTRAL)&up]=0.90; return w
def simulate(d,easing_mode):
    n=len(d); close=d["Close"].values; r=np.zeros(n); r[1:]=close[1:]/close[:-1]-1
    yrs=(d["time"].iloc[-1]-d["time"].iloc[0]).days/365.25; spy=n/yrs; tgt=build_weight(d)
    ceil=np.where(cap==9,1.30,np.array([STATE_ALLOC.get(c,1.30) for c in cap])); tgt=np.minimum(tgt,ceil)
    ez={"confirmed":ezc,"raw":easing,"off":np.zeros(n,bool)}[easing_mode]
    tgt=np.where(ez&(tgt<0.70),0.70,tgt)
    tl=np.concatenate([[0.0],tgt[:-1]]); dep=np.array([VGB_1Y.get(int(y),0.001) for y in d["time"].dt.year.values])
    nav=np.empty(n); nav[0]=INIT; drr=np.zeros(n); held=tl
    for t in range(n):
        w=held[t]; wp=held[t-1] if t>0 else 0.0; cfr=max(0,1-w); lfr=max(0,w-1); buy=max(0,w-wp); sell=max(0,wp-w)
        drr[t]=w*r[t]+cfr*dep[t]/spy-lfr*BORROW/spy-(buy+sell)*TC-sell*TAX
        if t>0: nav[t]=nav[t-1]*(1+drr[t])
    o=d[["time"]].copy(); o["nav"]=nav; o["ret"]=drr; o["w"]=held; return o,spy
def met(nav,time,ret,spy):
    nav=np.asarray(nav,float); time=pd.DatetimeIndex(time); yrs=(time[-1]-time[0]).days/365.25; cagr=(nav[-1]/nav[0])**(1/yrs)-1
    ex=np.asarray(ret)-RF/spy; sh=ex.mean()/ex.std()*np.sqrt(spy) if ex.std()>0 else 0
    rmax=np.maximum.accumulate(nav); mdd=((nav-rmax)/rmax).min(); return dict(cagr=cagr,sharpe=sh,mdd=mdd,calmar=cagr/-mdd if mdd<0 else 0,fin=nav[-1])
def sub(o,spy,a,b):
    s=o[(o["time"]>=a)&(o["time"]<=b)].reset_index(drop=True)
    if len(s)<20: return None
    return met(INIT*s["nav"].values/s["nav"].values[0],s["time"],s["ret"].values,spy)

PERIODS={"FULL 2000-now":(px["time"].min(),px["time"].max()),"Pre-2014":(pd.Timestamp("2000-01-01"),pd.Timestamp("2013-12-31")),
         "Modern 2014-now":(pd.Timestamp("2014-01-01"),px["time"].max()),"2011-13 (easing era)":(pd.Timestamp("2011-01-01"),pd.Timestamp("2013-12-31")),
         "2012 only":(pd.Timestamp("2012-01-01"),pd.Timestamp("2012-12-31"))}
MODES=["confirmed (PROD)","off (asym)","raw"]
res={}
for mode in MODES:
    em={"confirmed (PROD)":"confirmed","off (asym)":"off","raw":"raw"}[mode]
    o,spy=simulate(px,em); res[mode]={"o":o,"spy":spy,"p":{nm:sub(o,spy,a,b) for nm,(a,b) in PERIODS.items()}}
# count floor-active days (easing pushed weight up)
print(f"easing-confirmed days={int(ezc.sum())}  easing-raw days={int(easing.sum())}")
print("\n"+"="*96); print("DISABLE EASING FLOOR (asymmetry: keep CAP, drop monetary re-risk) — DT_10_25_25 + macro"); print("="*96)
for nm in PERIODS:
    print(f"\n--- {nm} ---"); print(f"  {'easing mode':20s}{'CAGR':>9s}{'Sharpe':>8s}{'MaxDD':>9s}{'Calmar':>8s}{'FinalNAV':>11s}")
    for mode in MODES:
        m=res[mode]["p"][nm]
        if m: print(f"  {mode:20s}{m['cagr']*100:8.2f}%{m['sharpe']:8.2f}{m['mdd']*100:8.1f}%{m['calmar']:8.2f}{m['fin']/1e9:10.2f}B")
print("\nDONE.")
