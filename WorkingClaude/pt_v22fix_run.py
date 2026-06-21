#!/usr/bin/env python3
"""Re-run V2.2's 4 arms with the FULL E1VFVN30 history (2016+) — fixes the
parking-dead-before-2021-09 data bug discovered 2026-06-10 (old e1vfvn30_daily.csv
started 2021-09 -> all faithful sims had NO ETF parking for 2014-2021)."""
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
EVENTS=[("2014-05-08",1,False),("2015-08-24",3,False),("2016-01-18",3,True),("2018-05-28",1,False),
        ("2020-03-12",2,False),("2022-04-20",1,False),("2022-06-20",2,True),("2022-09-29",2,True),
        ("2023-10-31",1,False),("2024-04-19",4,False),("2025-04-03",4,False),("2026-03-09",3,False)]
def size_of(st,gr): return (1.0 if st==1 else 0.5)*(0.5 if gr else 1.0)
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
    nav["time"]=pd.to_datetime(nav["time"]); return nav
def addcap(sig,navlog,tw,tag):
    elig=pd.read_csv(os.path.join(W,"data","capit_event_elig_full.csv"),parse_dates=["event"])
    bc=(navlog.set_index("time")["cash_pct"]/100.0).clip(lower=0)
    r2,tw2,ts=[],dict(tw),[]
    for i,(ds,st,gr) in enumerate(EVENTS):
        d=pd.Timestamp(ds); e=elig[elig["event"]==d].copy()
        e=e[[t in prices and d in prices[t] for t in e["ticker"]]]
        g=e[e["pbz"]<-1]; c=e[e["pbz"]<0]
        pick=g if len(g)>=3 else (c if len(c)>=3 else e)
        pick=pick.nsmallest(15,"pbz") if len(pick)>15 else pick
        names=list(pick["ticker"])
        if len(names)<3: continue
        pos=bc.index.searchsorted(d); cf=float(bc.iloc[max(0,pos-2):pos+1].mean())
        wt=size_of(st,gr)*max(cf,0.0)
        if wt<=0.005: continue
        pt="CAP"+tag+"_E"+str(i); shn.TIER_PRIORITY[pt]=95
        tw2[pt]=wt/len(names); ts.append(pt)
        for t in names: r2.append({"time":d,"ticker":t,"play_type":pt,"ta":500.0,"Close":prices[t][d]})
    ex=dict(hold_days_by_tier={t:60 for t in ts},stop_exempt_tiers=set(ts),slot_exempt_tiers=set(ts),
            tier_position_limit={t:15 for t in ts})
    return pd.concat([sig,pd.DataFrame(r2)],ignore_index=True),tw2,ex
def met(s):
    s=s.dropna(); r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; dd=(s/s.cummax()-1).min(); sh=r.mean()/r.std()*np.sqrt(252)
    return cagr*100,dd*100,sh,cagr/abs(dd)
print("running 4 arms with FULL ETF history (2016+)...")
balB=runb(sig_mom,TIER_BAL,"BAL_fe",TIER_WEIGHTS)
sb,tb,eb=addcap(sig_mom,balB,TIER_WEIGHTS,"B")
balC=runb(sb,TIER_BAL+[t for t in tb if t.startswith("CAP")],"BAL_fe_cap",tb,eb)
lagB=runl(sig_lag,LAG_TW,"LAG_fe")
sl,tl,el=addcap(sig_lag,lagB,LAG_TW,"L")
lagC=runl(sl,tl,"LAG_fe_cap",el)
for nm,nv in [("bal_fe",balB),("bal_fe_cap",balC),("lag_fe",lagB),("lag_fe_cap",lagC)]:
    nv.to_csv(os.path.join(W,"data","pt_v22fix_"+nm+".csv"),index=False)
sA=balB.set_index("time")["nav"]; sAc=balC.set_index("time")["nav"]
sL=lagB.set_index("time")["nav"]; sLc=lagC.set_index("time")["nav"]
for lbl,a,b in [("V2.2 base (full-ETF park)",sA,sL),("V2.2 + CAPIT (full-ETF park)",sAc,sLc)]:
    s=(a+b.reindex(a.index).ffill()).dropna(); c,d,sh,cal=met(s)
    print("%s: CAGR %.2f%%  MaxDD %.1f%%  Sharpe %.2f  Calmar %.2f" % (lbl,c,d,sh,cal))
print("(old broken-ETF refs: base 23.20/Sh1.64 | +capit 25.50/-20.6/Sh1.75/Cal1.24)")
st=pd.Series(state_by_date)
for lbl,nv in [("BAL",balB),("LAG",lagB)]:
    d=nv.set_index("time"); d["st"]=st.reindex(d.index).ffill()
    g=d[d.index>=pd.Timestamp("2016-01-07")].groupby("st")[["cash_pct","cash_etf_pct","deployed_pct"]].mean().round(1)
    print("--- "+lbl+" avg by state 2016+ (cash%/ETF%/stock%):"); print(g.to_string())
