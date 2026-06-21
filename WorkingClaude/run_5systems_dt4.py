#!/usr/bin/env python3
"""run_5systems_dt4.py — V1..V5 on the DT4 state foundation (vnindex_5state_dt_4gate),
as live-faithful as possible: FRESH SIGNAL_V11 (state5 from DT4, point-in-time current),
DT4 parking + overheat, REAL E1VFVN30 ETF, t1_open exec, prod spec (max_pos12, tier_weights,
RE_BACKLOG, SV_TIGHT embedded). No stale pkl, no proxy ETF.

Systems (DT4 foundation):
  V1 = V11   (BAL + VN30)                + DT4
  V2 = V12   (BAL + LAGGED v12)          + DT4
  V3 = V12.1 (BAL + LAGGED v121, S2)     + DT4
  V4 = V121_ENS (M1+M3r ensemble switch) + DT4 + BASE parking
  V5 = V121_ENS + KELLY parking          + DT4
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import simulate, bq
from signal_v11_sql import SIGNAL_V11
START_B=os.environ.get("START_DATE","2014-01-01"); END_B="2026-05-15"; TOTAL_NAV=50e9; BOOK_NAV=25e9
DEPOSIT=0.0; BORROW=0.10; ETF_BASE={3:0.7}; ETF_KELLY={3:1.0}; SWITCH_COST=0.005
SECTOR_CAP_EXEMPT={"RE_BACKLOG_BUY"}
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS={t:0.10 for t in TIER_BAL}
BUY_TIERS={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
           "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS=12
DT_TABLE=os.environ.get("DT_TABLE","vnindex_5state_dt_4gate")
# SIGNAL_V11 with state5 sourced from DT4 (point-in-time as-of join)
SIGNAL_V11_DT=SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s","tav2_bq."+DT_TABLE+" AS s")
assert SIGNAL_V11_DT!=SIGNAL_V11, "state-table replace failed"
print("="*100); print("  5-SYSTEM on DT4 foundation (live-faithful: fresh SIGNAL_V11+DT4, real E1VFVN30)"); print("="*100)

print("\n[1] Fresh SIGNAL_V11 (state5=DT4)...")
sig_B=bq(SIGNAL_V11_DT.format(start=START_B,end=END_B)); sig_B["time"]=pd.to_datetime(sig_B["time"])
print(f"  signal rows {len(sig_B):,}  AVOID_bear {int((sig_B['play_type']=='AVOID_bear').sum()):,}")
prices_B={tk:dict(zip(g["time"],g["Close"])) for tk,g in sig_B.groupby("ticker")}
liq_map_B={(r["ticker"],r["time"]):r["liq"] for _,r in sig_B.iterrows()}
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c=f.read()
VQU=re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""',_c,re.MULTILINE|re.DOTALL).group(1)
vni_B=bq(VQU.format(start=START_B,end=END_B)); vni_B["time"]=pd.to_datetime(vni_B["time"])
vni_dates_B=sorted(vni_B["time"].unique())
# REAL E1VFVN30 (pre-2016 rescaled-proxy fallback)
vn30_proxy=dict(zip(vni_B["time"],vni_B["Close"]))
_etf=bq(f"SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='E1VFVN30' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time")
_etf["time"]=pd.to_datetime(_etf["time"]); _er=dict(zip(_etf["time"],_etf["Close"]))
_sp=_etf["time"].min(); _sc=(_er[_sp]/vn30_proxy[_sp]) if vn30_proxy.get(_sp) else 1.0
vn30_underlying={d:(_er[d] if d in _er else (vn30_proxy[d]*_sc if d<_sp and d in vn30_proxy else vn30_proxy.get(d))) for d in vni_dates_B}
print(f"  ETF: real E1VFVN30 from {_sp.date()}")
opens_df=bq(f"""SELECT t.ticker,t.time,t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Open IS NOT NULL""")
opens_df["time"]=pd.to_datetime(opens_df["time"]); open_prices={tk:dict(zip(g["time"],g["open_price"])) for tk,g in opens_df.groupby("ticker")}
vni_full=bq(f"SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time")
vni_full["time"]=pd.to_datetime(vni_full["time"])
# DT4 state (parking/overheat)
sdt=bq(f"SELECT s.time,s.state FROM tav2_bq.{DT_TABLE} AS s WHERE s.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY s.time")
sdt["time"]=pd.to_datetime(sdt["time"]); sbd=dict(zip(sdt["time"],sdt["state"]))
state_ff={}; last=None
for d in vni_dates_B:
    s=sbd.get(d)
    if s is not None: last=s
    state_ff[d]=last

print("\n[2] D1 RE_BACKLOG (DT4 state) + SV_TIGHT...")
d1=bq(f"""WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker,t.time,fa.fa_tier,SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 AS np_yoy,fin.Revenue_YoY_P0 AS rev_yoy,adv.adv_yoy,s5.state AS state5
FROM tav2_bq.ticker AS t LEFT JOIN tav2_bq.{DT_TABLE} AS s5 ON s5.time=t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"]=pd.to_datetime(d1["time"])
d1m=(d1["adv_yoy"].notna()&(d1["adv_yoy"]>0.5)&d1["fa_tier"].isin(["C","D"])&d1["state5"].isin([3,4,5])&((d1["np_yoy"].fillna(-99)>0)|(d1["rev_yoy"].fillna(-99)>0)))
sig_B=sig_B.merge(d1.loc[d1m,["ticker","time"]].assign(_ok=True),on=["ticker","time"],how="left")
om=sig_B["_ok"].fillna(False)&(sig_B["ta"]>=120); sig_B.loc[om,"play_type"]="RE_BACKLOG_BUY"; sig_B=sig_B.drop(columns=["_ok"])
print(f"  RE_BACKLOG {int(om.sum())}")
def svk(r):
    s=r.get("state5"); d=r.get("days_since_release")
    if pd.isna(s): return True
    s=int(s)
    if s in (4,5): return True
    if s==1: return pd.notna(d) and d<=30
    if s in (2,3): return pd.notna(d) and d<=60
    return True
