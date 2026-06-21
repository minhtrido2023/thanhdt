#!/usr/bin/env python3
"""
pt_v21_faithful.py — V2.1F: the faithful champion, assembled.
===============================================================================
V2.1F = BAL 25B + LAG-v12.1 25B (static, no switching)
        + regime-size: LAG entries with 8L rating>=4 HALVED when DT5G==BEAR at signal
        + committed capitulation sleeve (playbook) in EACH book, sized on that
          book's own free cash (two real accounts each running the playbook)
All transaction-level: T+1 Open fills, slippage, 20%-ADV caps, 0.3%TC, no margin.

Ablation reported:
  V2.1 plain            = BAL + LAG121                       (prior run, recomputed refs)
  V2.1 + BEAR-rule      = BAL + LAG121_B
  V2.1 + CAPIT          = BAL_cap + LAG121_cap
  V2.1F (full)          = BAL_cap + LAG121_B_cap             <- the system
Run: python pt_v21_faithful.py
"""
import sys, os, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate

W = r"/home/trido/thanhdt/WorkingClaude"
BOOK = 25_000_000_000
EVENTS = [("2014-05-08",1,False),("2015-08-24",3,False),("2016-01-18",3,True),
          ("2018-05-28",1,False),("2020-03-12",2,False),
          ("2022-04-20",1,False),("2022-06-20",2,True),("2022-09-29",2,True),
          ("2023-10-31",1,False),("2024-04-19",4,False),("2025-04-03",4,False),
          ("2026-03-09",3,False)]
def size_of(state, grind):
    return (1.0 if state == 1 else 0.5) * (0.5 if grind else 1.0)

print("[1] Loading data...")
panel = pd.read_csv(os.path.join(W,"data","v4f_panel_2014.csv"), parse_dates=["time"])
vni_dates = sorted(panel["time"].unique())
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in panel.groupby("ticker")}
opens  = {tk: dict(zip(g["time"], g["Open"]))  for tk, g in panel.groupby("ticker")}
liqlk  = {(r.ticker, r.time): r.liq_adv for r in panel.itertuples()}
dtg = pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"), parse_dates=["time"])
state_by_date = {t: int(s) for t, s in zip(dtg["time"], dtg["state"])}
last_st = None
for d in vni_dates:
    if d in state_by_date: last_st = state_by_date[d]
    elif last_st is not None: state_by_date[d] = last_st

print("[2] LAG schedule + 8L BEAR rule...")
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
base_rows=[]
for _,row in e_hl3.iterrows():
    tk=row["ticker"]; entry=offd(row["Release_Date"],5)
    if entry is None or tk not in prices: continue
    sd=offd(entry,-1)
    if sd is None or sd not in prices[tk]: continue
    base_rows.append({"time":sd,"ticker":tk,"hi":row["surprise_B_MA"]>0.5,"Close":prices[tk][sd]})
lagdf=pd.DataFrame(base_rows).sort_values("time")
lagdf["time"]=pd.to_datetime(lagdf["time"]).astype("datetime64[ns]")
rt=pd.read_csv(os.path.join(W,"data","fa_ratings_8l_hist.csv"),parse_dates=["time"]).sort_values("time")
rt["time"]=pd.to_datetime(rt["time"]).astype("datetime64[ns]")
lagdf=pd.merge_asof(lagdf, rt.rename(columns={"time":"rt_time"})[["ticker","rt_time","rating"]],
                    left_on="time", right_on="rt_time", by="ticker", direction="backward")
lagdf["bear_weak"]=(lagdf["time"].map(lambda d: state_by_date.get(d,3))==2) & (lagdf["rating"]>=4)
def mk_sig(bear_rule):
    d=lagdf.copy()
    if bear_rule:
        d["play_type"]=np.where(d["bear_weak"], np.where(d["hi"],"LAG_HI_B","LAG_LO_B"),
                                np.where(d["hi"],"LAG_HI","LAG_LO"))
    else:
        d["play_type"]=np.where(d["hi"],"LAG_HI","LAG_LO")
    d["ta"]=400.0
    return d[["time","ticker","play_type","ta","Close"]]
n_weak=int(lagdf["bear_weak"].sum())
print(f"    LAG entries {len(lagdf)} | BEAR x rating>=4 (halved): {n_weak}")
shn.TIER_PRIORITY.update({"LAG_HI":88,"LAG_LO":82,"LAG_HI_B":88,"LAG_LO_B":82})
LAG_TW   = {"LAG_HI":0.10,"LAG_LO":0.08}
LAG_TW_B = {**LAG_TW, "LAG_HI_B":0.05, "LAG_LO_B":0.04}

LIQ = dict(liquidity_volume_pct=0.20, max_fill_days=5, liquidity_lookup=liqlk, exit_slippage_tiered=True)
BASE_KW = dict(max_positions=12, min_hold=2, slippage=0.001, init_nav=BOOK,
               deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_by_date,
               open_prices=opens, t1_open_exec=True, **LIQ)

