# -*- coding: utf-8 -*-
"""Round 16 — Tier-based position sizing × EX-BULL threshold tightening.

Two structural improvements untried in rounds 1-15:

  (1) Tier-based position sizing — current is equal-weight 10% per slot.
      Concentrate capital in higher-conviction tiers (MEGA P3M=37%) over
      lower (MOMENTUM_S P3M=12.9%).

  (2) EX-BULL threshold tightening — in state=5 (extreme bull), require
      higher score for entry (filter late-cycle blow-off chasing).

Test strategy: BAL+Fin/RE-max-4 at 50B (single-book sim, 100% capital).
Note: in production, this single-book result × 0.5 ≈ contribution to BA-system.

Variants:
  A1 baseline (equal-weight, v10 SQL)
  A2 tier-mild        (MEGA 13%, MOMENTUM 12%, MOMENTUM_N 11%, MOMENTUM_S 9%, DVR 8%)
  A3 tier-aggressive  (MEGA 16%, MOMENTUM 14%, MOMENTUM_N 12%, MOMENTUM_S 7%, DVR 6%)
  A4 tier-defensive   (MEGA 12%, MOMENTUM 11%, MOMENTUM_N 11%, MOMENTUM_S 9%, DVR 9%)
  B1 baseline (equal-weight, v11 EX-BULL+15 SQL)
  B2 = A2 + v11
  B3 = A3 + v11

Compare to BA-system 50B baseline (CAGR 17.97%, Sh 1.12, DD -20.4% as single-book BAL_Fin4).
"""
import os
import sys
import io

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE, END_DATE

# v10 baseline SQL (current production)
from test_round14_stability import SIGNAL_V10

# v11 SQL: same as v10 but EX-BULL state=5 entries require +15 higher score
SIGNAL_V11 = """
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
    -- EX-BULL (state=5) +15 threshold tightening
    WHEN ta >= 185 AND state5 = 5 AND fa_tier IN ('C','D') THEN 'MEGA'
    WHEN ta >= 185 AND state5 = 5 THEN 'S_PRO'
    WHEN ta >= 170 AND state5 = 5 AND fa_tier IN ('C','D') THEN 'MOMENTUM'
    WHEN ta >= 170 AND state5 = 5 AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'
    -- BULL (state=4) standard thresholds
    WHEN ta >= 170 AND state5 = 4 AND fa_tier IN ('C','D') THEN 'MEGA'
    WHEN ta >= 170 AND state5 = 4 THEN 'S_PRO'
    WHEN ta >= 155 AND state5 = 4 AND fa_tier IN ('C','D') THEN 'MOMENTUM'
    WHEN ta >= 155 AND state5 = 4 AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'
    -- NEUTRAL state=3 standard
    WHEN ta >= 155 AND state5 = 3 AND fa_tier IN ('C','D') THEN 'MOMENTUM_N'
    WHEN fa_tier IN ('A','B') AND pe_z < -0.5 AND ta >= 95 AND state5 IN (3,4,5) AND NOT warn_ext THEN 'COMPOUNDER_BUY'
    WHEN fa_tier = 'C' AND ta >= 100 AND state5 IN (4,5) AND ((np_yoy > 0.20) OR (rev_yoy > 0.20)) THEN 'DEEP_VALUE_RECOVERY'
    -- MOMENTUM_S threshold +15 in EX-BULL (state=5)
    WHEN ta >= 155 AND state5 = 5 THEN 'MOMENTUM_S'
    WHEN ta >= 140 AND state5 = 4 THEN 'MOMENTUM_S'
    -- MOMENTUM_A threshold +15 in EX-BULL
    WHEN ta >= 140 AND state5 = 5 THEN 'MOMENTUM_A'
    WHEN ta >= 125 AND state5 = 4 THEN 'MOMENTUM_A'
    WHEN ta >= 140 AND state5 = 3 THEN 'MOMENTUM_S_N'
    WHEN fa_tier IN ('A','B') AND ta >= 70 AND ta < 130 THEN 'COMPOUNDER_HOLD'
    WHEN fa_tier IN ('A','B') THEN 'WAIT'
    ELSE 'PASS'
  END AS play_type,
  ta, liq, sec
FROM classified WHERE liq >= 1e9
"""

# ─── Load data once ──────────────────────────────────────────────────────────
print("=" * 100)
print("  ROUND 16 — Tier-sized positions × EX-BULL threshold tightening")
print("=" * 100)

print("\nLoading v10 signals (full 2014-2026)…")
sig_v10 = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig_v10["time"] = pd.to_datetime(sig_v10["time"])
print(f"  v10: {len(sig_v10):,} rows")

print("Loading v11 signals (EX-BULL+15)…")
sig_v11 = bq(SIGNAL_V11.format(start=START_DATE, end=END_DATE))
sig_v11["time"] = pd.to_datetime(sig_v11["time"])
print(f"  v11: {len(sig_v11):,} rows")

# State 5 tier shift summary
v10_s5 = sig_v10[(sig_v10["sec"].notna())].copy()
v11_s5 = sig_v11.copy()

# Common loads
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_v10.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_v10.iterrows()}
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
       "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# Tier weight variants (sum doesn't need to = 100% — slots fill independently)
TIER_VARIANTS = {
    "equal-weight":     None,  # baseline (1/max_positions = 10%)
    "tier-mild":        {"MEGA": 0.13, "MOMENTUM": 0.12, "MOMENTUM_N": 0.11,
                         "MOMENTUM_S": 0.09, "DEEP_VALUE_RECOVERY": 0.08},
    "tier-aggressive":  {"MEGA": 0.16, "MOMENTUM": 0.14, "MOMENTUM_N": 0.12,
                         "MOMENTUM_S": 0.07, "DEEP_VALUE_RECOVERY": 0.06},
    "tier-defensive":   {"MEGA": 0.12, "MOMENTUM": 0.11, "MOMENTUM_N": 0.11,
                         "MOMENTUM_S": 0.09, "DEEP_VALUE_RECOVERY": 0.09},
}


