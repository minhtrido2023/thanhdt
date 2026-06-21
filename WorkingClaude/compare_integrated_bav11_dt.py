# -*- coding: utf-8 -*-
"""
compare_integrated_bav11_dt.py
==============================
Integrated BA v11 comparison: TQ34b vs DT variants.

CRITICAL: per memory, v2g standalone wins didn't transfer to BA-integrated
(+1.28pp standalone but -2.40pp integrated). Must test integrated.

Strategy: run only the BAL leg (faster than full 5-system, but captures the
main state-dependent behavior). BAL leg uses state_by_date for tier sizing.

For each state CSV:
  - Build state_ff (forward-filled state by date)
  - Apply SV_TIGHT filter (state-dependent days_since_release)
  - Apply overheat AVOID (state==5 + Close/MA200 > 1.30)
  - Run simulate() with BAL config

Compare final NAV / CAGR / Sharpe / MaxDD per variant.
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
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12

STATE_CSVS = {
    "TQ34b":         "data/vnindex_5state_tam_quan_v3_4b_full_history.csv",
    "DT_5_15_15":    "data/vnindex_5state_dt_5_15_15.csv",
    "DT_7_20_20":    "data/vnindex_5state_dt_7_20_20.csv",
    "DT_10_25_25":   "data/vnindex_5state_dt_10_25_25.csv",
    "DT_15_30_25":   "data/vnindex_5state_dt_15_30_25.csv",
}

print("="*100)
print("  INTEGRATED BA v11 — TQ34b vs DT variants (BAL leg, 25B per book)")
print("="*100)

# ─── Load common signals ─────────────────────────────────────────────────
print("\n[1] Loading signals + prices + VNI...")
with open("data/ba_v11_unified_12y_sig.pkl","rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
sig_B = sig_B[(sig_B["time"]>=START_B) & (sig_B["time"]<=END_B)].copy()
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c = f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)
prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
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

# ─── D1 RE_BACKLOG (computed once, applies to all variants) ──────────────
print("\n[2] D1 RE_BACKLOG_BUY reclassification (using BQ canonical state)...")
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
sig_B = sig_B.merge(d1_q, on=["ticker","time"], how="left")
omask = sig_B["_d1_ok"].fillna(False) & (sig_B["ta"]>=120)
sig_B.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
sig_B = sig_B.drop(columns=["_d1_ok"])

# ─── Sector + universe (once) ────────────────────────────────────────────
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}


def sv_tight_keep(row):
    s = row.get("state5"); days = row.get("days_since_release")
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True


def run_variant(state_csv_path, label):
    """Load state CSV, build state_ff, apply SV_TIGHT + overheat, run BAL sim."""
    state_df = pd.read_csv(state_csv_path)
    state_df["time"] = pd.to_datetime(state_df["time"])
    state_df = state_df[(state_df["time"]>=START_B) & (state_df["time"]<=END_B)][["time","state"]]

    # Forward-fill state by trading day
    sbd = dict(zip(state_df["time"], state_df["state"]))
    state_ff = {}; last = None
    for d in vni_dates_B:
        s = sbd.get(d)
        if s is not None: last = s
        state_ff[d] = last

    # ----- SV_TIGHT (state-dependent days_since_release filter) ----------
    # state5 mapping: we need to add a state5 column to sig_B for the filter
    sig_v = sig_B.copy()
    state_series = pd.Series(state_ff).reset_index()
    state_series.columns = ["time","state5_dyn"]
    sig_v = sig_v.merge(state_series, on="time", how="left")
    # Use dynamic state5 from current variant
    if "state5" in sig_v.columns:
        sig_v["state5"] = sig_v["state5_dyn"].fillna(sig_v["state5"])
    else:
        sig_v["state5"] = sig_v["state5_dyn"]
    sig_v = sig_v.drop(columns=["state5_dyn"])

    mb_buy = sig_v["play_type"].isin(BUY_TIERS_V11)
    keep_mask = (~mb_buy) | sig_v.apply(sv_tight_keep, axis=1)
    sig_v = sig_v[keep_mask].copy()

    # ----- Overheat AVOID -----
    v_st = vni_full.merge(state_df, on="time", how="left"); v_st["state"] = v_st["state"].ffill()
    v_st["overheat"] = ((v_st["Close"]/v_st["MA200"]>1.30) & ((v_st["state"]==5) | (v_st["D_RSI"]>0.75)))
    oh = set(v_st[v_st["overheat"]]["time"])
    sig_v.loc[sig_v["time"].isin(oh) & sig_v["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"

    # ----- Simulate -----
    nav, _ = simulate(sig_v, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
        tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff,
        cash_etf_states=ETF_BASE, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        **LIQ, name=label)
    nav["time"] = pd.to_datetime(nav["time"])
    s = nav.set_index("time")["nav"]
    return s


def metrics(nav_s, label, baseline=None):
    """Compute CAGR / Sharpe / MaxDD."""
    init = nav_s.iloc[0]
    final = nav_s.iloc[-1]
    years = (nav_s.index[-1] - nav_s.index[0]).days / 365.25
    cagr = (final/init) ** (1/years) - 1
    daily_ret = nav_s.pct_change().dropna()
    sharpe = daily_ret.mean()/daily_ret.std()*np.sqrt(252) if daily_ret.std() > 0 else 0
    rm = nav_s.expanding().max()
    dd = ((nav_s - rm)/rm).min()
    cal = cagr/(-dd) if dd < 0 else float('inf')
    out = {"label":label, "final":final/1e9, "cagr":cagr*100,
           "sharpe":sharpe, "maxdd":dd*100, "calmar":cal}
    if baseline is not None:
        out["d_cagr"] = (cagr - baseline["cagr"]/100) * 100
    return out


# ─── Run all variants ────────────────────────────────────────────────────
print("\n[3] Running BAL legs for each state variant...")
results = {}
for name, csv_path in STATE_CSVS.items():
    print(f"  [Variant {name}] state CSV: {csv_path}")
    try:
        nav_s = run_variant(csv_path, f"BAL_{name}")
        print(f"    final NAV: {nav_s.iloc[-1]/1e9:.3f}B")
        results[name] = nav_s
    except Exception as e:
        print(f"    ERROR: {e}")
        import traceback; traceback.print_exc()

# ─── Summary ─────────────────────────────────────────────────────────────
print("\n"+"="*100)
print("  INTEGRATED BA v11 RESULTS (BAL leg, 25B book, 2014-2026)")
print("="*100)
print(f"\n  {'Variant':<14} {'Final NAV':>10} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'ΔCAGR':>8}")

# Compute baseline (TQ34b)
m_tq = metrics(results["TQ34b"], "TQ34b")
print(f"  {'TQ34b':<14} {m_tq['final']:>9.3f}B {m_tq['cagr']:>+6.2f}% {m_tq['sharpe']:>7.2f} {m_tq['maxdd']:>+6.1f}% {m_tq['calmar']:>7.2f} {'baseline':>8}")

for name, nav_s in results.items():
    if name == "TQ34b": continue
    m = metrics(nav_s, name, baseline=m_tq)
    print(f"  {m['label']:<14} {m['final']:>9.3f}B {m['cagr']:>+6.2f}% {m['sharpe']:>7.2f} {m['maxdd']:>+6.1f}% {m['calmar']:>7.2f} {m['d_cagr']:>+6.2f}pp")

# IS/OOS split
print("\n  By period (IS 2014-2019 / OOS 2020-2026):")
for label, sd, ed in [("IS 14-19","2014-01-01","2019-12-31"), ("OOS 20-26","2020-01-01","2026-05-15")]:
    print(f"\n  [{label}]")
    print(f"  {'Variant':<14} {'CAGR':>8} {'ΔCAGR':>8}")
    tq_sub = results["TQ34b"].loc[sd:ed]
    m_tq_p = metrics(tq_sub, "TQ34b")
    print(f"  {'TQ34b':<14} {m_tq_p['cagr']:>+6.2f}% {'baseline':>8}")
    for name, nav_s in results.items():
        if name == "TQ34b": continue
        sub = nav_s.loc[sd:ed]
        m = metrics(sub, name, baseline=m_tq_p)
        print(f"  {name:<14} {m['cagr']:>+6.2f}% {m['d_cagr']:>+6.2f}pp")

# Save NAV time series
combined = pd.DataFrame({name: nav for name, nav in results.items()})
combined.to_csv(os.path.join(WORKDIR, "data/dt_variants_bav11_nav.csv"))
print(f"\n  Saved NAVs -> data/dt_variants_bav11_nav.csv")
