#!/usr/bin/env python3
"""V2.2 backtest with CAPIT v2.1 parameters (2026-06-10 playbook chot):
- NEUTRAL base 0.5 -> 0.75
- WASHOUT threshold 40% -> 30% (2 new events: 2024-08-05, 2025-10-20)
- BEAR guard: base=0.5 only if (dd52w > -25% OR vn_rv10_cooling), else SKIP
  -> 2022-09-29 BEAR: dd=-26.3%, no cooling -> BLOCKED (was 0.25)
  -> 2022-06-20 BEAR: dd=-22.8% > -25% -> PASSES (unchanged 0.25)
  -> 2020-03-12 BEAR: dd=-24.9% > -25% -> PASSES (unchanged 0.5)
- Hold 60td (was already 60 in addcap)
Uses capit_event_elig_v21.csv (adds 2024-08-05 and 2025-10-20 elig tickers)
"""
import sys, os, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate
W = r"/home/trido/thanhdt/WorkingClaude"
BOOK=25_000_000_000
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS={t:0.10 for t in TIER_BAL}
BUY_TIERS={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A","MOMENTUM_S_N",
           "DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY","COMPOUNDER_BUY","S_PRO"}

# CAPIT v2.1 events: (date, dt5g_state, grind, dd52w_pct, vn_cooling)
# dd52w_pct and vn_cooling only needed for BEAR (state=2) to decide guard
EVENTS_V21=[
    ("2014-05-08", 1, False, 0.0,  False),   # CRISIS
    ("2015-08-24", 3, False, 0.0,  False),   # NEUTRAL
    ("2016-01-18", 3, True,  0.0,  False),   # NEUTRAL grind
    ("2018-05-28", 1, False, 0.0,  False),   # CRISIS
    ("2020-03-12", 2, False, -24.9,False),   # BEAR: dd=-24.9% > -25% -> PASS
    ("2022-04-20", 1, False, 0.0,  False),   # CRISIS
    ("2022-06-20", 2, True,  -22.8,True),    # BEAR grind: dd=-22.8% > -25% -> PASS
    ("2022-09-29", 2, True,  -26.3,False),   # BEAR grind: dd=-26.3% <= -25%, no cool -> BLOCKED
    ("2023-10-31", 1, False, 0.0,  False),   # CRISIS
    ("2024-04-19", 4, False, 0.0,  False),   # BULL
    ("2024-08-05", 1, True,  0.0,  False),   # CRISIS grind (NEW at 30% threshold)
    ("2025-04-03", 4, False, 0.0,  False),   # BULL
    ("2025-10-20", 3, False, 0.0,  False),   # NEUTRAL (NEW at 30% threshold)
    ("2026-03-09", 3, False, 0.0,  False),   # NEUTRAL
]

def size_of_v21(st, gr, dd52w=0.0, vn_cooling=False):
    """CAPIT v2.1 base sizing per state."""
    if st == 1:   base = 1.0                                       # CRISIS: always full
    elif st == 3: base = 0.75                                      # NEUTRAL: 0.5->0.75
    elif st in (4, 5): base = 0.5                                  # BULL/EX-BULL
    elif st == 2:                                                   # BEAR: conditional guard
        base = 0.5 if (dd52w > -25.0 or vn_cooling) else 0.0
    else: base = 0.5
    return base * (0.5 if gr else 1.0)

panel=pd.read_csv(os.path.join(W,"data","v4f_panel_2014.csv"),parse_dates=["time"])
vni_dates=sorted(panel["time"].unique())
prices={tk:dict(zip(g["time"],g["Close"])) for tk,g in panel.groupby("ticker")}
opens={tk:dict(zip(g["time"],g["Open"])) for tk,g in panel.groupby("ticker")}
liqlk={(r.ticker,r.time):r.liq_adv for r in panel.itertuples()}
dtg=pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"),parse_dates=["time"])
state_by_date={t:int(s) for t,s in zip(dtg["time"],dtg["state"])}
last=None
for d in vni_dates:
    if d in state_by_date: last=state_by_date[d]
    elif last is not None: state_by_date[d]=last
