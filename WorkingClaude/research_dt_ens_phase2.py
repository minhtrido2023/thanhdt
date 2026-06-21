# -*- coding: utf-8 -*-
"""research_dt_ens_phase2.py — DT4 × ensemble integration, PHASE 2.

Designs (all vs canonical V121_ENS TQ34b from Phase-1 cache):
  E1  DT-Kelly parking on LAGGED idle cash (BASE {3:0.7} and KELLY {3:1.0})
  E2  Decouple: SVT/overheat on TQ34b, ETF parking on DT4 (BASE) for BAL+VN30
  E3  Same as E2 but KELLY parking intensity
  E4  DT CRISIS override: when DT in {0=CRISIS,1=BEAR} force switched leg to ETF or cash
  COMBO  stack the winners (+ weekly cadence cad5/dwell40 from E0)

Reuses data/dt_ens_legs.pkl (TQ legs). Mirrors Phase-1 data + VNINDEX-proxy ETF.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B = "2014-01-01"; END_B = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10
ETF_BASE = {3: 0.7}; ETF_KELLY = {3: 1.0}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
SWITCH_COST = 0.005
DT_CSV = "data/vnindex_5state_dt_10_25_25.csv"
TQ_CSV = "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"

print("="*104); print("  PHASE 2 — DT4 × ensemble integration designs E1/E2/E3/E4 + combos"); print("="*104)

# ── load Phase-1 cache (TQ legs + signals) ──────────────────────────────────
with open("data/dt_ens_legs.pkl","rb") as f: C = pickle.load(f)
common = C["common"]
bal_ret_tq = C["bal_ret_tq"]; vn30_ret_tq = C["vn30_ret_tq"]; lag_ret_v121 = C["lag_ret_v121"]
nav_bal_tq = C["nav_bal_tq"]; nav_vn30_tq = C["nav_vn30_tq"]; nav_lag_v121 = C["nav_lag_v121"]
m1_126 = C["m1_126"].reindex(common).ffill().fillna(1).astype(int)
m3_126 = C["m3_126"].reindex(common).ffill().fillna(1).astype(int)
print(f"  cache loaded: common={len(common)}  ({common[0].date()}→{common[-1].date()})")

# ── common data (needed for new sims) ───────────────────────────────────────
print("\n[1] Reloading data for new sims...")
with open("data/ba_v11_unified_12y_sig.pkl", "rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c=f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)
prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B)); vni_B["time"]=pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))
vni_full = bq(f"""SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

def load_state_ff(csv):
    sdf = pd.read_csv(csv); sdf["time"]=pd.to_datetime(sdf["time"])
    sdf = sdf[(sdf["time"]>=START_B)&(sdf["time"]<=END_B)][["time","state"]]
    sbd = dict(zip(sdf["time"], sdf["state"])); ff={}; last=None
    for d in vni_dates_B:
        s = sbd.get(d)
        if s is not None: last=s
        ff[d]=last
    return sdf, ff
dt_sdf, dt_ff = load_state_ff(DT_CSV)
tq_sdf, tq_ff = load_state_ff(TQ_CSV)

# ── LAGGED leg builder with optional DT parking (E1) ────────────────────────
print("\n[2] LAGGED schedule...")
with open("data/earnings_px.pkl","rb") as f: px_data=pickle.load(f)
px_data["time"]=pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time",columns="ticker",values="Close",aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index=master_idx
all_dates = np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov=pickle.load(f); ov["time"]=pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time",columns="ticker",values="Open",aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time",columns="ticker",values="Volume_3M_P50",aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
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

