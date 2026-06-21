# -*- coding: utf-8 -*-
"""pt_lagvn30_audit_2014.py — standalone "LAGGED + VN30-when-idle" monoculture, AUDIT edition.
ONE 50B wallet: LAGGED HL_3y earnings plays take priority; VN30 (top-30) momentum fills the idle
capacity (LAGGED is active ~40% of the time, so its idle cash works in VN30 momentum instead of
sitting in ETF). Per-name VND kept comparable to the standalone 25B books (momentum 5%/name, LAG
5%/4% — the one-wallet convention). DT5G state, T+1 Open, all BQ. Output: data/lagvn30_audit_2014_now.csv.
"""
import os, sys, io, pickle, bisect
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v11_sql import SIGNAL_V11
from pt_dates import detect_end_date
from regime_size_overlay import apply_regime_size
from audit_lib import emit_audit

START_DATE="2014-01-02"; END_DATE=detect_end_date()
STATE_TABLE="tav2_bq.vnindex_5state_dt5g_live"   # DT5G default (user 2026-06-13)
# UNIV: "vn30" = momentum leg restricted to top-30 (original); "full" = full prune universe (BAL).
UNIV=(sys.argv[1].lower() if len(sys.argv)>1 else "vn30"); assert UNIV in ("vn30","full")
SEC_CAP=6 if UNIV=="vn30" else 4   # full-BAL matches V2.3 BAL sector-8 cap 4
NAV=50e9; MOM_W=0.05; LAG_HI_W=0.05; LAG_LO_W=0.04; MAX_POS=24
MOMLBL="VN30(top30)" if UNIV=="vn30" else "full-BAL"
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
BUY_TIERS_V11={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
               "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
AUDIT_PATH=os.path.join(WORKDIR,"data",("lagvn30" if UNIV=="vn30" else "lagbal")+"_audit_2014_now.csv")
print("="*92); print(f" LAGGED + {MOMLBL}(idle) one-wallet 50B AUDIT {START_DATE}->{END_DATE}  DT5G, T+1 Open, BQ"); print("="*92)

# ---- momentum signals (DT5G) ----
print("[2] momentum signals + D1 + SV_TIGHT + regime_size...")
sig=bq(SIGNAL_V11.format(start=START_DATE,end=END_DATE)); sig["time"]=pd.to_datetime(sig["time"]); assert len(sig)<1_990_000
rel=bq(f"""SELECT tf.ticker,tf.Release_Date FROM tav2_bq.ticker_financial tf
WHERE tf.Release_Date BETWEEN DATE_SUB(DATE '{START_DATE}',INTERVAL 120 DAY) AND DATE '{END_DATE}'""")
rel["Release_Date"]=pd.to_datetime(rel["Release_Date"])
rbt=rel.sort_values(["ticker","Release_Date"]).groupby("ticker")["Release_Date"].apply(list).to_dict()
ds=np.empty(len(sig))
for i,(tk,t) in enumerate(zip(sig["ticker"].values,sig["time"].values)):
    arr=rbt.get(tk)
    if not arr: ds[i]=np.nan; continue
    j=bisect.bisect_right(arr,pd.Timestamp(t)); ds[i]=np.nan if j==0 else (pd.Timestamp(t)-arr[j-1]).days
sig["days_since_release"]=ds
state_df=bq(f"SELECT s.time,s.state FROM {STATE_TABLE} s WHERE s.time<=DATE '{END_DATE}'")
state_df["time"]=pd.to_datetime(state_df["time"]); state_by_date=dict(zip(state_df["time"],state_df["state"]))
vni_full=bq(f"""SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
vni_full["time"]=pd.to_datetime(vni_full["time"])
vni_full["oh"]=(vni_full["Close"]/vni_full["MA200"]>1.30)&((vni_full["time"].map(state_by_date)==5)|(vni_full["D_RSI"]>0.75))
overheat_dates=set(vni_full[vni_full["oh"]]["time"]); sig["state"]=sig["time"].map(state_by_date)
d1=bq(f"""WITH adv AS (SELECT f.ticker,f.time f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 adv_yoy,
  LEAD(f.time) OVER(PARTITION BY f.ticker ORDER BY f.time) nx FROM tav2_bq.ticker_financial f),
fa AS (SELECT f.ticker,f.time f_time,f.tier ft,LEAD(f.time) OVER(PARTITION BY f.ticker ORDER BY f.time) nx FROM tav2_bq.fa_ratings f),
fin AS (SELECT f.ticker,f.time ft,f.Revenue_YoY_P0 ry,LEAD(f.time) OVER(PARTITION BY f.ticker ORDER BY f.time) nx FROM tav2_bq.ticker_financial f)
SELECT t.ticker,t.time,fa.ft fa_tier,SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 np_yoy,fin.ry rev_yoy,adv.adv_yoy,s5.state state5
FROM tav2_bq.ticker t LEFT JOIN {STATE_TABLE} s5 ON s5.time=t.time
LEFT JOIN fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.nx IS NULL OR t.time<fa.nx)
LEFT JOIN fin ON fin.ticker=t.ticker AND t.time>=fin.ft AND (fin.nx IS NULL OR t.time<fin.nx)
LEFT JOIN adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.nx IS NULL OR t.time<adv.nx)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)""")
d1["time"]=pd.to_datetime(d1["time"])
d1m=(d1["adv_yoy"].notna()&(d1["adv_yoy"]>0.5)&d1["fa_tier"].isin(["C","D"])&d1["state5"].isin([3,4,5])
     &((d1["np_yoy"].fillna(-99)>0)|(d1["rev_yoy"].fillna(-99)>0)))
sig=sig.merge(d1.loc[d1m,["ticker","time"]].assign(_ok=True),on=["ticker","time"],how="left")
sig.loc[sig["_ok"].fillna(False)&(sig["ta"]>=120),"play_type"]="RE_BACKLOG_BUY"; sig=sig.drop(columns=["_ok"])
_st=sig["state"];_dy=sig["days_since_release"];keep=pd.Series(True,index=sig.index)
keep[_st==1]=(_dy.notna()&(_dy<=30))[_st==1];keep[_st.isin([2,3])]=(_dy.notna()&(_dy<=60))[_st.isin([2,3])]
mb=sig["play_type"].isin(BUY_TIERS_V11);sig_f=sig[(~mb)|keep].copy()
sig_f.loc[sig_f["time"].isin(overheat_dates)&sig_f["play_type"].isin(BUY_TIERS_V11),"play_type"]="AVOID_overheated"
sig_f,RS=apply_regime_size(sig_f,START_DATE,END_DATE,bq,base_tiers=TIER_BAL,full_size=MOM_W,weak_size=MOM_W/2)

# ---- common data + top30 ----
print("[3] prices/opens/sector/top30...")
opens_df=bq(f"""SELECT t.ticker,t.time,t.Open op FROM tav2_bq.ticker t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' AND t.Open IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)""")
opens_df["time"]=pd.to_datetime(opens_df["time"]); assert len(opens_df)<1_990_000
open_prices={tk:dict(zip(g["time"],g["op"])) for tk,g in opens_df.groupby("ticker")}
prices={tk:dict(zip(g["time"],g["Close"])) for tk,g in sig_f.groupby("ticker")}
liq_map=dict(zip(zip(sig_f["ticker"],sig_f["time"]),sig_f["liq"]))
vni=bq(VNI_QUERY.format(start=START_DATE,end=END_DATE)); vni["time"]=pd.to_datetime(vni["time"])
vni_dates=sorted(vni["time"].unique()); vni_close_by_date=dict(zip(vni["time"],vni["Close"]))
sec_map=bq("""SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) s FROM tav2_bq.ticker t
WHERE t.ICB_Code IS NOT NULL AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)""").set_index("ticker")["s"].to_dict()
top30=set(bq("""SELECT t.ticker FROM tav2_bq.ticker t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])
state_ff={};last=None
for d in vni_dates:
    s=state_by_date.get(d); last=s if s is not None else last; state_ff[d]=last

# momentum leg: top30 (VN30) or full prune universe (BAL)
sig_mom=(sig_f[sig_f["ticker"].isin(top30)] if UNIV=="vn30" else sig_f)[["time","ticker","play_type","ta","Close"]].copy()

# ---- LAGGED schedule + BQ prices ----
print("[4] LAGGED HL_3y schedule (BQ prices)...")
cal=bq(VNI_QUERY.format(start="2013-06-01",end=END_DATE)); cal["time"]=pd.to_datetime(cal["time"])
all_dates=np.array(sorted(cal["time"].unique()),dtype="datetime64[ns]")
with open("earnings_surprise_data.pkl","rb") as f: fin=pickle.load(f)
fin["Release_Date"]=pd.to_datetime(fin["Release_Date"]); FLOOR=1e9
fin["exp_B_MA"]=fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"]=((fin["NP_P0"]-fin["exp_B_MA"])/np.maximum(np.abs(fin["exp_B_MA"]),FLOOR)).clip(-5,5)
evc=pd.read_csv("earnings_events_classified.csv",parse_dates=["Release_Date"])
evm=evc.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],on=["ticker","quarter","Release_Date"],how="left")
evm=evm.sort_values(["ticker","Release_Date"]).reset_index(drop=True); evm["surprise_B_MA"]=evm["surprise_B_MA"].fillna(0)
LN2=np.log(2);HL=3.0; evm["prior_n_good"]=0; evm["pa_HL3"]=np.nan
for tk,g in evm.groupby("ticker"):
    h=[]
    for ri in g.index.tolist():
        row=evm.loc[ri]; cur=row["Release_Date"]; evm.at[ri,"prior_n_good"]=len(h)
        if h:
            da=pd.to_datetime([d for d,_ in h]); pa=np.array([p for _,p in h])
            w=np.exp(-LN2*((cur-da).days.values/365.25)/HL); evm.at[ri,"pa_HL3"]=(pa*w).sum()/w.sum() if w.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"]>=15 and pd.notna(row["post_ret"]): h.append((cur,row["post_ret"]))
e3=evm[(evm["NP_R"]>=15)&(evm["prior_n_good"]>=4)&(evm["pa_HL3"]>=5)].copy()
sw_,ew_=pd.Timestamp(START_DATE),pd.Timestamp(END_DATE)
def offd(ref,off):
    pos=np.searchsorted(all_dates,np.datetime64(ref),side="right")-1; t=pos+off
    return pd.Timestamp(all_dates[t]) if 0<=t<len(all_dates) else None
lag_cand=[]
for _,row in e3.iterrows():
    en=offd(row["Release_Date"],5)
    if en is None or en<sw_ or en>ew_: continue
    sd=offd(en,-1)
    if sd is None: continue
    lag_cand.append({"sd":sd,"ticker":row["ticker"],"surprise":row["surprise_B_MA"]})
lag_universe=sorted({c["ticker"] for c in lag_cand})
chunks=[lag_universe[i:i+250] for i in range(0,len(lag_universe),250)]; parts=[]
for ch in chunks:
    inl=",".join(f"'{t}'" for t in ch)
    parts.append(bq(f"""SELECT t.ticker,t.time,t.Open,t.Close,t.Volume_3M_P50 FROM tav2_bq.ticker t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' AND t.ticker IN ({inl})"""))
lagpx=pd.concat(parts,ignore_index=True); lagpx["time"]=pd.to_datetime(lagpx["time"])
for tk,g in lagpx.groupby("ticker"):
    gc=g[g["Close"].notna()]
    prices.setdefault(tk,{}).update(dict(zip(gc["time"],gc["Close"].astype(float))))
    go=g[g["Open"].notna()]
    open_prices.setdefault(tk,{}).update(dict(zip(go["time"],go["Open"].astype(float))))
    gl=g[g["Volume_3M_P50"].notna()&g["Close"].notna()]
    for d,a,px in zip(gl["time"],gl["Volume_3M_P50"].astype(float),gl["Close"].astype(float)): liq_map[(tk,d)]=a*px
lag_rows=[]
for c in lag_cand:
    px_sd=prices.get(c["ticker"],{}).get(c["sd"],np.nan)
    if pd.isna(px_sd) or px_sd<=0: continue
    lag_rows.append({"time":c["sd"],"ticker":c["ticker"],"play_type":"LAG_HI" if c["surprise"]>0.5 else "LAG_LO","ta":400.0,"Close":float(px_sd)})
sig_lag=pd.DataFrame(lag_rows,columns=["time","ticker","play_type","ta","Close"])
print(f"  {MOMLBL} momentum rows {len(sig_mom)} | LAGGED signals {len(sig_lag)}")

# ---- merge into one book; LAGGED priority above MEGA ----
shn.TIER_PRIORITY.update({"LAG_HI":110,"LAG_LO":105})
sig_all=pd.concat([sig_mom,sig_lag],ignore_index=True)
allowed=list(RS["allowed_tiers"])+["LAG_HI","LAG_LO"]
tw={**RS["tier_weights"],"LAG_HI":LAG_HI_W,"LAG_LO":LAG_LO_W}
LIQ={"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map,"exit_slippage_tiered":True}
print("[5] simulate one wallet 50B...")
ev,_=[],None
nav,_=simulate(sig_all,prices,vni_dates,allowed_tiers=allowed,max_positions=MAX_POS,hold_days=45,stop_loss=-0.20,
    min_hold=2,slippage=0.001,init_nav=NAV,tier_weights=tw,tier_weights_by_state=RS["tier_weights_by_state"],
    ticker_sector_map=sec_map,sector_limit_per_sector={8:SEC_CAP},sector_cap_exempt_tiers=set(RS["sector_cap_exempt"])|{"LAG_HI","LAG_LO"},
    hold_days_by_tier={"LAG_HI":25,"LAG_LO":25},stop_exempt_tiers={"LAG_HI","LAG_LO"},
    tier_position_limit={"LAG_HI":12,"LAG_LO":12},deposit_annual=0.0,borrow_annual=0.10,state_by_date=state_ff,
    open_prices=open_prices,t1_open_exec=True,entry_alt_prices=None,event_log=ev,force_close_eod=False,name="lagvn30",**LIQ)
nav["time"]=pd.to_datetime(nav["time"])
print(f"  events {len(ev)}; final {nav.set_index('time')['nav'].iloc[-1]/1e9:.4f}B")

print("[6] emit audit...")
meta=[("system",f"LAGGED+{MOMLBL}(idle) one-wallet 50B: LAGGED HL_3y earnings (priority) + {MOMLBL} momentum fills idle capacity. NO ETF parking. DT5G state. sector-8 cap {SEC_CAP}"),
 ("source_script","pt_lagvn30_audit_2014.py (T+1 Open, all BQ, no intraday). per-name 5%/name (mom), LAG 5%/4% = one-wallet convention (per-name VND ~ standalone 25B books)"),
 ("period",f"{START_DATE} -> {END_DATE}"),("state_source",STATE_TABLE),
 ("execution_rule","signal t -> exec t+1 OPEN; multi-day fill <=20% ADV/day x5; sells next Open"),
 ("priority_rule","LAG_HI/LAG_LO priority 110/105 (above MEGA 100) -> LAGGED earnings plays fill FIRST; VN30 momentum fills remaining of max 24 slots when LAGGED idle"),
 ("sizing","momentum tiers 5%/name (weak 2.5% in BEAR/CRISIS via 8L regime_size); LAG_HI 5%, LAG_LO 4%. max 24 positions. hold: momentum 45d (stop -20%), LAGGED 25d (stop-exempt). sector-grp-8 cap 6 (LAGGED exempt)"),
 ("cash_identity","single book: cash(d)=cash(d-1)+SUM TX net + cash_carry(d) (carry=borrow on intraday neg cash). nav = cash + stocks(mark BQ Close); combined_nav = nav (one book)"),
 ("metric_formulas","CAGR/Sharpe(252)/MaxDD/Calmar on DAILY combined_nav")]
res=emit_audit(AUDIT_PATH,"LAGVN30",meta,[{"label":"BOOK","nav_df":nav,"init":NAV,"events":ev,"etf":[]}],vni_close_by_date)
m=res["metrics"]; sc=res["selfcheck"]
print("="*92)
print(f" LAGGED+VN30 AUDIT final {res['combined'].iloc[-1]/1e9:.2f}B  CAGR {m['cagr']*100:.2f}%  Sharpe {m['sharpe_252']:.2f}  MaxDD {m['max_dd']*100:.1f}%  Calmar {m['calmar']:.2f}")
print(f" self-check {sc}")
print(f" -> {AUDIT_PATH} ({res['n_tx']} TX rows)"); print("="*92)
