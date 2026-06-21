#!/usr/bin/env python3
"""run_fa8l_regime.py — regime-conditional SIZE overlay on the V11 book, comparing the WEAK flag:
  base          — no size modulation (control)
  regime_oldR   — weak = 8L discrete rating>=4   (the prior-art run_prodspec_rating_BC regime_size)
  regime_DE     — weak = per-group tier in {D,E} from fa_ratings_8l (better-calibrated compounder bottom)
Weak buy-rows are HALVED (0.05 vs 0.10) ONLY in BEAR/CRISIS (state<=2) via tier_weights_by_state.
Book signal = the OLD-fa play_types (FAbase pkl); we only modulate SIZE, never the gate (the integration
that won in prior art). V1 book (BAL+VN30); Full / IS(2014-19) / OOS(2020-now).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0,WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B="2014-01-01"; END_B="2026-05-15"
TOTAL_NAV=50_000_000_000; BOOK_NAV=TOTAL_NAV/2
DEPOSIT=0.0; BORROW=0.10; ETF_BASE={3:0.7}
TIER_BAL=["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
BUY_TIERS_V11={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
               "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS=12; FULL_SIZE=0.10; WEAK_SIZE=0.05
STATE_CSV="data/vnindex_5state_tam_quan_v3_4b_full_history.csv"

print("[shared] VNI/open/state/universe...")
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c=f.read()
VNI_Q=re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)
vni_B=bq(VNI_Q.format(start=START_B,end=END_B)); vni_B["time"]=pd.to_datetime(vni_B["time"])
vni_dates_B=sorted(vni_B["time"].unique()); vn30_proxy=dict(zip(vni_B["time"],vni_B["Close"]))
_etf=bq(f"""SELECT t.time,t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='E1VFVN30'
 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
_etf["time"]=pd.to_datetime(_etf["time"]); _er=dict(zip(_etf["time"],_etf["Close"]))
_sp=_etf["time"].min(); _sc=(_er[_sp]/vn30_proxy[_sp]) if vn30_proxy.get(_sp) else 1.0
vn30_underlying={}
for d in vni_dates_B:
    if d in _er: vn30_underlying[d]=_er[d]
    elif d<_sp and d in vn30_proxy: vn30_underlying[d]=vn30_proxy[d]*_sc
    elif d in vn30_proxy: vn30_underlying[d]=vn30_proxy[d]
opens_df=bq(f"""SELECT t.ticker,t.time,t.Open AS open_price FROM tav2_bq.ticker AS t
 WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
   AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Open IS NOT NULL""")
opens_df["time"]=pd.to_datetime(opens_df["time"])
open_prices={tk:dict(zip(g["time"],g["open_price"])) for tk,g in opens_df.groupby("ticker")}
vni_full=bq(f"""SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t
 WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"]=pd.to_datetime(vni_full["time"])
state_df=pd.read_csv(STATE_CSV); state_df["time"]=pd.to_datetime(state_df["time"])
state_df=state_df[(state_df["time"]>=START_B)&(state_df["time"]<=END_B)][["time","state"]]
sbd=dict(zip(state_df["time"],state_df["state"])); state_ff={}; last=None
for d in vni_dates_B:
    s=sbd.get(d)
    if s is not None: last=s
    state_ff[d]=last
v=vni_full.merge(state_df,on="time",how="left"); v["state"]=v["state"].ffill()
v["oh"]=((v["Close"]/v["MA200"]>1.30)&((v["state"]==5)|(v["D_RSI"]>0.75)))
oh_dates=set(v[v["oh"]]["time"])
top30=set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
 WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
 AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
 GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*COALESCE(t.Price,t.Close)) DESC LIMIT 30""")["ticker"])
