# -*- coding: utf-8 -*-
"""
test_c3_refinements.py
======================
Final refinement test before production recommendation.

Variants:
  V_PROD               baseline current production
  C3_modest            SVT s3=60→90 ONLY (no cash_etf change, safest)
  C3_cons              SVT s3=90 + cash_etf {2:0.5, 3:0.7}
  C3_tight_uniform     SVT s1=s2=s3=30 (tighter uniformly)
  C3_loose_s3_120      SVT s3=120 (super loose NEUTRAL)
  C3_loose_s3_180      SVT s3=180 (very loose)
  C3_no_svt_only       Remove SVT entirely, everything else baseline

Goal: find absolute sweet spot for the SVT lever.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B = "2014-01-01"
END_B   = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12
STATE_CSV_TQ34B = "vnindex_5state_tam_quan_v3_4b_full_history.csv"

print("="*100)
print("  REFINEMENT TEST — SVT lever + safety variants")
print("="*100)

# Common setup (abbreviated, same as before)
print("\n[1] Load + setup...")
with open("ba_v11_unified_12y_sig.pkl","rb") as f: sig_canon = pickle.load(f)
sig_canon["time"] = pd.to_datetime(sig_canon["time"])
sig_canon = sig_canon[(sig_canon["time"]>=START_B) & (sig_canon["time"]<=END_B)].copy()

with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c = f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)
prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_canon.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_canon.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))

opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk,g in opens_df.groupby("ticker")}

vni_full = bq(f"""SELECT t.time, t.Close, t.MA50, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

state_df_tq = pd.read_csv(STATE_CSV_TQ34B)
state_df_tq["time"] = pd.to_datetime(state_df_tq["time"])
state_df_tq = state_df_tq[(state_df_tq["time"]>=START_B) & (state_df_tq["time"]<=END_B)][["time","state"]]
sbd_tq = dict(zip(state_df_tq["time"], state_df_tq["state"]))
state_ff_tq = {}; last=None
for d in vni_dates_B:
    s = sbd_tq.get(d)
    if s is not None: last = s
    state_ff_tq[d] = last

