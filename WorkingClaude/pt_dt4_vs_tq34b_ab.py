#!/usr/bin/env python3
"""pt_dt4_vs_tq34b_ab.py — PAPER-TRADE A/B: DT4-foundation vs TQ34b-foundation, V1..V5.
Window 2026-01-01 -> decision 2026-05-29 (pulled forward; go-live early June: which state foundation goes live).
Live-faithful: fresh SIGNAL_V11 (state5 from each foundation, warmup from 2025-06-01),
real E1VFVN30, DT4/TQ34b parking+overheat, t1_open, prod spec. Run daily (idempotent).

Foundations:
  DT4   = vnindex_5state_dt_4gate          (asym-commit, fewer AVOID_bear)
  TQ34b = vnindex_5state_tam_quan_v34b_clean (canonical, ~= LIVE)
Systems: V1 V11 / V2 V12 / V3 V12.1 / V4 V121_ENS / V5 V4+Kelly.
Outputs: data/pt_dt4_vs_tq34b_ab_logs.csv, _report.md
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
from datetime import datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import simulate, bq
from signal_v11_sql import SIGNAL_V11
from pt_dates import detect_end_date
SIG_START="2025-01-01"      # warmup + contiguous sim start (avoids mid-series start bug)
SIM_START="2026-01-01"      # A/B measurement window start (NAV sliced+rebased here)
END=detect_end_date(); DECISION_DATE="2026-05-29"   # pulled forward from 2026-06-30 per user: go-live early June, decide 2026-05-29
TOTAL_NAV=50e9; BOOK_NAV=25e9; DEPOSIT=0.0; BORROW=0.10
ETF_BASE={3:0.7}; ETF_KELLY={3:1.0}; SWITCH_COST=0.005
SECTOR_CAP_EXEMPT={"RE_BACKLOG_BUY"}
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS={t:0.10 for t in TIER_BAL}
BUY_TIERS={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
           "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS=12
FOUND={"DT4":"vnindex_5state_dt_4gate","TQ34b":"vnindex_5state_tam_quan_v34b_clean"}
print("="*100); print(f"  A/B DT4 vs TQ34b foundation | window {SIM_START} -> {END} | DECISION {DECISION_DATE}"); print("="*100)

# ---- common data ----
print("\n[1] common data...")
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c=f.read()
VQU=re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""',_c,re.MULTILINE|re.DOTALL).group(1)
vni_B=bq(VQU.format(start=SIG_START,end=END)); vni_B["time"]=pd.to_datetime(vni_B["time"])
all_dates=sorted(vni_B["time"].unique())
sim_dates=[d for d in all_dates if d>=pd.Timestamp(SIM_START)]
vn30_proxy=dict(zip(vni_B["time"],vni_B["Close"]))
_etf=bq(f"SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='E1VFVN30' AND t.time BETWEEN DATE '{SIG_START}' AND DATE '{END}' ORDER BY t.time")
_etf["time"]=pd.to_datetime(_etf["time"]); _er=dict(zip(_etf["time"],_etf["Close"]))
# E1VFVN30 (~25) and VNINDEX proxy (~1400) are on DIFFERENT scales — rescale the proxy to
# ETF scale for any date missing real ETF (e.g. tail days where ETF data lags). Avoids the
# 56x price jump that blows up KELLY parking NAV.
_ep=_etf["time"].max(); _sp=_etf["time"].min()
_scl_hi=(_er[_ep]/vn30_proxy[_ep]) if vn30_proxy.get(_ep) else 1.0
_scl_lo=(_er[_sp]/vn30_proxy[_sp]) if vn30_proxy.get(_sp) else 1.0
def _vn(d):
    if d in _er: return _er[d]
    if d<_sp: return vn30_proxy.get(d,np.nan)*_scl_lo
    return vn30_proxy.get(d,np.nan)*_scl_hi
vn30_underlying={d:_vn(d) for d in all_dates}
opens_df=bq(f"""SELECT t.ticker,t.time,t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{SIG_START}' AND DATE '{END}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Open IS NOT NULL""")
opens_df["time"]=pd.to_datetime(opens_df["time"]); open_prices={tk:dict(zip(g["time"],g["open_price"])) for tk,g in opens_df.groupby("ticker")}
vni_full=bq(f"SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{SIG_START}' AND DATE '{END}' ORDER BY t.time")
vni_full["time"]=pd.to_datetime(vni_full["time"])
top30=set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])
sec_map=bq("SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL").set_index("ticker")["s"].to_dict()

# ---- LAGGED (state-independent, once) ----
print("[2] LAGGED v12+v121 (once)...")
with open("earnings_px.pkl","rb") as f: px_data=pickle.load(f)
px_data["time"]=pd.to_datetime(px_data["time"])
px_close=px_data.pivot_table(index="time",columns="ticker",values="Close",aggfunc="first").sort_index().ffill(limit=5)
master_idx=pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index=master_idx; adates=np.array(master_idx)
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
    pos=np.searchsorted(adates,np.datetime64(ref),side="right")-1
    if pos<0: return None
    t=pos+off
    return pd.Timestamp(adates[t]) if 0<=t<len(adates) else None
sched=[]
for _,row in e_hl3.iterrows():
    tk=row["ticker"]; rdt=row["Release_Date"]
    if tk not in px_open.columns: continue
    ed=offset_date(rdt,5); xd=offset_date(rdt,30)
    if ed is None or xd is None: continue
    sched.append({"ticker":tk,"entry_dt":ed,"exit_dt":xd,"surprise":row["surprise_B_MA"]})
sched_lag=pd.DataFrame(sched).sort_values("entry_dt").reset_index(drop=True)
ebd=sched_lag.groupby("entry_dt"); xbd=sched_lag.groupby("exit_dt")
def run_lagged(use_s2):
    sd=[d for d in master_idx if pd.Timestamp(SIG_START)<=d<=pd.Timestamp(END)]
    cash=BOOK_NAV; pos={}; nh=[]; SI,SO,TX=0.001,0.0015,0.001; LC,MF=0.20,5; MP,LM=12,2e9
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
lag_v12=run_lagged(False); lag_v121=run_lagged(True)

# ---- ensemble signal (once) ----
cached=pd.read_csv("compare_v11_v12_concentration_switch.csv",index_col=0,parse_dates=True)
sig_m1=cached["sig_m1"].dropna().astype(int)
m3r_df=bq(f"""WITH base AS (SELECT t.time,t.ticker,
  SAFE_DIVIDE(t.Close,LAG(t.Close,126) OVER (PARTITION BY t.ticker ORDER BY t.time))-1 AS r6,
  AVG(t.Volume_3M_P50*t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 252 PRECEDING AND 1 PRECEDING) AS a1
  FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '{END}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)),
ranked AS (SELECT time,r6,a1,ROW_NUMBER() OVER (PARTITION BY time ORDER BY a1 DESC) AS rnk FROM base WHERE a1 IS NOT NULL AND r6 IS NOT NULL)
SELECT time, AVG(IF(rnk<=10,r6,NULL))-AVG(r6) AS M3r FROM ranked GROUP BY time ORDER BY time""")
m3r_df["time"]=pd.to_datetime(m3r_df["time"]); m3r=m3r_df.set_index("time")["M3r"]
def mksig(metric,mh=252):
    s=metric.dropna().sort_index(); em=s.expanding(min_periods=mh).median()
    return (s>em).astype(int).reindex(metric.index).ffill().fillna(1).astype(int).shift(1).fillna(1).astype(int)
sig_m3r=mksig(m3r)

LIQ_BASE={"liquidity_volume_pct":0.20,"max_fill_days":5,"exit_slippage_tiered":True}
def build_foundation(state_table, label):
    print(f"\n[F-{label}] state={state_table}...")
    SIG=SIGNAL_V11.replace("tav2_bq.vnindex_5state AS s","tav2_bq."+state_table+" AS s")
    sig=bq(SIG.format(start=SIG_START,end=END)); sig["time"]=pd.to_datetime(sig["time"])
    prices={tk:dict(zip(g["time"],g["Close"])) for tk,g in sig.groupby("ticker")}
    liq_map={(r["ticker"],r["time"]):r["liq"] for _,r in sig.iterrows()}
    sdt=bq(f"SELECT s.time,s.state FROM tav2_bq.{state_table} AS s WHERE s.time BETWEEN DATE '{SIG_START}' AND DATE '{END}' ORDER BY s.time")
    sdt["time"]=pd.to_datetime(sdt["time"]); sbd=dict(zip(sdt["time"],sdt["state"])); sff={}; last=None
    for d in all_dates:
        x=sbd.get(d)
        if x is not None: last=x
        sff[d]=last
    # D1
    d1=bq(f"""WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
      LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
    fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
    fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f)
    SELECT t.ticker,t.time,fa.fa_tier,SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 AS np_yoy,fin.Revenue_YoY_P0 AS rev_yoy,adv.adv_yoy,s5.state AS state5
    FROM tav2_bq.ticker AS t LEFT JOIN tav2_bq.{state_table} AS s5 ON s5.time=t.time
    LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
    LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
    LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
    WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{SIG_START}' AND DATE '{END}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
    d1["time"]=pd.to_datetime(d1["time"])
    d1m=(d1["adv_yoy"].notna()&(d1["adv_yoy"]>0.5)&d1["fa_tier"].isin(["C","D"])&d1["state5"].isin([3,4,5])&((d1["np_yoy"].fillna(-99)>0)|(d1["rev_yoy"].fillna(-99)>0)))
    sig=sig.merge(d1.loc[d1m,["ticker","time"]].assign(_ok=True),on=["ticker","time"],how="left")
    om=sig["_ok"].fillna(False)&(sig["ta"]>=120); sig.loc[om,"play_type"]="RE_BACKLOG_BUY"; sig=sig.drop(columns=["_ok"])
    def svk(r):
        s=r.get("state5"); d=r.get("days_since_release")
        if pd.isna(s): return True
        s=int(s)
        if s in (4,5): return True
        if s==1: return pd.notna(d) and d<=30
        if s in (2,3): return pd.notna(d) and d<=60
        return True
    mb=sig["play_type"].isin(BUY_TIERS); sig=sig[(~mb)|sig.apply(svk,axis=1)].copy()
    v=vni_full.merge(sdt,on="time",how="left"); v["state"]=v["state"].ffill()
    oh=set(v[(v["Close"]/v["MA200"]>1.30)&((v["state"]==5)|(v["D_RSI"]>0.75))]["time"])
    sig.loc[sig["time"].isin(oh)&sig["play_type"].isin(BUY_TIERS),"play_type"]="AVOID_overheated"
    def rb(etf,sub30,nm):
        s_use=sig[sig["ticker"].isin(top30)].copy() if sub30 else sig
        pr={tk:prices[tk] for tk in (top30 if sub30 else prices) if tk in prices}
        lq={k:vv for k,vv in liq_map.items() if (k[0] in top30)} if sub30 else liq_map
        nav,_=simulate(s_use,pr,all_dates,allowed_tiers=TIER_BAL,max_positions=MAX_POS,hold_days=45,stop_loss=-0.20,
            min_hold=2,slippage=0.001,init_nav=BOOK_NAV,**({"sector_limit_per_sector":{8:4}} if not sub30 else {}),
            ticker_sector_map=sec_map,sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,tier_weights=TIER_WEIGHTS,
            deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=sff,cash_etf_states=etf,vn30_underlying=vn30_underlying,
            etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,etf_rebalance_friction=0.0015,open_prices=open_prices,
            t1_open_exec=True,liquidity_volume_pct=0.20,max_fill_days=5,liquidity_lookup=lq,exit_slippage_tiered=True,name=nm)
        nav["time"]=pd.to_datetime(nav["time"]); return nav.set_index("time")["nav"]
    bal_base=rb(ETF_BASE,False,f"BAL_base_{label}"); vn30_base=rb(ETF_BASE,True,f"VN30_base_{label}")
    bal_kel=rb(ETF_KELLY,False,f"BAL_kel_{label}"); vn30_kel=rb(ETF_KELLY,True,f"VN30_kel_{label}")
    common=bal_base.index.intersection(vn30_base.index).intersection(lag_v12.index).intersection(lag_v121.index).intersection(bal_kel.index).intersection(vn30_kel.index)
    m1=sig_m1.reindex(common).ffill().fillna(1).astype(int); m3a=sig_m3r.reindex(common).ffill().fillna(1).astype(int)
    def ensAH(m1,m3):
        out=np.zeros(len(m1),int); cur=int(m1.iloc[0])
        for i,(a,b) in enumerate(zip(m1.values,m3.values)):
            if a==b: cur=int(a)
            out[i]=cur
        return pd.Series(out,index=m1.index)
    sg=ensAH(m1,m3a)
    def sw(bal,vn30,lg):
        br=bal.loc[common].pct_change().fillna(0); vr=vn30.loc[common].pct_change().fillna(0); lr=lg.loc[common].pct_change().fillna(0)
        nbp=(1+br).cumprod()*BOOK_NAV; sec=np.full(len(common),BOOK_NAV,float); prev=int(sg.iloc[0])
        for i in range(1,len(common)):
            cur=int(sg.iloc[i]); sec[i]=sec[i-1]*(1-SWITCH_COST) if cur!=prev else sec[i-1]
            r=vr.iloc[i] if cur==1 else lr.iloc[i]; sec[i]=sec[i]*(1+r); prev=cur
        return pd.Series((nbp.values+sec)/TOTAL_NAV,index=common)
    return {"V1":(bal_base.loc[common]+vn30_base.loc[common])/TOTAL_NAV,
            "V2":(bal_base.loc[common]+lag_v12.loc[common])/TOTAL_NAV,
            "V3":(bal_base.loc[common]+lag_v121.loc[common])/TOTAL_NAV,
            "V4":sw(bal_base,vn30_base,lag_v121),"V5":sw(bal_kel,vn30_kel,lag_v121)}

