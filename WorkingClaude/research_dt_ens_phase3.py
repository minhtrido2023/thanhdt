# -*- coding: utf-8 -*-
"""research_dt_ens_phase3.py — DT4 × ensemble, PHASE 3: parking-intensity sweep on the
DECOUPLE winner (SVT=TQ34b, parking=DT4) + mechanism control (opposite decouple).

Question 1: optimal DT-parking intensity on the decouple architecture? Sweep
  {3:0.7}(=E2 BASE), {3:0.85}, {3:1.0}(=E3 KELLY), {2:0.4,3:0.85} (mild BEAR park) —
  does adding mild BEAR-state parking recover E3's return with E2's drawdown?
Question 2 (control): is the DT benefit really in the PARKING channel? Run the OPPOSITE
  decouple (SVT=DT4, parking=TQ34b). If that's NOT a win, the benefit is parking-only.

Reuses data/dt_ens_legs.pkl (TQ legs + signals). Daily + weekly(5/40) ensemble.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B="2014-01-01"; END_B="2026-05-15"; TOTAL_NAV=50e9; BOOK_NAV=25e9
DEPOSIT=0.0; BORROW=0.10; SWITCH_COST=0.005
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
               "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
DT_CSV="vnindex_5state_dt_10_25_25.csv"; TQ_CSV="vnindex_5state_tam_quan_v3_4b_full_history.csv"
print("="*104); print("  PHASE 3 — parking-intensity sweep on DECOUPLE + mechanism control"); print("="*104)

with open("data/dt_ens_legs.pkl","rb") as f: C=pickle.load(f)
common=C["common"]; nav_lag_v121=C["nav_lag_v121"]
m1=C["m1_126"].reindex(common).ffill().fillna(1).astype(int)
m3=C["m3_126"].reindex(common).ffill().fillna(1).astype(int)

print("\n[1] Reload data...")
with open("ba_v11_unified_12y_sig.pkl","rb") as f: sig_B=pickle.load(f)
sig_B["time"]=pd.to_datetime(sig_B["time"])
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c=f.read()
VQU=re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""',_c,re.MULTILINE|re.DOTALL).group(1)
prices_B={tk:dict(zip(g["time"],g["Close"])) for tk,g in sig_B.groupby("ticker")}
liq_map_B={(r["ticker"],r["time"]):r["liq"] for _,r in sig_B.iterrows()}
vni_B=bq(VQU.format(start=START_B,end=END_B)); vni_B["time"]=pd.to_datetime(vni_B["time"])
vni_dates_B=sorted(vni_B["time"].unique()); vn30_underlying=dict(zip(vni_B["time"],vni_B["Close"]))
vni_full=bq(f"""SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"]=pd.to_datetime(vni_full["time"])
top30=set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])
sec_map=bq("""SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t
WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ={"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

def load_ff(csv):
    sdf=pd.read_csv(csv); sdf["time"]=pd.to_datetime(sdf["time"])
    sdf=sdf[(sdf["time"]>=START_B)&(sdf["time"]<=END_B)][["time","state"]]
    sbd=dict(zip(sdf["time"],sdf["state"])); ff={}; last=None
    for d in vni_dates_B:
        s=sbd.get(d)
        if s is not None: last=s
        ff[d]=last
    return sdf,ff
dt_sdf,dt_ff=load_ff(DT_CSV); tq_sdf,tq_ff=load_ff(TQ_CSV)

def run_legs(svt_sdf, park_ff, etf_states, label):
    v=vni_full.merge(svt_sdf,on="time",how="left"); v["state"]=v["state"].ffill()
    v["overheat"]=((v["Close"]/v["MA200"]>1.30)&((v["state"]==5)|(v["D_RSI"]>0.75)))
    oh=set(v[v["overheat"]]["time"]); sv=sig_B.copy()
    sv.loc[sv["time"].isin(oh)&sv["play_type"].isin(BUY_TIERS_V11),"play_type"]="AVOID_overheated"
    nb,_=simulate(sv,prices_B,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=10,hold_days=45,
        stop_loss=-0.20,min_hold=2,slippage=0.001,init_nav=BOOK_NAV,sector_limit_per_sector={8:4},
        ticker_sector_map=sec_map,deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=park_ff,
        cash_etf_states=etf_states,vn30_underlying=vn30_underlying,**LIQ,name=f"BAL_{label}")
    nb["time"]=pd.to_datetime(nb["time"]); nbs=nb.set_index("time")["nav"]
    s30=sv[sv["ticker"].isin(top30)].copy(); p30={tk:prices_B[tk] for tk in top30 if tk in prices_B}
    l30={k:vv for k,vv in liq_map_B.items() if k[0] in top30}; L30={**LIQ,"liquidity_lookup":l30}
    nv,_=simulate(s30,p30,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=10,hold_days=45,
        stop_loss=-0.20,min_hold=2,slippage=0.001,init_nav=BOOK_NAV,ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=park_ff,
        cash_etf_states=etf_states,vn30_underlying=vn30_underlying,**L30,name=f"VN30_{label}")
    nv["time"]=pd.to_datetime(nv["time"]); nvs=nv.set_index("time")["nav"]
    print(f"    [{label}] BAL={nbs.iloc[-1]/1e9:.2f}B VN30={nvs.iloc[-1]/1e9:.2f}B")
    return nbs,nvs

# DECOUPLE: SVT=TQ, parking=DT, varying intensity
INTENS = {
  "DEC {3:.7}":        {3:0.7},
  "DEC {3:.85}":       {3:0.85},
  "DEC {3:1.0}":       {3:1.0},
  "DEC {2:.4,3:.85}":  {2:0.4, 3:0.85},
}
print("\n[2] DECOUPLE intensity sweep (SVT=TQ, park=DT)...")
legs={}
for name,etf in INTENS.items():
    legs[name]=run_legs(tq_sdf, dt_ff, etf, name)
print("\n[3] CONTROL opposite decouple (SVT=DT, park=TQ {3:.7})...")
legs["OPP SVT=DT park=TQ"]=run_legs(dt_sdf, tq_ff, {3:0.7}, "OPP")
print("[3b] CANON repro (SVT=TQ park=TQ {3:.7})...")
legs["CANON SVT=TQ park=TQ"]=run_legs(tq_sdf, tq_ff, {3:0.7}, "CANON")

# ── ensemble + eval ─────────────────────────────────────────────────────────
def ens(m1b,m3b,cad=1,dw=0):
    idx=m1b.index; out=np.zeros(len(idx),int); cur=int(m1b.iloc[0]); lf=-10**9
    for i in range(len(idx)):
        if i%cad==0:
            a,b=int(m1b.iloc[i]),int(m3b.iloc[i])
            if a==b and a!=cur and (i-lf)>=dw: cur=a; lf=i
        out[i]=cur
    return pd.Series(out,index=idx)
def to_ret(nav): return nav.reindex(common).ffill().pct_change().fillna(0)
r_lag=to_ret(nav_lag_v121)
def eval_cfg(bal_ret,vn30_ret,lag_ret,sig):
    nbp=(1+bal_ret).cumprod()*BOOK_NAV; sec=np.full(len(common),BOOK_NAV,float)
    prev=int(sig.iloc[0]); flips=0
    for i in range(1,len(common)):
        cur=int(sig.iloc[i])
        if cur!=prev: sec[i]=sec[i-1]*(1-SWITCH_COST); flips+=1
        else: sec[i]=sec[i-1]
        r=vn30_ret.iloc[i] if cur==1 else lag_ret.iloc[i]; sec[i]=sec[i]*(1+r); prev=cur
    return pd.Series((nbp.values+sec)/TOTAL_NAV,index=common),flips
def mets(nav,st,en):
    s=nav[(nav.index>=st)&(nav.index<=en)]
    if len(s)<30: return None
    r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25; spy=len(r)/yrs if yrs>0 else 252
    return {"CAGR":((s.iloc[-1]/s.iloc[0])**(1/yrs)-1)*100,"Sharpe":r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0,
            "DD":((s-s.cummax())/s.cummax()).min()*100}
periods=[("FULL","2014-01-01","2026-05-15"),("IS","2014-01-01","2019-12-31"),
         ("OOS20","2020-01-01","2026-05-15"),("OOS24","2024-01-01","2026-05-15")]
sig_d=ens(m1,m3,1,0); sig_w=ens(m1,m3,5,40)

rows=[]
for name,(nbs,nvs) in legs.items():
    for sname,sig in [("daily",sig_d),("weekly",sig_w)]:
        nav,flips=eval_cfg(to_ret(nbs),to_ret(nvs),r_lag,sig)
        mm={pl:mets(nav,pd.Timestamp(s),pd.Timestamp(e)) for pl,s,e in periods}
        rows.append({"config":name,"switch":sname,"flips":flips,
            "Full":mm["FULL"]["CAGR"],"IS":mm["IS"]["CAGR"],"OOS20":mm["OOS20"]["CAGR"],
            "OOS24":mm["OOS24"]["CAGR"],"DD":mm["FULL"]["DD"],"Sharpe":mm["FULL"]["Sharpe"]})
df=pd.DataFrame(rows)
base=df[(df["config"]=="CANON SVT=TQ park=TQ")&(df["switch"]=="daily")].iloc[0]
print("\n"+"="*112)
print(f"  {'config':<24}{'switch':>7}{'Full':>8}{'ΔF':>6}{'IS':>8}{'OOS20':>8}{'OOS24':>8}{'ΔO24':>7}{'DD':>8}{'Sh':>6}{'flips':>6}")
print("-"*112)
for _,r in df.iterrows():
    print(f"  {r['config']:<24}{r['switch']:>7}{r['Full']:>+7.2f}%{r['Full']-base['Full']:>+6.2f}"
          f"{r['IS']:>+7.2f}%{r['OOS20']:>+7.2f}%{r['OOS24']:>+7.2f}%{r['OOS24']-base['OOS24']:>+6.2f}"
          f"{r['DD']:>+7.2f}%{r['Sharpe']:>+6.2f}{r['flips']:>6}")
print("="*112)
df.to_csv("data/dt_ens_phase3_sweep.csv",index=False)
print("  Saved -> data/dt_ens_phase3_sweep.csv\nDONE phase 3.")
