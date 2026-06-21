#!/usr/bin/env python3
"""
pt_margin_test.py — V6-v3's margin<=150% tested on V2.2 (faithful).
===============================================================================
Engine now supports max_gross_exposure: stock buys may draw cash negative down to
-(mge-1)*NAV at borrow 10%/yr; ETF parking never margins; JIT-ETF-sell still funds
buys before borrowing. Capit sizing unchanged (size x free cash, clipped >=0).

Arms (all WITH capit, vs V2.2 ref 25.50%/-20.6/Sh1.75/Cal1.24):
  M-LAG : margin 1.5 on LAG book only (it skips entries in busy earnings seasons)
  M-BOTH: margin 1.5 on both books
Reports realized margin usage (min cash%, days cash<0) and borrow drag.
Run: python pt_margin_test.py
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
def size_of(st,gr): return (1.0 if st==1 else 0.5)*(0.5 if gr else 1.0)

print("[1] Loading...")
panel = pd.read_csv(os.path.join(W,"data","v4f_panel_2014.csv"), parse_dates=["time"])
vni_dates = sorted(panel["time"].unique())
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in panel.groupby("ticker")}
opens  = {tk: dict(zip(g["time"], g["Open"]))  for tk, g in panel.groupby("ticker")}
liqlk  = {(r.ticker, r.time): r.liq_adv for r in panel.itertuples()}
dtg = pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"), parse_dates=["time"])
state_by_date = {t: int(s) for t, s in zip(dtg["time"], dtg["state"])}
last=None
for d in vni_dates:
    if d in state_by_date: last=state_by_date[d]
    elif last is not None: state_by_date[d]=last
vnx = pd.read_csv(os.path.join(W,"data/VNINDEX.csv"), usecols=["time","Close","MA200","D_RSI"], parse_dates=["time"])
vnx = vnx[vnx["time"] >= panel["time"].min()]
etf = pd.read_csv(os.path.join(W,"data","e1vfvn30_daily.csv"), parse_dates=["time"])
vn30_und = pd.Series(etf["Close"].values, index=etf["time"])
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
def BKW(mge=None):
    d=dict(max_positions=12, min_hold=2, slippage=0.001, init_nav=BOOK,
           deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_by_date,
           open_prices=opens, t1_open_exec=True, **LIQ)
    if mge: d["max_gross_exposure"]=mge
    return d
ETF_KW = dict(vn30_underlying=vn30_und, etf_mgmt_fee_annual=0.0,
              etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015)

def run_bal(label,mge=None,sig=None,tw=None,extra=None):
    nav,_=simulate(sig if sig is not None else sig_mom,prices,vni_dates,
        allowed_tiers=sorted(set((sig if sig is not None else sig_mom)["play_type"]) & set((tw or TIER_WEIGHTS).keys())) if sig is not None else TIER_BAL,
        tier_weights=tw or TIER_WEIGHTS,
        hold_days=45,stop_loss=-0.20,sector_limit_per_sector={8:4},ticker_sector_map=sec_map,
        sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},cash_etf_states={3:0.7},**ETF_KW,
        name=label,**BKW(mge),**(extra or {}))
    nav["time"]=pd.to_datetime(nav["time"]); return nav
def run_lagb(label,mge=None,sig=None,tw=None,extra=None):
    s = sig if sig is not None else sig_lag; w = tw or LAG_TW
    lagts={t for t in set(s["play_type"]) if t.startswith("LAG")}
    kw=dict(hold_days=25, stop_loss=-0.99,
            stop_exempt_tiers=lagts | set((extra or {}).get("stop_exempt_tiers",set())),
            hold_days_by_tier={**{t:25 for t in lagts}, **(extra or {}).get("hold_days_by_tier",{})},
            tier_position_limit={**{t:12 for t in lagts}, **(extra or {}).get("tier_position_limit",{})},
            cash_etf_states={3:0.7},**ETF_KW)
    if extra and "slot_exempt_tiers" in extra: kw["slot_exempt_tiers"]=extra["slot_exempt_tiers"]
    nav,_=simulate(s,prices,vni_dates,allowed_tiers=sorted(set(s["play_type"])),tier_weights=w,
                   name=label,**BKW(mge),**kw)
    nav["time"]=pd.to_datetime(nav["time"]); return nav
def add_capit(sig, navlog, tw, tag):
    elig=pd.read_csv(os.path.join(W,"data","capit_event_elig_full.csv"),parse_dates=["event"])
    basecash=(navlog.set_index("time")["cash_pct"]/100.0).clip(lower=0)
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
def usage(nav):
    cp=nav["cash_pct"]; return cp.min(), int((cp<0).sum()), nav["deployed_pct"].max()

print("[2] Margin arms...")
# M-LAG: margin only on LAG book
lagM = run_lagb("LAG_m15", mge=1.5)
sigc,twc,exc = add_capit(sig_lag, lagM, LAG_TW, "L")
lagMc = run_lagb("LAG_m15_cap", mge=1.5, sig=sigc, tw=twc, extra=exc)
# M-BOTH: BAL margin too
balM = run_bal("BAL_m15", mge=1.5)
sigb,twb,exb = add_capit(sig_mom, balM, TIER_WEIGHTS, "B")
balMc_nav,_ = simulate(sigb,prices,vni_dates,allowed_tiers=TIER_BAL+[t for t in twb if t.startswith("CAPIT")],
    tier_weights=twb,hold_days=45,stop_loss=-0.20,sector_limit_per_sector={8:4},ticker_sector_map=sec_map,
    sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},cash_etf_states={3:0.7},**ETF_KW,
    name="BAL_m15_cap",**BKW(1.5),**exb)
balMc_nav["time"]=pd.to_datetime(balMc_nav["time"]); balMc=balMc_nav

navA_cap = pd.read_csv(os.path.join(W,"data","pt_v4_full_faithful_nav_A_cap.csv"),parse_dates=["time"])
lag_pc   = pd.read_csv(os.path.join(W,"data","pt_orch_lag_park_cap.csv"),parse_dates=["time"])
sAc=navA_cap.set_index("time")["nav"]; sLc=lag_pc.set_index("time")["nav"]
sLMc=lagMc.set_index("time")["nav"]; sBMc=balMc.set_index("time")["nav"]

print("\n"+"="*94)
print("MARGIN <=150% (V6-v3) on V2.2 — faithful, with capit")
print("="*94)
print(f"  {'arm':<40}{'CAGR':>8}{'MaxDD':>9}{'Sharpe':>8}{'Calmar':>8}")
combos=[("V2.2 ref (no margin)",            sAc, sLc),
        ("V2.2 + margin150 LAG only",       sAc, sLMc),
        ("V2.2 + margin150 BOTH books",     sBMc, sLMc)]
for lbl,a,b in combos:
    s=(a+b.reindex(a.index).ffill()).dropna(); c,d,sh,cal=metrics(s)
    print(f"  {lbl:<40}{c:>7.2f}%{d:>8.1f}%{sh:>8.2f}{cal:>8.2f}")
print("\n  realized margin usage:")
for lbl,nv in [("LAG m1.5 (base)",lagM),("LAG m1.5+cap",lagMc),("BAL m1.5+cap",balMc)]:
    mn,nd,mx=usage(nv)
    print(f"    {lbl:<18}: min cash {mn:6.1f}%  days cash<0: {nd:>4}  max deployed {mx:5.1f}%")
for nm,nv in [("lag_m15",lagM),("lag_m15_cap",lagMc),("bal_m15_cap",balMc)]:
    nv.to_csv(os.path.join(W,f"data/pt_margin_{nm}.csv"),index=False)
print("  Saved: data/pt_margin_*.csv")