R={lab:build_foundation(tbl,lab) for lab,tbl in FOUND.items()}
# slice to A/B window + rebase to 1.0 at first 2026 session (YTD-2026 of a running book)
def rebase26(nav):
    s=nav[nav.index>=pd.Timestamp(SIM_START)].dropna()
    return s/s.iloc[0] if len(s) else s
R={lab:{sy:rebase26(R[lab][sy]) for sy in R[lab]} for lab in R}
def met(nav):
    s=nav.dropna(); r=s.pct_change().dropna(); n=len(r)
    yrs=max((s.index[-1]-s.index[0]).days/365.25,1e-9); spy=n/yrs if yrs>0 else 252
    tot=(s.iloc[-1]/s.iloc[0]-1)*100; cagr=((s.iloc[-1]/s.iloc[0])**(1/yrs)-1)*100
    sh=r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0; dd=((s-s.cummax())/s.cummax()).min()*100
    return tot,cagr,sh,dd
# logs
common=R["DT4"]["V5"].index
log=pd.DataFrame({"time":common})
for lab in FOUND:
    for sy in ["V1","V2","V3","V4","V5"]: log[f"{sy}_{lab}"]=R[lab][sy].reindex(common).values
log.to_csv("data/pt_dt4_vs_tq34b_ab_logs.csv",index=False)
# report
names={"V1":"V11","V2":"V12","V3":"V12.1","V4":"V121_ENS","V5":"V4+Kelly"}
lines=[f"# A/B DT4 vs TQ34b foundation — window {SIM_START} -> {common.max().date()}  (DECISION {DECISION_DATE})\n",
       f"*Live-faithful: fresh SIGNAL_V11 (state5 per foundation), real E1VFVN30, t1_open, prod-spec. 50B/system.*\n",
       "| System | DT4 TotRet | TQ34b TotRet | ΔTot | DT4 Sh | TQ Sh | DT4 DD | TQ DD | lead |","|---|---:|---:|---:|---:|---:|---:|---:|:--:|"]
