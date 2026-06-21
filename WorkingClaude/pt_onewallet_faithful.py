#!/usr/bin/env python3
"""
pt_onewallet_faithful.py — ONE 50B wallet: momentum + LAG + capit + ETF parking.
===============================================================================
Tests the user's architecture question: do we need two separate 25B books, or is
ONE ledger with sleeve weights better? Capital flows naturally: when LAG is idle
(no earnings events ~60% of time) its cash serves momentum/parking/capit, and
vice versa. Sleeve sizing keeps per-position VND comparable to the two-book setup
(mom 5% of 50B NAV ~= 10% of 25B; LAG 5%/4% ~= 10%/8% of 25B).
  Sleeve 1 MOMENTUM: BA-v11 TIER_BAL, w=0.05/name
  Sleeve 2 LAG     : earnings schedule, w=0.05/0.04, 25td, no stop, cap 8+8
  Sleeve 3 CAPIT   : committed playbook sleeve, sized on the wallet's true idle cash
  Sleeve 4 PARKING : idle cash -> E1VFVN30 in NEUTRAL {3:0.7} (same as V4 spec)
Compare vs two-book V2.1+CAPIT (23.86%/Sh1.71/DD-20.8 faithful).
Run: python pt_onewallet_faithful.py
"""
import sys, os, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate

W = r"/home/trido/thanhdt/WorkingClaude"
INIT = 50_000_000_000
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY","COMPOUNDER_BUY","S_PRO"}
EVENTS = [("2014-05-08",1,False),("2015-08-24",3,False),("2016-01-18",3,True),
          ("2018-05-28",1,False),("2020-03-12",2,False),
          ("2022-04-20",1,False),("2022-06-20",2,True),("2022-09-29",2,True),
          ("2023-10-31",1,False),("2024-04-19",4,False),("2025-04-03",4,False),
          ("2026-03-09",3,False)]
def size_of(state, grind):
    return (1.0 if state == 1 else 0.5) * (0.5 if grind else 1.0)

print("[1] Loading...")
panel = pd.read_csv(os.path.join(W,"data","v4f_panel_2014.csv"), parse_dates=["time"])
vni_dates = sorted(panel["time"].unique())
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in panel.groupby("ticker")}
opens  = {tk: dict(zip(g["time"], g["Open"]))  for tk, g in panel.groupby("ticker")}
liqlk  = {(r.ticker, r.time): r.liq_adv for r in panel.itertuples()}
dtg = pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"), parse_dates=["time"])
state_by_date = {t: int(s) for t, s in zip(dtg["time"], dtg["state"])}
last_st=None
for d in vni_dates:
    if d in state_by_date: last_st=state_by_date[d]
    elif last_st is not None: state_by_date[d]=last_st
vnx = pd.read_csv(os.path.join(W,"data/VNINDEX.csv"), usecols=["time","Close","MA200","D_RSI"], parse_dates=["time"])
vnx = vnx[vnx["time"] >= panel["time"].min()]
etf = pd.read_csv(os.path.join(W,"data","e1vfvn30_daily.csv"), parse_dates=["time"])
vn30_und = pd.Series(etf["Close"].values, index=etf["time"])

# momentum signal (same construction as all faithful runs)
sig_b = pickle.load(open(os.path.join(W,"data/ba_v11_unified_12y_sig.pkl"),"rb"))
sig_b["time"] = pd.to_datetime(sig_b["time"])
sig_b = sig_b[sig_b["time"] >= panel["time"].min()].copy()
def sv_tight_keep(row):
    s, days = row["state5"], row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days <= 30
    if s in (2,3): return pd.notna(days) and days <= 60
    return True