def run_lagged(init_nav, park_state_ff=None, park_etf_states=None):
    sim_days=[d for d in master_idx if pd.Timestamp(START_B)<=d<=pd.Timestamp(END_B)]
    cash=init_nav; positions={}; nav_hist=[]
    SLIP_IN,SLIP_OUT,TAX=0.001,0.0015,0.001; LIQ_CAP,MAX_FILL=0.20,5; ETF_FRIC=0.0015
    etf_shares=0.0; MAX_POS_L,LIQ_MIN=12,2e9
    sdict={(r["ticker"],r["entry_dt"]):r["surprise"] for _,r in sched_lag.iterrows()}
    for dt in sim_days:
        epx=vn30_underlying.get(dt); eok=epx is not None and not pd.isna(epx) and epx>0
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
        if park_etf_states is not None and eok:  # PRE-FILL SELL
            st=park_state_ff.get(dt); st=int(st) if st is not None else 3
            frac=park_etf_states.get(st,0.0); ev_=etf_shares*epx; pool=cash+ev_; tgt=pool*frac
            if ev_-tgt>pool*0.005:
                s=ev_-tgt; cash+=s-s*ETF_FRIC; etf_shares-=s/epx
        if dt in ebd.groups:
            mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
            nav_now=cash+mtm+(etf_shares*epx if eok else 0.0)
            for _,en in ebd.get_group(dt).iterrows():
                tk=en["ticker"]
                if tk in positions or len(positions)>=MAX_POS_L: continue
                fpx=px_open.at[dt,tk] if tk in px_open.columns else np.nan
                if pd.isna(fpx) or fpx<=0: continue
                adv=liq_l.at[dt,tk] if tk in liq_l.columns else 0
                if pd.isna(adv) or adv*fpx<LIQ_MIN: continue
                pos_pct=0.10 if sdict.get((tk,dt),0)>0.5 else 0.08
                target=pos_pct*nav_now; cap=LIQ_CAP*adv*MAX_FILL*fpx; alloc=min(target,cap)
                if alloc>cash and park_etf_states is not None and eok and etf_shares>0:
                    need=alloc-cash; ev_=etf_shares*epx; rel=min(need,ev_)
                    cash+=rel-rel*ETF_FRIC; etf_shares-=rel/epx
                if alloc<1e6 or alloc>cash: continue
                eff=fpx*(1+SLIP_IN); sh=alloc/eff; cash-=sh*eff
                positions[tk]={"entry_dt":dt,"exit_dt":en["exit_dt"],"shares":sh,"entry_px":fpx}
        if park_etf_states is not None and eok and cash>0:  # POST-FILL SWEEP
            st=park_state_ff.get(dt); st=int(st) if st is not None else 3
            frac=park_etf_states.get(st,0.0)
            if frac>0:
                ev_=etf_shares*epx; pool=cash+ev_; tgt=pool*frac; d=tgt-ev_
                if d>pool*0.005:
                    buy=min(d,cash); cash-=buy+buy*ETF_FRIC; etf_shares+=buy/epx
        mtm=sum(p["shares"]*px_close.at[dt,tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt,tk]))
        ev_=etf_shares*epx if eok else 0.0
        nav_hist.append({"time":dt,"nav":cash+mtm+ev_})
    return pd.DataFrame(nav_hist).set_index("time")["nav"]

print("  E1: LAGGED + DT parking (BASE, KELLY)...")
nav_lag_dt_base  = run_lagged(BOOK_NAV, park_state_ff=dt_ff, park_etf_states=ETF_BASE)
nav_lag_dt_kelly = run_lagged(BOOK_NAV, park_state_ff=dt_ff, park_etf_states=ETF_KELLY)
print(f"    LAG noPark={nav_lag_v121.iloc[-1]/1e9:.2f}B  DT_BASE={nav_lag_dt_base.iloc[-1]/1e9:.2f}B  DT_KELLY={nav_lag_dt_kelly.iloc[-1]/1e9:.2f}B")