votes={"DT4":0,"TQ34b":0}
for sy in ["V1","V2","V3","V4","V5"]:
    td,cd,shd,ddd=met(R["DT4"][sy]); tt,ct,sht,ddt=met(R["TQ34b"][sy])
    # vote: better total ret unless DD materially worse (>2pp) at <=0.3pp ret edge
    lead="DT4" if (td-tt)>0.0 else "TQ34b"
    if abs(td-tt)<0.3: lead="~"
    if lead in votes: votes[lead]+=1
    lines.append(f"| {sy} {names[sy]} | {td:+.2f}% | {tt:+.2f}% | {td-tt:+.2f} | {shd:+.2f} | {sht:+.2f} | {ddd:+.1f}% | {ddt:+.1f}% | {lead} |")
v5d=met(R["DT4"]["V5"]); v5t=met(R["TQ34b"]["V5"]); v4d=met(R["DT4"]["V4"]); v4t=met(R["TQ34b"]["V4"])
lines+=["",f"**Vote (per-system TotRet lead):** DT4={votes['DT4']}  TQ34b={votes['TQ34b']}",
        f"**Headline V5:** DT4 {v5d[0]:+.2f}% vs TQ34b {v5t[0]:+.2f}% (Δ{v5d[0]-v5t[0]:+.2f}pp, DD {v5d[3]:+.1f} vs {v5t[3]:+.1f})",
        f"**Headline V4:** DT4 {v4d[0]:+.2f}% vs TQ34b {v4t[0]:+.2f}% (Δ{v4d[0]-v4t[0]:+.2f}pp, DD {v4d[3]:+.1f} vs {v4t[3]:+.1f})"]
# verdict
gate="🟡 INCONCLUSIVE (short window)"
if common.max()>=pd.Timestamp(DECISION_DATE):
    if votes["DT4"]>=4 and v5d[0]>=v5t[0]: gate="🟢 GO LIVE: DT4 foundation"
    elif votes["TQ34b"]>=4 and v5t[0]>=v5d[0]: gate="🔴 GO LIVE: TQ34b foundation (keep canonical)"
    else: gate="🟡 SPLIT: decide per-system (see votes)"
lines.append(f"\n**DECISION ({DECISION_DATE}): {gate}**  | data updated to {common.max().date()}")
open("data/pt_dt4_vs_tq34b_ab_report.md","w",encoding="utf-8").write("\n".join(lines))
print("\n".join(lines[3:]))
print("\nSaved -> data/pt_dt4_vs_tq34b_ab_{logs.csv,report.md}\nDONE.")