sec_map=bq("""SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
 FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()

def sv_tight_keep(row):
    s=row.get("state5"); days=row.get("days_since_release")
    if pd.isna(s): return True
    s=int(s)
    if s in (4,5): return True
    if s==1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True

# ── load book signal (OLD fa play_types) + D1 + SV_TIGHT + overheat ──────────
print("[signal] FAbase book + D1 + SV_TIGHT + overheat...")
sig=pickle.load(open("data/ba_v11_FAbase_sig.pkl","rb")); sig["time"]=pd.to_datetime(sig["time"])
sig=sig[(sig["time"]>=START_B)&(sig["time"]<=END_B)].copy()
d1=bq(f"""
WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
   LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,
   LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,
   LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker,t.time,fa.fa_tier,SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 AS np_yoy,fin.Revenue_YoY_P0 AS rev_yoy,
  adv.adv_yoy,s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time=t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"]=pd.to_datetime(d1["time"])
dm=(d1["adv_yoy"].notna()&(d1["adv_yoy"]>0.5)&d1["fa_tier"].isin(["C","D"])
    &d1["state5"].isin([3,4,5])&((d1["np_yoy"].fillna(-99)>0)|(d1["rev_yoy"].fillna(-99)>0)))
dq=d1.loc[dm,["ticker","time"]].assign(_d1=True)
sig=sig.merge(dq,on=["ticker","time"],how="left")
om=sig["_d1"].fillna(False)&(sig["ta"]>=120); sig.loc[om,"play_type"]="RE_BACKLOG_BUY"; sig=sig.drop(columns=["_d1"])
mb=sig["play_type"].isin(BUY_TIERS_V11)
sig=sig[(~mb)|sig.apply(sv_tight_keep,axis=1)].copy()
sig.loc[sig["time"].isin(oh_dates)&sig["play_type"].isin(BUY_TIERS_V11),"play_type"]="AVOID_overheated"

# ── attach point-in-time 8L rating + per-group tier (as-of by eff_date) ──────
print("[attach] 8L rating + per-group tier (as-of)...")
rh=pd.read_csv("data/rating_8l_history.csv")
rh["eff_date"]=pd.to_datetime(rh["eff_date"])
rh=rh.sort_values("eff_date")[["ticker","eff_date","rating","tier"]].rename(columns={"eff_date":"time","tier":"tier8l"})
sig=sig.sort_values("time")
sig=pd.merge_asof(sig, rh, on="time", by="ticker", direction="backward")
buy=sig["play_type"].isin(BUY_TIERS_V11)
print(f"  coverage buy-rows: rating={sig.loc[buy,'rating'].notna().mean():.1%} tier={sig.loc[buy,'tier8l'].notna().mean():.1%}")
print(f"  buy-rows flagged weak: rating>=4 -> {int(((sig['rating']>=4)&buy).sum()):,}  "
      f"tier in DE -> {int((sig['tier8l'].isin(['D','E'])&buy).sum()):,}")

LIQ_BASE={"liquidity_volume_pct":0.20,"max_fill_days":5,"exit_slippage_tiered":True}

def run_book(sig_use, prices, liq_map, allowed, twbs, exempt, vn30=False, label=""):
    if vn30:
        sig_use=sig_use[sig_use["ticker"].isin(top30)].copy()
        prices={tk:prices[tk] for tk in top30 if tk in prices}
        liq_map={k:vv for k,vv in liq_map.items() if k[0] in top30}
    LIQ={**LIQ_BASE,"liquidity_lookup":liq_map}
    kw=dict(allowed_tiers=allowed,max_positions=MAX_POS,hold_days=45,stop_loss=-0.20,
        min_hold=2,slippage=0.001,init_nav=BOOK_NAV,ticker_sector_map=sec_map,
        tier_weights={t:FULL_SIZE for t in allowed},tier_weights_by_state=twbs,
        deposit_annual=DEPOSIT,borrow_annual=BORROW,state_by_date=state_ff,
        cash_etf_states=ETF_BASE,vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,etf_rebalance_friction=0.0015,
        open_prices=open_prices,t1_open_exec=True,**LIQ,name=label)
    if not vn30:
        kw["sector_limit_per_sector"]={8:4}; kw["sector_cap_exempt_tiers"]=exempt
    nav,_=simulate(sig_use,prices,vni_dates_B,**kw)
    nav["time"]=pd.to_datetime(nav["time"]); return nav.set_index("time")["nav"]

def build_mode(mode):
    s=sig.copy()
    base_tiers=list(TIER_BAL); exempt={"RE_BACKLOG_BUY"}
    if mode=="base":
        return s, base_tiers, None, exempt
    if mode=="exclude5":
        m=(s["rating"]==5)&s["play_type"].isin(set(base_tiers))
        s.loc[m,"play_type"]="AVOID_r5"
        print(f"    [exclude5] suppressed {int(m.sum()):,} rating-5 buy rows")
        return s, base_tiers, None, exempt
    if mode=="regime_oldR":
        weakmask=(s["rating"]>=4)
    else:  # regime_DE
        weakmask=s["tier8l"].isin(["D","E"])
    m=weakmask & s["play_type"].isin(set(base_tiers))
    s.loc[m,"play_type"]=s.loc[m,"play_type"]+"_W"
    weak_tiers=[t+"_W" for t in base_tiers]; allowed=base_tiers+weak_tiers
    twbs={st:{**{t:FULL_SIZE for t in base_tiers},**{t:WEAK_SIZE for t in weak_tiers}} for st in (1,2)}
    exempt={"RE_BACKLOG_BUY","RE_BACKLOG_BUY_W"}
    return s, allowed, twbs, exempt

def metrics(nav,a,b):
    s=nav[(nav.index>=a)&(nav.index<=b)].dropna()
    if len(s)<30: return None
    rets=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    spy=len(rets)/yrs if yrs>0 else 252
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sh=rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd=((s-s.cummax())/s.cummax()).min(); cal=cagr/abs(dd) if dd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100,"Calmar":cal}

