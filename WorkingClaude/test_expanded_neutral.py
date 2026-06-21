# -*- coding: utf-8 -*-
"""Test expanded NEUTRAL tier set — add more tiers to BA-core for NEUTRAL state.

Current: only MOMENTUM_N (TA≥155 + FA C/D + state=3) fires in NEUTRAL → 18% deployment
Hypothesis: adding MOMENTUM_S_N or NEUTRAL versions of MOMENTUM_S would raise NEUTRAL deployment

Variants tested (BAL+Fin/RE-max-4 50B, 1% deposit realistic):
  E0 baseline (current — MOMENTUM_N only in NEUTRAL)
  E1 + MOMENTUM_S_N (TA≥140 + state=3)
  E2 + relaxed NEUTRAL MOMENTUM_N (TA≥140 instead of 155)
  E3 + MOMENTUM_S_N + DEEP_VALUE_RECOVERY allowed in state=3
  E4 lowest thresholds across NEUTRAL (most aggressive)

Compare against V6 ETF parking 70% (winner from previous test).
"""
import os
import sys
import io

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY

START_DATE = "2014-01-01"
END_DATE = "2026-03-30"

# v10 SQL but with parameterized tier rules — we'll keep SQL fixed and just change tier list
# Memory: SQL determines play_type. To expand NEUTRAL, we change SQL classification.

# Common v10 score formula
SCORE_BODY = """
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
"""

# E0 baseline (= v10 production)
SQL_E0 = SCORE_BODY + """
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
  END AS play_type, ta, liq, sec
FROM classified WHERE liq >= 1e9
"""

# E2: relaxed NEUTRAL MOMENTUM_N threshold (155 → 140) — fires more in NEUTRAL
SQL_E2 = SQL_E0.replace(
    "WHEN ta >= 155 AND state5 = 3 AND fa_tier IN ('C','D') THEN 'MOMENTUM_N'",
    "WHEN ta >= 140 AND state5 = 3 AND fa_tier IN ('C','D') THEN 'MOMENTUM_N'"
)

# E3 (same as E0 SQL; we add MOMENTUM_S_N + DEEP_VALUE_RECOVERY_N to tier set in sim)
# Need to handle DVR-in-NEUTRAL. Add new tier label:
SQL_E3 = SCORE_BODY + """
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
    WHEN fa_tier = 'C' AND ta >= 100 AND state5 = 3 AND ((np_yoy > 0.20) OR (rev_yoy > 0.20)) THEN 'DEEP_VALUE_RECOVERY_N'
    WHEN ta >= 140 AND state5 IN (4,5) THEN 'MOMENTUM_S'
    WHEN ta >= 125 AND state5 IN (4,5) THEN 'MOMENTUM_A'
    WHEN ta >= 140 AND state5 = 3 THEN 'MOMENTUM_S_N'
    WHEN fa_tier IN ('A','B') AND ta >= 70 AND ta < 130 THEN 'COMPOUNDER_HOLD'
    WHEN fa_tier IN ('A','B') THEN 'WAIT'
    ELSE 'PASS'
  END AS play_type, ta, liq, sec
FROM classified WHERE liq >= 1e9
"""

print("=" * 100)
print("  EXPANDED NEUTRAL TIER SET — raise deployment in NEUTRAL state")
print(f"  Period: {START_DATE} → {END_DATE} | Deposit rate = 1.0%/yr (realistic)")
print("=" * 100)

# Load all needed data
print("\nLoading data…")
sig_e0 = bq(SQL_E0.format(start=START_DATE, end=END_DATE))
sig_e0["time"] = pd.to_datetime(sig_e0["time"])
print(f"  E0 signals: {len(sig_e0):,}")

sig_e2 = bq(SQL_E2.format(start=START_DATE, end=END_DATE))
sig_e2["time"] = pd.to_datetime(sig_e2["time"])
print(f"  E2 signals: {len(sig_e2):,}")

sig_e3 = bq(SQL_E3.format(start=START_DATE, end=END_DATE))
sig_e3["time"] = pd.to_datetime(sig_e3["time"])
print(f"  E3 signals: {len(sig_e3):,}")

prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_e0.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_e0.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

