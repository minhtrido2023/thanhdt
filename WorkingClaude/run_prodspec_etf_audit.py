#!/usr/bin/env python3
"""run_prodspec_etf_audit.py — INTEGRITY AUDIT: is V4/V5 2014-now performance inflated
by the VNINDEX-proxy ETF parking leg?

run_5systems_prodspec.py uses vn30_underlying = VNINDEX (proxy). The real ETF parked is
E1VFVN30 (tracks VN30, exists 2016-01-07+). Memory warns proxy overstates ~16pp. V5 (KELLY,
parks 100% idle cash in NEUTRAL) is the most exposed. This script runs V4 (BASE) and V5
(KELLY) under BOTH ETF underlyings and reports full-2014 / 2016+ / 2024+ to quantify the
'số ảo' (illusory return) component. Real-ETF dict falls back to VNINDEX pre-2016.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import simulate, bq
import os as _os; START_B=_os.environ.get("START_DATE","2014-01-01"); END_B="2026-05-15"; TOTAL_NAV=50e9; BOOK_NAV=25e9
DEPOSIT=0.0; BORROW=0.10; ETF_BASE={3:0.7}; ETF_KELLY={3:1.0}
SECTOR_CAP_EXEMPT={"RE_BACKLOG_BUY"}
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11={t:0.10 for t in TIER_BAL}
BUY_TIERS_V11={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
               "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS=12; SWITCH_COST=0.005
print("="*100); print("  INTEGRITY AUDIT — V4/V5 ETF leg: VNINDEX proxy vs real E1VFVN30"); print("="*100)
print("\n[1] Load...")
with open("data/ba_v11_unified_12y_sig.pkl","rb") as f: sig_B=pickle.load(f)
sig_B["time"]=pd.to_datetime(sig_B["time"]); sig_B=sig_B[(sig_B["time"]>=START_B)&(sig_B["time"]<=END_B)].copy()
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c=f.read()
VQU=re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""',_c,re.MULTILINE|re.DOTALL).group(1)
prices_B={tk:dict(zip(g["time"],g["Close"])) for tk,g in sig_B.groupby("ticker")}
liq_map_B={(r["ticker"],r["time"]):r["liq"] for _,r in sig_B.iterrows()}
vni_B=bq(VQU.format(start=START_B,end=END_B)); vni_B["time"]=pd.to_datetime(vni_B["time"])
vni_dates_B=sorted(vni_B["time"].unique())
vn30_proxy=dict(zip(vni_B["time"],vni_B["Close"]))     # VNINDEX proxy (current prod-spec)
# real E1VFVN30
etf=bq(f"""SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='E1VFVN30'
AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
etf["time"]=pd.to_datetime(etf["time"]); etf_real=dict(zip(etf["time"],etf["Close"]))
print(f"  E1VFVN30 coverage: {etf['time'].min().date()} -> {etf['time'].max().date()} ({len(etf)} days)")
# real dict with pre-2016 fallback to proxy (rescaled at splice so no jump)
vn30_real={}
splice=etf["time"].min()
scale=vn30_proxy.get(splice) and (etf_real[splice]/vn30_proxy[splice])
for d in vni_dates_B:
    if d in etf_real: vn30_real[d]=etf_real[d]
    elif d<splice and d in vn30_proxy: vn30_real[d]=vn30_proxy[d]*scale  # rescaled proxy pre-2016
# divergence stat 2024+
e2=etf[etf["time"]>="2024-01-01"].set_index("time")["Close"]
vnitmp=vni_B[vni_B["time"]>="2024-01-01"].set_index("time")["Close"]
if len(e2)>2 and len(vnitmp)>2:
    er=e2.iloc[-1]/e2.iloc[0]-1; vr=vnitmp.iloc[-1]/vnitmp.iloc[0]-1
    print(f"  2024-01->end return:  VNINDEX {vr*100:+.1f}%   E1VFVN30 {er*100:+.1f}%   gap {(vr-er)*100:+.1f}pp")