navs={}
for mode in ["base","exclude5","regime_oldR"]:
    print(f"\n[run] {mode}")
    s,allowed,twbs,exempt=build_mode(mode)
    prices={tk:dict(zip(g["time"],g["Close"])) for tk,g in s.groupby("ticker")}
    liq_map={(r["ticker"],r["time"]):r["liq"] for _,r in s.iterrows()}
    bal=run_book(s,prices,liq_map,allowed,twbs,exempt,vn30=False,label=f"{mode}_BAL")
    v30=run_book(s,prices,liq_map,allowed,twbs,exempt,vn30=True,label=f"{mode}_VN30")
    common=bal.index.intersection(v30.index)
    navs[mode]=(bal.loc[common]+v30.loc[common])

common=navs["base"].index
for m in navs: common=common.intersection(navs[m].index)
segs=[("Full",common.min(),common.max()),
      ("IS 2014-2019",pd.Timestamp("2014-01-01"),pd.Timestamp("2019-12-31")),
      ("OOS 2020-now",pd.Timestamp("2020-01-01"),common.max())]
print("\n"+"="*100)
print("  V11 BOOK regime_size: weak-flag = rating>=4 (oldR) vs per-group tier D/E (DE)  —  Δ vs base")
print("="*100)
print(f"  {'Segment':<15}{'base CAGR/Sh/DD':<26}{'EXCLUDE5 (Δ)':<30}{'regime_oldR (Δ)':<30}")
for nm,a,b in segs:
    mb_=metrics(navs['base'].loc[common],a,b)
    me=metrics(navs['exclude5'].loc[common],a,b)
    mo=metrics(navs['regime_oldR'].loc[common],a,b)
    if not(mb_ and me and mo): continue
    print(f"  {nm:<15}{mb_['CAGR']:6.2f}% {mb_['Sharpe']:.2f} {mb_['DD']:6.1f}    "
          f"{me['CAGR']:6.2f}%({me['CAGR']-mb_['CAGR']:+.2f}) Sh{me['Sharpe']:.2f} DD{me['DD']:.1f}   "
          f"{mo['CAGR']:6.2f}%({mo['CAGR']-mb_['CAGR']:+.2f}) Sh{mo['Sharpe']:.2f} DD{mo['DD']:.1f}")
pd.DataFrame({k:v.loc[common] for k,v in navs.items()}).to_csv("data/fa8l_regime_navs.csv")
print("\n  saved data/fa8l_regime_navs.csv\nDONE.")
