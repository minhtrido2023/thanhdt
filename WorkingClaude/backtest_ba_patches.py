#!/usr/bin/env python3
"""
backtest_ba_patches.py
======================
Test 3 BA-system patches motivated by Q1 2026 DVR-trap behavior:

  P1 — Add MOMENTUM_QUALITY to BAL tier set
       BAL currently skips FA A/B momentum picks → falls to DVR (FA C/D)
       in topping markets. P1 closes the gap.

  P2 — Block DVR when MEGA+MOMENTUM tiers are thin (<2 picks on day)
       Treats "regime exhaustion" as defensive signal; prevents
       fallback into late-cycle value traps.

  P3 — VNI overheated filter (VNINDEX/MA200 > 1.30 → skip new BAL buys)
       Pre-emptive de-risk at bull-market extremes.

Tests all 6 variants: BL_v10, P1, P2, P3, P1+P2, P1+P2+P3.
Periods reported: FULL, OOS_2024+, PRE_2024, Y2026Q1, Y2022.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

import simulate_holistic_nav as shn
shn.END_DATE = "2026-05-13"
from simulate_holistic_nav import simulate, bq, VNI_QUERY, START_DATE

END_DATE = shn.END_DATE

# Inline SIGNAL_V10 (avoids importing test_round14_stability which runs full sim at import)
SIGNAL_V10 = """
WITH fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
),
classified AS (
  SELECT t.ticker, t.time, t.Close,
    (CASE WHEN t.D_RSI > 0.50 THEN 25 ELSE 0 END
    + CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200 THEN 25 ELSE 0 END
    + CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3 AND t.Close > t.Close_T1 THEN 20 ELSE 0 END
    + CASE WHEN t.D_MACDdiff > 0 THEN 15 ELSE 0 END
    + CASE WHEN t.Close > t.MA20 THEN 15 ELSE 0 END
    + CASE WHEN t.D_RSI > 0.75 THEN 5 ELSE 0 END
    + CASE WHEN t.D_RSI < 0.30 THEN -10 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE < t.PE_MA5Y - 0.5*t.PE_SD5Y THEN 15 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE > t.PE_MA5Y + 1.0*t.PE_SD5Y THEN -15 ELSE 0 END
    + CASE WHEN t.VNINDEX_RSI_Max3M > 0.65 THEN 10 ELSE 0 END
    + CASE WHEN t.ID_HI_3Y <= 5 THEN 8 ELSE 0 END
    + CASE WHEN t.D_RSI_Max1W > 0.65 THEN 5 ELSE 0 END
    + CASE WHEN t.FSCORE >= 8 THEN 10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P4 * 1.5 AND t.NP_P4 > 0 THEN 8 ELSE 0 END
    + CASE WHEN t.NP_P0 < t.NP_P4 * 0.7 AND t.NP_P4 > 0 THEN -8 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (8,9) THEN 5 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (4,7) THEN -5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 * 1.005 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 < t.MA50_T1 THEN -5 ELSE 0 END
    + CASE WHEN t.HI_3M_T1 > 0 AND t.Close / t.HI_3M_T1 < 0.85 THEN -10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P1 * 1.2 AND t.NP_P1 > 0 THEN 8 ELSE 0 END
    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier="D" THEN 10 ELSE 0 END
    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier="A" THEN -10 ELSE 0 END) AS ta,
    s5.state AS state5, fa.fa_tier,
    SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy, fin.Revenue_YoY_P0 AS rev_yoy,
    (t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0) AS pe_z,
    (t.D_RSI > 0.90 OR (t.MA20 > 0 AND t.Close / t.MA20 > 1.25)) AS warn_ext,
    t.Volume_3M_P50 * t.Close AS liq, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec
  FROM tav2_bq.ticker AS t
  LEFT JOIN tav2_bq.vnindex_5state AS s5 ON s5.time = t.time
  LEFT JOIN fa_dated AS fa ON fa.ticker = t.ticker AND t.time >= fa.f_time
       AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
  LEFT JOIN fin_dated AS fin ON fin.ticker = t.ticker AND t.time >= fin.fin_time
       AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
  WHERE t.time BETWEEN DATE '{start}' AND DATE '{end}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
)
SELECT ticker, time, Close,
  CASE
    WHEN state5 IN (1, 2) THEN 'AVOID_bear'
    WHEN fa_tier = 'E' THEN 'AVOID_faE'
    WHEN ta >= 170 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MEGA'
    WHEN ta >= 170 AND state5 IN (4,5) THEN 'S_PRO'
    WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MOMENTUM'
    WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'
    WHEN ta >= 155 AND state5 = 3 AND fa_tier IN ('C','D') THEN 'MOMENTUM_N'
    WHEN fa_tier IN ('A','B') AND pe_z < -0.5 AND ta >= 95 AND state5 IN (3,4,5) AND NOT warn_ext THEN 'COMPOUNDER_BUY'
    WHEN fa_tier = 'C' AND ta >= 100 AND state5 IN (4,5) AND ((np_yoy > 0.20) OR (rev_yoy > 0.20)) THEN 'DEEP_VALUE_RECOVERY'
    WHEN ta >= 140 AND state5 IN (4,5) THEN 'MOMENTUM_S'
    WHEN ta >= 125 AND state5 IN (4,5) THEN 'MOMENTUM_A'
    WHEN ta >= 140 AND state5 = 3 THEN 'MOMENTUM_S_N'
    WHEN fa_tier IN ('A','B') AND ta >= 70 AND ta < 130 THEN 'COMPOUNDER_HOLD'
    WHEN fa_tier IN ('A','B') THEN 'WAIT'
    ELSE 'PASS'
  END AS play_type,
  ta, liq, sec