opens_df=bq(f"""SELECT t.ticker,t.time,t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Open IS NOT NULL""")
opens_df["time"]=pd.to_datetime(opens_df["time"])
open_prices={tk:dict(zip(g["time"],g["open_price"])) for tk,g in opens_df.groupby("ticker")}
vni_full=bq(f"""SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"]=pd.to_datetime(vni_full["time"])
sdf_tq=pd.read_csv("data/vnindex_5state_tam_quan_v3_4b_full_history.csv"); sdf_tq["time"]=pd.to_datetime(sdf_tq["time"])
sdf_tq=sdf_tq[(sdf_tq["time"]>=START_B)&(sdf_tq["time"]<=END_B)][["time","state"]]
sbd=dict(zip(sdf_tq["time"],sdf_tq["state"])); ff_tq={}; last=None
for d in vni_dates_B:
    s=sbd.get(d)
    if s is not None: last=s
    ff_tq[d]=last
print("\n[2] D1 + SV_TIGHT...")
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
sig_B=sig_B.merge(d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True),on=["ticker","time"],how="left")
omask=sig_B["_d1_ok"].fillna(False)&(sig_B["ta"]>=120); sig_B.loc[omask,"play_type"]="RE_BACKLOG_BUY"; sig_B=sig_B.drop(columns=["_d1_ok"])
def sv_keep(row):
    s=row.get("state5"); days=row.get("days_since_release")
    if pd.isna(s): return True
    s=int(s)
    if s in (4,5): return True
    if s==1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb=sig_B["play_type"].isin(BUY_TIERS_V11); sig_B=sig_B[(~mb)|sig_B.apply(sv_keep,axis=1)].copy()
v=vni_full.merge(sdf_tq,on="time",how="left"); v["state"]=v["state"].ffill()
oh=set(v[(v["Close"]/v["MA200"]>1.30)&((v["state"]==5)|(v["D_RSI"]>0.75))]["time"])
sig_v=sig_B.copy(); sig_v.loc[sig_v["time"].isin(oh)&sig_v["play_type"].isin(BUY_TIERS_V11),"play_type"]="AVOID_overheated"
top30=set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])
sec_map=bq("""SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t
WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ={"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}
def run_bal(etf_states,vn30u,label):
    nav,_=simulate(sig_v,prices_B,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=MAX_POS,hold_days=45,
        stop_loss=-0.20,min_hold=2,slippage=0.001,init_nav=BOOK_NAV,sector_limit_per_sector={8:4},
        ticker_sector_map=sec_map,sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=ff_tq,cash_etf_states=etf_states,
        vn30_underlying=vn30u,etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,open_prices=open_prices,t1_open_exec=True,**LIQ,name=label)
    nav["time"]=pd.to_datetime(nav["time"]); s=nav.set_index("time")["nav"]; print(f"  {label}: {s.iloc[-1]/1e9:.2f}B"); return s
def run_vn30(etf_states,vn30u,label):
    s30=sig_v[sig_v["ticker"].isin(top30)].copy(); p30={tk:prices_B[tk] for tk in top30 if tk in prices_B}
    l30={k:vv for k,vv in liq_map_B.items() if k[0] in top30}; L30={**LIQ,"liquidity_lookup":l30}
    nav,_=simulate(s30,p30,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=MAX_POS,hold_days=45,
        stop_loss=-0.20,min_hold=2,slippage=0.001,init_nav=BOOK_NAV,ticker_sector_map=sec_map,
        tier_weights=TIER_WEIGHTS_V11,deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=ff_tq,
        cash_etf_states=etf_states,vn30_underlying=vn30u,etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,open_prices=open_prices,t1_open_exec=True,**L30,name=label)
    nav["time"]=pd.to_datetime(nav["time"]); s=nav.set_index("time")["nav"]; print(f"  {label}: {s.iloc[-1]/1e9:.2f}B"); return s
print("\n[3] BAL/VN30 legs (4 combos)...")
bal_base_px=run_bal(ETF_BASE,vn30_proxy,"BAL_BASE_proxy");  vn30_base_px=run_vn30(ETF_BASE,vn30_proxy,"VN30_BASE_proxy")
bal_base_re=run_bal(ETF_BASE,vn30_real,"BAL_BASE_real");    vn30_base_re=run_vn30(ETF_BASE,vn30_real,"VN30_BASE_real")
bal_kel_px=run_bal(ETF_KELLY,vn30_proxy,"BAL_KEL_proxy");   vn30_kel_px=run_vn30(ETF_KELLY,vn30_proxy,"VN30_KEL_proxy")
bal_kel_re=run_bal(ETF_KELLY,vn30_real,"BAL_KEL_real");     vn30_kel_re=run_vn30(ETF_KELLY,vn30_real,"VN30_KEL_real")

print("\n[4] LAGGED v121...")
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
def run_lagged(init):
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
                pp=0.10 if en["surprise"]>0.5 else 0.08
                alloc=min(pp*nav_now,LC*adv*MF*fpx)
                if alloc<1e6 or alloc>cash: continue
                eff=fpx*(1+SI); sh=alloc/eff; cash-=sh*eff
                pos[tk]={"exit_dt":en["exit_dt"],"shares":sh}
        mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in pos.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
        nh.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(nh).set_index("time")["nav"]
lag=run_lagged(BOOK_NAV); print(f"  LAG v121: {lag.iloc[-1]/1e9:.2f}B")

print("\n[5] Ensemble...")
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
common=bal_base_px.index.intersection(vn30_base_px.index).intersection(lag.index)
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
        cur=int(sig.iloc[i])
        sec[i]=sec[i-1]*(1-SWITCH_COST) if cur!=prev else sec[i-1]
        r=vr.iloc[i] if cur==1 else lr.iloc[i]; sec[i]=sec[i]*(1+r); prev=cur
    return pd.Series((nbp.values+sec)/TOTAL_NAV,index=common)
navs={
 "V4 BASE  proxy": swnav(bal_base_px,vn30_base_px,lag,sigAH),
 "V4 BASE  REAL ": swnav(bal_base_re,vn30_base_re,lag,sigAH),
 "V5 KELLY proxy": swnav(bal_kel_px,vn30_kel_px,lag,sigAH),
 "V5 KELLY REAL ": swnav(bal_kel_re,vn30_kel_re,lag,sigAH),
}
def met(nav,st,en):
    s=nav[(nav.index>=st)&(nav.index<=en)].dropna()
    if len(s)<30: return None
    r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25; spy=len(r)/yrs if yrs>0 else 252
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0; dd=((s-s.cummax())/s.cummax()).min()
    return {"CAGR":cagr*100,"DD":dd*100,"Sharpe":r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0}
periods=[("FULL14","2014-01-01","2026-05-15"),("2016+","2016-01-07","2026-05-15"),("2024+","2024-01-01","2026-05-15")]
print("\n"+"="*92)
print(f"  {'Arm':<16}" + "".join([f"{p[0]+' CAGR':>13}{'DD':>8}" for p in periods]))
print("-"*92)
for name,nav in navs.items():
    row=f"  {name:<16}"
    for _,st,en in periods:
        m=met(nav,pd.Timestamp(st),pd.Timestamp(en)); row+=f"{m['CAGR']:>+12.2f}%{m['DD']:>+7.1f}%"
    print(row)
print("="*92)
print("  PROXY INFLATION (proxy CAGR - real CAGR):")
for tag,a,b in [("V4 BASE","V4 BASE  proxy","V4 BASE  REAL "),("V5 KELLY","V5 KELLY proxy","V5 KELLY REAL ")]:
    for _,st,en in periods:
        ma=met(navs[a],pd.Timestamp(st),pd.Timestamp(en)); mb=met(navs[b],pd.Timestamp(st),pd.Timestamp(en))
        print(f"    {tag} {_:<7}: proxy {ma['CAGR']:+.2f}% - real {mb['CAGR']:+.2f}% = INFLATION {ma['CAGR']-mb['CAGR']:+.2f}pp")
pd.DataFrame(navs).to_csv("data/prodspec_etf_audit_nav.csv")
print("\n  Saved -> data/prodspec_etf_audit_nav.csv\nDONE.")
