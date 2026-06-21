#!/usr/bin/env python3
"""run_bal_argdiff.py — isolate WHY prod-spec BAL_kelly(+111%) != pt BAL(+41%) on identical
data (prices/signal/state/universe all verified identical). Run BAL simulate (KELLY {3:1.0},
real E1VFVN30, fresh 2024) under prod-spec args vs pt args, toggling each difference.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import simulate, bq
START_B="2024-01-01"; END_B="2026-05-15"; BOOK_NAV=25e9
ETF_KELLY={3:1.0}; SECTOR_CAP_EXEMPT={"RE_BACKLOG_BUY"}
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS={t:0.10 for t in TIER_BAL}
BUY_TIERS={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
           "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS=12; POSITION_VND=1.25e9; FILL_CAP=0.20; T1_TOP_ADV=50e9
print("[load] pkl signal + processing (prod-spec style)...")
sig_B=pickle.load(open("data/ba_v11_unified_12y_sig.pkl","rb")); sig_B["time"]=pd.to_datetime(sig_B["time"])
sig_B=sig_B[(sig_B["time"]>=START_B)&(sig_B["time"]<=END_B)].copy()
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c=f.read()
VQU=re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""',_c,re.MULTILINE|re.DOTALL).group(1)
prices_B={tk:dict(zip(g["time"],g["Close"])) for tk,g in sig_B.groupby("ticker")}
liq_map_B={(r["ticker"],r["time"]):r["liq"] for _,r in sig_B.iterrows()}
vni_B=bq(VQU.format(start=START_B,end=END_B)); vni_B["time"]=pd.to_datetime(vni_B["time"])
vni_dates_B=sorted(vni_B["time"].unique())
vn30_proxy=dict(zip(vni_B["time"],vni_B["Close"]))
etf=bq(f"SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='E1VFVN30' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time")
etf["time"]=pd.to_datetime(etf["time"]); etf_real=dict(zip(etf["time"],etf["Close"]))
vn30_underlying={d:(etf_real[d] if d in etf_real else vn30_proxy.get(d)) for d in vni_dates_B}
opens_df=bq(f"""SELECT t.ticker,t.time,t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Open IS NOT NULL""")
opens_df["time"]=pd.to_datetime(opens_df["time"]); open_prices={tk:dict(zip(g["time"],g["open_price"])) for tk,g in opens_df.groupby("ticker")}
vni_full=bq(f"SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time")
vni_full["time"]=pd.to_datetime(vni_full["time"])
sdf=pd.read_csv("data/vnindex_5state_tam_quan_v3_4b_full_history.csv"); sdf["time"]=pd.to_datetime(sdf["time"])
sdf=sdf[(sdf["time"]>=START_B)&(sdf["time"]<=END_B)][["time","state"]]
sbd=dict(zip(sdf["time"],sdf["state"])); state_ff={}; last=None
for d in vni_dates_B:
    s=sbd.get(d);
    if s is not None: last=s
    state_ff[d]=last
# D1
d1=bq(f"""WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker,t.time,fa.fa_tier,SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 AS np_yoy,fin.Revenue_YoY_P0 AS rev_yoy,adv.adv_yoy,s5.state AS state5
FROM tav2_bq.ticker AS t LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time=t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"]=pd.to_datetime(d1["time"])
d1m=(d1["adv_yoy"].notna()&(d1["adv_yoy"]>0.5)&d1["fa_tier"].isin(["C","D"])&d1["state5"].isin([3,4,5])&((d1["np_yoy"].fillna(-99)>0)|(d1["rev_yoy"].fillna(-99)>0)))
sig_B=sig_B.merge(d1.loc[d1m,["ticker","time"]].assign(_ok=True),on=["ticker","time"],how="left")
om=sig_B["_ok"].fillna(False)&(sig_B["ta"]>=120); sig_B.loc[om,"play_type"]="RE_BACKLOG_BUY"; sig_B=sig_B.drop(columns=["_ok"])
def svk(r):
    s=r.get("state5"); d=r.get("days_since_release")
    if pd.isna(s): return True
    s=int(s)
    if s in (4,5): return True
    if s==1: return pd.notna(d) and d<=30
    if s in (2,3): return pd.notna(d) and d<=60
    return True
