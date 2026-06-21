# -*- coding: utf-8 -*-
"""pt_value_book.py — VALUE-BOOK leg (co-equal value pillar candidate for the V2.3 core).
Design from value_horizon_ic.py (2026-06-19): value is a LONG-HORIZON edge (earn_yield 1/PE IC rises
+0.11@1m -> +0.405@12m; pb_z DIES at 12m; momentum negative in quality universe). So:
  selection = sector-neutral earn_yield (1/PE) PRIMARY + cfo_yield (1/PCF) secondary  [NOT pb_z]
  universe  = gate-quality (ROE_Min5Y/ROIC5Y/FSCORE) + liquidity  (8L gate<=3 proxy)
  hold      = LONG: quarterly rebal (post-earnings q2m5), positions persist while still top-ranked
  measure   = full-cycle + IS/OOS + GRIND + per-year (NOT short-horizon Sharpe)
Standalone NAV, T+1 Open, self-check (live-period cash-flow identity 0 VND). DT5G gate OFF for the raw
edge measure (integration comes later). Env: NAV_TOTAL_B(20) TOPN(20) AUDIT_START/END.
"""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, r"/home/trido/thanhdt/WorkingClaude"); os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq, simulate
import simulate_holistic_nav as shn
from pt_dates import detect_end_date

NAV   = float(os.environ.get("NAV_TOTAL_B","20"))*1e9
START = os.environ.get("AUDIT_START","2014-01-02"); END = os.environ.get("AUDIT_END") or detect_end_date()
TOPN  = int(os.environ.get("TOPN","20")); HOLD_D = int(os.environ.get("HOLD_D","250"))
print("="*96); print(f"  VALUE-BOOK | NAV {NAV/1e9:.0f}B | {START}->{END} | earn_yield+cfo_yield, gate-quality, "
      f"quarterly rebal, hold~{HOLD_D}d, top{TOPN}"); print("="*96)

vd = bq(f"SELECT t.time FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY t.time")
vd["time"]=pd.to_datetime(vd["time"]); vni_dates=list(vd["time"])
# quarterly rebal = first trading day of Feb/May/Aug/Nov (post-earnings)
sdt=pd.Series(vni_dates)
rebals=[g.min() for _,g in sdt.groupby([sdt.dt.year, sdt.dt.month]) ]
rebals=[pd.Timestamp(r) for r in rebals if pd.Timestamp(r).month in (2,5,8,11)]
print(f"[1] {len(vni_dates)} sessions, {len(rebals)} quarterly rebals")

sig_rows, names = [], set()
for rd in rebals:
    e = bq(f"""SELECT p.ticker, SAFE_DIVIDE(1.0,p.PE) ey, SAFE_DIVIDE(1.0,p.PCF) cfy,
      CAST(FLOOR(p.ICB_Code/1000) AS INT64) sec, p.Close
    FROM tav2_bq.ticker_prune p
    WHERE p.time=DATE '{rd.date()}' AND p.PE>0 AND p.PCF>0
      AND p.ROE_Min5Y>=0.10 AND p.ROIC5Y>=0.08 AND p.FSCORE>=5
      AND COALESCE(p.Price,p.Close)*p.Volume/1e9>=2""")
    if e.empty: continue
    e["ey_sn"]=e["ey"]-e.groupby("sec")["ey"].transform("mean")     # sector-neutral earn-yield
    z=lambda s:(s-s.mean())/s.std(ddof=0) if s.std(ddof=0)>0 else s*0
    e["score"]=z(e["ey_sn"])+0.5*z(e["cfy"])                        # earn-yield primary + cfo secondary
    pick=e.nlargest(TOPN,"score")
    for _,r in pick.iterrows():
        sig_rows.append({"time":rd,"ticker":r["ticker"],"play_type":"VALUE","ta":500.0,"Close":float(r["Close"])})
        names.add(r["ticker"])
sig=pd.DataFrame(sig_rows,columns=["time","ticker","play_type","ta","Close"])
print(f"[2] {len(sig)} signals, {len(names)} names, avg {len(sig)/max(1,sig['time'].nunique()):.1f}/rebal")

nm=sorted(names); parts=[]
for i in range(0,len(nm),250):
    inl=",".join(f"'{t}'" for t in nm[i:i+250])
    parts.append(bq(f"SELECT t.ticker,t.time,t.Open,t.Close,t.Volume_3M_P50 FROM tav2_bq.ticker t WHERE t.time BETWEEN DATE '{START}' AND DATE '{END}' AND t.ticker IN ({inl})"))
