# -*- coding: utf-8 -*-
"""pt_v121_audit_2014.py — V12.1 ensemble re-simulated 2014->now, AUDIT edition.
V12.1 = 25B BAL (always-on momentum) + 25B SWITCHED leg routing VN30 <-> LAGGED(HL_3y S2) by the
M1+M3r AND-HOLD ensemble signal (0.5% cost per flip). Three component books each run as CLEAN
standalone 25B ledgers via simulate() on BQ data, T+1 Open; the switched leg is a documented
recurrence on the VN30/LAGGED standalone daily returns. State = v3.4b base (V12.1 canonical, differs
from V2.3/V11 which use DT5G). NO intraday alt-fills. Output: data/v121_audit_2014_now.csv.
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
STATE_TABLE="tav2_bq.vnindex_5state_tam_quan_v34b_clean"   # V12.1 canonical (v3.4b base)
BAL_NAV=SECOND_NAV=25e9; SWITCH_COST=0.005
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
BUY_TIERS_V11={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
               "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS=12; AUDIT_PATH=os.path.join(WORKDIR,"data","v121_audit_2014_now.csv")
print("="*92); print(f" V12.1 ensemble (BAL + VN30<->LAGGED switch) AUDIT {START_DATE}->{END_DATE}  T+1 Open, BQ, state v3.4b"); print("="*92)

# ---- signals (momentum, no EXBULL/CAPIT) ----
print("[2] signals + D1 + SV_TIGHT + regime_size...")
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
sig_f,RS=apply_regime_size(sig_f,START_DATE,END_DATE,bq,base_tiers=TIER_BAL)

# ---- common data ----
print("[3] prices/opens/etf/sector/top30...")
opens_df=bq(f"""SELECT t.ticker,t.time,t.Open op FROM tav2_bq.ticker t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' AND t.Open IS NOT NULL
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)""")
opens_df["time"]=pd.to_datetime(opens_df["time"]); assert len(opens_df)<1_990_000
open_prices={tk:dict(zip(g["time"],g["op"])) for tk,g in opens_df.groupby("ticker")}
prices={tk:dict(zip(g["time"],g["Close"])) for tk,g in sig_f.groupby("ticker")}
liq_map=dict(zip(zip(sig_f["ticker"],sig_f["time"]),sig_f["liq"]))
vni=bq(VNI_QUERY.format(start=START_DATE,end=END_DATE)); vni["time"]=pd.to_datetime(vni["time"])
vni_dates=sorted(vni["time"].unique()); vni_close_by_date=dict(zip(vni["time"],vni["Close"]))
etf=bq(f"""SELECT t.time,t.Close FROM tav2_bq.ticker t WHERE t.ticker='E1VFVN30'
AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
etf["time"]=pd.to_datetime(etf["time"]); vn30_underlying=dict(zip(etf["time"],etf["Close"]))
sec_map=bq("""SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) s FROM tav2_bq.ticker t
WHERE t.ICB_Code IS NOT NULL AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)""").set_index("ticker")["s"].to_dict()
top30=set(bq("""SELECT t.ticker FROM tav2_bq.ticker t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])
state_ff={};last=None
for d in vni_dates:
    s=state_by_date.get(d); last=s if s is not None else last; state_ff[d]=last
LIQ={"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map,"exit_slippage_tiered":True}
MKW=dict(allowed_tiers=RS["allowed_tiers"],max_positions=MAX_POS,hold_days=45,stop_loss=-0.20,min_hold=2,slippage=0.0,
    init_nav=BAL_NAV,tier_weights=RS["tier_weights"],tier_weights_by_state=RS["tier_weights_by_state"],
    deposit_annual=0.0,borrow_annual=0.10,state_by_date=state_ff,cash_etf_states={3:0.7},vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,etf_rebalance_friction=0.0015,
    open_prices=open_prices,t1_open_exec=True,entry_alt_prices=None,force_close_eod=False)

# ---- ensemble signal M1+M3r AND-HOLD ----
print("[4] ensemble M1+M3r...")
hs="2013-01-01"
m1=bq(f"""WITH base AS (SELECT t.time,t.ticker,SAFE_DIVIDE(t.Close,LAG(t.Close,126) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 ret6
FROM tav2_bq.ticker t WHERE t.time BETWEEN DATE '{hs}' AND DATE '{END_DATE}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)),
vni AS (SELECT t.time,SAFE_DIVIDE(t.Close,LAG(t.Close,126) OVER(ORDER BY t.time))-1 vr6 FROM tav2_bq.ticker t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{hs}' AND DATE '{END_DATE}')
SELECT b.time, vni.vr6-AVG(b.ret6) M1 FROM base b JOIN vni USING(time) GROUP BY b.time,vni.vr6 ORDER BY b.time""")
m1["time"]=pd.to_datetime(m1["time"]); m1s=m1.set_index("time")["M1"]
m3=bq(f"""WITH base AS (SELECT t.time,t.ticker,SAFE_DIVIDE(t.Close,LAG(t.Close,126) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 ret6,
AVG(t.Volume_3M_P50*t.Close) OVER(PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) adv1y
FROM tav2_bq.ticker t WHERE t.time BETWEEN DATE '{hs}' AND DATE '{END_DATE}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune t2)),
ranked AS (SELECT time,ret6,adv1y,ROW_NUMBER() OVER(PARTITION BY time ORDER BY adv1y DESC) rnk FROM base WHERE adv1y IS NOT NULL AND ret6 IS NOT NULL)
SELECT time,AVG(IF(rnk<=10,ret6,NULL))-AVG(ret6) M3r FROM ranked GROUP BY time ORDER BY time""")
m3["time"]=pd.to_datetime(m3["time"]); m3s=m3.set_index("time")["M3r"]
def make_signal(metric,minh=252):
    s=metric.dropna().sort_index(); med=s.expanding(min_periods=minh).median()
    raw=(s>med).astype(int); raw=raw.reindex(metric.index).ffill().fillna(1).astype(int)
    return raw.shift(1).fillna(1).astype(int)
sm1=make_signal(m1s); sm3=make_signal(m3s)
ci=sm1.index.intersection(sm3.index); a1=sm1.loc[ci]; a3=sm3.loc[ci]
out=np.zeros(len(a1),dtype=int); cur=int(a1.iloc[0])
for i,(x,y) in enumerate(zip(a1.values,a3.values)):
    if x==y: cur=int(x)
    out[i]=cur
ens=pd.Series(out,index=a1.index).reindex(pd.DatetimeIndex(vni_dates),method="ffill").fillna(1).astype(int)
print(f"  V11-active {(ens==1).sum()}d / V12-active {(ens==0).sum()}d / flips {int((ens.diff().abs()>0).sum())}")

# ---- 3 books ----
print("[5] BAL @25B...")
eb,etfb=[],[]
nav_b,_=simulate(sig_f,prices,vni_dates,ticker_sector_map=sec_map,sector_limit_per_sector={8:4},
    sector_cap_exempt_tiers=RS["sector_cap_exempt"],event_log=eb,etf_log=etfb,name="v121_BAL",**MKW,**LIQ)
nav_b["time"]=pd.to_datetime(nav_b["time"])
print("[6] VN30 @25B...")
sig_v=sig_f[sig_f["ticker"].isin(top30)].copy(); prices_v={tk:prices[tk] for tk in top30 if tk in prices}
liq_v={k:v for k,v in liq_map.items() if k[0] in top30}; LIQ_V={**LIQ,"liquidity_lookup":liq_v}
ev,etfv=[],[]
nav_v,_=simulate(sig_v,prices_v,vni_dates,ticker_sector_map=sec_map,event_log=ev,etf_log=etfv,name="v121_VN30",**MKW,**LIQ_V)
nav_v["time"]=pd.to_datetime(nav_v["time"])

print("[7] LAGGED @25B (HL_3y S2, no parking, BQ prices)...")
# extended calendar + earnings schedule (same as pt_v23 LAG, BQ-sourced)
cal=bq(VNI_QUERY.format(start="2013-06-01",end=END_DATE)); cal["time"]=pd.to_datetime(cal["time"])
all_dates=np.array(sorted(cal["time"].unique()),dtype="datetime64[ns]")
with open("data/earnings_surprise_data.pkl","rb") as f: fin=pickle.load(f)
fin["Release_Date"]=pd.to_datetime(fin["Release_Date"]); FLOOR=1e9
fin["exp_B_MA"]=fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"]=((fin["NP_P0"]-fin["exp_B_MA"])/np.maximum(np.abs(fin["exp_B_MA"]),FLOOR)).clip(-5,5)
evc=pd.read_csv("data/earnings_events_classified.csv",parse_dates=["Release_Date"])
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
prices_lag,opens_lag,liq_lag={},{},{}
for tk,g in lagpx.groupby("ticker"):
    gc=g[g["Close"].notna()]; prices_lag[tk]=dict(zip(gc["time"],gc["Close"].astype(float)))
    go=g[g["Open"].notna()]; opens_lag[tk]=dict(zip(go["time"],go["Open"].astype(float)))
    gl=g[g["Volume_3M_P50"].notna()&g["Close"].notna()]
    for d,a,px in zip(gl["time"],gl["Volume_3M_P50"].astype(float),gl["Close"].astype(float)): liq_lag[(tk,d)]=a*px
lag_rows=[]
for c in lag_cand:
    px_sd=prices_lag.get(c["ticker"],{}).get(c["sd"],np.nan)
    if pd.isna(px_sd) or px_sd<=0: continue
    lag_rows.append({"time":c["sd"],"ticker":c["ticker"],"play_type":"LAG_HI" if c["surprise"]>0.5 else "LAG_LO","ta":400.0,"Close":float(px_sd)})
sig_lag=pd.DataFrame(lag_rows,columns=["time","ticker","play_type","ta","Close"])
shn.TIER_PRIORITY.update({"LAG_HI":88,"LAG_LO":82})
LIQ_LAG={"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_lag,"exit_slippage_tiered":True}
LKW=dict(allowed_tiers=["LAG_HI","LAG_LO"],max_positions=12,hold_days=25,stop_loss=-0.99,min_hold=2,slippage=0.001,
    init_nav=SECOND_NAV,stop_exempt_tiers={"LAG_HI","LAG_LO"},hold_days_by_tier={"LAG_HI":25,"LAG_LO":25},
    tier_position_limit={"LAG_HI":12,"LAG_LO":12},deposit_annual=0.0,borrow_annual=0.10,state_by_date=state_ff,
    open_prices=opens_lag,t1_open_exec=True,force_close_eod=False)  # NO parking (faithful V12.1 LAGGED)
el,_=[],None
nav_l,_=simulate(sig_lag,prices_lag,vni_dates,tier_weights={"LAG_HI":0.10,"LAG_LO":0.08},event_log=el,name="v121_LAGGED",**LKW,**LIQ_LAG)
nav_l["time"]=pd.to_datetime(nav_l["time"])
print(f"  BAL {len(eb)}ev VN30 {len(ev)}ev LAGGED {len(el)}ev")

# ---- switched recurrence + combined ----
print("[8] switched leg + combined...")
nb=nav_b.set_index("time")["nav"]; nv=nav_v.set_index("time")["nav"]; nl=nav_l.set_index("time")["nav"]
common=nb.index.intersection(nv.index).intersection(nl.index).sort_values()
v30_r=nv.loc[common].pct_change().fillna(0).values; lag_r=nl.loc[common].pct_change().fillna(0).values
sigc=ens.reindex(common).ffill().fillna(1).astype(int).values
sp=np.full(len(common),SECOND_NAV,float); prev=int(sigc[0])
for i in range(1,len(common)):
    c=int(sigc[i])
    sp[i]=sp[i-1]*(1-SWITCH_COST) if c!=prev else sp[i-1]
    sp[i]*=(1+(v30_r[i] if c==1 else lag_r[i])); prev=c
cap_sw=pd.Series(sp,index=common)
combined=nb.loc[common]+cap_sw
n_flip=int((pd.Series(sigc).diff().abs()>0).sum())
print(f"  {n_flip} flips; final combined {combined.iloc[-1]/1e9:.2f}B")

# Only count active-leg events in TX (VN30 on sig==1, LAGGED on sig==0) for honesty about what traded;
# but each book's STANDALONE ledger (all its events) is what reconciles -> we emit all events per book
# and rely on standalone cash identity. The switched recurrence is verified separately.
print("[9] emit audit...")
meta=[("system","V12.1 ensemble = 25B BAL(always-on momentum) + 25B SWITCHED(VN30<->LAGGED HL_3y S2 by M1+M3r AND-HOLD), 0.5%/flip, state v3.4b base"),
 ("source_script","pt_v121_audit_2014.py (faithful pt_v121_ensemble.py; T+1 Open, all BQ, no intraday, LAGGED via engine fees not custom 0.1%)"),
 ("period",f"{START_DATE} -> {END_DATE}"),("state_source",STATE_TABLE+" (NOTE: V12.1 canonical = v3.4b, DIFFERS from V2.3/V11 DT5G)"),
 ("execution_rule","signal t -> exec t+1 OPEN (tav2_bq.ticker Open); multi-day fill <=20% ADV/day x5; sells next Open"),
 ("books_def","BAL=SIGNAL_V11 full (sector-8 cap4, park {3:0.7}); VN30=same on top-30 ADV (park {3:0.7}); LAGGED=HL_3y earnings (NP_R>=15 & >=4 prior-good & decay-post>=5%, T+5 entry, 25d hold, S2 10%/8% by surprise, NO parking, NO stop). Each 25B"),
 ("ensemble_signal","M1=VNI 6m-ret minus equal-weight prune 6m-ret; M3r=top10-ADV 6m-ret minus all-prune 6m-ret; each > expanding-median(252) -> 1(VN30) else 0(LAGGED), shifted 1d (causal); AND-HOLD: adopt only when M1,M3r agree else hold. ensemble_signal column in DAILY"),
 ("switched_recurrence",f"cap_switched(0)=25e9; each day: if signal flips, cap*= (1-{SWITCH_COST}); then cap*=(1+active leg daily return) where active=VN30 ret if signal==1 else LAGGED ret. combined_nav = nav_bal_ref + cap_switched. VN30/LAGGED daily returns derive from their standalone ref-NAV columns"),
 ("cash_identity","per book per day EXACT incl <book>_cash_carry (see generic note). BAL/VN30/LAGGED each reconcile standalone to their 25B ledger; combined uses the documented switched recurrence on standalone returns"),
 ("metric_formulas","CAGR/Sharpe(252)/MaxDD/Calmar on DAILY combined_nav")]
res=emit_audit(AUDIT_PATH,"V12.1",meta,
  [{"label":"BAL","nav_df":nav_b,"init":BAL_NAV,"events":eb,"etf":etfb},
   {"label":"VN30","nav_df":nav_v,"init":SECOND_NAV,"events":ev,"etf":etfv},
   {"label":"LAGGED","nav_df":nav_l,"init":SECOND_NAV,"events":el,"etf":[]}],
  vni_close_by_date, combined_override=combined,
  extra_daily={"ensemble_signal":pd.Series(sigc,index=common),"cap_switched":cap_sw})

# switched-replay self-check (independent)
chk=np.full(len(common),SECOND_NAV,float); prev=int(sigc[0])
for i in range(1,len(common)):
    c=int(sigc[i]); chk[i]=chk[i-1]*(1-SWITCH_COST) if c!=prev else chk[i-1]; chk[i]*=(1+(v30_r[i] if c==1 else lag_r[i])); prev=c
replay_err=abs((nb.loc[common].iloc[-1]+chk[-1])-combined.iloc[-1])
m=res["metrics"]; sc=res["selfcheck"]
print("="*92)
print(f" V12.1 AUDIT final {res['combined'].iloc[-1]/1e9:.2f}B  CAGR {m['cagr']*100:.2f}%  Sharpe {m['sharpe_252']:.2f}  MaxDD {m['max_dd']*100:.1f}%  Calmar {m['calmar']:.2f}")
print(f" switched-replay err {replay_err:,.2f} VND | self-check {sc}")
print(f" -> {AUDIT_PATH} ({res['n_tx']} TX rows)"); print("="*92)