# ── BAL+VN30 builder: SVT on svt_ff, parking on park_ff (E2/E3) ─────────────
def run_state_legs(svt_sdf, park_ff, park_etf_states, label):
    v=vni_full.merge(svt_sdf,on="time",how="left"); v["state"]=v["state"].ffill()
    v["overheat"]=((v["Close"]/v["MA200"]>1.30)&((v["state"]==5)|(v["D_RSI"]>0.75)))
    oh=set(v[v["overheat"]]["time"])
    sv=sig_B.copy()
    sv.loc[sv["time"].isin(oh)&sv["play_type"].isin(BUY_TIERS_V11),"play_type"]="AVOID_overheated"
    nb,_=simulate(sv,prices_B,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=10,hold_days=45,
        stop_loss=-0.20,min_hold=2,slippage=0.001,init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4},ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=park_ff,
        cash_etf_states=park_etf_states,vn30_underlying=vn30_underlying,**LIQ,name=f"BAL_{label}")
    nb["time"]=pd.to_datetime(nb["time"]); nbs=nb.set_index("time")["nav"]
    s30=sv[sv["ticker"].isin(top30)].copy(); p30={tk:prices_B[tk] for tk in top30 if tk in prices_B}
    l30={k:vv for k,vv in liq_map_B.items() if k[0] in top30}; L30={**LIQ,"liquidity_lookup":l30}
    nv,_=simulate(s30,p30,vni_dates_B,allowed_tiers=TIER_BAL,max_positions=10,hold_days=45,
        stop_loss=-0.20,min_hold=2,slippage=0.001,init_nav=BOOK_NAV,ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=park_ff,
        cash_etf_states=park_etf_states,vn30_underlying=vn30_underlying,**L30,name=f"VN30_{label}")
    nv["time"]=pd.to_datetime(nv["time"]); nvs=nv.set_index("time")["nav"]
    print(f"    [{label}] BAL={nbs.iloc[-1]/1e9:.2f}B VN30={nvs.iloc[-1]/1e9:.2f}B")
    return nbs, nvs

print("\n[3] E2/E3: BAL+VN30 SVT=TQ, parking=DT...")
nav_bal_dec_base, nav_vn30_dec_base   = run_state_legs(tq_sdf, dt_ff, ETF_BASE,  "DEC_BASE")
nav_bal_dec_kelly, nav_vn30_dec_kelly = run_state_legs(tq_sdf, dt_ff, ETF_KELLY, "DEC_KELLY")

# ── ensemble + eval ─────────────────────────────────────────────────────────
def ensemble_signal(m1_bin, m3_bin, cadence=1, min_dwell=0):
    idx=m1_bin.index; out=np.zeros(len(idx),int); cur=int(m1_bin.iloc[0]); lf=-10**9
    for i in range(len(idx)):
        if i%cadence==0:
            a,b=int(m1_bin.iloc[i]),int(m3_bin.iloc[i])
            if a==b and a!=cur and (i-lf)>=min_dwell: cur=a; lf=i
        out[i]=cur
    return pd.Series(out,index=idx)

etf_ret = pd.Series(vni_B.set_index("time")["Close"]).reindex(common).ffill().pct_change().fillna(0)
dt_state_common = pd.Series({d: dt_ff.get(d) for d in common}).reindex(common).ffill().fillna(3).astype(int)

def to_ret(nav): return nav.reindex(common).ffill().pct_change().fillna(0)

def eval_cfg(bal_ret, vn30_ret, lag_ret, signal, crisis_mode=None):
    """crisis_mode: None|'etf'|'cash' — when DT in {0,1} override switched leg."""
    nav_bal_path=(1+bal_ret).cumprod()*BOOK_NAV
    second=np.full(len(common),BOOK_NAV,float); prev=int(signal.iloc[0]); flips=0
    for i in range(1,len(common)):
        cur=int(signal.iloc[i])
        crisis = crisis_mode is not None and dt_state_common.iloc[i] in (0,1)
        if cur!=prev and not crisis: second[i]=second[i-1]*(1-SWITCH_COST); flips+=1
        else: second[i]=second[i-1]
        if crisis:
            r = etf_ret.iloc[i] if crisis_mode=='etf' else 0.0
        else:
            r = vn30_ret.iloc[i] if cur==1 else lag_ret.iloc[i]
        second[i]=second[i]*(1+r); prev=cur
    total=nav_bal_path.values+second
    return pd.Series(total/TOTAL_NAV,index=common), flips

def metrics(nav,st,en):
    s=nav[(nav.index>=st)&(nav.index<=en)]
    if len(s)<30: return None
    r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    spy=len(r)/yrs if yrs>0 else 252
    return {"CAGR":((s.iloc[-1]/s.iloc[0])**(1/yrs)-1)*100 if yrs>0 else 0,
            "Sharpe":r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0,
            "DD":((s-s.cummax())/s.cummax()).min()*100}

periods=[("FULL","2014-01-01","2026-05-15"),("IS14-19","2014-01-01","2019-12-31"),
         ("OOS20","2020-01-01","2026-05-15"),("OOS24","2024-01-01","2026-05-15")]

