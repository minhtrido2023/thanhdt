#!/usr/bin/env python3
"""
pt_orchestrator_test.py — concentration signal reborn as a PARKING ALLOCATOR.
===============================================================================
The V4 ensemble switch died on a real ledger (liquidate whole book -> dead capital).
The signal (M1+M3r AND-HOLD: market dominated by a few megacaps) may still have
value if it only modulates the CHEAP lever: how much idle cash parks in E1VFVN30.
Flip cost = 0.15% friction on idle cash, ~30x cheaper than flipping a stock book
-> the cost asymmetry that killed the switch disappears.

Arms (two-real-25B-ledger V2.1 frame, all faithful):
  A. V2.1 ref                    : BAL parks {3:0.7}, LAG no parking   (have: 21.60%)
  B. + LAG parking               : LAG book also parks {3:0.7}
  C. + CONC-tilt (on top of B)   : on sig_AH==1 (concentrated) days both books use
       {3:1.0, 4:1.0, 5:0.8} — park ALL idle in ETF through NEUTRAL/BULL;
       on sig_AH==0 days fall back to base {3:0.7}.
Then +CAPIT on the winner. Compare vs V2.1+CAPIT 23.86%/Sh1.71.
Run: python pt_orchestrator_test.py
"""
import sys, os, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate

W = r"/home/trido/thanhdt/WorkingClaude"
BOOK = 25_000_000_000
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS = {t: 0.10 for t in TIER_BAL}
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
rc = pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_rscap.csv"), parse_dates=["time"])
sigAH = pd.Series(rc["sig_AH"].values, index=rc["time"]).reindex(pd.Index(vni_dates)).ffill().fillna(1).astype(int)
CONC_MAP = {1:0.0, 2:0.0, 3:1.0, 4:1.0, 5:0.8}
conc_by_date = {d: CONC_MAP for d in vni_dates if int(sigAH.loc[d]) == 1}
print(f"    concentrated days: {len(conc_by_date)}/{len(vni_dates)}")

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
LAG_TW={"LAG_HI":0.10,"LAG_LO":0.08}

LIQ = dict(liquidity_volume_pct=0.20, max_fill_days=5, liquidity_lookup=liqlk, exit_slippage_tiered=True)
BASE_KW = dict(max_positions=12, min_hold=2, slippage=0.001, init_nav=BOOK,
               deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_by_date,
               open_prices=opens, t1_open_exec=True, **LIQ)
ETF_KW = dict(vn30_underlying=vn30_und, etf_mgmt_fee_annual=0.0,
              etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015)

def run_bal(label, conc=False):
    kw=dict(hold_days=45, stop_loss=-0.20, sector_limit_per_sector={8:4},
            ticker_sector_map=sec_map, sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},
            cash_etf_states={3:0.7}, **ETF_KW)
    if conc: kw["cash_etf_states_by_date"]=conc_by_date
    nav,_=simulate(sig_mom,prices,vni_dates,allowed_tiers=TIER_BAL,tier_weights=TIER_WEIGHTS,
                   name=label,**BASE_KW,**kw)
    nav["time"]=pd.to_datetime(nav["time"]); return nav

def run_lag(sig, tw, label, park=False, conc=False, extra=None):
    lagts={t for t in set(sig["play_type"]) if t.startswith("LAG")}
    kw=dict(hold_days=25, stop_loss=-0.99,
            stop_exempt_tiers=lagts | set((extra or {}).get("stop_exempt_tiers",set())),
            hold_days_by_tier={**{t:25 for t in lagts}, **(extra or {}).get("hold_days_by_tier",{})},
            tier_position_limit={**{t:12 for t in lagts}, **(extra or {}).get("tier_position_limit",{})})
    if extra and "slot_exempt_tiers" in extra: kw["slot_exempt_tiers"]=extra["slot_exempt_tiers"]
    if park:
        kw.update(cash_etf_states={3:0.7}, **ETF_KW)
        if conc: kw["cash_etf_states_by_date"]=conc_by_date
    nav,_=simulate(sig,prices,vni_dates,allowed_tiers=sorted(set(sig["play_type"])),tier_weights=tw,
                   name=label,**BASE_KW,**kw)
    nav["time"]=pd.to_datetime(nav["time"]); return nav

