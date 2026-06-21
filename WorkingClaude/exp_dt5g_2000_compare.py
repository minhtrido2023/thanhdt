# -*- coding: utf-8 -*-
"""
exp_dt5g_2000_compare.py — research-only (NO deploy).
Compare full-history (2000-now) DT5G with LIGHT DT-gate (dt_5_15_15) vs CANONICAL
(dt_10_25_25), each WITH the full macro overlay + breadth gate. Macro signal depends
only on price/US/SBV (not the DT base) so it is computed once and applied to both.
DT base = asym_dir_commit applied to the v3.4b full_history base (covers 2000+).
Reuses the exact macro_signal / build_weight / simulate / metrics logic from
sim_dt4g_macro_overlay.py (the canonical DT5G backtest). Sanity: canonical run must
≈ docstring figure (DT5G nav_macro ~20.13%, 2000-now).
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
from sbv_macro_overlay import SBV_REFI_EVENTS

STATE_ALLOC = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
TC, TAX, BORROW, INIT = 0.001, 0.001, 0.10, 1_000_000_000
NEUTRAL, CRISIS, BEAR, EXBULL = 3, 1, 2, 5
RF = 0.001
VGB_1Y = {2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,
          2008:.14,2009:.09,2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,
          2016:.05,2017:.045,2018:.04,2019:.036,2020:.025,2021:.012,2022:.035,2023:.025,
          2024:.02,2025:.025,2026:.027}
US_REFI_LAG = 5
T_DOM_MILD, T_DOM_STRONG, T_DOM_EXTREME = 0.5, 1.5, 3.0
REFI_CUT_FROM_PEAK = 0.5
BREADTH_FILE = r"/home/trido/thanhdt/WorkingClaude/data/preprocess_others_market_indicators_all_tickers.csv"
BREADTH_TH, BREADTH_MIN_UNIVERSE = 0.50, 100
CAP_COMMIT = 7

DT_VARIANTS = {
    "CANON dt_10_25_25": dict(default=10, enter_crisis=25, exit_crisis=10, enter_exbull=25, exit_exbull=10),
    "LIGHT dt_5_15_15":  dict(default=5,  enter_crisis=15, exit_crisis=5,  enter_exbull=15, exit_exbull=5),
}

def asym_dir_commit(states, default, enter_crisis, exit_crisis, enter_exbull, exit_exbull):
    states = np.asarray(states, dtype=int); out = states.copy()
    committed = states[0]; ps, pr = states[0], 1
    for t in range(1, len(states)):
        s = states[t]
        if s == ps: pr += 1
        else: ps, pr = s, 1
        if ps == committed: out[t] = committed; continue
        if ps == CRISIS:   need = enter_crisis
        elif ps == EXBULL: need = enter_exbull
        elif committed == CRISIS: need = exit_crisis
        elif committed == EXBULL: need = exit_exbull
        else: need = default
        if pr >= need: committed = ps
        out[t] = committed
    return out

# ───── 1. data (price/US/SBV — NO dt_4gate join; we build the DT base ourselves) ─────
print("[1] VNINDEX price + MA200/RSI (BQ); v3.4b base (2000+ CSV); US; SBV...")
px = bq("""SELECT p.time, p.Close, p.MA200, p.D_RSI FROM tav2_bq.ticker AS p
WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"] = pd.to_datetime(px["time"]); px = px.dropna(subset=["Close"]).sort_values("time").reset_index(drop=True)
base = pd.read_csv("data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
base["time"] = pd.to_datetime(base["time"])
px = px.merge(base[["time", "state"]].rename(columns={"state": "base_state"}), on="time", how="inner")
px = px.dropna(subset=["base_state"]).reset_index(drop=True); px["base_state"] = px["base_state"].astype(int)

us = pd.read_csv("data/us_market_history.csv", parse_dates=["time"]).sort_values("time")
key = px[["time"]].copy(); key["jt"] = key["time"] - pd.Timedelta(days=1)
um = pd.merge_asof(key.sort_values("jt"), us.rename(columns={"time": "us_time"}),
                   left_on="jt", right_on="us_time", direction="backward").sort_values("time").reset_index(drop=True)
px = px.merge(um[["time", "vix", "spx_dd_1y", "vix_ma252"]], on="time", how="left")
ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"]); ev["time"] = pd.to_datetime(ev["time"])
dr = pd.DataFrame({"time": pd.date_range(px["time"].min(), px["time"].max(), freq="D")}).merge(ev, on="time", how="left")
dr["refi"] = dr["refi"].ffill().bfill()
px = px.merge(dr, on="time", how="left"); px["refi"] = px["refi"].ffill().bfill()
px["refi_chg6m"] = (px["refi"] - px["refi"].shift(126)).shift(US_REFI_LAG)
px["refi_peak6m"] = px["refi"].rolling(126, min_periods=20).max()
px["refi_cut"] = ((px["refi_peak6m"] - px["refi"]) >= REFI_CUT_FROM_PEAK).shift(US_REFI_LAG).fillna(False)
px["vni_r6m"] = px["Close"] / px["Close"].shift(126) - 1
px["bull"] = ((px["vni_r6m"] > 0.15) & (px["Close"] > px["MA200"])).shift(1).fillna(False)
px["us_decoupled"] = False
try:
    bd = pd.read_csv(BREADTH_FILE); bd["time"] = pd.to_datetime(bd["time"])
    bd = bd[["time", "Breadth_MA200", "Breadth_Total_MA200"]].sort_values("time")
    px = pd.merge_asof(px.sort_values("time"), bd, on="time", direction="backward").sort_values("time").reset_index(drop=True)
    px["us_decoupled"] = ((px["Breadth_Total_MA200"].fillna(0) >= BREADTH_MIN_UNIVERSE)
                          & (px["Breadth_MA200"] >= BREADTH_TH)).shift(1).fillna(False)
except Exception as e:
    print(f"  [breadth guard inactive: {e} -> fail-safe no-suppress]")
print(f"  {len(px):,} rows {px['time'].iloc[0].date()}->{px['time'].iloc[-1].date()}  bull {int(px['bull'].sum())}  decoup {int(px['us_decoupled'].sum())}")

# ───── 2. macro signal (computed ONCE; independent of DT base) ─────
def macro_signal(d):
    n = len(d); vix=d["vix"].values; sdd=d["spx_dd_1y"].values; vixma=d["vix_ma252"].values
    rc6=d["refi_chg6m"].values; cut=d["refi_cut"].values.astype(bool)
    bull=d["bull"].values.astype(bool); decoup=d["us_decoupled"].values.astype(bool)
    cap=np.full(n,9); easing=np.zeros(n,bool)
    for t in range(n):
        v,dd,vm,rr = vix[t],sdd[t],vixma[t],rc6[t]
        if bull[t] or decoup[t]: us_crisis=us_bear=us_mild=False
        else:
            us_crisis=(not np.isnan(dd) and dd<-0.25) or (not np.isnan(v) and v>35)
            us_bear  =(not np.isnan(dd) and dd<-0.15) and (not np.isnan(v) and v>25)
            us_mild  =(not np.isnan(dd) and dd<-0.10) and (not np.isnan(v) and v>20)
        dom_ext=(not np.isnan(rr) and rr>=T_DOM_EXTREME); dom_str=(not np.isnan(rr) and rr>=T_DOM_STRONG)
        dom_mild=(not np.isnan(rr) and rr>=T_DOM_MILD)
        if us_crisis or dom_ext: cap[t]=CRISIS
        elif us_bear or dom_str: cap[t]=BEAR
        elif us_mild or dom_mild: cap[t]=NEUTRAL
        us_calm=(not np.isnan(v) and not np.isnan(vm) and v<vm) and (not np.isnan(dd) and dd>-0.05)
        if cap[t]==9 and cut[t] and us_calm: easing[t]=True
    close=d["Close"].values; persist=np.zeros(n,int)
    for t in range(n): persist[t]=persist[t-1]+1 if (t>0 and easing[t]) else (1 if easing[t] else 0)
    price_up=np.zeros(n,bool); price_up[10:]=close[10:]>close[:-10]
    easing_conf=easing & (persist>=10) & price_up
    return cap, easing_conf

def _commit_cap(arr,K):
    if K<=1: return arr.copy()
    out=arr.copy(); c=arr[0]; ps,pr=arr[0],1
    for t in range(1,len(arr)):
        if arr[t]==ps: pr+=1
        else: ps,pr=arr[t],1
        if pr>=K: c=ps
        out[t]=c
    return out

cap, easing_conf = macro_signal(px); cap = _commit_cap(cap, CAP_COMMIT)
print(f"[2] macro: cap-CRISIS {int((cap==CRISIS).sum())}d cap-BEAR {int((cap==BEAR).sum())}d cap-NEUTRAL {int((cap==NEUTRAL).sum())}d easing-conf {int(easing_conf.sum())}d")

def build_weight(d, trend=True, confirm=10):
    n=len(d); st=d["state"].values.astype(int); close=d["Close"].values; ma200=d["MA200"].values; rsi=d["D_RSI"].values
    w=np.array([STATE_ALLOC[s] for s in st],float)
    if trend:
        up_raw=(close>ma200)&(~np.isnan(ma200))&(np.nan_to_num(rsi,nan=0.0)<=0.72)
        up=np.zeros(n,bool); curf=False; ru=rd=0
        for t in range(n):
            if up_raw[t]: ru+=1; rd=0
            else: rd+=1; ru=0
            if not curf and ru>=confirm: curf=True
            elif curf and rd>=confirm: curf=False
            up[t]=curf
        w[(st==NEUTRAL)&up]=0.90
    return w

def simulate(d, use_macro=False, easing_mode="off", dep_by_year=VGB_1Y):
    n=len(d); close=d["Close"].values; r=np.zeros(n); r[1:]=close[1:]/close[:-1]-1
    yrs=(d["time"].iloc[-1]-d["time"].iloc[0]).days/365.25; spy=n/yrs
    tgt=build_weight(d)
    if use_macro:
        ceil=np.where(cap==9,1.30,np.array([STATE_ALLOC.get(c,1.30) for c in cap]))
        tgt=np.minimum(tgt,ceil)
        ez={"confirmed":easing_conf,"off":np.zeros(n,bool)}[easing_mode]
        tgt=np.where(ez&(tgt<0.70),0.70,tgt)
    tgt_lag=np.concatenate([[0.0],tgt[:-1]])
    dep_arr=np.array([dep_by_year.get(int(y),0.001) for y in d["time"].dt.year.values])
    nav=np.empty(n); nav[0]=INIT; drr=np.zeros(n); held=tgt_lag
    for t in range(n):
        w=held[t]; wp=held[t-1] if t>0 else 0.0
        c_frac=max(0.0,1-w); l_frac=max(0.0,w-1); buy=max(0.0,w-wp); sell=max(0.0,wp-w)
        drr[t]=w*r[t]+c_frac*dep_arr[t]/spy-l_frac*BORROW/spy-(buy+sell)*TC-sell*TAX
        if t>0: nav[t]=nav[t-1]*(1+drr[t])
    out=d[["time","Close","state"]].copy(); out["w"]=held; out["nav"]=nav; out["ret"]=drr
    return out, spy

def metrics(nav,time,ret,spy):
    nav=np.asarray(nav,float); time=pd.DatetimeIndex(time)
    yrs=(time[-1]-time[0]).days/365.25; cagr=(nav[-1]/nav[0])**(1/yrs)-1
    ex=np.asarray(ret)-RF/spy; sh=ex.mean()/ex.std()*np.sqrt(spy) if ex.std()>0 else 0
    rmax=np.maximum.accumulate(nav); mdd=((nav-rmax)/rmax).min()
    return dict(cagr=cagr,sharpe=sh,mdd=mdd,calmar=cagr/-mdd if mdd<0 else 0,final=nav[-1])

def sub(out,spy,a,b):
    seg=out[(out["time"]>=a)&(out["time"]<=b)].reset_index(drop=True)
    if len(seg)<20: return None
    nv=INIT*seg["nav"].values/seg["nav"].values[0]
    return metrics(nv,seg["time"],seg["ret"].values,spy)

PERIODS={"FULL 2000-now":(px["time"].min(),px["time"].max()),
         "Pre-2014":(pd.Timestamp("2000-01-01"),pd.Timestamp("2013-12-31")),
         "Modern 2014-now":(pd.Timestamp("2014-01-01"),px["time"].max()),
         "2007-08 GFC":(pd.Timestamp("2007-01-01"),pd.Timestamp("2009-03-31")),
         "2011 inflation":(pd.Timestamp("2011-01-01"),pd.Timestamp("2012-06-30")),
         "COVID 2020":(pd.Timestamp("2020-01-01"),pd.Timestamp("2020-12-31")),
         "2022 hikes":(pd.Timestamp("2022-01-01"),pd.Timestamp("2022-12-31"))}

results={}
for vname,p in DT_VARIANTS.items():
    px["state"]=asym_dir_commit(px["base_state"].values, **p)
    ntr=int((px["state"].values[1:]!=px["state"].values[:-1]).sum())
    _, spy = simulate(px, use_macro=False)
    mac,_ = simulate(px, use_macro=True, easing_mode="confirmed")  # DT5G = macro+confirmed easing
    results[vname]={"trans":ntr, "spy":spy, "periods":{nm:sub(mac,spy,a,b) for nm,(a,b) in PERIODS.items()}}

print("\n"+"="*104)
print("DT5G full-history (2000-now, macro overlay + breadth gate) — LIGHT vs CANONICAL DT-gate")
print("="*104)
for nm in PERIODS:
    print(f"\n--- {nm} ---")
    print(f"  {'variant':20s}{'CAGR':>9s}{'Sharpe':>8s}{'MaxDD':>9s}{'Calmar':>8s}{'FinalNAV':>12s}")
    for vname in DT_VARIANTS:
        m=results[vname]["periods"][nm]
        if m: print(f"  {vname:20s}{m['cagr']*100:8.2f}%{m['sharpe']:8.2f}{m['mdd']*100:8.1f}%{m['calmar']:8.2f}{m['final']/1e9:11.2f}B")
print("\n#transitions (DT base, full):  " + "  ".join(f"{v}={results[v]['trans']}" for v in DT_VARIANTS))
print("DONE.")