# precompute return series
r_bal_tq=to_ret(nav_bal_tq); r_vn30_tq=to_ret(nav_vn30_tq); r_lag_v121=to_ret(nav_lag_v121)
r_lag_dt_base=to_ret(nav_lag_dt_base); r_lag_dt_kelly=to_ret(nav_lag_dt_kelly)
r_bal_dec_base=to_ret(nav_bal_dec_base); r_vn30_dec_base=to_ret(nav_vn30_dec_base)
r_bal_dec_kelly=to_ret(nav_bal_dec_kelly); r_vn30_dec_kelly=to_ret(nav_vn30_dec_kelly)

sig_daily = ensemble_signal(m1_126, m3_126, 1, 0)
sig_weekly = ensemble_signal(m1_126, m3_126, 5, 40)   # E0 winner

configs = {
  "CANON (TQ legs, daily)":          (r_bal_tq,        r_vn30_tq,        r_lag_v121,     sig_daily,  None),
  "E1 LAG+DT park BASE":             (r_bal_tq,        r_vn30_tq,        r_lag_dt_base,  sig_daily,  None),
  "E1 LAG+DT park KELLY":            (r_bal_tq,        r_vn30_tq,        r_lag_dt_kelly, sig_daily,  None),
  "E2 decouple BASE (DT park)":      (r_bal_dec_base,  r_vn30_dec_base,  r_lag_v121,     sig_daily,  None),
  "E3 decouple KELLY (DT park)":     (r_bal_dec_kelly, r_vn30_dec_kelly, r_lag_v121,     sig_daily,  None),
  "E4 CRISIS->ETF (TQ legs)":        (r_bal_tq,        r_vn30_tq,        r_lag_v121,     sig_daily,  'etf'),
  "E4 CRISIS->CASH (TQ legs)":       (r_bal_tq,        r_vn30_tq,        r_lag_v121,     sig_daily,  'cash'),
  "COMBO A: E3+E1KELLY":             (r_bal_dec_kelly, r_vn30_dec_kelly, r_lag_dt_kelly, sig_daily,  None),
  "COMBO B: E3+E1KELLY+weekly":      (r_bal_dec_kelly, r_vn30_dec_kelly, r_lag_dt_kelly, sig_weekly, None),
  "COMBO C: E1KELLY+CRISIS->ETF":    (r_bal_tq,        r_vn30_tq,        r_lag_dt_kelly, sig_daily,  'etf'),
  "COMBO D: E3+E1KELLY+CRISIS->ETF": (r_bal_dec_kelly, r_vn30_dec_kelly, r_lag_dt_kelly, sig_daily,  'etf'),
}

navs={}; results={}
for name,(b,v,l,sig,cm) in configs.items():
    nav,flips=eval_cfg(b,v,l,sig,crisis_mode=cm); navs[name]=nav
    results[name]={"flips":flips, **{pl:metrics(nav,pd.Timestamp(s),pd.Timestamp(e)) for pl,s,e in periods}}

canon=results["CANON (TQ legs, daily)"]
print("\n"+"="*104)
print(f"  {'Config':<34}{'Full':>8}{'ΔFull':>7}{'IS':>8}{'OOS20':>8}{'OOS24':>8}{'ΔO24':>7}{'DD':>8}{'flips':>6}")
print("-"*104)
for name,res in results.items():
    f=res["FULL"]["CAGR"]; df=f-canon["FULL"]["CAGR"]
    o=res["OOS24"]["CAGR"]; do=o-canon["OOS24"]["CAGR"]
    print(f"  {name:<34}{f:>+7.2f}%{df:>+7.2f}{res['IS14-19']['CAGR']:>+7.2f}%"
          f"{res['OOS20']['CAGR']:>+7.2f}%{o:>+7.2f}%{do:>+6.2f}{res['FULL']['DD']:>+7.2f}%{res['flips']:>6}")
print("="*104)
print("  Sharpe (FULL):")
for name,res in results.items():
    print(f"    {name:<34} {res['FULL']['Sharpe']:+.2f}")

pd.DataFrame(navs).to_csv("data/dt_ens_phase2_nav.csv")
print("\n  Saved -> data/dt_ens_phase2_nav.csv")
print("DONE phase 2.")