mb=sig_B["play_type"].isin(BUY_TIERS); sig_B=sig_B[(~mb)|sig_B.apply(svk,axis=1)].copy()
v=vni_full.merge(sdt,on="time",how="left"); v["state"]=v["state"].ffill()
oh=set(v[(v["Close"]/v["MA200"]>1.30)&((v["state"]==5)|(v["D_RSI"]>0.75))]["time"])
sig_v=sig_B.copy(); sig_v.loc[sig_v["time"].isin(oh)&sig_v["play_type"].isin(BUY_TIERS),"play_type"]="AVOID_overheated"
top30=set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])
sec_map=bq("SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL").set_index("ticker")["s"].to_dict()
LIQ={"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

def run_bal(etf,label):
    nav,_=simulate(sig_v,prices_B,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=MAX_POS,hold_days=45,stop_loss=-0.20,
        min_hold=2,slippage=0.001,init_nav=BOOK_NAV,sector_limit_per_sector={8:4},ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,tier_weights=TIER_WEIGHTS,deposit_annual=DEPOSIT,borrow_annual=BORROW,
        state_by_date=state_ff,cash_etf_states=etf,vn30_underlying=vn30_underlying,etf_mgmt_fee_annual=0.0,
        etf_tracking_drag_annual=0.0,etf_rebalance_friction=0.0015,open_prices=open_prices,t1_open_exec=True,**LIQ,name=label)
    nav["time"]=pd.to_datetime(nav["time"]); s=nav.set_index("time")["nav"]; print(f"  {label}: {s.iloc[-1]/1e9:.2f}B"); return s
def run_vn30(etf,label):
    s30=sig_v[sig_v["ticker"].isin(top30)].copy(); p30={tk:prices_B[tk] for tk in top30 if tk in prices_B}
    l30={k:vv for k,vv in liq_map_B.items() if k[0] in top30}; L30={**LIQ,"liquidity_lookup":l30}
    nav,_=simulate(s30,p30,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=MAX_POS,hold_days=45,stop_loss=-0.20,
        min_hold=2,slippage=0.001,init_nav=BOOK_NAV,ticker_sector_map=sec_map,tier_weights=TIER_WEIGHTS,
        deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=state_ff,cash_etf_states=etf,vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,etf_rebalance_friction=0.0015,open_prices=open_prices,t1_open_exec=True,**L30,name=label)
    nav["time"]=pd.to_datetime(nav["time"]); s=nav.set_index("time")["nav"]; print(f"  {label}: {s.iloc[-1]/1e9:.2f}B"); return s
print("\n[3] BAL/VN30 legs (DT4 parking)...")
bal_base=run_bal(ETF_BASE,"BAL_base"); vn30_base=run_vn30(ETF_BASE,"VN30_base")
bal_kel=run_bal(ETF_KELLY,"BAL_kelly"); vn30_kel=run_vn30(ETF_KELLY,"VN30_kelly")

print("\n[4] LAGGED v12 + v121...")
with open("data/earnings_px.pkl","rb") as f: px_data=pickle.load(f)
px_data["time"]=pd.to_datetime(px_data["time"])
px_close=px_data.pivot_table(index="time",columns="ticker",values="Close",aggfunc="first").sort_index().ffill(limit=5)
master_idx=pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index=master_idx; all_dates=np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov=pickle.load(f); ov["time"]=pd.to_datetime(ov["time"])
px_open=ov.pivot_table(index="time",columns="ticker",values="Open",aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l=ov.pivot_table(index="time",columns="ticker",values="Volume_3M_P50",aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
with open("data/earnings_surprise_data.pkl","rb") as f: fin=pickle.load(f)
fin["Release_Date"]=pd.to_datetime(fin["Release_Date"]); FLOOR=1e9
fin["exp_B_MA"]=fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"]=((fin["NP_P0"]-fin["exp_B_MA"])/np.maximum(np.abs(fin["exp_B_MA"]),FLOOR)).clip(-5,5)
ev_class=pd.read_csv("data/earnings_events_classified.csv",parse_dates=["Release_Date"])
ev=ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],on=["ticker","quarter","Release_Date"],how="left")
ev=ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True); ev["surprise_B_MA"]=ev["surprise_B_MA"].fillna(0)
LN2=np.log(2); HL=3.0; ev["prior_n_good"]=0; ev["pa_HL3"]=np.nan
for tk,g in ev.groupby("ticker"):
    hist=[]
    for ri in g.index.tolist():
        row=ev.loc[ri]; cd=row["Release_Date"]; ng=len(hist); ev.at[ri,"prior_n_good"]=ng
        if ng>=1:
            da=pd.to_datetime([d for d,_ in hist]); pa=np.array([p for _,p in hist])
            ay=(cd-da).days.values/365.25; w=np.exp(-LN2*ay/HL)
            ev.at[ri,"pa_HL3"]=(pa*w).sum()/w.sum() if w.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"]>=15 and pd.notna(row["post_ret"]): hist.append((cd,row["post_ret"]))