vnx=pd.read_csv(os.path.join(W,"VNINDEX.csv"),usecols=["time","Close","MA200","D_RSI"],parse_dates=["time"])
vnx=vnx[vnx["time"]>=panel["time"].min()]
etf=pd.read_csv(os.path.join(W,"data","e1vfvn30_daily_full.csv"),parse_dates=["time"])
vn30_und=pd.Series(etf["Close"].values,index=etf["time"])
sig_b=pickle.load(open(os.path.join(W,"ba_v11_unified_12y_sig.pkl"),"rb"))
sig_b["time"]=pd.to_datetime(sig_b["time"]); sig_b=sig_b[sig_b["time"]>=panel["time"].min()].copy()
def svk(row):
    s,days=row["state5"],row["days_since_release"]
    if pd.isna(s): return True
    s=int(s)
    if s in (4,5): return True
    if s==1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb=sig_b["play_type"].isin(BUY_TIERS)
sig_b=sig_b[(~mb)|sig_b.apply(svk,axis=1)].copy()
v=vnx.merge(pd.DataFrame({"time":list(state_by_date.keys()),"st":list(state_by_date.values())}),on="time",how="left")
v["st"]=v["st"].ffill()
oh=set(v[(v["Close"]/v["MA200"]>1.30)&((v["st"]==5)|(v["D_RSI"]>0.75))]["time"])
sig_b.loc[sig_b["time"].isin(oh)&sig_b["play_type"].isin(BUY_TIERS),"play_type"]="AVOID_overheated"
sec_map=sig_b.dropna(subset=["sec"]).drop_duplicates("ticker").set_index("ticker")["sec"].to_dict()
sig_mom=sig_b[["time","ticker","play_type","ta","Close"]].copy()
with open(os.path.join(W,"earnings_surprise_data.pkl"),"rb") as f: fin=pickle.load(f)
fin["Release_Date"]=pd.to_datetime(fin["Release_Date"]); FLOOR=1e9
fin["exp_B_MA"]=fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"]=((fin["NP_P0"]-fin["exp_B_MA"])/np.maximum(np.abs(fin["exp_B_MA"]),FLOOR)).clip(-5,5)
ev_class=pd.read_csv(os.path.join(W,"earnings_events_classified.csv"),parse_dates=["Release_Date"])
ev=ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],on=["ticker","quarter","Release_Date"],how="left")
ev=ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True); ev["surprise_B_MA"]=ev["surprise_B_MA"].fillna(0)
LN2=np.log(2); HL=3.0; ev["prior_n_good"]=0; ev["pa_HL3"]=np.nan
for tk,g in ev.groupby("ticker"):
    hist=[]
    for ri in g.index.tolist():
        row=ev.loc[ri]; cur=row["Release_Date"]; ev.at[ri,"prior_n_good"]=len(hist)
        if hist:
            da=pd.to_datetime([d for d,_ in hist]); pa=np.array([p for _,p in hist])
            wts=np.exp(-LN2*((cur-da).days.values/365.25)/HL)
            ev.at[ri,"pa_HL3"]=(pa*wts).sum()/wts.sum() if wts.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"]>=15 and pd.notna(row["post_ret"]): hist.append((cur,row["post_ret"]))
e3=ev[(ev["NP_R"]>=15)&(ev["prior_n_good"]>=4)&(ev["pa_HL3"]>=5)].copy()
arr=np.array(vni_dates,dtype="datetime64[ns]")
def offd(ref,off):
    pos=np.searchsorted(arr,np.datetime64(ref),side="right")-1; t=pos+off
    return pd.Timestamp(arr[t]) if 0<=t<len(arr) else None
rows=[]
for _,row in e3.iterrows():
    tk=row["ticker"]; entry=offd(row["Release_Date"],5)
    if entry is None or tk not in prices: continue
    sd=offd(entry,-1)
    if sd is None or sd not in prices[tk]: continue
    rows.append({"time":sd,"ticker":tk,"play_type":"LAG_HI" if row["surprise_B_MA"]>0.5 else "LAG_LO","ta":400.0,"Close":prices[tk][sd]})