mb = sig_b["play_type"].isin(BUY_TIERS)
sig_b = sig_b[(~mb) | sig_b.apply(sv_tight_keep, axis=1)].copy()
v = vnx.merge(pd.DataFrame({"time": list(state_by_date.keys()), "st": list(state_by_date.values())}), on="time", how="left")
v["st"]=v["st"].ffill()
oh = set(v[(v["Close"]/v["MA200"]>1.30)&((v["st"]==5)|(v["D_RSI"]>0.75))]["time"])
sig_b.loc[sig_b["time"].isin(oh) & sig_b["play_type"].isin(BUY_TIERS), "play_type"]="AVOID_overheated"
sec_map = sig_b.dropna(subset=["sec"]).drop_duplicates("ticker").set_index("ticker")["sec"].to_dict()
sig_mom = sig_b[["time","ticker","play_type","ta","Close"]].copy()

# LAG schedule
with open(os.path.join(W,"data/earnings_surprise_data.pkl"),"rb") as f: fin = pickle.load(f)
fin["Release_Date"]=pd.to_datetime(fin["Release_Date"]); FLOOR=1e9
fin["exp_B_MA"]=fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"]=((fin["NP_P0"]-fin["exp_B_MA"])/np.maximum(np.abs(fin["exp_B_MA"]),FLOOR)).clip(-5,5)
ev_class=pd.read_csv(os.path.join(W,"data/earnings_events_classified.csv"),parse_dates=["Release_Date"])
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
e_hl3=ev[(ev["NP_R"]>=15)&(ev["prior_n_good"]>=4)&(ev["pa_HL3"]>=5)].copy()
arr=np.array(vni_dates,dtype="datetime64[ns]")
def offd(ref,off):
    pos=np.searchsorted(arr,np.datetime64(ref),side="right")-1; t=pos+off
    return pd.Timestamp(arr[t]) if 0<=t<len(arr) else None
rows=[]
for _,row in e_hl3.iterrows():
    tk=row["ticker"]; entry=offd(row["Release_Date"],5)
    if entry is None or tk not in prices: continue
    sd=offd(entry,-1)
    if sd is None or sd not in prices[tk]: continue
    rows.append({"time":sd,"ticker":tk,"play_type":"LAG_HI" if row["surprise_B_MA"]>0.5 else "LAG_LO",
                 "ta":400.0,"Close":prices[tk][sd]})
sig_lag=pd.DataFrame(rows)
shn.TIER_PRIORITY.update({"LAG_HI":88,"LAG_LO":82})

# one-wallet sleeve weights: per-position VND comparable to two-book setup
TW = {**{t:0.05 for t in TIER_BAL}, "LAG_HI":0.05, "LAG_LO":0.04}
TIERS = TIER_BAL + ["LAG_HI","LAG_LO"]
sig_all = pd.concat([sig_mom, sig_lag], ignore_index=True)

LIQ = dict(liquidity_volume_pct=0.20, max_fill_days=5, liquidity_lookup=liqlk, exit_slippage_tiered=True)
COMMON = dict(max_positions=24, min_hold=2, slippage=0.001, init_nav=INIT,
              hold_days=45, stop_loss=-0.20,
              sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
              sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},
              deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_by_date,
              cash_etf_states={3:0.7}, vn30_underlying=vn30_und,
              etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
              open_prices=opens, t1_open_exec=True, **LIQ)
LAGX = dict(hold_days_by_tier={"LAG_HI":25,"LAG_LO":25},
            stop_exempt_tiers={"LAG_HI","LAG_LO"},
            tier_position_limit={"LAG_HI":8,"LAG_LO":8})

def run(sig, tiers, label, tw, extra):
    nav,_=simulate(sig,prices,vni_dates,allowed_tiers=tiers,tier_weights=tw,name=label,**COMMON,**extra)
    nav["time"]=pd.to_datetime(nav["time"]); return nav
def metrics(s):
    s=s.dropna(); r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; dd=(s/s.cummax()-1).min(); sh=r.mean()/r.std()*np.sqrt(252)
    return cagr*100, dd*100, sh, (cagr/abs(dd) if dd<0 else 0)