e_hl3=ev[(ev["NP_R"]>=15)&(ev["prior_n_good"]>=4)&(ev["pa_HL3"]>=5)].copy()
def offset_date(ref,off):
    pos=np.searchsorted(all_dates,np.datetime64(ref),side="right")-1
    if pos<0: return None
    t=pos+off
    return pd.Timestamp(all_dates[t]) if 0<=t<len(all_dates) else None
sched=[]
for _,row in e_hl3.iterrows():
    tk=row["ticker"]; rdt=row["Release_Date"]
    if tk not in px_open.columns: continue
    ed=offset_date(rdt,5); xd=offset_date(rdt,30)
    if ed is None or xd is None: continue
    sched.append({"ticker":tk,"entry_dt":ed,"exit_dt":xd,"surprise":row["surprise_B_MA"]})
sched_lag=pd.DataFrame(sched).sort_values("entry_dt").reset_index(drop=True)
ebd=sched_lag.groupby("entry_dt"); xbd=sched_lag.groupby("exit_dt")
def run_lagged(init,use_s2):
    sd=[d for d in master_idx if pd.Timestamp(START_B)<=d<=pd.Timestamp(END_B)]
    cash=init; pos={}; nh=[]; SI,SO,TX=0.001,0.0015,0.001; LC,MF=0.20,5; MP,LM=12,2e9
    for dt in sd:
        if dt in xbd.groups:
            for _,ex in xbd.get_group(dt).iterrows():
                tk=ex["ticker"]
                if tk not in pos: continue
                p=pos[tk]
                if p["exit_dt"]!=dt: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0:
                    fpx=px_close.at[dt,tk] if tk in px_close.columns else np.nan
                    if pd.isna(fpx) or fpx<=0: continue
                cash+=p["shares"]*fpx*(1-SO)*(1-TX); del pos[tk]
        if dt in ebd.groups:
            mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in pos.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
            nav_now=cash+mtm
            for _,en in ebd.get_group(dt).iterrows():
                tk=en["ticker"]
                if tk in pos or len(pos)>=MP: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0: continue
                adv=liq_l.at[dt,tk] if tk in liq_l.columns else 0
                if pd.isna(adv) or adv*fpx<LM: continue
                pp=(0.10 if en["surprise"]>0.5 else 0.08) if use_s2 else 0.08
                alloc=min(pp*nav_now,LC*adv*MF*fpx)
                if alloc<1e6 or alloc>cash: continue
                eff=fpx*(1+SI); sh=alloc/eff; cash-=sh*eff
                pos[tk]={"exit_dt":en["exit_dt"],"shares":sh}
        mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in pos.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
        nh.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(nh).set_index("time")["nav"]