FROM classified WHERE liq >= 1e9
"""
TIER_BAL_BL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
TIER_BAL_P1 = TIER_BAL_BL + ["MOMENTUM_QUALITY"]

# ─────────────────────────────────────────────────────────────────────────
# CACHE SIGNALS
# ─────────────────────────────────────────────────────────────────────────
CACHE_FILE = "data/ba_patches_signal_cache.pkl"
if os.path.exists(CACHE_FILE):
    print(f"Loading cached signals from {CACHE_FILE} ...", flush=True)
    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)
    sig = cache["sig"]
    vni = cache["vni"]
    sec_map = cache["sec_map"]
    top30 = cache["top30"]
    print(f"  {len(sig):,} signal rows, {sig['time'].min().date()} → {sig['time'].max().date()}")
else:
    print(f"Window: {START_DATE} → {END_DATE}")
    print("Loading signals from BQ ...", flush=True)
    sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} signal rows", flush=True)

    vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
    vni["time"] = pd.to_datetime(vni["time"])

    sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
        FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
        AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
        """).set_index("ticker")["s"].to_dict()

    top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
        WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
        AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
        GROUP BY t.ticker
        ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

    with open(CACHE_FILE, "wb") as f:
        pickle.dump({"sig":sig, "vni":vni, "sec_map":sec_map, "top30":top30}, f)
    print(f"  Cached → {CACHE_FILE}")

# ─────────────────────────────────────────────────────────────────────────
# COMPUTE VNI / MA200 for P3
# ─────────────────────────────────────────────────────────────────────────
print("Computing VNI/MA200 for P3 ...", flush=True)
vni_sorted = vni.sort_values("time").reset_index(drop=True)
vni_sorted["MA200"] = vni_sorted["Close"].rolling(200, min_periods=200).mean()
vni_sorted["vni_ma200_ratio"] = vni_sorted["Close"] / vni_sorted["MA200"]
overheated_dates = set(vni_sorted[vni_sorted["vni_ma200_ratio"] > 1.30]["time"])
print(f"  Overheated days (VNI/MA200 > 1.30): {len(overheated_dates)}")

# Build derived sig fields once
# Primary momentum tiers (NOT including MOMENTUM_QUALITY — that's a separate axis;
# DVR fallback only happens when these PRIMARY tiers are dry)
sig["primary_mom"] = sig["play_type"].isin(["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","S_PRO"])
day_primary_mom = sig[sig["primary_mom"]].groupby("time")["ticker"].nunique().to_dict()
# P2 threshold: if < 2 primary-momentum picks on a day, block DVR that day
print(f"  Days with <2 primary-momentum picks (P2 will block DVR): "
      f"{sum(1 for d in day_primary_mom.values() if d < 2) + (len(sig['time'].unique()) - len(day_primary_mom))}")

vni_dates = sorted(vni["time"].unique())
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

LIQ_FULL = {"liquidity_volume_pct":0.20, "max_fill_days":5,
            "liquidity_lookup":liq_map, "exit_slippage_tiered":True}