vn30_df = bq(f"""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vn30_df["time"] = pd.to_datetime(vn30_df["time"])
vn30_underlying = dict(zip(vn30_df["time"], vn30_df["Close"]))

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
       "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
DEPOSIT = 0.01

# Tier sets
TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
TIER_BAL_E1 = TIER_BAL + ["MOMENTUM_S_N"]
TIER_BAL_E3 = TIER_BAL + ["MOMENTUM_S_N", "DEEP_VALUE_RECOVERY_N"]

variants = [
    # SQL, allowed_tiers, etf_states, label
    (sig_e0, TIER_BAL,    None,       "E0 baseline (1% dep, no ETF)"),
    (sig_e0, TIER_BAL_E1, None,       "E1 + MOMENTUM_S_N"),
    (sig_e2, TIER_BAL,    None,       "E2 relaxed MOMENTUM_N (140 thresh)"),
    (sig_e3, TIER_BAL_E3, None,       "E3 + M_S_N + DVR_N (full expand)"),
    (sig_e0, TIER_BAL,    {3: 0.7},   "E0 + V6 ETF 70% NEUTRAL"),
    (sig_e0, TIER_BAL_E1, {3: 0.7},   "E1 + V6 ETF 70% NEUTRAL ⭐ combo"),
    (sig_e3, TIER_BAL_E3, {3: 0.7},   "E3 + V6 ETF 70% NEUTRAL ⭐ combo"),
]

prices_by_sig = {
    id(sig_e0): prices,
    id(sig_e2): {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_e2.groupby("ticker")},
    id(sig_e3): {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_e3.groupby("ticker")},
}
liq_by_sig = {
    id(sig_e0): liq_map,
    id(sig_e2): {(r["ticker"], r["time"]): r["liq"] for _, r in sig_e2.iterrows()},
    id(sig_e3): {(r["ticker"], r["time"]): r["liq"] for _, r in sig_e3.iterrows()},
}

print(f"\n  Running {len(variants)} variants…\n")
print(f"  {'Variant':<42} {'CAGR':>8} {'Sharpe':>8} {'DD':>8} {'Calmar':>8} {'AvgDep':>8}")
print(f"  {'-'*42} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

results = []
for sig, tiers, etf_states, label in variants:
    p = prices_by_sig[id(sig)]
    lm = liq_by_sig[id(sig)]
    LIQ_use = {**LIQ, "liquidity_lookup": lm}
    nav_df, _ = simulate(sig, p, vni_dates,
        allowed_tiers=tiers, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT,
        state_by_date=state_by_date,
        cash_etf_states=etf_states,
        vn30_underlying=vn30_underlying if etf_states else None,
        **LIQ_use, name=label)
    m = metrics(nav_df, pd.DataFrame(), label)
    avg_dep = nav_df["deployed_pct"].mean()
    results.append({"variant": label, **m, "avg_dep_pct": avg_dep})
    print(f"  {label:<42} {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+8.2f} "
          f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+8.2f} {avg_dep:>+7.1f}%")

df = pd.DataFrame(results)

base = df[df["variant"] == "E0 baseline (1% dep, no ETF)"].iloc[0]
print(f"\n  Δ vs E0 baseline (1% deposit, no ETF, no expanded tiers):")
print(f"  CAGR={base['cagr_pct']:.2f}% Sh={base['sharpe']:.2f} DD={base['max_dd_pct']:.1f}% AvgDep={base['avg_dep_pct']:.1f}%")
for _, r in df.iterrows():
    if r["variant"].startswith("E0 baseline"):
        continue
    print(f"\n  {r['variant']}")
    print(f"    ΔCAGR {r['cagr_pct']-base['cagr_pct']:+.2f}pp, "
          f"ΔSharpe {r['sharpe']-base['sharpe']:+.2f}, "
          f"ΔDD {r['max_dd_pct']-base['max_dd_pct']:+.1f}pp, "
          f"ΔDep {r['avg_dep_pct']-base['avg_dep_pct']:+.1f}pp")

df.to_csv(os.path.join(WORKDIR, "data/expanded_neutral_results.csv"), index=False)
print(f"\n  Saved: expanded_neutral_results.csv")
