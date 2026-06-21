# -*- coding: utf-8 -*-
"""pt_v11_audit_2014.py — V11 "Song Sinh" re-simulated 2014->now, AUDIT edition.
V11 = two momentum books (BAL full-universe + VN30 top-30), both BA-v11 stack (SIGNAL_V11 +
SV_TIGHT + overheat/P3 + D1 RE_BACKLOG + regime_size), KELLY ETF parking {3:1.0} (100% idle cash
to E1VFVN30 in NEUTRAL), static 50/50 combine. NO LAG, NO CAPIT, NO allocator, NO EXBULL-suppress
(those are V2.3-era). Auditable harness: T+1 Open fills (no intraday), ALL data from tav2_bq.*,
state from vnindex_5state_dt5g_live. Output: data/v11_audit_2014_now.csv (audit_lib format).
"""
import os, sys, io, bisect
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR); os.chdir(WORKDIR)
from simulate_holistic_nav import simulate, bq, VNI_QUERY
from signal_v11_sql import SIGNAL_V11
from pt_dates import detect_end_date
from regime_size_overlay import apply_regime_size
from audit_lib import emit_audit

START_DATE = "2014-01-02"; END_DATE = detect_end_date()
STATE_TABLE = "tav2_bq.vnindex_5state_dt5g_live"
BOOK_NAV = 25e9
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A",
                 "MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12
AUDIT_PATH = os.path.join(WORKDIR, "data", "v11_audit_2014_now.csv")
print("="*90); print(f" V11 Song Sinh (BAL+VN30 50/50, KELLY 1.0) AUDIT {START_DATE}->{END_DATE}  T+1 Open, BQ"); print("="*90)

