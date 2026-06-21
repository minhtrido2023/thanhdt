#!/usr/bin/env python3
"""run_prodspec_v12_state.py — PROD-SPEC: does V12 with DT4 beat V12 with LIVE/TQ34b?
V12 = BAL + LAGGED (no VN30, no ensemble). Only the BAL-leg parking state varies:
  TQ34b (v3.4b), LIVE (BQ vnindex_5state), DT4 (vnindex_5state_dt_10_25_25), all BASE {3:0.7}.
Shows V12 (LAG no-S2) and V12.1 (LAG +S2). Full prod spec (max_pos=12, tier_weights,
RE_BACKLOG, SV_TIGHT, t1_open_exec).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import simulate, bq
START_B="2014-01-01"; END_B="2026-05-15"; TOTAL_NAV=50e9; BOOK_NAV=25e9
DEPOSIT=0.0; BORROW=0.10; ETF_BASE={3:0.7}
SECTOR_CAP_EXEMPT={"RE_BACKLOG_BUY"}
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11={t:0.10 for t in TIER_BAL}
BUY_TIERS_V11={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
               "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS=12
print("="*100); print("  PROD-SPEC V12 state test: TQ34b vs LIVE vs DT4 (BAL parking)"); print("="*100)
print("\n[1] Load...")
with open("ba_v11_unified_12y_sig.pkl","rb") as f: sig_B=pickle.load(f)
sig_B["time"]=pd.to_datetime(sig_B["time"]); sig_B=sig_B[(sig_B["time"]>=START_B)&(sig_B["time"]<=END_B)].copy()
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c=f.read()
VQU=re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""',_c,re.MULTILINE|re.DOTALL).group(1)
prices_B={tk:dict(zip(g["time"],g["Close"])) for tk,g in sig_B.groupby("ticker")}
liq_map_B={(r["ticker"],r["time"]):r["liq"] for _,r in sig_B.iterrows()}
vni_B=bq(VQU.format(start=START_B,end=END_B)); vni_B["time"]=pd.to_datetime(vni_B["time"])
vni_dates_B=sorted(vni_B["time"].unique()); vn30_underlying=dict(zip(vni_B["time"],vni_B["Close"]))
opens_df=bq(f"""SELECT t.ticker,t.time,t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Open IS NOT NULL""")
opens_df["time"]=pd.to_datetime(opens_df["time"])
open_prices={tk:dict(zip(g["time"],g["open_price"])) for tk,g in opens_df.groupby("ticker")}
vni_full=bq(f"""SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"]=pd.to_datetime(vni_full["time"])

def load_ff_csv(csv):
    sdf=pd.read_csv(csv); sdf["time"]=pd.to_datetime(sdf["time"])
    return sdf[(sdf["time"]>=START_B)&(sdf["time"]<=END_B)][["time","state"]]
def load_ff_bq():
    sdf=bq(f"SELECT s.time,s.state FROM tav2_bq.vnindex_5state AS s WHERE s.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY s.time")
    sdf["time"]=pd.to_datetime(sdf["time"]); return sdf[["time","state"]]
def to_ff(sdf):
    sbd=dict(zip(sdf["time"],sdf["state"])); ff={}; last=None
    for d in vni_dates_B:
        s=sbd.get(d)
        if s is not None: last=s
        ff[d]=last
    return ff
sdf_tq=load_ff_csv("vnindex_5state_tam_quan_v3_4b_full_history.csv")
sdf_dt=load_ff_csv("vnindex_5state_dt_10_25_25.csv")
sdf_live=load_ff_bq()
ff_tq=to_ff(sdf_tq); ff_dt=to_ff(sdf_dt); ff_live=to_ff(sdf_live)
# confirm LIVE vs TQ identity
both=set(sdf_tq["time"]).intersection(set(sdf_live["time"]))
m=pd.merge(sdf_tq,sdf_live,on="time",suffixes=("_tq","_live"))
ndiff=int((m["state_tq"]!=m["state_live"]).sum())
print(f"  LIVE vs TQ34b state diffs: {ndiff} / {len(m)}  (0 => LIVE==v3.4b)")
ddiff=int((pd.merge(sdf_tq,sdf_dt,on='time',suffixes=('_tq','_dt')).eval('state_tq!=state_dt')).sum())
print(f"  DT vs TQ34b state diffs:   {ddiff}")