# D1
d1 = bq(f"""
WITH adv_dated AS (
  SELECT f.ticker, f.time AS f_time,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f
),
fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
)
SELECT t.ticker, t.time, fa.fa_tier,
  SAFE_DIVIDE(t.NP_P0, t.NP_P4)-1 AS np_yoy,
  fin.Revenue_YoY_P0 AS rev_yoy, adv.adv_yoy, s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time = t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
           & d1["state5"].isin([3,4,5])
           & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_q = d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True)
sig_canon = sig_canon.merge(d1_q, on=["ticker","time"], how="left")
omask = sig_canon["_d1_ok"].fillna(False) & (sig_canon["ta"]>=120)
sig_canon.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
sig_canon = sig_canon.drop(columns=["_d1_ok"])

# Filter functions
def apply_sv_tight(sig, days_by_state):
    if days_by_state is None: return sig.copy()
    def keep(row):
        s = row.get("state5"); days = row.get("days_since_release")
        if pd.isna(s): return True
        s = int(s)
        if s in (4,5): return True
        thr = days_by_state.get(s)
        if thr is None: return True
        return pd.notna(days) and days <= thr
    mb_buy = sig["play_type"].isin(BUY_TIERS_V11)
    keep_mask = (~mb_buy) | sig.apply(keep, axis=1)
    return sig[keep_mask].copy()

def apply_avoid_bear(sig, bear_states=(1,2)):
    sig = sig.copy()
    state_series = pd.DataFrame({"time": list(state_ff_tq.keys()), "_st": list(state_ff_tq.values())})
    sig = sig.merge(state_series, on="time", how="left")
    block = sig["_st"].isin(bear_states) & sig["play_type"].isin(BUY_TIERS_V11)
    sig.loc[block, "play_type"] = "AVOID_bear"
    return sig.drop(columns=["_st"])

def apply_overheat(sig, ma200_thr=1.30, rsi_thr=0.75, oh_states=(5,)):
    v = vni_full.merge(state_df_tq, on="time", how="left"); v["state"] = v["state"].ffill()
    cond_price = v["Close"]/v["MA200"] > ma200_thr
    cond_state = v["state"].isin(oh_states)
    cond_rsi   = v["D_RSI"] > rsi_thr
    v["overheat"] = cond_price & (cond_state | cond_rsi)
    oh = set(v[v["overheat"]]["time"])
    sig = sig.copy()
    sig.loc[sig["time"].isin(oh) & sig["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
    return sig

def run_sim(sig, cash_etf, label):
    nav, _ = simulate(sig, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT, tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff_tq,
        cash_etf_states=cash_etf, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        **LIQ, name=label)
    nav["time"] = pd.to_datetime(nav["time"])
    return nav.set_index("time")["nav"]

def metrics(nav_s):
    init = nav_s.iloc[0]; final = nav_s.iloc[-1]
    years = (nav_s.index[-1] - nav_s.index[0]).days/365.25
    cagr = (final/init)**(1/years)-1
    daily = nav_s.pct_change().dropna()
    sh = daily.mean()/daily.std()*np.sqrt(252) if daily.std()>0 else 0
    rm = nav_s.expanding().max()
    dd = ((nav_s-rm)/rm).min()
    return {"final":final/1e9, "cagr":cagr*100, "sharpe":sh, "maxdd":dd*100,
            "calmar": cagr/(-dd) if dd<0 else float('inf')}

def build_run(svt, bear, oh, etf, label):
    sig = apply_avoid_bear(sig_canon, bear_states=bear)
    sig = apply_sv_tight(sig, svt)
    sig = apply_overheat(sig, **oh)
    return run_sim(sig, etf, label)

# ─── Configs ─────────────────────────────────────────────────────────────
OH_PROD = dict(ma200_thr=1.30, rsi_thr=0.75, oh_states=(5,))
BEAR_PROD = (1,2)

CFG = {
    "V_PROD":               dict(svt={1:30,2:60,3:60},   bear=BEAR_PROD, oh=OH_PROD, etf={3:0.7}),
    "C3_modest_SVTonly":    dict(svt={1:30,2:60,3:90},   bear=BEAR_PROD, oh=OH_PROD, etf={3:0.7}),
    "C3_modest_PLUS_ETF":   dict(svt={1:30,2:60,3:90},   bear=BEAR_PROD, oh=OH_PROD, etf={2:0.5, 3:0.7}),
    "C3_uniform_tight":     dict(svt={1:30,2:30,3:30},   bear=BEAR_PROD, oh=OH_PROD, etf={3:0.7}),
    "C3_loose_120":         dict(svt={1:30,2:60,3:120},  bear=BEAR_PROD, oh=OH_PROD, etf={3:0.7}),
    "C3_loose_180":         dict(svt={1:30,2:60,3:180},  bear=BEAR_PROD, oh=OH_PROD, etf={3:0.7}),
    "C3_no_svt_only":       dict(svt=None,                bear=BEAR_PROD, oh=OH_PROD, etf={3:0.7}),
    "C3_no_svt_ETF":        dict(svt=None,                bear=BEAR_PROD, oh=OH_PROD, etf={2:0.5, 3:0.7}),
    "C3_no_svt_OH":         dict(svt=None,                bear=BEAR_PROD, oh=dict(ma200_thr=1.25, rsi_thr=0.70, oh_states=(4,5)), etf={3:0.7}),
}

print("\n[2] Run all candidates...")
results = {}
for name, cfg in CFG.items():
    print(f"  {name}...")
    results[name] = build_run(cfg["svt"], cfg["bear"], cfg["oh"], cfg["etf"], name)

# Summary
print("\n" + "="*100)
print("  RESULTS")
print("="*100)
m_prod_full = metrics(results["V_PROD"])
m_prod_is   = metrics(results["V_PROD"].loc["2014-01-01":"2019-12-31"])
m_prod_oos  = metrics(results["V_PROD"].loc["2020-01-01":"2026-05-15"])

print(f"\n  {'Variant':<24} {'Full':>8} {'IS':>8} {'OOS':>8} {'ΔFull':>8} {'ΔIS':>8} {'ΔOOS':>8} {'DD':>7} {'Sh':>5}")
for name in CFG.keys():
    nav = results[name]
    m_f = metrics(nav)
    m_i = metrics(nav.loc["2014-01-01":"2019-12-31"])
    m_o = metrics(nav.loc["2020-01-01":"2026-05-15"])
    df = m_f["cagr"] - m_prod_full["cagr"]
    di = m_i["cagr"] - m_prod_is["cagr"]
    do = m_o["cagr"] - m_prod_oos["cagr"]
    print(f"  {name:<24} {m_f['cagr']:>+6.2f}% {m_i['cagr']:>+6.2f}% {m_o['cagr']:>+6.2f}% "
          f"{df:>+6.2f}pp {di:>+6.2f}pp {do:>+6.2f}pp {m_f['maxdd']:>+6.1f}% {m_f['sharpe']:>5.2f}")

# Sub-periods for top 3
print("\n  Sub-period (4-year):")
periods = [("14-17","2014-01-01","2017-12-31"), ("18-19","2018-01-01","2019-12-31"),
           ("20-22","2020-01-01","2022-12-31"), ("23-26","2023-01-01","2026-05-15")]
print(f"  {'Variant':<24}", end="")
for p,_,_ in periods: print(f"{p:>8}", end="")
print()
for name in ["V_PROD","C3_modest_SVTonly","C3_modest_PLUS_ETF","C3_loose_120","C3_no_svt_only","C3_no_svt_ETF"]:
    print(f"  {name:<24}", end="")
    for _, sd, ed in periods:
        sub = results[name].loc[sd:ed]
        m = metrics(sub)
        print(f"{m['cagr']:>+6.2f}%", end="  ")
    print()