# ─────────────────────────────────────────────────────────────────────────
# PATCH TRANSFORMS
# ─────────────────────────────────────────────────────────────────────────
def apply_patch(sig, patches):
    """Return sig copy with play_type rewritten per patches enabled."""
    s = sig.copy()
    if "P2" in patches:
        # Days where ZERO primary-momentum picks exist
        all_days = set(s["time"].unique())
        days_with_primary = {d for d, n in day_primary_mom.items() if n >= 2}
        thin_days = all_days - days_with_primary
        # block DVR on those days
        mask = (s["play_type"] == "DEEP_VALUE_RECOVERY") & (s["time"].isin(thin_days))
        s.loc[mask, "play_type"] = "AVOID_thinregime"
    if "P3" in patches:
        # block ALL bull buys on overheated days (sim only buys on date d, so this prevents new entries that day)
        # We keep existing positions untouched — just mark new picks AVOID
        mask = s["time"].isin(overheated_dates) & (s["play_type"].isin(
            ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","DEEP_VALUE_RECOVERY","S_PRO","S","MOMENTUM_A"]))
        s.loc[mask, "play_type"] = "AVOID_overheated"
    return s

# ─────────────────────────────────────────────────────────────────────────
# RUN VARIANT
# ─────────────────────────────────────────────────────────────────────────
def run_variant(label, patches):
    print(f"\n{'='*70}\n  {label}: patches={patches}\n{'='*70}", flush=True)
    s = apply_patch(sig, patches)
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in s.groupby("ticker")}

    tier_bal = TIER_BAL_P1 if "P1" in patches else TIER_BAL_BL

    print(f"  Tier set (BAL): {tier_bal}", flush=True)
    # BAL
    nav_bal, _ = simulate(s, prices, vni_dates,
        allowed_tiers=tier_bal, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    # VN30 (use same patches for P3 only; P1/P2 logical to apply too but VN30 small universe)
    sig_vn30 = s[s["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=tier_bal, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_V)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    nav_bal_s = nav_bal.set_index("time")["nav"] / 50e9
    nav_vn30_s = nav_vn30.set_index("time")["nav"] / 50e9
    common = nav_bal_s.index.intersection(nav_vn30_s.index)
    ba_nav = 0.5 * nav_bal_s.loc[common] + 0.5 * nav_vn30_s.loc[common]
    ba_nav.name = label
    return ba_nav

def win_metrics(nav, start, end, label):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    rets = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    spy = len(rets)/yrs if yrs > 0 else 252
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs) - 1 if yrs > 0 else 0
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std() > 0 else 0
    dd = (s - s.cummax())/s.cummax()
    mdd = dd.min()
    return {"label":label,"CAGR":cagr,"Sharpe":sh,"MaxDD":mdd,"Calmar":cagr/abs(mdd) if mdd<0 else 0,
            "n":len(s),"wealth":s.iloc[-1]/s.iloc[0]}

# ─────────────────────────────────────────────────────────────────────────
# RUN ALL VARIANTS
# ─────────────────────────────────────────────────────────────────────────
VARIANTS = [
    ("BL_v10",       set()),
    ("P1",           {"P1"}),
    ("P2",           {"P2"}),
    ("P3",           {"P3"}),
    ("P1+P2",        {"P1","P2"}),
    ("P1+P2+P3",     {"P1","P2","P3"}),
]

results = {}
for label, patches in VARIANTS:
    results[label] = run_variant(label, patches)

# ─────────────────────────────────────────────────────────────────────────
# REPORT
# ─────────────────────────────────────────────────────────────────────────
periods = [
    ("FULL", pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("PRE_2024", pd.Timestamp("2014-04-01"), pd.Timestamp("2023-12-31")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2022_crash", pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026", pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]

print("\n\n" + "="*120)
print("BA PATCH BACKTEST RESULTS — full 12-yr canonical sim (50B BAL+VN30, slip 0.1%, liq cap 20% ADV)")
print("="*120)

all_rows = []
for period_name, p_start, p_end in periods:
    print(f"\n─── {period_name} ({p_start.date()} → {p_end.date()}) ───")
    print(f"  {'Variant':<14}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}{'wealth':>10}")
    for label, _ in VARIANTS:
        m = win_metrics(results[label], p_start, p_end, label)
        if m is None: continue
        all_rows.append({"period":period_name, **m})
        print(f"  {label:<14}{m['CAGR']:>+10.2%}{m['Sharpe']:>+10.2f}{m['MaxDD']:>+10.2%}{m['Calmar']:>+10.2f}{m['wealth']:>+10.2f}")

# Save
pd.DataFrame(all_rows).to_csv("data/ba_patches_results.csv", index=False)
nav_df = pd.DataFrame({k: v for k, v in results.items()})
nav_df.to_csv("data/ba_patches_nav.csv")
print("\nSaved: ba_patches_results.csv, ba_patches_nav.csv")