def add_capit(sig, navlog, tw, tag):
    elig=pd.read_csv(os.path.join(W,"data","capit_event_elig_full.csv"),parse_dates=["event"])
    basecash=navlog.set_index("time")["cash_pct"]/100.0
    rows2,tw2,tiers=[],dict(tw),[]
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
        pt=f"CAPIT{tag}_E{i}"; shn.TIER_PRIORITY[pt]=95
        tw2[pt]=wt/len(names); tiers.append(pt)
        for t in names: rows2.append({"time":d,"ticker":t,"play_type":pt,"ta":500.0,"Close":prices[t][d]})
    extra=dict(hold_days_by_tier={t:60 for t in tiers}, stop_exempt_tiers=set(tiers),
               slot_exempt_tiers=set(tiers), tier_position_limit={t:15 for t in tiers})
    return pd.concat([sig,pd.DataFrame(rows2)],ignore_index=True), tw2, extra

def metrics(s):
    s=s.dropna(); r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; dd=(s/s.cummax()-1).min(); sh=r.mean()/r.std()*np.sqrt(252)
    return cagr*100, dd*100, sh, (cagr/abs(dd) if dd<0 else 0)

print("[2] Arms...")
navA      = pd.read_csv(os.path.join(W,"data","pt_v4_full_faithful_nav_A.csv"), parse_dates=["time"])  # BAL ref
navA_conc = run_bal("BAL_conc", conc=True)
nav_l     = run_lag(sig_lag, LAG_TW, "LAG_ref")
nav_lP    = run_lag(sig_lag, LAG_TW, "LAG_park", park=True)
nav_lPC   = run_lag(sig_lag, LAG_TW, "LAG_park_conc", park=True, conc=True)

sA  = navA.set_index("time")["nav"]; sAc_ = navA_conc.set_index("time")["nav"]
combos=[("A: V2.1 ref (BAL{3:.7} + LAG no-park)", sA,  nav_l.set_index("time")["nav"]),
        ("B: + LAG parking {3:0.7}",              sA,  nav_lP.set_index("time")["nav"]),
        ("C: B + CONC-tilt on BOTH books",        sAc_, nav_lPC.set_index("time")["nav"])]
print("\n"+"="*94)
print("ORCHESTRATOR TEST — concentration signal as PARKING allocator (faithful, 2x25B)")
print("="*94)
print(f"  {'arm':<42}{'CAGR':>8}{'MaxDD':>9}{'Sharpe':>8}{'Calmar':>8}")
best=None
for lbl,a,b in combos:
    s=(a+b.reindex(a.index).ffill()).dropna(); c,d,sh,cal=metrics(s)
    print(f"  {lbl:<42}{c:>7.2f}%{d:>8.1f}%{sh:>8.2f}{cal:>8.2f}")
print("\n[3] + CAPIT on arm C (and ref comparison)...")
sigc, twc, exc = add_capit(sig_lag, nav_lPC, LAG_TW, "L")
nav_lPCc = run_lag(sigc, twc, "LAG_pc_cap", park=True, conc=True, extra=exc)
# BAL conc + capit
elig_done=False
sigb2, twb2, exb2 = add_capit(sig_mom, navA_conc, TIER_WEIGHTS, "B")
kwb=dict(hold_days=45, stop_loss=-0.20, sector_limit_per_sector={8:4},
         ticker_sector_map=sec_map, sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},
         cash_etf_states={3:0.7}, cash_etf_states_by_date=conc_by_date, **ETF_KW, **exb2)
navB2,_=simulate(sigb2,prices,vni_dates,allowed_tiers=TIER_BAL+[t for t in twb2 if t.startswith("CAPIT")],
                 tier_weights=twb2,name="BAL_conc_cap",**BASE_KW,**kwb)
navB2["time"]=pd.to_datetime(navB2["time"])
sFull=(navB2.set_index("time")["nav"]+nav_lPCc.set_index("time")["nav"].reindex(navB2.set_index("time").index).ffill()).dropna()
c,d,sh,cal=metrics(sFull)
print(f"  C + CAPIT (full orchestrator)             {c:>7.2f}%{d:>8.1f}%{sh:>8.2f}{cal:>8.2f}")
print(f"  ref: V2.1+CAPIT (no conc-tilt)              23.86%   -20.8%    1.71    1.15")
for nm,nv in [("bal_conc",navA_conc),("lag_park",nav_lP),("lag_park_conc",nav_lPC)]:
    nv.to_csv(os.path.join(W,f"data/pt_orch_{nm}.csv"),index=False)
print("  Saved: data/pt_orch_*.csv")