sig_lag=pd.DataFrame(rows)
shn.TIER_PRIORITY.update({"LAG_HI":88,"LAG_LO":82})
LAG_TW={"LAG_HI":0.10,"LAG_LO":0.08}
LIQ=dict(liquidity_volume_pct=0.20,max_fill_days=5,liquidity_lookup=liqlk,exit_slippage_tiered=True)
BKW=dict(max_positions=12,min_hold=2,slippage=0.001,init_nav=BOOK,deposit_annual=0.0,borrow_annual=0.10,
         state_by_date=state_by_date,open_prices=opens,t1_open_exec=True,**LIQ)
EK=dict(vn30_underlying=vn30_und,etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,etf_rebalance_friction=0.0015)
def runb(sig,tiers,label,tw,extra=None):
    nav,_=simulate(sig,prices,vni_dates,allowed_tiers=tiers,tier_weights=tw,
        hold_days=45,stop_loss=-0.20,sector_limit_per_sector={8:4},ticker_sector_map=sec_map,
        sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},cash_etf_states={3:0.7},**EK,name=label,**BKW,**(extra or {}))
    nav["time"]=pd.to_datetime(nav["time"]); return nav
def runl(sig,tw,label,extra=None):
    lagts={t for t in set(sig["play_type"]) if t.startswith("LAG")}
    kw=dict(hold_days=25,stop_loss=-0.99,stop_exempt_tiers=lagts|set((extra or {}).get("stop_exempt_tiers",set())),
        hold_days_by_tier={**{t:25 for t in lagts},**(extra or {}).get("hold_days_by_tier",{})},
        tier_position_limit={**{t:12 for t in lagts},**(extra or {}).get("tier_position_limit",{})},
        cash_etf_states={3:0.7},**EK)
    if extra and "slot_exempt_tiers" in extra: kw["slot_exempt_tiers"]=extra["slot_exempt_tiers"]
    nav,_=simulate(sig,prices,vni_dates,allowed_tiers=sorted(set(sig["play_type"])),tier_weights=tw,name=label,**BKW,**kw)

# ============ CAPACITY TEST: LAG base book at increasing capital ============
def met(s):
    s=s.dropna(); r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; dd=(s/s.cummax()-1).min(); sh=r.mean()/r.std()*np.sqrt(252)
    return cagr*100,dd*100,sh,cagr/abs(dd)

def runl_cap(sig,tw,label,nav_cap):
    lagts={t for t in set(sig["play_type"]) if t.startswith("LAG")}
    bkw=dict(BKW); bkw["init_nav"]=nav_cap
    kw=dict(hold_days=25,stop_loss=-0.99,stop_exempt_tiers=lagts,
        hold_days_by_tier={t:25 for t in lagts},
        tier_position_limit={t:12 for t in lagts},
        cash_etf_states={3:0.7},**EK)
    nav,_=simulate(sig,prices,vni_dates,allowed_tiers=sorted(set(sig["play_type"])),tier_weights=tw,name=label,**bkw,**kw)
    nav["time"]=pd.to_datetime(nav["time"]); return nav

print("\n"+"="*78)
print("LAG CAPACITY TEST (base, no capit) — return-per-dollar as book scales")
print("="*78)
for cap in [25, 40, 60, 80, 120]:
    nav=runl_cap(sig_lag,LAG_TW,f"LAG_{cap}B",cap*1_000_000_000)
    s=nav.set_index("time")
    dep=s["deployed_pct"].mean(); etf=s["cash_etf_pct"].mean()
    for lbl,st in [("FULL","2014-01-01"),("2025+","2025-01-01")]:
        m=met(s["nav"][s.index>=st])
        print(f"  {cap:>3}B {lbl:6}: CAGR {m[0]:5.1f}%  DD {m[1]:6.1f}  Sh {m[2]:.2f}  | avg_deployed {dep:4.1f}%  avg_ETFpark {etf:4.1f}%")