# --- signals + SV_TIGHT + overheat + D1 + regime_size (identical to pt_v11_tq34b, no EXBULL) ---
print("[2] signals...")
sig = bq(SIGNAL_V11.format(start=START_DATE, end=END_DATE)); sig["time"] = pd.to_datetime(sig["time"])
assert len(sig) < 1_990_000
rel = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE_SUB(DATE '{START_DATE}', INTERVAL 120 DAY) AND DATE '{END_DATE}'""")
rel["Release_Date"] = pd.to_datetime(rel["Release_Date"])
rbt = rel.sort_values(["ticker","Release_Date"]).groupby("ticker")["Release_Date"].apply(list).to_dict()
ds = np.empty(len(sig))
for i,(tk,t) in enumerate(zip(sig["ticker"].values, sig["time"].values)):
    arr = rbt.get(tk);
    if not arr: ds[i]=np.nan; continue
    j = bisect.bisect_right(arr, pd.Timestamp(t)); ds[i] = np.nan if j==0 else (pd.Timestamp(t)-arr[j-1]).days
sig["days_since_release"] = ds
state_df = bq(f"SELECT s.time, s.state FROM {STATE_TABLE} AS s WHERE s.time <= DATE '{END_DATE}'")
state_df["time"] = pd.to_datetime(state_df["time"]); state_by_date = dict(zip(state_df["time"], state_df["state"]))
vni_full = bq(f"""SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["oh"] = (vni_full["Close"]/vni_full["MA200"]>1.30)&((vni_full["time"].map(state_by_date)==5)|(vni_full["D_RSI"]>0.75))
overheat_dates = set(vni_full[vni_full["oh"]]["time"]); sig["state"] = sig["time"].map(state_by_date)
d1 = bq(f"""WITH adv AS (SELECT f.ticker,f.time f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 adv_yoy,
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
d1["time"] = pd.to_datetime(d1["time"])
d1m = (d1["adv_yoy"].notna()&(d1["adv_yoy"]>0.5)&d1["fa_tier"].isin(["C","D"])&d1["state5"].isin([3,4,5])
       &((d1["np_yoy"].fillna(-99)>0)|(d1["rev_yoy"].fillna(-99)>0)))
sig = sig.merge(d1.loc[d1m,["ticker","time"]].assign(_ok=True), on=["ticker","time"], how="left")
sig.loc[sig["_ok"].fillna(False)&(sig["ta"]>=120),"play_type"]="RE_BACKLOG_BUY"; sig=sig.drop(columns=["_ok"])
_st=sig["state"]; _dy=sig["days_since_release"]; keep=pd.Series(True,index=sig.index)
keep[_st==1]=(_dy.notna()&(_dy<=30))[_st==1]; keep[_st.isin([2,3])]=(_dy.notna()&(_dy<=60))[_st.isin([2,3])]
mb=sig["play_type"].isin(BUY_TIERS_V11); sig_f=sig[(~mb)|keep].copy()
sig_f.loc[sig_f["time"].isin(overheat_dates)&sig_f["play_type"].isin(BUY_TIERS_V11),"play_type"]="AVOID_overheated"
sig_f, RS = apply_regime_size(sig_f, START_DATE, END_DATE, bq, base_tiers=TIER_BAL)

# --- common data ---
print("[3] prices/opens/etf/sector/top30...")
opens_df = bq(f"""SELECT t.ticker,t.time,t.Open op FROM tav2_bq.ticker t
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
state_ff={}; last=None
for d in vni_dates:
    s=state_by_date.get(d); last=s if s is not None else last; state_ff[d]=last
LIQ={"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map,"exit_slippage_tiered":True}
KW=dict(allowed_tiers=RS["allowed_tiers"],max_positions=MAX_POS,hold_days=45,stop_loss=-0.20,min_hold=2,
    slippage=0.0,init_nav=BOOK_NAV,tier_weights=RS["tier_weights"],tier_weights_by_state=RS["tier_weights_by_state"],
    deposit_annual=0.0,borrow_annual=0.10,state_by_date=state_ff,cash_etf_states={3:1.0},vn30_underlying=vn30_underlying,
    etf_mgmt_fee_annual=0.0,etf_tracking_drag_annual=0.0,etf_rebalance_friction=0.0015,
    open_prices=open_prices,t1_open_exec=True,entry_alt_prices=None,force_close_eod=False)

print("[4] BAL book (full universe)...")
ev_b,etf_b=[],[]
nav_b,_=simulate(sig_f,prices,vni_dates,ticker_sector_map=sec_map,sector_limit_per_sector={8:4},
    sector_cap_exempt_tiers=RS["sector_cap_exempt"],event_log=ev_b,etf_log=etf_b,name="v11_BAL",**KW,**LIQ)
nav_b["time"]=pd.to_datetime(nav_b["time"]); print(f"  BAL {len(ev_b)} ev; final {nav_b.set_index('time')['nav'].iloc[-1]/1e9:.4f}B")

print("[5] VN30 book (top30)...")
sig_v=sig_f[sig_f["ticker"].isin(top30)].copy(); prices_v={tk:prices[tk] for tk in top30 if tk in prices}
liq_v={k:v for k,v in liq_map.items() if k[0] in top30}; LIQ_V={**LIQ,"liquidity_lookup":liq_v}
ev_v,etf_v=[],[]
nav_v,_=simulate(sig_v,prices_v,vni_dates,ticker_sector_map=sec_map,event_log=ev_v,etf_log=etf_v,name="v11_VN30",**KW,**LIQ_V)
nav_v["time"]=pd.to_datetime(nav_v["time"]); print(f"  VN30 {len(ev_v)} ev; final {nav_v.set_index('time')['nav'].iloc[-1]/1e9:.4f}B")

print("[6] emit audit...")
meta=[("system","V11 Song Sinh = BAL(full) + VN30(top30) momentum, 50/50 static, KELLY ETF parking {3:1.0}, on DT5G"),
 ("source_script","pt_v11_audit_2014.py (faithful pt_v11_tq34b.py config; T+1 Open, all BQ, no intraday, no EXBULL-suppress)"),
 ("period",f"{START_DATE} -> {END_DATE}"),("state_source",STATE_TABLE),
 ("execution_rule","signal t -> exec t+1 OPEN (tav2_bq.ticker Open); multi-day fill <=20% ADV/day, 5 days; sells at next Open"),
 ("fee_buy","buy fee = buy_amount x ((1+0.0015)x(1+slip)-1), slip=0 both books"),
 ("fee_sell","sell fee = sell_amount x (1-(1-0.0015-0.001)x(1-slip)x(1-tier_slip)); tier_slip 0/.001/.003/.005 by %ADV"),
 ("etf_parking","KELLY: NEUTRAL(state 3) parks 100% idle cash in E1VFVN30 (cash_etf_states={3:1.0}); friction 0.15%/side; ETF priced at tav2_bq.ticker E1VFVN30 Close"),
 ("books_def","BAL = SIGNAL_V11 full prune universe (sector-8 cap 4); VN30 = same signal restricted to top-30 by 2020-2024 avg ADV (no sector cap). Each 25B, hold 45d, stop -20%, max 12, tier 10%/name (weak 5% in BEAR/CRISIS via 8L regime_size)"),
 ("cash_identity","per book per day: cash(d)-cash(d-1)==SUM TX [sell:+(sell_amount-fee)|buy:-(buy_amount+fee)]; cash(d)=<book>_cash_ref in DAILY"),
 ("nav_identity","nav_<book>_ref = <book>_cash_ref + <book>_stocks_ref(mark BQ Close) + <book>_etf_ref(E1VFVN30 Close); MTM rows (reason startswith MTM) mark open pos/lots at last Close so cash_ref+SUM(MTM)=nav_ref"),
 ("metric_formulas","CAGR=(end/0)^(365.25/days)-1; Sharpe=mean(dret)/std*sqrt(252); MaxDD=min(nav/cummax-1); Calmar=CAGR/|MaxDD|; on DAILY combined_nav=nav_bal_ref+nav_vn30_ref")]
res=emit_audit(AUDIT_PATH,"V11",meta,
  [{"label":"BAL","nav_df":nav_b,"init":BOOK_NAV,"events":ev_b,"etf":etf_b},
   {"label":"VN30","nav_df":nav_v,"init":BOOK_NAV,"events":ev_v,"etf":etf_v}],vni_close_by_date)
m=res["metrics"]; sc=res["selfcheck"]
print("="*90)
print(f" V11 AUDIT  final {res['combined'].iloc[-1]/1e9:.2f}B  CAGR {m['cagr']*100:.2f}%  Sharpe {m['sharpe_252']:.2f}  MaxDD {m['max_dd']*100:.1f}%  Calmar {m['calmar']:.2f}")
print(f" self-check: {sc}")
print(f" -> {AUDIT_PATH} ({res['n_tx']} TX rows)"); print("="*90)
