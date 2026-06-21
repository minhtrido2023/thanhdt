# -*- coding: utf-8 -*-
"""
tune_bav11_filters.py
=====================
Re-tune BA v11 state-aware filters (state PRESERVED — user insight that
market_state reflects crowd psychology + has real informational value).

Goal: improve OOS by tuning filter parameters without dropping state.

Three families of tests:
  (A) ABLATION — remove each filter to measure marginal value
  (B) SV_TIGHT day sweep — tighten/loosen per state
  (C) AVOID_bear/overheat tuning — soften bear block; broaden overheat
  (D) cash_etf parking sweep — broaden states that earn ETF carry

All runs use canonical signals + TQ34b state + standard 25B BAL leg.
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
STATE_CSV_TQ34B = "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"

print("="*100)
print("  BA v11 FILTER RE-TUNING (state PRESERVED)")
print("="*100)

# ─── Load ────────────────────────────────────────────────────────────────
print("\n[1] Load...")
with open("data/ba_v11_unified_12y_sig.pkl","rb") as f: sig_canon = pickle.load(f)
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

# Add FA tier from canonical pickle (need for AVOID_bear-exempt-AB)
# The pickle doesn't have fa_tier; query for it
print("[2] Query fa_tier...")
fa_q = bq(f"""
WITH dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
)
SELECT t.ticker, t.time, fa.fa_tier
FROM tav2_bq.ticker AS t
LEFT JOIN dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
""")
fa_q["time"] = pd.to_datetime(fa_q["time"])
sig_canon = sig_canon.merge(fa_q, on=["ticker","time"], how="left")

# D1 base
print("[3] D1 RE_BACKLOG query (state-aware {3,4,5})...")
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

# ─── Filter functions (parameterized) ────────────────────────────────────
def apply_sv_tight(sig, days_by_state, exempt_states=(4,5)):
    """days_by_state: dict like {1: 30, 2: 60, 3: 60}.
       States in exempt_states pass-through (no filter)."""
    def keep(row):
        s = row.get("state5"); days = row.get("days_since_release")
        if pd.isna(s): return True
        s = int(s)
        if s in exempt_states: return True
        thr = days_by_state.get(s)
        if thr is None: return True
        return pd.notna(days) and days <= thr
    mb_buy = sig["play_type"].isin(BUY_TIERS_V11)
    keep_mask = (~mb_buy) | sig.apply(keep, axis=1)
    return sig[keep_mask].copy()

def apply_avoid_bear(sig, bear_states=(1,2), exempt_fa_tiers=()):
    """Block buys in bear_states unless ticker has fa_tier in exempt_fa_tiers."""
    sig = sig.copy()
    state_series = pd.DataFrame({"time": list(state_ff_tq.keys()), "_st": list(state_ff_tq.values())})
    sig = sig.merge(state_series, on="time", how="left")
    in_bear = sig["_st"].isin(bear_states)
    if exempt_fa_tiers:
        exempt = sig["fa_tier"].isin(exempt_fa_tiers)
        block = in_bear & sig["play_type"].isin(BUY_TIERS_V11) & ~exempt
    else:
        block = in_bear & sig["play_type"].isin(BUY_TIERS_V11)
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

def evaluate(sig, cash_etf, label):
    nav = run_sim(sig, cash_etf, label)
    m_full = metrics(nav)
    m_is   = metrics(nav.loc["2014-01-01":"2019-12-31"])
    m_oos  = metrics(nav.loc["2020-01-01":"2026-05-15"])
    return nav, m_full, m_is, m_oos

# ─── BASELINE V_PROD ─────────────────────────────────────────────────────
print("\n[4] Baseline V_PROD (current production filters)...")
PROD_SVT = {1: 30, 2: 60, 3: 60}
PROD_BEAR = {"bear_states": (1,2), "exempt_fa_tiers": ()}
PROD_OH = {"ma200_thr": 1.30, "rsi_thr": 0.75, "oh_states": (5,)}
PROD_CASH_ETF = {3: 0.7}

def apply_all(sig, svt, bear, oh):
    sig = apply_avoid_bear(sig, **bear)
    sig = apply_sv_tight(sig, svt, exempt_states=(4,5))
    sig = apply_overheat(sig, **oh)
    return sig

sig_prod = apply_all(sig_canon, PROD_SVT, PROD_BEAR, PROD_OH)
nav_prod, m_prod_full, m_prod_is, m_prod_oos = evaluate(sig_prod, PROD_CASH_ETF, "V_PROD")
print(f"  V_PROD  Full {m_prod_full['cagr']:+.2f}%  IS {m_prod_is['cagr']:+.2f}%  OOS {m_prod_oos['cagr']:+.2f}%  DD_F {m_prod_full['maxdd']:+.1f}%  Sh {m_prod_full['sharpe']:.2f}")

def fmt(name, mf, mis, moos):
    return (f"  {name:<28} Full {mf['cagr']:+.2f}% (Δ{mf['cagr']-m_prod_full['cagr']:+.2f})  "
            f"IS {mis['cagr']:+.2f}% (Δ{mis['cagr']-m_prod_is['cagr']:+.2f})  "
            f"OOS {moos['cagr']:+.2f}% (Δ{moos['cagr']-m_prod_oos['cagr']:+.2f})  "
            f"DD_F {mf['maxdd']:+.1f}%  Sh {mf['sharpe']:.2f}")

# ─── (A) ABLATION ────────────────────────────────────────────────────────
print("\n" + "="*100)
print("  (A) ABLATION — remove each filter individually")
print("="*100)

# Remove SV_TIGHT (allow all)
sig_x = apply_avoid_bear(sig_canon, **PROD_BEAR)
sig_x = apply_overheat(sig_x, **PROD_OH)
_, mf, mis, moos = evaluate(sig_x, PROD_CASH_ETF, "no_SVT")
print(fmt("no_SVT", mf, mis, moos))

# Remove AVOID_bear
sig_x = apply_sv_tight(sig_canon, PROD_SVT, exempt_states=(4,5))
sig_x = apply_overheat(sig_x, **PROD_OH)
_, mf, mis, moos = evaluate(sig_x, PROD_CASH_ETF, "no_AVOID_bear")
print(fmt("no_AVOID_bear", mf, mis, moos))

# Remove overheat
sig_x = apply_avoid_bear(sig_canon, **PROD_BEAR)
sig_x = apply_sv_tight(sig_x, PROD_SVT, exempt_states=(4,5))
_, mf, mis, moos = evaluate(sig_x, PROD_CASH_ETF, "no_overheat")
print(fmt("no_overheat", mf, mis, moos))

# Remove cash_etf
_, mf, mis, moos = evaluate(sig_prod, None, "no_cash_etf")
print(fmt("no_cash_etf", mf, mis, moos))

# ─── (B) SV_TIGHT day sweep ──────────────────────────────────────────────
print("\n" + "="*100)
print("  (B) SV_TIGHT day sweep")
print("="*100)

svt_variants = [
    {1: 15, 2: 30, 3: 30},
    {1: 15, 2: 45, 3: 45},
    {1: 30, 2: 30, 3: 30},
    {1: 30, 2: 45, 3: 45},   # tighter
    {1: 30, 2: 45, 3: 60},
    {1: 30, 2: 60, 3: 90},   # looser
    {1: 30, 2: 90, 3: 60},
    {1: 45, 2: 60, 3: 60},
    {1: 45, 2: 90, 3: 90},
]
for svt in svt_variants:
    sig_x = apply_all(sig_canon, svt, PROD_BEAR, PROD_OH)
    _, mf, mis, moos = evaluate(sig_x, PROD_CASH_ETF, f"svt_{svt}")
    lbl = f"SVT s1={svt[1]} s2={svt[2]} s3={svt[3]}"
    print(fmt(lbl, mf, mis, moos))

# ─── (C) AVOID_bear / overheat tuning ────────────────────────────────────
print("\n" + "="*100)
print("  (C) AVOID_bear & overheat tuning")
print("="*100)

bear_variants = [
    {"bear_states": (1,), "exempt_fa_tiers": ()},                  # only block CRISIS
    {"bear_states": (1,2), "exempt_fa_tiers": ("A",)},             # block bear but A-tier exempt
    {"bear_states": (1,2), "exempt_fa_tiers": ("A","B")},          # block bear but A/B exempt
    {"bear_states": (1,2), "exempt_fa_tiers": ()},                 # current
]
for bear in bear_variants:
    sig_x = apply_all(sig_canon, PROD_SVT, bear, PROD_OH)
    _, mf, mis, moos = evaluate(sig_x, PROD_CASH_ETF, f"bear_{bear}")
    excl = "+".join(bear["exempt_fa_tiers"]) or "none"
    lbl = f"bear={bear['bear_states']} excl={excl}"
    print(fmt(lbl, mf, mis, moos))

oh_variants = [
    {"ma200_thr": 1.20, "rsi_thr": 0.75, "oh_states": (5,)},
    {"ma200_thr": 1.20, "rsi_thr": 0.75, "oh_states": (4,5)},
    {"ma200_thr": 1.25, "rsi_thr": 0.70, "oh_states": (4,5)},
    {"ma200_thr": 1.30, "rsi_thr": 0.70, "oh_states": (4,5)},
    {"ma200_thr": 1.30, "rsi_thr": 0.75, "oh_states": (5,)},      # current
    {"ma200_thr": 1.30, "rsi_thr": 0.75, "oh_states": (4,5)},
    {"ma200_thr": 1.40, "rsi_thr": 0.80, "oh_states": (5,)},
]
for oh in oh_variants:
    sig_x = apply_all(sig_canon, PROD_SVT, PROD_BEAR, oh)
    _, mf, mis, moos = evaluate(sig_x, PROD_CASH_ETF, f"oh_{oh}")
    lbl = f"OH ma200>{oh['ma200_thr']} rsi>{oh['rsi_thr']} st={oh['oh_states']}"
    print(fmt(lbl, mf, mis, moos))

# ─── (D) cash_etf parking sweep ──────────────────────────────────────────
print("\n" + "="*100)
print("  (D) cash_etf parking sweep")
print("="*100)

etf_variants = [
    {3: 0.7},                                # current
    {3: 0.5},
    {3: 1.0},
    {2: 0.3, 3: 0.7},
    {2: 0.5, 3: 0.7},
    {2: 0.3, 3: 0.7, 4: 0.3},
    {2: 0.5, 3: 0.7, 4: 0.5},
    {1: 0.3, 2: 0.5, 3: 0.7, 4: 0.5, 5: 0.3},
    None,                                    # no ETF
]
for etf in etf_variants:
    _, mf, mis, moos = evaluate(sig_prod, etf, f"etf_{etf}")
    print(fmt(f"ETF={etf}", mf, mis, moos))

print("\n" + "="*100)
print("  Run complete. Pick top OOS improvers from each section for combined test.")
print("="*100)