print("[2] ONE-WALLET base (mom + LAG + parking)...")
nav1 = run(sig_all, TIERS, "OW_base", TW, LAGX)
s1=nav1.set_index("time")["nav"]; c1,d1,sh1,cal1=metrics(s1)
print(f"    base: CAGR {c1:.2f}%  MaxDD {d1:.1f}%  Sharpe {sh1:.2f}")

print("[3] + CAPIT (sized on the wallet's true idle cash)...")
elig=pd.read_csv(os.path.join(W,"data","capit_event_elig_full.csv"),parse_dates=["event"])
basecash=nav1.set_index("time")["cash_pct"]/100.0
rows2,tw2,ct=[],dict(TW),[]
for i,(ds,st,gr) in enumerate(EVENTS):
    d=pd.Timestamp(ds); e=elig[elig["event"]==d].copy()
    e=e[[t in prices and d in prices[t] for t in e["ticker"]]]
    g=e[e["pbz"]<-1]; c=e[e["pbz"]<0]
    pick=g if len(g)>=3 else (c if len(c)>=3 else e)
    pick=pick.nsmallest(15,"pbz") if len(pick)>15 else pick
    names=list(pick["ticker"])
    if len(names)<3: continue
    pos=basecash.index.searchsorted(d); cf=float(basecash.iloc[max(0,pos-2):pos+1].mean())
    wt=size_of(st,gr)*max(cf,0.0)
    if wt<=0.005: continue
    pt=f"CAPIT_E{i}"; shn.TIER_PRIORITY[pt]=95
    tw2[pt]=wt/len(names); ct.append(pt)
    for t in names: rows2.append({"time":d,"ticker":t,"play_type":pt,"ta":500.0,"Close":prices[t][d]})
sig2=pd.concat([sig_all,pd.DataFrame(rows2)],ignore_index=True)
EX2=dict(hold_days_by_tier={**LAGX["hold_days_by_tier"], **{t:60 for t in ct}},
         stop_exempt_tiers=LAGX["stop_exempt_tiers"]|set(ct),
         slot_exempt_tiers=set(ct),
         tier_position_limit={**LAGX["tier_position_limit"], **{t:15 for t in ct}})
nav2 = run(sig2, TIERS+ct, "OW_capit", tw2, EX2)
s2=nav2.set_index("time")["nav"]; c2,d2,sh2,cal2=metrics(s2)

print("\n"+"="*92)
print("ONE WALLET vs TWO BOOKS (faithful, 50B, 2014 -> now)")
print("="*92)
print(f"  {'architecture':<38}{'CAGR':>8}{'MaxDD':>9}{'Sharpe':>8}{'Calmar':>8}")
print(f"  {'ONE-WALLET base (mom+LAG+park)':<38}{c1:>7.2f}%{d1:>8.1f}%{sh1:>8.2f}{cal1:>8.2f}")
print(f"  {'ONE-WALLET + CAPIT':<38}{c2:>7.2f}%{d2:>8.1f}%{sh2:>8.2f}{cal2:>8.2f}")
print(f"  {'TWO-BOOK V2.1 plain (ref)':<38}{'21.60%':>8}{'-20.5%':>9}{'1.59':>8}{'1.05':>8}")
print(f"  {'TWO-BOOK V2.1+CAPIT (ref)':<38}{'23.86%':>8}{'-20.8%':>9}{'1.71':>8}{'1.15':>8}")
dep=nav1.set_index("time")[["cash_pct","cash_etf_pct","deployed_pct"]]
print(f"\n  one-wallet base avg: cash {dep['cash_pct'].mean():.0f}%  etf {dep['cash_etf_pct'].mean():.0f}%  deployed {dep['deployed_pct'].mean():.0f}%")
nav1.to_csv(os.path.join(W,"data/pt_onewallet_base.csv"),index=False)
nav2.to_csv(os.path.join(W,"data/pt_onewallet_capit.csv"),index=False)
print("  Saved: data/pt_onewallet_{base,capit}.csv")