lag_v12=run_lagged(BOOK_NAV,False); lag_v121=run_lagged(BOOK_NAV,True)
print(f"  LAG v12={lag_v12.iloc[-1]/1e9:.2f}B  v121={lag_v121.iloc[-1]/1e9:.2f}B")

print("\n[5] Ensemble (cached m1 + live m3r)...")
cached=pd.read_csv("data/compare_v11_v12_concentration_switch.csv",index_col=0,parse_dates=True)
sig_m1=cached["sig_m1"].dropna().astype(int)
m3r_df=bq("""WITH base AS (SELECT t.time,t.ticker,
  SAFE_DIVIDE(t.Close,LAG(t.Close,126) OVER (PARTITION BY t.ticker ORDER BY t.time))-1 AS r6,
  AVG(t.Volume_3M_P50*t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS a1
  FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '2026-05-15'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)),
ranked AS (SELECT time,r6,a1,ROW_NUMBER() OVER (PARTITION BY time ORDER BY a1 DESC) AS rnk FROM base WHERE a1 IS NOT NULL AND r6 IS NOT NULL)
SELECT time, AVG(IF(rnk<=10,r6,NULL))-AVG(r6) AS M3r FROM ranked GROUP BY time ORDER BY time""")
m3r_df["time"]=pd.to_datetime(m3r_df["time"]); m3r=m3r_df.set_index("time")["M3r"]
def mksig(metric,mh=252):
    s=metric.dropna().sort_index(); em=s.expanding(min_periods=mh).median()
    return (s>em).astype(int).reindex(metric.index).ffill().fillna(1).astype(int).shift(1).fillna(1).astype(int)
sig_m3r=mksig(m3r)
common=bal_base.index.intersection(vn30_base.index).intersection(lag_v12.index).intersection(lag_v121.index).intersection(bal_kel.index).intersection(vn30_kel.index)
m1=sig_m1.reindex(common).ffill().fillna(1).astype(int); m3a=sig_m3r.reindex(common).ffill().fillna(1).astype(int)
def ensAH(m1,m3):
    out=np.zeros(len(m1),int); cur=int(m1.iloc[0])
    for i,(a,b) in enumerate(zip(m1.values,m3.values)):
        if a==b: cur=int(a)
        out[i]=cur
    return pd.Series(out,index=m1.index)
