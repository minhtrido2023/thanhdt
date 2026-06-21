# -*- coding: utf-8 -*-
"""
test_v5_dt_integrated.py
========================
Test if DT_10_25_25 state-machine smoothing helps V5 (ETF_KELLY) integrated.

Hypothesis: V5 (ETF_KELLY = {3: 1.0}, 100% ETF parking in NEUTRAL) is MORE
sensitive to state transitions than V11 (BAL with ETF_BASE = {3: 0.7}) because:
  1. NEUTRAL↔BULL transition = full ETF flip (100% NAV affected)
  2. BEAR→NEUTRAL = 100% idle cash → ETF immediately
  3. 155 transitions × etf_rebalance_friction (0.15%) = drag accumulates
  4. DT_10_25_25 (34 transitions) reduces by 78%

V5 = 50/50 BAL(TQ+KELLY) + VN30(TQ+KELLY)

Test matrix:
  TQ34b + KELLY (= canonical V5)
  DT_10_25_25 + KELLY
  TQ34b + BASE  (= V1, for reference)
  DT_10_25_25 + BASE
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
ETF_BASE  = {3: 0.7}
ETF_KELLY = {3: 1.0}  # V5
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12

STATES = {
    "TQ34b":       "data/vnindex_5state_tam_quan_v3_4b_full_history.csv",
    "DT_10_25_25": "data/vnindex_5state_dt_10_25_25.csv",
}

print("="*100)
print("  V5 (ETF_KELLY) INTEGRATED — TQ34b vs DT_10_25_25")
print("="*100)

# ─── Common load ─────────────────────────────────────────────────────────
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

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

# Top 30 universe for VN30 leg
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# D1
print("[2] D1 RE_BACKLOG...")
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

# ─── State loaders ───────────────────────────────────────────────────────
def load_state(csv_path):
    sdf = pd.read_csv(csv_path)
    sdf["time"] = pd.to_datetime(sdf["time"])
    sdf = sdf[(sdf["time"]>=START_B) & (sdf["time"]<=END_B)][["time","state"]]
    sbd = dict(zip(sdf["time"], sdf["state"]))
    sff = {}; last=None
    for d in vni_dates_B:
        s = sbd.get(d)
        if s is not None: last = s
        sff[d] = last
    return sdf, sff

state_data = {name: load_state(csv) for name, csv in STATES.items()}

# Filter functions (V_PROD style)
def apply_sv_tight(sig, sff):
    days_by_state = {1: 30, 2: 60, 3: 60}
    sig = sig.copy()
    if "state5" in sig.columns: sig = sig.drop(columns=["state5"])
    sss = pd.DataFrame({"time": list(sff.keys()), "state5": list(sff.values())})
    sig = sig.merge(sss, on="time", how="left")
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

def apply_overheat(sig, sdf):
    v = vni_full.merge(sdf, on="time", how="left"); v["state"] = v["state"].ffill()
    v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
    oh = set(v[v["overheat"]]["time"])
    sig = sig.copy()
    sig.loc[sig["time"].isin(oh) & sig["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
    return sig

def run_bal(sig, sff, cash_etf, label):
    nav, _ = simulate(sig, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT, tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sff,
        cash_etf_states=cash_etf, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        **LIQ, name=label)
    nav["time"] = pd.to_datetime(nav["time"])
    return nav.set_index("time")["nav"]

def run_vn30(sig, sff, cash_etf, label):
    sig30 = sig[sig["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
    LIQ30 = {**LIQ, "liquidity_lookup":liq30}
    nav, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map, tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sff,
        cash_etf_states=cash_etf, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        **LIQ30, name=label)
    nav["time"] = pd.to_datetime(nav["time"])
    return nav.set_index("time")["nav"]

def run_v5(state_name, cash_etf):
    """V5 = 50/50 BAL+VN30 with same state + ETF config."""
    sdf, sff = state_data[state_name]
    # Apply standard V_PROD filters using this state
    sig_v = apply_sv_tight(sig_canon, sff)
    sig_v = apply_overheat(sig_v, sdf)
    print(f"    -> running BAL...")
    nav_bal = run_bal(sig_v, sff, cash_etf, f"{state_name}_BAL")
    print(f"    -> running VN30...")
    nav_vn30 = run_vn30(sig_v, sff, cash_etf, f"{state_name}_VN30")
    # Combine 50/50
    combined = (nav_bal + nav_vn30)
    return combined, nav_bal, nav_vn30

# ─── Run 4 combos ────────────────────────────────────────────────────────
print("\n[3] Run V5 + variants...")
results = {}

print("  [V1_TQ_BASE] TQ34b + ETF_BASE (= V1 for ref)...")
results["V1_TQ_BASE"], _, _ = run_v5("TQ34b", ETF_BASE)

print("  [V1_DT_BASE] DT_10_25_25 + ETF_BASE...")
results["V1_DT_BASE"], _, _ = run_v5("DT_10_25_25", ETF_BASE)

print("  [V5_TQ_KELLY] TQ34b + ETF_KELLY (= canonical V5)...")
results["V5_TQ_KELLY"], _, _ = run_v5("TQ34b", ETF_KELLY)

print("  [V5_DT_KELLY] DT_10_25_25 + ETF_KELLY...")
results["V5_DT_KELLY"], _, _ = run_v5("DT_10_25_25", ETF_KELLY)

# B&H ref
bh = pd.DataFrame({"time": list(vn30_underlying.keys()), "Close": list(vn30_underlying.values())})
bh = bh.sort_values("time").reset_index(drop=True)
bh["nav"] = TOTAL_NAV * bh["Close"] / bh["Close"].iloc[0]  # full NAV (TOTAL_NAV not BOOK_NAV since V5 is combined)
results["B&H"] = bh.set_index("time")["nav"]

# ─── Metrics ─────────────────────────────────────────────────────────────
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

print("\n" + "="*100)
print("  RESULTS — V5 vs V1 with TQ34b vs DT_10_25_25 (50B total NAV)")
print("="*100)

# Baseline V5_TQ_KELLY
m_base = metrics(results["V5_TQ_KELLY"])
m_base_is = metrics(results["V5_TQ_KELLY"].loc["2014-01-01":"2019-12-31"])
m_base_oos = metrics(results["V5_TQ_KELLY"].loc["2020-01-01":"2026-05-15"])

print(f"\n  {'Combo':<22} {'Final':>10} {'CAGR':>8} {'IS':>8} {'OOS':>8} {'DD':>7} {'Sharpe':>7}")
for name in ["V1_TQ_BASE","V1_DT_BASE","V5_TQ_KELLY","V5_DT_KELLY"]:
    nav = results[name]
    m = metrics(nav)
    m_is = metrics(nav.loc["2014-01-01":"2019-12-31"])
    m_oos = metrics(nav.loc["2020-01-01":"2026-05-15"])
    print(f"  {name:<22} {m['final']:>9.2f}B {m['cagr']:>+6.2f}% {m_is['cagr']:>+6.2f}% {m_oos['cagr']:>+6.2f}% {m['maxdd']:>+6.1f}% {m['sharpe']:>7.2f}")
m_bh = metrics(results["B&H"])
print(f"  {'B&H':<22} {m_bh['final']:>9.2f}B {m_bh['cagr']:>+6.2f}% {'-':>7} {'-':>7} {m_bh['maxdd']:>+6.1f}% {m_bh['sharpe']:>7.2f}")

# Δ analysis
print("\n  Δ Analysis:")
print(f"  V1 BASE: DT vs TQ: ΔCAGR Full = {metrics(results['V1_DT_BASE'])['cagr']-metrics(results['V1_TQ_BASE'])['cagr']:+.2f}pp  IS = {metrics(results['V1_DT_BASE'].loc['2014':'2019'])['cagr']-metrics(results['V1_TQ_BASE'].loc['2014':'2019'])['cagr']:+.2f}pp  OOS = {metrics(results['V1_DT_BASE'].loc['2020':])['cagr']-metrics(results['V1_TQ_BASE'].loc['2020':])['cagr']:+.2f}pp")
print(f"  V5 KELLY: DT vs TQ: ΔCAGR Full = {metrics(results['V5_DT_KELLY'])['cagr']-metrics(results['V5_TQ_KELLY'])['cagr']:+.2f}pp  IS = {metrics(results['V5_DT_KELLY'].loc['2014':'2019'])['cagr']-metrics(results['V5_TQ_KELLY'].loc['2014':'2019'])['cagr']:+.2f}pp  OOS = {metrics(results['V5_DT_KELLY'].loc['2020':])['cagr']-metrics(results['V5_TQ_KELLY'].loc['2020':])['cagr']:+.2f}pp")

# Sub-period
print("\n  Sub-period CAGR (4-year):")
periods = [("14-17","2014-01-01","2017-12-31"), ("18-19","2018-01-01","2019-12-31"),
           ("20-22","2020-01-01","2022-12-31"), ("23-26","2023-01-01","2026-05-15")]
print(f"  {'Combo':<22}", end="")
for p,_,_ in periods: print(f"{p:>9}", end="")
print()
for name in ["V1_TQ_BASE","V1_DT_BASE","V5_TQ_KELLY","V5_DT_KELLY"]:
    print(f"  {name:<22}", end="")
    for _, sd, ed in periods:
        sub = results[name].loc[sd:ed]
        m = metrics(sub)
        print(f"{m['cagr']:>+7.2f}%", end="  ")
    print()

# Save
combined = pd.DataFrame({n: nav for n, nav in results.items()})
combined.to_csv(os.path.join(WORKDIR, "data/v5_dt_integrated_nav.csv"))
print(f"\n  Saved -> data/v5_dt_integrated_nav.csv")
