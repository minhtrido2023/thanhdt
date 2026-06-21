#!/usr/bin/env python3
"""run_prodspec_dt_v6.py — PROD-SPEC head-to-head: V4 (BASE) vs V5 (=V121_Kelly, KELLY)
vs V6 (DT-parking {3:0.85}).  Full production spec (max_pos=12, tier_weights 10%,
RE_BACKLOG_BUY, SV_TIGHT, t1_open_exec) — identical to run_5systems_prodspec.py.

DECOUPLE for V6: SV_TIGHT + overheat stay on TQ34b (baked into sig pkl + sig_v_tq);
only the ETF-parking state_by_date is swapped to DT4, intensity {3:0.85}.
Also tests DT {3:1.0} and weekly switch cadence (cad=5, dwell=40) on every arm.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B="2014-01-01"; END_B="2026-05-15"; TOTAL_NAV=50e9; BOOK_NAV=25e9
DEPOSIT=0.0; BORROW=0.10
ETF_BASE={3:0.7}; ETF_KELLY={3:1.0}; ETF_DT085={3:0.85}
SECTOR_CAP_EXEMPT={"RE_BACKLOG_BUY"}
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11={t:0.10 for t in TIER_BAL}
BUY_TIERS_V11={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
               "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS=12; SWITCH_COST=0.005
STATE_CSV_TQ="vnindex_5state_tam_quan_v3_4b_full_history.csv"
STATE_CSV_DT="vnindex_5state_dt_10_25_25.csv"
print("="*100); print("  PROD-SPEC V4(BASE) vs V5(KELLY=V121_Kelly) vs V6(DT {3:0.85}) — head-to-head"); print("="*100)

# ── 1. signals/prices/VNI/opens ─────────────────────────────────────────────
print("\n[1] Load signals/prices/VNI/opens...")
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

# ── 2. states ff (TQ for parking-canon + DT for parking-v6) ─────────────────
def load_ff(csv):
    sdf=pd.read_csv(csv); sdf["time"]=pd.to_datetime(sdf["time"])
    sdf=sdf[(sdf["time"]>=START_B)&(sdf["time"]<=END_B)][["time","state"]]
    sbd=dict(zip(sdf["time"],sdf["state"])); ff={}; last=None
    for d in vni_dates_B:
        s=sbd.get(d)
        if s is not None: last=s
        ff[d]=last
    return sdf,ff
state_df_tq,state_ff_tq=load_ff(STATE_CSV_TQ)
state_df_dt,state_ff_dt=load_ff(STATE_CSV_DT)

# ── 3. D1 RE_BACKLOG ────────────────────────────────────────────────────────
print("\n[3] D1 RE_BACKLOG...")
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
sig_B=sig_B.drop(columns=["_d1_ok"]); print(f"  RE_BACKLOG: {int(omask.sum()):,}")

# ── 4. SV_TIGHT (TQ state5 baked in pkl) ────────────────────────────────────
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

# ── 5. overheat (TQ) ────────────────────────────────────────────────────────
v=vni_full.merge(state_df_tq,on="time",how="left"); v["state"]=v["state"].ffill()
v["overheat"]=((v["Close"]/v["MA200"]>1.30)&((v["state"]==5)|(v["D_RSI"]>0.75)))
oh=set(v[v["overheat"]]["time"]); sig_v_tq=sig_B.copy()
sig_v_tq.loc[sig_v_tq["time"].isin(oh)&sig_v_tq["play_type"].isin(BUY_TIERS_V11),"play_type"]="AVOID_overheated"

# ── 6. universe ─────────────────────────────────────────────────────────────
top30=set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])
sec_map=bq("""SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t
WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ={"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# ── 7. prod-spec runners ────────────────────────────────────────────────────
def run_bal(sig_use,state_ff,etf,label):
    nav,_=simulate(sig_use,prices_B,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=MAX_POS,hold_days=45,
        stop_loss=-0.20,min_hold=2,slippage=0.001,init_nav=BOOK_NAV,sector_limit_per_sector={8:4},
        ticker_sector_map=sec_map,sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=state_ff,cash_etf_states=etf,
        vn30_underlying=vn30_underlying,etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,open_prices=open_prices,t1_open_exec=True,**LIQ,name=label)
    nav["time"]=pd.to_datetime(nav["time"]); s=nav.set_index("time")["nav"]; print(f"  {label}: {s.iloc[-1]/1e9:.2f}B"); return s
def run_vn30(sig_use,state_ff,etf,label):
    s30=sig_use[sig_use["ticker"].isin(top30)].copy(); p30={tk:prices_B[tk] for tk in top30 if tk in prices_B}
    l30={k:vv for k,vv in liq_map_B.items() if k[0] in top30}; L30={**LIQ,"liquidity_lookup":l30}
    nav,_=simulate(s30,p30,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=MAX_POS,hold_days=45,
        stop_loss=-0.20,min_hold=2,slippage=0.001,init_nav=BOOK_NAV,ticker_sector_map=sec_map,
        tier_weights=TIER_WEIGHTS_V11,deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=state_ff,
        cash_etf_states=etf,vn30_underlying=vn30_underlying,etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,open_prices=open_prices,t1_open_exec=True,**L30,name=label)
    nav["time"]=pd.to_datetime(nav["time"]); s=nav.set_index("time")["nav"]; print(f"  {label}: {s.iloc[-1]/1e9:.2f}B"); return s

print("\n[7] Legs...")
bal_tq_base =run_bal(sig_v_tq,state_ff_tq,ETF_BASE,"BAL_TQ_base")     # V4
vn30_tq_base=run_vn30(sig_v_tq,state_ff_tq,ETF_BASE,"VN30_TQ_base")
bal_tq_kel  =run_bal(sig_v_tq,state_ff_tq,ETF_KELLY,"BAL_TQ_kelly")   # V5
vn30_tq_kel =run_vn30(sig_v_tq,state_ff_tq,ETF_KELLY,"VN30_TQ_kelly")
bal_dt_085  =run_bal(sig_v_tq,state_ff_dt,ETF_DT085,"BAL_DT_085")     # V6
vn30_dt_085 =run_vn30(sig_v_tq,state_ff_dt,ETF_DT085,"VN30_DT_085")
bal_dt_kel  =run_bal(sig_v_tq,state_ff_dt,ETF_KELLY,"BAL_DT_kelly")   # V6b
vn30_dt_kel =run_vn30(sig_v_tq,state_ff_dt,ETF_KELLY,"VN30_DT_kelly")

# ── 8. LAGGED v121 ──────────────────────────────────────────────────────────
print("\n[8] LAGGED v121...")
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
def run_lagged(init_nav):
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
                pos_pct=0.10 if en["surprise"]>0.5 else 0.08
                target=pos_pct*nav_now; cap=LIQ_CAP*adv*MAX_FILL*fpx; alloc=min(target,cap)
                if alloc<1e6 or alloc>cash: continue
                eff=fpx*(1+SLIP_IN); sh=alloc/eff; cash-=sh*eff
                positions[tk]={"entry_dt":dt,"exit_dt":en["exit_dt"],"shares":sh,"entry_px":fpx}
        mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
        nh.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(nh).set_index("time")["nav"]
nav_lag_v121=run_lagged(BOOK_NAV); print(f"  LAG v121: {nav_lag_v121.iloc[-1]/1e9:.2f}B")

# ── 9. ensemble (cached m1 + live m3r, prod-spec) ───────────────────────────
print("\n[9] M1+M3r ensemble...")
cached=pd.read_csv("compare_v11_v12_concentration_switch.csv",index_col=0,parse_dates=True)
sig_m1=cached["sig_m1"].dropna().astype(int)
m3r_df=bq("""WITH base AS (SELECT t.time,t.ticker,
  SAFE_DIVIDE(t.Close,LAG(t.Close,126) OVER (PARTITION BY t.ticker ORDER BY t.time))-1 AS ret_6m,
  AVG(t.Volume_3M_P50*t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS adv_1y
  FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '2026-05-15'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)),
ranked AS (SELECT time,ret_6m,adv_1y,ROW_NUMBER() OVER (PARTITION BY time ORDER BY adv_1y DESC) AS rnk
  FROM base WHERE adv_1y IS NOT NULL AND ret_6m IS NOT NULL)
SELECT time, AVG(IF(rnk<=10,ret_6m,NULL))-AVG(ret_6m) AS M3r FROM ranked GROUP BY time ORDER BY time""")
m3r_df["time"]=pd.to_datetime(m3r_df["time"]); m3r=m3r_df.set_index("time")["M3r"]
def make_signal(metric,mh=252):
    s=metric.dropna().sort_index(); em=s.expanding(min_periods=mh).median()
    raw=(s>em).astype(int).reindex(metric.index).ffill().fillna(1).astype(int)
    return raw.shift(1).fillna(1).astype(int)
sig_m3r=make_signal(m3r)

common=bal_tq_base.index.intersection(vn30_tq_base.index).intersection(nav_lag_v121.index)\
    .intersection(bal_tq_kel.index).intersection(vn30_tq_kel.index)\
    .intersection(bal_dt_085.index).intersection(vn30_dt_085.index)\
    .intersection(bal_dt_kel.index).intersection(vn30_dt_kel.index)
m1=sig_m1.reindex(common).ffill().fillna(1).astype(int)
m3a=sig_m3r.reindex(common).ffill().fillna(1).astype(int)
def ens_AH(m1,m3,cad=1,dw=0):
    out=np.zeros(len(m1),int); cur=int(m1.iloc[0]); lf=-10**9
    for i in range(len(m1)):
        if i%cad==0:
            a,b=int(m1.iloc[i]),int(m3.iloc[i])
            if a==b and a!=cur and (i-lf)>=dw: cur=a; lf=i
        out[i]=cur
    return pd.Series(out,index=m1.index)
sig_daily=ens_AH(m1,m3a,1,0); sig_weekly=ens_AH(m1,m3a,5,40)

def switched_nav(bal_s,vn30_s,lag_s,signal):
    br=bal_s.pct_change().fillna(0); vr=vn30_s.pct_change().fillna(0); lr=lag_s.pct_change().fillna(0)
    nbp=(1+br).cumprod()*BOOK_NAV; sec=np.full(len(common),BOOK_NAV,float); prev=int(signal.iloc[0]); flips=0
    for i in range(1,len(common)):
        cur=int(signal.iloc[i])
        if cur!=prev: sec[i]=sec[i-1]*(1-SWITCH_COST); flips+=1
        else: sec[i]=sec[i-1]
        r=vr.iloc[i] if cur==1 else lr.iloc[i]; sec[i]=sec[i]*(1+r); prev=cur
    return pd.Series((nbp.values+sec)/TOTAL_NAV,index=common),flips

arms={
 "V4 BASE daily":       (bal_tq_base, vn30_tq_base, sig_daily),
 "V4 BASE weekly":      (bal_tq_base, vn30_tq_base, sig_weekly),
 "V5 KELLY daily(=Kelly)":(bal_tq_kel, vn30_tq_kel, sig_daily),
 "V5 KELLY weekly":     (bal_tq_kel, vn30_tq_kel, sig_weekly),
 "V6 DT085 daily":      (bal_dt_085, vn30_dt_085, sig_daily),
 "V6 DT085 weekly ⭐":   (bal_dt_085, vn30_dt_085, sig_weekly),
 "V6b DT KELLY daily":  (bal_dt_kel, vn30_dt_kel, sig_daily),
 "V6b DT KELLY weekly": (bal_dt_kel, vn30_dt_kel, sig_weekly),
}
def metrics(nav,st,en):
    s=nav[(nav.index>=st)&(nav.index<=en)].dropna()
    if len(s)<30: return None
    r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25; spy=len(r)/yrs if yrs>0 else 252
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0; dd=((s-s.cummax())/s.cummax()).min()
    return {"CAGR":cagr*100,"Sharpe":r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0,"DD":dd*100,
            "Calmar":cagr/abs(dd) if dd<0 else 0}
periods=[("FULL","2014-01-01","2026-05-15"),("IS","2014-01-01","2019-12-31"),
         ("OOS20","2020-01-01","2026-05-15"),("OOS24","2024-01-01","2026-05-15")]
print("\n"+"="*112)
print(f"  {'Arm':<24}{'Full':>8}{'IS':>8}{'OOS20':>8}{'OOS24':>8}{'DD':>8}{'Calmar':>7}{'Sharpe':>7}{'flips':>6}")
print("-"*112)
navs={}
for name,(b,vv,sig) in arms.items():
    nav,flips=switched_nav(b.loc[common],vv.loc[common],nav_lag_v121.loc[common],sig); navs[name]=nav
    mm={pl:metrics(nav,pd.Timestamp(s),pd.Timestamp(e)) for pl,s,e in periods}
    print(f"  {name:<24}{mm['FULL']['CAGR']:>+7.2f}%{mm['IS']['CAGR']:>+7.2f}%{mm['OOS20']['CAGR']:>+7.2f}%"
          f"{mm['OOS24']['CAGR']:>+7.2f}%{mm['FULL']['DD']:>+7.2f}%{mm['FULL']['Calmar']:>+6.2f}{mm['FULL']['Sharpe']:>+7.2f}{flips:>6}")
print("="*112)
pd.DataFrame(navs).to_csv("data/prodspec_dt_v6_nav.csv")
print("  Saved -> data/prodspec_dt_v6_nav.csv\nDONE.")
