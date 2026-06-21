# -*- coding: utf-8 -*-
"""
export_dt5g_transitions.py
==========================
Exports the CANONICAL DT5G (with breadth gate) state series 2000->now for dev to
re-simulate and reconcile. Uses the EXACT canonical code-path
(= sim_dt4g_macro_overlay.py: BQ VNINDEX + vnindex_5state_dt_4gate + macro fusion +
breadth gate + cap-commit K=7 + confirmed easing + weight-ceiling NAV).

Writes (to data/ AND into the deploy package for hand-off):
  dt5g_transitions.csv     — one row per STATE transition (date, from->to, driver, ...)
  dt5g_daily_reference.csv — per-day reference (state, weight, NAV, all inputs) for
                             row-by-row reconciliation (this is what localizes the 1% gap)

Headline numbers printed must match canonical: nav_base 19.17% / nav_macro 20.13% /
~113B (2000-now, 1B). If a dev rebuild differs, run reconcile_dt5g.py against the daily ref.
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
from sbv_macro_overlay import SBV_REFI_EVENTS

STATE_ALLOC = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
SNAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
TC, TAX, BORROW, INIT = 0.001, 0.001, 0.10, 1_000_000_000
NEUTRAL, CRISIS, BEAR = 3, 1, 2
US_REFI_LAG = 5; T_DOM_MILD, T_DOM_STRONG, T_DOM_EXTREME = 0.5, 1.5, 3.0
REFI_CUT_FROM_PEAK = 0.5; CAP_COMMIT = 7
VGB_1Y = {2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,
          2008:.14,2009:.09,2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,
          2016:.05,2017:.045,2018:.04,2019:.036,2020:.025,2021:.012,2022:.035,2023:.025,
          2024:.02,2025:.025,2026:.027}
# breadth now from BQ ticker_prune (see below) to match live engine; Downloads CSV deprecated
BREADTH_TH, BREADTH_MIN_UNIVERSE = 0.50, 100

# ── data (identical to canonical) ──
px = bq("""SELECT p.time, p.Close, p.MA200, p.D_RSI, s.state FROM tav2_bq.ticker AS p
JOIN tav2_bq.vnindex_5state_dt_4gate AS s ON s.time=p.time
WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"] = pd.to_datetime(px["time"]); px["state"] = px["state"].astype(int)
px = px.dropna(subset=["Close", "state"]).sort_values("time").reset_index(drop=True)
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
    # breadth = % of ticker_prune above MA200, computed from BQ — IDENTICAL to the live engine
    # macro_state_live.get_macro_state (was: a local Downloads CSV; switched 2026-06-02 to match live).
    bd = bq(f"""SELECT t.time, AVG(IF(t.Close>t.MA200,1.0,0.0)) AS Breadth_MA200,
       COUNT(*) AS Breadth_Total_MA200
FROM tav2_bq.ticker AS t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.MA200 IS NOT NULL AND t.time BETWEEN DATE '2014-01-01' AND DATE '{px["time"].max().date()}'
GROUP BY t.time ORDER BY t.time""")
    bd["time"] = pd.to_datetime(bd["time"])
    px = px.merge(bd, on="time", how="left")   # exact-date join (matches live engine)
    px["us_decoupled"] = ((px["Breadth_Total_MA200"].fillna(0) >= BREADTH_MIN_UNIVERSE)
                          & (px["Breadth_MA200"] >= BREADTH_TH)).shift(1).fillna(False)
except Exception as e:
    print(f"[breadth guard inactive: {e}]")
n = len(px)

# ── macro fusion (canonical + gate) ──
vix=px["vix"].values; sdd=px["spx_dd_1y"].values; vixma=px["vix_ma252"].values
rc6=px["refi_chg6m"].values; cut=px["refi_cut"].values.astype(bool)
bull=px["bull"].values.astype(bool); decoup=px["us_decoupled"].values.astype(bool)
cap=np.full(n,9); easing=np.zeros(n,bool); src=np.array([""]*n,dtype=object)
for t in range(n):
    v,dd,vm,rr=vix[t],sdd[t],vixma[t],rc6[t]
    if bull[t] or decoup[t]:
        uc=ub=umn=False
    else:
        uc=(not np.isnan(dd) and dd<-0.25) or (not np.isnan(v) and v>35)
        ub=(not np.isnan(dd) and dd<-0.15) and (not np.isnan(v) and v>25)
        umn=(not np.isnan(dd) and dd<-0.10) and (not np.isnan(v) and v>20)
    de=(not np.isnan(rr) and rr>=T_DOM_EXTREME); ds=(not np.isnan(rr) and rr>=T_DOM_STRONG); dm=(not np.isnan(rr) and rr>=T_DOM_MILD)
    if uc or de: cap[t]=CRISIS; src[t]="US-crisis" if uc else "SBV-tighten-extreme"
    elif ub or ds: cap[t]=BEAR; src[t]="US-bear" if ub else "SBV-tighten-strong"
    elif umn or dm: cap[t]=NEUTRAL; src[t]="US-mild" if umn else "SBV-tighten-mild"
    calm=(not np.isnan(v) and not np.isnan(vm) and v<vm) and (not np.isnan(dd) and dd>-0.05)
    if cap[t]==9 and cut[t] and calm: easing[t]=True; src[t]="SBV-cut+US-calm"