def run_one(label, signal_df, tier_w):
    nav_df, trades_df = simulate(
        signal_df, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        tier_weights=tier_w,
        **LIQ, name=label)
    m = metrics(nav_df, trades_df, label)
    # Tier exposure breakdown
    if len(trades_df):
        tier_dist = trades_df["play_type"].value_counts(normalize=True).to_dict()
    else:
        tier_dist = {}
    # Avg position-size weighted return per tier
    avg_ret_by_tier = {}
    for t in TIER_BAL:
        sub = trades_df[trades_df["play_type"] == t]
        if len(sub):
            avg_ret_by_tier[t] = sub["ret_net"].mean() * 100
    return m, tier_dist, avg_ret_by_tier, len(trades_df)


# ─── Run grid ────────────────────────────────────────────────────────────────
results = []
configs = []

# v10 (baseline SQL) × all 4 tier variants
for tw_label, tw in TIER_VARIANTS.items():
    label = f"v10 / {tw_label}"
    configs.append(("v10", tw_label, sig_v10, tw, label))

# v11 (EX-BULL+15 SQL) × top 3 tier variants (skip defensive — least promising)
for tw_label in ["equal-weight", "tier-mild", "tier-aggressive"]:
    tw = TIER_VARIANTS[tw_label]
    label = f"v11 / {tw_label}"
    configs.append(("v11", tw_label, sig_v11, tw, label))

print(f"\n  Running {len(configs)} variants…")
print()
print(f"  {'Variant':<30} {'CAGR':>8} {'Sharpe':>8} {'MaxDD':>8} {'Calmar':>8} {'trades':>8}")
print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

tier_dist_all = {}
ret_by_tier_all = {}

for sql_v, tw_label, sig, tw, label in configs:
    m, tdist, ret_t, ntr = run_one(label, sig, tw)
    results.append({"sql": sql_v, "tier_var": tw_label,
                    "cagr_pct": m["cagr_pct"], "sharpe": m["sharpe"],
                    "max_dd_pct": m["max_dd_pct"], "calmar": m["calmar"],
                    "n_trades": m["n_trades"]})
    tier_dist_all[label] = tdist
    ret_by_tier_all[label] = ret_t
    print(f"  {label:<30} {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+8.2f} "
          f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+8.2f} {m['n_trades']:>8d}")

df = pd.DataFrame(results)

# ─── Pretty matrix: SQL × tier_var ───────────────────────────────────────────
print(f"\n{'=' * 100}")
print(f"  MATRICES: SQL_version × tier_variant")
print(f"{'=' * 100}")

for metric, label in [("cagr_pct", "CAGR (%)"),
                       ("sharpe", "Sharpe"),
                       ("max_dd_pct", "MaxDD (%)"),
                       ("calmar", "Calmar")]:
    print(f"\n  {label}:")
    pivot = df.pivot(index="sql", columns="tier_var", values=metric)
    print(pivot.round(2).to_string())

# ─── Tier distribution & per-tier returns ────────────────────────────────────
print(f"\n{'=' * 100}")
print(f"  TIER DISTRIBUTION (% of trades) — v10 baseline vs v10 tier-aggressive")
print(f"{'=' * 100}")
print(f"\n  {'Tier':<22} {'v10 baseline':>15} {'v10 tier-agg':>15} {'v11 baseline':>15}")
for t in TIER_BAL:
    a = tier_dist_all.get("v10 / equal-weight", {}).get(t, 0) * 100
    b = tier_dist_all.get("v10 / tier-aggressive", {}).get(t, 0) * 100
    c = tier_dist_all.get("v11 / equal-weight", {}).get(t, 0) * 100
    print(f"  {t:<22} {a:>+13.1f}% {b:>+13.1f}% {c:>+13.1f}%")

print(f"\n  AVG NET RETURN per tier (v10 baseline):")
for t, r in ret_by_tier_all.get("v10 / equal-weight", {}).items():
    print(f"    {t:<22} {r:>+6.2f}%")

# ─── Save ────────────────────────────────────────────────────────────────────
out_path = os.path.join(WORKDIR, "data/round16_results.csv")
df.to_csv(out_path, index=False)
print(f"\n  Saved: {out_path}")

# ─── Δ vs baseline ───────────────────────────────────────────────────────────
base = df[(df["sql"] == "v10") & (df["tier_var"] == "equal-weight")].iloc[0]
print(f"\n{'=' * 100}")
print(f"  Δ vs v10/equal-weight baseline (CAGR={base['cagr_pct']:.2f}% Sh={base['sharpe']:.2f} "
      f"DD={base['max_dd_pct']:.1f}% Cal={base['calmar']:.2f})")
print(f"{'=' * 100}")
print(f"\n  {'Variant':<30} {'ΔCAGR':>10} {'ΔSharpe':>10} {'ΔDD':>10} {'ΔCalmar':>10}")
for _, r in df.iterrows():
    label = f"{r['sql']} / {r['tier_var']}"
    if label == "v10 / equal-weight":
        continue
    print(f"  {label:<30} {r['cagr_pct']-base['cagr_pct']:>+9.2f}pp "
          f"{r['sharpe']-base['sharpe']:>+9.2f} "
          f"{r['max_dd_pct']-base['max_dd_pct']:>+9.1f}pp "
          f"{r['calmar']-base['calmar']:>+9.2f}")
