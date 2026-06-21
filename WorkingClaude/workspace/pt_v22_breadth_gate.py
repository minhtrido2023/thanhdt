#!/usr/bin/env python3
"""Breadth-gate test on V2.3 production baseline (V2.2 BAL|LAG + CAPIT v2.1).

Gate: block NEW BAL entries when the signal date is in the DEAD-MONEY cell
  (DT5G state>=3) & (breadth_s < LV) & (b_mom10 >= MOM)   [slow bleed; fast
  washout b_mom10<MOM stays OPEN — that cell is a buy, +15.8%/86%].
Breadth = % of ticker_prune above MA200 (MA10 smoothed, causal). Signals close t,
exec t+1 open -> causal.

Variants: G1 = gate all TIER_BAL entries; G2 = gate momentum tiers only.
Baseline = production V2.3 (NO exbull suppression — not live).
--grid: robustness grid + IS/OOS walk-forward on the BAL arm (no capit, faster).
"""
import sys, os, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate
BOOK=25_000_000_000
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS={t:0.10 for t in TIER_BAL}
BUY_TIERS={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A","MOMENTUM_S_N",
           "DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY","COMPOUNDER_BUY","S_PRO"}
MOM_TIERS={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S"}  # G2: momentum-only gate

GRID = "--grid" in sys.argv

EVENTS_V21=[
    ("2014-05-08",1,False,0.0,False),("2015-08-24",3,False,0.0,False),
    ("2016-01-18",3,True,0.0,False),("2018-05-28",1,False,0.0,False),
    ("2020-03-12",2,False,-24.9,False),("2022-04-20",1,False,0.0,False),
    ("2022-06-20",2,True,-22.8,True),("2022-09-29",2,True,-26.3,False),
    ("2023-10-31",1,False,0.0,False),("2024-04-19",4,False,0.0,False),
    ("2024-08-05",1,True,0.0,False),("2025-04-03",4,False,0.0,False),
    ("2025-10-20",3,False,0.0,False),("2026-03-09",3,False,0.0,False),
]
def size_of_v21(st,gr,dd52w=0.0,vn_cooling=False):
    if st==1: base=1.0
    elif st==3: base=0.75
    elif st in (4,5): base=0.5
    elif st==2: base=0.5 if (dd52w>-25.0 or vn_cooling) else 0.0
    else: base=0.5
    return base*(0.5 if gr else 1.0)

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

# --- breadth compass panel (causal) ---
bc=pd.read_csv(os.path.join(W,"data","breadth_compass_panel.csv"),parse_dates=["time"])
bc=bc.sort_values("time").reset_index(drop=True)
bc["b_mom10"]=bc["breadth_s"]-bc["breadth_s"].shift(10)
bc["b_mom40"]=bc["breadth_s"]-bc["breadth_s"].shift(40)
def deadmoney_dates(lv,mom):
    m=(bc["state"]>=3)&(bc["breadth_s"]<lv)&(bc["b_mom10"]>=mom)
    return set(bc.loc[m.fillna(False),"time"])
def bleed_dates(mom40,lv_max=1.0):
    m=(bc["state"]>=3)&(bc["b_mom40"]<mom40)&(bc["breadth_s"]<lv_max)
    return set(bc.loc[m.fillna(False),"time"])

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
# NOTE: no EXBULL suppression here — baseline = live production V2.3
sec_map=sig_b.dropna(subset=["sec"]).drop_duplicates("ticker").set_index("ticker")["sec"].to_dict()
sig_mom=sig_b[["time","ticker","play_type","ta","Close"]].copy()

def gated(sig,dm,tiers):
    s=sig.copy()
    m=s["time"].isin(dm)&s["play_type"].isin(tiers)
    s.loc[m,"play_type"]="AVOID_deadmoney"
    return s,int(m.sum())

# --- LAG signals (unchanged) ---
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

LIQ_PCT=0.20; MAX_FILL_DAYS=5
def addcap_v21(sig,navlog,tw,tag):
    elig=pd.read_csv(os.path.join(W,"data","capit_event_elig_v21c.csv"),parse_dates=["event"])
    bcsh=(navlog.set_index("time")["cash_pct"]/100.0).clip(lower=0)
    r2,tw2,ts=[],dict(tw),[]
    for i,(ds,st,gr,dd52w,vn_cool) in enumerate(EVENTS_V21):
        d=pd.Timestamp(ds); sz=size_of_v21(st,gr,dd52w,vn_cool)
        if sz<=0.0: continue
        e=elig[elig["event"]==d].copy()
        e=e[[t in prices and d in prices[t] for t in e["ticker"]]]
        g_gold=e[e["pbz"]<-1]; c=e[e["pbz"]<0]
        pick=g_gold if len(g_gold)>=3 else (c if len(c)>=3 else e)
        pick=pick.nsmallest(15,"pbz") if len(pick)>15 else pick
        names=list(pick["ticker"])
        if len(names)<3: continue
        pos=bcsh.index.searchsorted(d); cf=float(bcsh.iloc[max(0,pos-2):pos+1].mean())
        wt=sz*max(cf,0.0)
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
def combo(a,b):
    return (a+b.reindex(a.index).ffill()).dropna()
def report(label,s):
    for wlbl,ws in [("FULL ","2014-01-01"),("2022+","2022-01-01"),("2025+","2025-01-01")]:
        sw=s[s.index>=pd.Timestamp(ws)]
        if len(sw)<2: continue
        c,d,sh,cal=met(sw)
        print(f"  {label} {wlbl}: CAGR {c:6.2f}%  MaxDD {d:6.1f}%  Sharpe {sh:5.2f}  Calmar {cal:5.2f}")
def peryear(s):
    y=s.resample("YE").last(); y0=s.resample("YE").first()
    return ((y/y0-1)*100).round(1)

# ============================================================================
LV0,MOM0=0.35,-0.06
DM0=deadmoney_dates(LV0,MOM0)
print(f"dead-money sessions (lv<{LV0:.0%}, mom10>={MOM0:+.0%}): {len(DM0)}")
yrs=pd.Series(sorted(DM0)).dt.year.value_counts().sort_index()
print("  by year:", dict(yrs))

if not GRID:
    print("\nrunning LAG arm (shared)...")
    lagB=runl(sig_lag,LAG_TW,"LAG")
    sl,tl,el=addcap_v21(sig_lag,lagB,LAG_TW,"L")
    lagC=runl(sl,tl,"LAG_cap",el)
    sLc=lagC.set_index("time")["nav"]

    BL0=bleed_dates(-0.10)
    results={}
    for name,tiers,dset in [("BASE",None,None),("G1_all",set(TIER_BAL),DM0),
                            ("G2_mom",MOM_TIERS,DM0),("G3_bleed",MOM_TIERS,BL0)]:
        if tiers is None: sg,nblk=sig_mom,0
        else: sg,nblk=gated(sig_mom,dset,tiers)
        balB=runb(sg,TIER_BAL,f"BAL_{name}",TIER_WEIGHTS)
        sb,tb,eb=addcap_v21(sg,balB,TIER_WEIGHTS,"B")
        balC=runb(sb,TIER_BAL+[t for t in tb if t.startswith("CAP")],f"BAL_{name}_cap",tb,eb)
        sAc=balC.set_index("time")["nav"]
        results[name]=(combo(sAc,sLc),nblk)
        print(f"\n[{name}] blocked signals: {nblk}")
        report(name,results[name][0])

    print("\n=== per-year combined (V2.3) ===")
    tab=pd.DataFrame({k:peryear(v[0]) for k,v in results.items()})
    tab.index=tab.index.year
    for k in results:
        if k!="BASE": tab[k+"-B"]=(tab[k]-tab["BASE"]).round(1)
    print(tab.to_string())
    for k,(s,_) in results.items():
        s.to_frame("nav").to_csv(os.path.join(W,"data",f"bgate_{k}.csv"))
else:
    # robustness grid + walk-forward on BAL arm only (no capit/LAG, faster)
    print("\nbaseline BAL arm...")
    balB=runb(sig_mom,TIER_BAL,"BAL_BASE",TIER_WEIGHTS)
    s0=balB.set_index("time")["nav"]
    def iswin(s): return s[(s.index>=pd.Timestamp("2014-01-01"))&(s.index<pd.Timestamp("2020-01-01"))]
    def ooswin(s): return s[s.index>=pd.Timestamp("2020-01-01")]
    b_is,b_oos=met(iswin(s0)),met(ooswin(s0))
    print(f"  BASE IS  2014-19: CAGR {b_is[0]:.2f}% DD {b_is[1]:.1f}% Cal {b_is[3]:.2f}")
    print(f"  BASE OOS 2020+ : CAGR {b_oos[0]:.2f}% DD {b_oos[1]:.1f}% Cal {b_oos[3]:.2f}")
    print(f"\nBLEED-gate grid (block MOM_TIERS in state>=3 & b_mom40<thr & breadth_s<lvmax)")
    print(f"{'mom40':>7}{'lvmax':>7}{'nBL':>6}{'blk':>6} | {'FULL dC':>8}{'dDD':>6}{'dCal':>6} | {'IS dC':>7}{'IS dCal':>8} | {'OOS dC':>7}{'OOS dCal':>9}")
    rows=[]
    for mom40 in (-0.08,-0.10,-0.12,-0.15):
        for lvmax in (0.55,1.0):
            dm=bleed_dates(mom40,lvmax)
            sg,nblk=gated(sig_mom,dm,MOM_TIERS)
            nav=runb(sg,TIER_BAL,f"BAL_bl{mom40}_{lvmax}",TIER_WEIGHTS)
            s1=nav.set_index("time")["nav"]
            f0,f1=met(s0),met(s1)
            i0,i1=met(iswin(s0)),met(iswin(s1))
            o0,o1=met(ooswin(s0)),met(ooswin(s1))
            rows.append(dict(mom40=mom40,lvmax=lvmax,nbl=len(dm),blk=nblk,
                dC=f1[0]-f0[0],dDD=f1[1]-f0[1],dCal=f1[3]-f0[3],
                is_dC=i1[0]-i0[0],is_dCal=i1[3]-i0[3],oos_dC=o1[0]-o0[0],oos_dCal=o1[3]-o0[3]))
            r=rows[-1]
            print(f"{mom40:>7.2f}{lvmax:>7.2f}{r['nbl']:>6}{r['blk']:>6} | {r['dC']:>+8.2f}{r['dDD']:>+6.1f}{r['dCal']:>+6.2f} | {r['is_dC']:>+7.2f}{r['is_dCal']:>+8.2f} | {r['oos_dC']:>+7.2f}{r['oos_dCal']:>+9.2f}")
    g=pd.DataFrame(rows); g.to_csv(os.path.join(W,"data","bgate_grid.csv"),index=False)
    best_is=g.loc[g["is_dCal"].idxmax()]
    print(f"\nwalk-forward: best-on-IS = mom40={best_is['mom40']:.2f} lvmax={best_is['lvmax']:.2f} "
          f"(IS dCal {best_is['is_dCal']:+.2f}) -> OOS dCAGR {best_is['oos_dC']:+.2f}pp, OOS dCal {best_is['oos_dCal']:+.2f}")