close=px["Close"].values; persist=np.zeros(n,int)
for t in range(n): persist[t]=persist[t-1]+1 if (t>0 and easing[t]) else (1 if easing[t] else 0)
price_up=np.zeros(n,bool); price_up[10:]=close[10:]>close[:-10]
easing_conf=easing & (persist>=10) & price_up
# commit cap K=7
def _commit(arr,K):
    out=arr.copy(); c=arr[0]; ps,pr=arr[0],1
    for t in range(1,len(arr)):
        if arr[t]==ps: pr+=1
        else: ps,pr=arr[t],1
        if pr>=K: c=ps
        out[t]=c
    return out
cap=_commit(cap,CAP_COMMIT)

# ── macro-adjusted STATE (published series) + weight + NAV ──
st=px["state"].values.astype(int)
sm=np.where(cap!=9,np.minimum(st,cap),st)
sm=np.where((cap==9)&easing_conf&(sm<NEUTRAL),NEUTRAL,sm).astype(int)
# weight (canonical build_weight: trend overlay, NEUTRAL->0.90 in confirmed uptrend) then macro ceiling/floor
ma200=px["MA200"].values; rsi=px["D_RSI"].values
w=np.array([STATE_ALLOC[s] for s in st],float)
up_raw=(close>ma200)&(~np.isnan(ma200))&(np.nan_to_num(rsi,nan=0.0)<=0.72)
up=np.zeros(n,bool); cf=False; ru=rd=0
for t in range(n):
    if up_raw[t]: ru+=1; rd=0
    else: rd+=1; ru=0
    if not cf and ru>=10: cf=True
    elif cf and rd>=10: cf=False
    up[t]=cf
w[(st==NEUTRAL)&up]=0.90
ceil=np.where(cap==9,1.30,np.array([STATE_ALLOC.get(c,1.30) for c in cap]))
w=np.minimum(w,ceil); w=np.where(easing_conf&(w<0.70),0.70,w)
# NAV (canonical: T+1 weight, time-var deposit, borrow, TC, tax)
r=np.zeros(n); r[1:]=close[1:]/close[:-1]-1
spy=n/((px["time"].iloc[-1]-px["time"].iloc[0]).days/365.25)
wl=np.concatenate([[0.0],w[:-1]]); ya=px["time"].dt.year.values
dep=np.array([VGB_1Y.get(int(y),0.001) for y in ya])
nav=np.empty(n); nav[0]=INIT
for t in range(n):
    ww=wl[t]; wp=wl[t-1] if t>0 else 0.0
    cfr=max(0,1-ww); lfr=max(0,ww-1); buy=max(0,ww-wp); sell=max(0,wp-ww)
    dret=ww*r[t]+cfr*dep[t]/spy-lfr*BORROW/spy-(buy+sell)*TC-sell*TAX
    if t>0: nav[t]=nav[t-1]*(1+dret)

# ── daily reference CSV ──
daily=pd.DataFrame({
    "time": px["time"].dt.strftime("%Y-%m-%d"),
    "vnindex_close": np.round(close,2),
    "dt4_state": st, "dt5g_state": sm,
    "cap": cap, "easing_conf": easing_conf.astype(int),
    "breadth_decoupled": decoup.astype(int),
    "weight": np.round(w,4),
    "nav": np.round(nav,2),
    "nav_rebased_1B": np.round(nav/nav[0]*1e9,2),
})
daily.to_csv("data/dt5g_daily_reference.csv", index=False)

# ── transitions CSV (of the published DT5G state sm) ──
rows=[]; prev_i=0
for t in range(1,n):
    if sm[t]!=sm[t-1]:
        if sm[t]<st[t]: drv=f"MACRO-cap ({src[t] if src[t] else 'stress'})"
        elif sm[t]>st[t]: drv="MACRO-easing"
        else: drv="DT4-regime"
        rows.append(dict(
            date=px["time"].iloc[t].strftime("%Y-%m-%d"),
            from_state=int(sm[t-1]), to_state=int(sm[t]),
            from_name=SNAME[int(sm[t-1])], to_name=SNAME[int(sm[t])],
            vnindex_close=round(float(close[t]),2),
            driver=drv, cap=int(cap[t]),
            dt4_state=int(st[t]), breadth_decoupled=int(decoup[t]),
            prev_state_sessions=t-prev_i))
        prev_i=t
tr=pd.DataFrame(rows)
tr.to_csv("data/dt5g_transitions.csv", index=False)

# ── copy into deploy package for hand-off ──
import shutil
pkgdir = os.path.join(WORKDIR, "deploy_golive_dt5g_v4")
for f in ("dt5g_transitions.csv", "dt5g_daily_reference.csv"):
    shutil.copy(os.path.join(WORKDIR, "data", f), os.path.join(pkgdir, f))

yrs=(px["time"].iloc[-1]-px["time"].iloc[0]).days/365.25
print(f"Rows: {n} ({px['time'].iloc[0].date()} -> {px['time'].iloc[-1].date()})")
print(f"DT5G transitions: {len(tr)}  |  macro-cap days: {int((sm<st).sum())}  easing-floor days: {int((sm>st).sum())}")
print(f"NAV check (must match canonical): final {nav[-1]/1e9:.2f}B  CAGR {((nav[-1]/nav[0])**(1/yrs)-1)*100:.2f}%")
print("Wrote: data/dt5g_transitions.csv, data/dt5g_daily_reference.csv (+ copied into deploy_golive_dt5g_v4/)")
print(tr.tail(8).to_string(index=False))