px=pd.concat(parts,ignore_index=True); px["time"]=pd.to_datetime(px["time"])
prices,opens,liq={},{},{}
for tk,g in px.groupby("ticker"):
    gc=g[g["Close"].notna()]; prices[tk]=dict(zip(gc["time"],gc["Close"].astype(float)))
    go=g[g["Open"].notna()];  opens[tk]=dict(zip(go["time"],go["Open"].astype(float)))
    gl=g[g["Volume_3M_P50"].notna()&g["Close"].notna()]
    for d,a,c in zip(gl["time"],gl["Volume_3M_P50"].astype(float),gl["Close"].astype(float)): liq[(tk,d)]=a*c
print(f"[3] price panel {len(px):,} rows")

shn.TIER_PRIORITY["VALUE"]=90; ev=[]
nav_df,_=simulate(sig,prices,vni_dates,allowed_tiers={"VALUE"},max_positions=TOPN,
    tier_weights={"VALUE":1.0/TOPN},hold_days=HOLD_D,min_hold=3,stop_loss=-0.95,reentry_blacklist_days=0,
    liquidity_lookup=liq,liquidity_volume_pct=0.20,max_fill_days=5,exit_slippage_tiered=True,
    open_prices=opens,t1_open_exec=True,init_nav=NAV,deposit_annual=0.0,borrow_annual=0.10,
    event_log=ev,force_close_eod=True,name="value")
nav_df["time"]=pd.to_datetime(nav_df["time"]); nav_df=nav_df.set_index("time")
e=pd.DataFrame(ev)
if not e.empty:
    e["ymd"]=pd.to_datetime(e["ymd"]); real=e[e["reason"]!="EOD"]
    real=real.assign(net=np.where(real["action"]=="sell",real["sell_amount"]-real["fee"],-(real["buy_amount"]+real["fee"])))
    f=real.groupby("ymd")["net"].sum().reindex(nav_df.index).fillna(0.0)
    cash=nav_df["cash"]; dc=cash.diff(); dc.iloc[0]=cash.iloc[0]-NAV
    err=float((dc-f).iloc[:-1].abs().max())
else: err=0.0
print(f"[4] final NAV {nav_df['nav'].iloc[-1]/1e9:.2f}B | SELF-CHECK live-period err={err:,.0f} VND {'PASS' if err<1000 else 'FAIL'}")

vni=bq(f"SELECT t.time,t.Close FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START}' AND DATE '{END}' ORDER BY t.time")
vni["time"]=pd.to_datetime(vni["time"]); vni=vni.set_index("time")["Close"]
def met(s):
    s=s.dropna();
    if len(s)<5: return None
    yrs=(s.index[-1]-s.index[0]).days/365.25; r=s.pct_change().dropna()
    cg=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; dd=(s/s.cummax()-1).min()
    return dict(cagr=cg*100,sh=r.mean()/r.std()*np.sqrt(252) if r.std()>0 else 0,dd=dd*100,cal=cg/abs(dd) if dd<0 else 0)
def show(l,n,v):
    m=met(n); mv=met(v)
    if not m: print(f"  {l:14s} (n/a)"); return
    print(f"  {l:14s} CAGR {m['cagr']:6.2f}%  Sh {m['sh']:4.2f}  DD {m['dd']:6.1f}%  Cal {m['cal']:4.2f}  | VNI {mv['cagr']:6.2f}% DD {mv['dd']:6.1f}%")
nav=nav_df["nav"]
nav.to_csv("data/value_book_nav.csv")   # save for blend-vs-production analysis
print("\n[5] WALK-FORWARD"); show("FULL",nav,vni)
show("IS 2014-19",nav[nav.index<='2019-12-31'],vni[vni.index<='2019-12-31'])
show("OOS 2020-26",nav[nav.index>='2020-01-01'],vni[vni.index>='2020-01-01'])
# correlation of monthly returns to VNINDEX (diversification proxy)
mn=nav.resample("ME").last().pct_change().dropna(); mv=vni.resample("ME").last().pct_change().dropna()
j=pd.concat([mn,mv],axis=1).dropna(); corr=j.iloc[:,0].corr(j.iloc[:,1])
print(f"\n[6] monthly-return corr to VNINDEX = {corr:+.2f}")
print("[7] GRIND 2025-09..2026-03 + per-year")
g=nav[(nav.index>='2025-09-01')&(nav.index<='2026-03-31')]; gv=vni[(vni.index>='2025-09-01')&(vni.index<='2026-03-31')]
if len(g)>1: print(f"  GRIND: value {(g.iloc[-1]/g.iloc[0]-1)*100:+.1f}%  vni {(gv.iloc[-1]/gv.iloc[0]-1)*100:+.1f}%")
for y in range(int(nav.index[0].year),int(nav.index[-1].year)+1):
    ny=nav[nav.index.year==y]; vy=vni[vni.index.year==y]
    if len(ny)<5: continue
    print(f"  {y}: value {(ny.iloc[-1]/ny.iloc[0]-1)*100:+6.1f}%  vni {(vy.iloc[-1]/vy.iloc[0]-1)*100:+6.1f}%")
print("="*96)