mb=sig_B["play_type"].isin(BUY_TIERS); sig_B=sig_B[(~mb)|sig_B.apply(svk,axis=1)].copy()
v=vni_full.merge(sdf,on="time",how="left"); v["state"]=v["state"].ffill()
oh=set(v[(v["Close"]/v["MA200"]>1.30)&((v["state"]==5)|(v["D_RSI"]>0.75))]["time"])
sig_v=sig_B.copy(); sig_v.loc[sig_v["time"].isin(oh)&sig_v["play_type"].isin(BUY_TIERS),"play_type"]="AVOID_overheated"
sec_map=bq("SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL").set_index("ticker")["s"].to_dict()
LIQ={"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}
# HYBRID alt prices (pt style)
print("[load] HYBRID alt-fill...")
intr=pickle.load(open("data/intraday_full.pkl","rb")); adv_by={}; pa,va,pt1,vt1={},{},{},{}
for tk,bars in intr.items():
    if bars is None or bars.empty: continue
    b=bars.copy(); b["time"]=pd.to_datetime(b["time"]); b["d"]=b["time"].dt.normalize()
    b["hm"]=b["time"].dt.strftime("%H:%M"); b["cv"]=b["close"].astype(float)*1000.0; b["vt"]=b["cv"]*b["volume"].astype(float)
    adv_by[tk]=float(b.groupby("d")["vt"].sum().mean())
    for hm,pd_,vd_ in [("14:45",pa,va),("11:15",pt1,vt1)]:
        for _,row in b[b["hm"]==hm].iterrows(): pd_.setdefault(tk,{})[row["d"]]=float(row["cv"]); vd_.setdefault(tk,{})[row["d"]]=float(row["vt"])
alt_hybrid={}
for tk in set(pa)|set(pt1):
    is_top=adv_by.get(tk,0)>=T1_TOP_ADV; sp=pa.get(tk,{}) if is_top else pt1.get(tk,{}); sv=va.get(tk,{}) if is_top else vt1.get(tk,{})
    for d,p in sp.items():
        vv=sv.get(d)
        if vv is not None and vv*FILL_CAP>=POSITION_VND: alt_hybrid.setdefault(tk,{})[d]=p

def run(label,**extra):
    nav,_=simulate(sig_v,prices_B,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=MAX_POS,hold_days=45,
        stop_loss=-0.20,min_hold=2,init_nav=BOOK_NAV,sector_limit_per_sector={8:4},ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,tier_weights=TIER_WEIGHTS,deposit_annual=0.0,borrow_annual=0.10,
        state_by_date=state_ff,cash_etf_states=ETF_KELLY,vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,etf_rebalance_friction=0.0015,
        open_prices=open_prices,t1_open_exec=True,**LIQ,**extra,name=label)
    nav["time"]=pd.to_datetime(nav["time"]); f=nav.set_index("time")["nav"].iloc[-1]
    print(f"  {label:<38} final={f/1e9:7.3f}B  ({(f/BOOK_NAV-1)*100:+.1f}%)")
    return f

print("\n=== BAL_kelly arg A/B (identical data) ===")
run("A prod-spec (slip .001, no hybrid)", slippage=0.001)
run("B prod + force_close_eod=False", slippage=0.001, force_close_eod=False)
run("C prod + HYBRID fill", slippage=0.001, entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid")
run("D pt-style (slip 0,hybrid,no-force)", slippage=0.0, entry_alt_prices=alt_hybrid, entry_fill_mode="v4_hybrid", force_close_eod=False)
print("DONE.")