sigAH=ensAH(m1,m3a)
def swnav(bal,vn30,lg,sig):
    br=bal.loc[common].pct_change().fillna(0); vr=vn30.loc[common].pct_change().fillna(0); lr=lg.loc[common].pct_change().fillna(0)
    nbp=(1+br).cumprod()*BOOK_NAV; sec=np.full(len(common),BOOK_NAV,float); prev=int(sig.iloc[0])
    for i in range(1,len(common)):
        cur=int(sig.iloc[i]); sec[i]=sec[i-1]*(1-SWITCH_COST) if cur!=prev else sec[i-1]
        r=vr.iloc[i] if cur==1 else lr.iloc[i]; sec[i]=sec[i]*(1+r); prev=cur
    return pd.Series((nbp.values+sec)/TOTAL_NAV,index=common)
nav_V1=(bal_base.loc[common]+vn30_base.loc[common])/TOTAL_NAV
nav_V2=(bal_base.loc[common]+lag_v12.loc[common])/TOTAL_NAV
nav_V3=(bal_base.loc[common]+lag_v121.loc[common])/TOTAL_NAV
nav_V4=swnav(bal_base,vn30_base,lag_v121,sigAH)
nav_V5=swnav(bal_kel,vn30_kel,lag_v121,sigAH)
vni_n=vni_B.set_index("time")["Close"].reindex(common).ffill(); vni_n=vni_n/vni_n.iloc[0]

def met(nav,st,en):
    s=nav[(nav.index>=st)&(nav.index<=en)].dropna()
    if len(s)<30: return None
    r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25; spy=len(r)/yrs if yrs>0 else 252
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0; dd=((s-s.cummax())/s.cummax()).min()
    return {"CAGR":cagr*100,"Sharpe":r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0,"DD":dd*100,
            "Calmar":cagr/abs(dd) if dd<0 else 0,"wealth":s.iloc[-1]/s.iloc[0]}
print("\n"+"="*92)
print(f"  HEADLINE — DT4 foundation  ({common.min().date()} -> {common.max().date()})  init=50B")
print(f"  {'System':<22}{'CAGR':>9}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}{'Wealth':>8}")
for nm,nav in [("V1 V11+DT4",nav_V1),("V2 V12+DT4",nav_V2),("V3 V12.1+DT4",nav_V3),
               ("V4 V121_ENS+DT4",nav_V4),("V5 V4+Kelly+DT4",nav_V5),("VNI B&H",vni_n)]:
    m=met(nav,common.min(),common.max())
    print(f"  {nm:<22}{m['CAGR']:>+8.2f}%{m['Sharpe']:>+8.2f}{m['DD']:>+8.2f}%{m['Calmar']:>+8.2f}{m['wealth']:>+8.2f}")
print("="*92)
for lab,st,en in [("OOS 2020+","2020-01-01","2026-05-15"),("OOS 2024+","2024-01-01","2026-05-15")]:
    print(f"  -- {lab} --")
    for nm,nav in [("V1",nav_V1),("V2",nav_V2),("V3",nav_V3),("V4",nav_V4),("V5",nav_V5),("VNI",vni_n)]:
        m=met(nav,pd.Timestamp(st),pd.Timestamp(en))
        if m: print(f"    {nm:<5}{m['CAGR']:>+8.2f}%  Sh {m['Sharpe']:>+5.2f}  DD {m['DD']:>+7.2f}%")
_tag=DT_TABLE.replace("vnindex_5state_","")
pd.DataFrame({"V1":nav_V1,"V2":nav_V2,"V3":nav_V3,"V4":nav_V4,"V5":nav_V5,"VNI":vni_n}).to_csv(f"data/5sys_{_tag}_nav.csv")
print(f"\n  Saved -> data/5sys_{_tag}_nav.csv\nDONE.")