def run_lag(sig, tw, label, extra=None):
    tiers=sorted(set(sig["play_type"]))
    lagts=set(t for t in tiers if t.startswith("LAG"))
    kw=dict(hold_days=25, stop_loss=-0.99,
            stop_exempt_tiers=lagts | set((extra or {}).get("stop_exempt_tiers",set())),
            hold_days_by_tier={**{t:25 for t in lagts}, **(extra or {}).get("hold_days_by_tier",{})},
            tier_position_limit={**{t:12 for t in lagts}, **(extra or {}).get("tier_position_limit",{})})
    if extra and "slot_exempt_tiers" in extra: kw["slot_exempt_tiers"]=extra["slot_exempt_tiers"]
    nav,_=simulate(sig,prices,vni_dates,allowed_tiers=tiers,tier_weights=tw,name=label,**BASE_KW,**kw)
    nav["time"]=pd.to_datetime(nav["time"])
    return nav

def add_capit(sig, navlog, tw, tag):
    elig=pd.read_csv(os.path.join(W,"data","capit_event_elig_full.csv"),parse_dates=["event"])
    basecash=navlog.set_index("time")["cash_pct"]/100.0
    rows,tw2,tiers=[],dict(tw),[]
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
        for t in names: rows.append({"time":d,"ticker":t,"play_type":pt,"ta":500.0,"Close":prices[t][d]})
    extra=dict(hold_days_by_tier={t:60 for t in tiers}, stop_exempt_tiers=set(tiers),
               slot_exempt_tiers=set(tiers), tier_position_limit={t:15 for t in tiers})
    return pd.concat([sig,pd.DataFrame(rows)],ignore_index=True), tw2, extra

def metrics(s):
    s=s.dropna(); r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; dd=(s/s.cummax()-1).min(); sh=r.mean()/r.std()*np.sqrt(252)
    return cagr*100, dd*100, sh, (cagr/abs(dd) if dd<0 else 0)

# ── BAL book arms: reuse saved logs from pt_v4_full_faithful (identical spec) ──
navA     = pd.read_csv(os.path.join(W,"data","pt_v4_full_faithful_nav_A.csv"), parse_dates=["time"])
navA_cap = pd.read_csv(os.path.join(W,"data","pt_v4_full_faithful_nav_A_cap.csv"), parse_dates=["time"])
sA, sAc = navA.set_index("time")["nav"], navA_cap.set_index("time")["nav"]

# ── LAG book arms ───────────────────────────────────────────────────────────
print("[3] LAG arms...")
nav_l    = run_lag(mk_sig(False), LAG_TW,   "LAG121")
nav_lB   = run_lag(mk_sig(True),  LAG_TW_B, "LAG121_B")
sigc, twc, exc = add_capit(mk_sig(False), nav_l, LAG_TW, "L")
nav_lC   = run_lag(sigc, twc, "LAG121_cap", exc)
sigbc, twbc, exbc = add_capit(mk_sig(True), nav_lB, LAG_TW_B, "LB")
nav_lBC  = run_lag(sigbc, twbc, "LAG121_B_cap", exbc)
for lbl,nv in [("LAG121",nav_l),("LAG121_B",nav_lB),("LAG121_cap",nav_lC),("LAG121_B_cap",nav_lBC)]:
    s=nv.set_index("time")["nav"]; c,d,sh,cal=metrics(s)
    print(f"    {lbl:<14}: CAGR {c:6.2f}%  MaxDD {d:6.1f}%  Sharpe {sh:.2f}  NAV {s.iloc[-1]/1e9:.1f}B")

# ── assemble systems ────────────────────────────────────────────────────────
print("\n" + "="*94)
print("V2.1F ABLATION (faithful, two real 25B ledgers, 2014 -> now)")
print("="*94)
combos = [("V2.1 plain (BAL+LAG121)",            sA,  nav_l.set_index("time")["nav"]),
          ("V2.1 + BEAR-rule",                   sA,  nav_lB.set_index("time")["nav"]),
          ("V2.1 + CAPIT",                       sAc, nav_lC.set_index("time")["nav"]),
          ("V2.1F FULL (BEAR-rule + CAPIT)",     sAc, nav_lBC.set_index("time")["nav"])]
print(f"  {'system':<36}{'CAGR':>8}{'MaxDD':>9}{'Sharpe':>8}{'Calmar':>8}{'NAV':>9}")
res={}
for lbl,a,b in combos:
    s=(a+b.reindex(a.index).ffill()).dropna()
    c,d,sh,cal=metrics(s); res[lbl]=(c,d,sh,cal)
    print(f"  {lbl:<36}{c:>7.2f}%{d:>8.1f}%{sh:>8.2f}{cal:>8.2f}{s.iloc[-1]/1e9:>8.1f}B")
print(f"\n  ref V4 faithful 14.20%/Sh1.10 | V4 faithful+capit 17.83%/Sh1.20 | VNI 11.42%/Sh0.69")
for name,nv in [("lag121_b",nav_lB),("lag121_cap",nav_lC),("lag121_b_cap",nav_lBC)]:
    nv.to_csv(os.path.join(W,f"data/pt_v21_{name}.csv"),index=False)
print("  Saved: data/pt_v21_*.csv")