# D1 RE_BACKLOG
print("\n[2] D1 RE_BACKLOG + SV_TIGHT...")
d1=bq(f"""
WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker,t.time,fa.fa_tier,SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 AS np_yoy,fin.Revenue_YoY_P0 AS rev_yoy,adv.adv_yoy,s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time=t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"]=pd.to_datetime(d1["time"])
d1_mask=(d1["adv_yoy"].notna()&(d1["adv_yoy"]>0.5)&d1["fa_tier"].isin(["C","D"])&d1["state5"].isin([3,4,5])
         &((d1["np_yoy"].fillna(-99)>0)|(d1["rev_yoy"].fillna(-99)>0)))
d1_q=d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True)
sig_B=sig_B.merge(d1_q,on=["ticker","time"],how="left")
omask=sig_B["_d1_ok"].fillna(False)&(sig_B["ta"]>=120); sig_B.loc[omask,"play_type"]="RE_BACKLOG_BUY"
sig_B=sig_B.drop(columns=["_d1_ok"])
def sv_tight_keep(row):
    s=row.get("state5"); days=row.get("days_since_release")
    if pd.isna(s): return True
    s=int(s)
    if s in (4,5): return True
    if s==1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb=sig_B["play_type"].isin(BUY_TIERS_V11); keep=(~mb)|sig_B.apply(sv_tight_keep,axis=1)
sig_B=sig_B[keep].copy(); print(f"  After SV_TIGHT: {len(sig_B):,}")

def make_sig_overheat(sdf):
    v=vni_full.merge(sdf,on="time",how="left"); v["state"]=v["state"].ffill()
    v["overheat"]=((v["Close"]/v["MA200"]>1.30)&((v["state"]==5)|(v["D_RSI"]>0.75)))
    oh=set(v[v["overheat"]]["time"]); sv=sig_B.copy()
    sv.loc[sv["time"].isin(oh)&sv["play_type"].isin(BUY_TIERS_V11),"play_type"]="AVOID_overheated"
    return sv
sig_tq=make_sig_overheat(sdf_tq); sig_dt=make_sig_overheat(sdf_dt); sig_live=make_sig_overheat(sdf_live)
sec_map=bq("""SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t
WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ={"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}
def run_bal(sig_use,state_ff,label):
    nav,_=simulate(sig_use,prices_B,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=MAX_POS,hold_days=45,
        stop_loss=-0.20,min_hold=2,slippage=0.001,init_nav=BOOK_NAV,sector_limit_per_sector={8:4},
        ticker_sector_map=sec_map,sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=state_ff,cash_etf_states=ETF_BASE,
        vn30_underlying=vn30_underlying,etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,open_prices=open_prices,t1_open_exec=True,**LIQ,name=label)
    nav["time"]=pd.to_datetime(nav["time"]); s=nav.set_index("time")["nav"]; print(f"  {label}: {s.iloc[-1]/1e9:.2f}B"); return s
print("\n[3] BAL legs (BASE parking, 3 states)...")
bal_tq=run_bal(sig_tq,ff_tq,"BAL_TQ"); bal_live=run_bal(sig_live,ff_live,"BAL_LIVE"); bal_dt=run_bal(sig_dt,ff_dt,"BAL_DT")

# LAGGED v12 (no S2) + v121 (S2)
print("\n[4] LAGGED...")
with open("earnings_px.pkl","rb") as f: px_data=pickle.load(f)
px_data["time"]=pd.to_datetime(px_data["time"])
px_close=px_data.pivot_table(index="time",columns="ticker",values="Close",aggfunc="first").sort_index().ffill(limit=5)
master_idx=pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index=master_idx; all_dates=np.array(master_idx)
with open("lagged_pos_ov.pkl","rb") as f: ov=pickle.load(f); ov["time"]=pd.to_datetime(ov["time"])
px_open=ov.pivot_table(index="time",columns="ticker",values="Open",aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l=ov.pivot_table(index="time",columns="ticker",values="Volume_3M_P50",aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
with open("earnings_surprise_data.pkl","rb") as f: fin=pickle.load(f)
fin["Release_Date"]=pd.to_datetime(fin["Release_Date"]); FLOOR=1e9
fin["exp_B_MA"]=fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"]=((fin["NP_P0"]-fin["exp_B_MA"])/np.maximum(np.abs(fin["exp_B_MA"]),FLOOR)).clip(-5,5)
ev_class=pd.read_csv("earnings_events_classified.csv",parse_dates=["Release_Date"])
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
def run_lagged(init_nav,use_s2):
    sim_days=[d for d in master_idx if pd.Timestamp(START_B)<=d<=pd.Timestamp(END_B)]
    cash=init_nav; positions={}; nh=[]; SLIP_IN,SLIP_OUT,TAX=0.001,0.0015,0.001; LIQ_CAP,MAX_FILL=0.20,5; LAGMP,LIQMIN=12,2e9
    for dt in sim_days:
        if dt in xbd.groups:
            for _,ex in xbd.get_group(dt).iterrows():
                tk=ex["ticker"]
                if tk not in positions: continue
                pos=positions[tk]
                if pos["exit_dt"]!=dt: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0:
                    fpx=px_close.at[dt,tk] if tk in px_close.columns else np.nan
                    if pd.isna(fpx) or fpx<=0: continue
                gross=pos["shares"]*fpx*(1-SLIP_OUT); cash+=gross*(1-TAX); del positions[tk]
        if dt in ebd.groups:
            mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
            nav_now=cash+mtm
            for _,en in ebd.get_group(dt).iterrows():
                tk=en["ticker"]
                if tk in positions or len(positions)>=LAGMP: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0: continue
                adv=liq_l.at[dt,tk] if tk in liq_l.columns else 0
                if pd.isna(adv) or adv*fpx<LIQMIN: continue
                pos_pct=(0.10 if en["surprise"]>0.5 else 0.08) if use_s2 else 0.08
                target=pos_pct*nav_now; cap=LIQ_CAP*adv*MAX_FILL*fpx; alloc=min(target,cap)
                if alloc<1e6 or alloc>cash: continue
                eff=fpx*(1+SLIP_IN); sh=alloc/eff; cash-=sh*eff
                positions[tk]={"entry_dt":dt,"exit_dt":en["exit_dt"],"shares":sh,"entry_px":fpx}
        mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
        nh.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(nh).set_index("time")["nav"]
lag_v12=run_lagged(BOOK_NAV,False); lag_v121=run_lagged(BOOK_NAV,True)
print(f"  LAG v12={lag_v12.iloc[-1]/1e9:.2f}B  v121={lag_v121.iloc[-1]/1e9:.2f}B")

common=bal_tq.index.intersection(bal_live.index).intersection(bal_dt.index).intersection(lag_v12.index).intersection(lag_v121.index)
def metrics(nav,st,en):
    s=nav[(nav.index>=st)&(nav.index<=en)].dropna()
    if len(s)<30: return None
    r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25; spy=len(r)/yrs if yrs>0 else 252
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0; dd=((s-s.cummax())/s.cummax()).min()
    return {"CAGR":cagr*100,"Sharpe":r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0,"DD":dd*100,"Calmar":cagr/abs(dd) if dd<0 else 0}
periods=[("FULL","2014-01-01","2026-05-15"),("IS","2014-01-01","2019-12-31"),
         ("OOS20","2020-01-01","2026-05-15"),("OOS24","2024-01-01","2026-05-15")]
arms={
 "V12  +TQ34b":  (bal_tq,  lag_v12), "V12  +LIVE":(bal_live,lag_v12), "V12  +DT4":(bal_dt,lag_v12),
 "V12.1+TQ34b":  (bal_tq,  lag_v121),"V12.1+LIVE":(bal_live,lag_v121),"V12.1+DT4":(bal_dt,lag_v121),
}
print("\n"+"="*100)
print(f"  {'Arm':<16}{'Full':>8}{'IS':>8}{'OOS20':>8}{'OOS24':>8}{'DD':>8}{'Calmar':>7}{'Sharpe':>7}")
print("-"*100)
for name,(b,l) in arms.items():
    nav=(b.loc[common]+l.loc[common])/TOTAL_NAV
    mm={pl:metrics(nav,pd.Timestamp(s),pd.Timestamp(e)) for pl,s,e in periods}
    print(f"  {name:<16}{mm['FULL']['CAGR']:>+7.2f}%{mm['IS']['CAGR']:>+7.2f}%{mm['OOS20']['CAGR']:>+7.2f}%"
          f"{mm['OOS24']['CAGR']:>+7.2f}%{mm['FULL']['DD']:>+7.2f}%{mm['FULL']['Calmar']:>+6.2f}{mm['FULL']['Sharpe']:>+7.2f}")
print("="*100)
print("DONE.")
