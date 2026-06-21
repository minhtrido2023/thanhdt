# -*- coding: utf-8 -*-
"""Stop-loss validation across multiple periods/regimes.

User concern (round 14/15): stop -25% gave +0.33pp CAGR on full 2014-2026 history,
but is that robust? Test stops [-15, -18, -20, -22, -25, -28, -30] across:
  - Full period 2014-2026
  - Sub-periods: 2014-2017 (calibration), 2018-2020 (chop+COVID),
    2021-2023 (mega bull + 2022 crash), 2024-2026 (recent bull)
  - Walk-forward: IS 2014-2019, OOS 2020-2026

Production base config: BAL+Fin/RE-max-4 (v10) at 50B, hold 45d, BL20.
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

# ─── Load data once ─────────────────────────────────────────────────
print("Loading v10 signals (full 2014-2026) ...")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows")
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates_full = sorted(vni["time"].unique())
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
       "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# ─── Periods ────────────────────────────────────────────────────────
PERIODS = [
    ("Full 2014-2026",      "2014-01-01", "2026-01-16"),
    ("2014-2017 (calib)",   "2014-01-01", "2017-12-31"),
    ("2018-2020 (chop+COVID)","2018-01-01", "2020-12-31"),
    ("2021-2023 (bull+crash)","2021-01-01", "2023-12-31"),
    ("2024-2026 (recent)",  "2024-01-01", "2026-01-16"),
    ("IS 2014-2019",        "2014-01-01", "2019-12-31"),
    ("OOS 2020-2026",       "2020-01-01", "2026-01-16"),
]

STOPS = [-0.15, -0.18, -0.20, -0.22, -0.25, -0.28, -0.30]


def run_one(period_name, start, end, stop):
    """Run one (period × stop) variant and return key metrics."""
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    vni_dates = [d for d in vni_dates_full if start_ts <= d <= end_ts]
    sig_period = sig[(sig["time"] >= start_ts) & (sig["time"] <= end_ts)].copy()

    nav_df, trades_df = simulate(
        sig_period, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45,
        stop_loss=stop, min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ,
        name=f"{period_name}_stop{int(stop*100)}",
    )
    m = metrics(nav_df, trades_df, f"{period_name}_stop{int(stop*100)}")

    # Stop-hit stats
    n_stops = (trades_df["reason"] == "STOP").sum() if len(trades_df) else 0
    n_total = len(trades_df)
    stop_pct = n_stops / n_total * 100 if n_total else 0
    avg_stop_ret = (trades_df[trades_df["reason"] == "STOP"]["ret_net"].mean() * 100
                    if n_stops else np.nan)

    return {
        "period": period_name,
        "stop_pct": int(stop * 100),
        "cagr_pct": m["cagr_pct"],
        "sharpe": m["sharpe"],
        "max_dd_pct": m["max_dd_pct"],
        "calmar": m["calmar"],
        "n_trades": n_total,
        "n_stops": n_stops,
        "stop_hit_pct": stop_pct,
        "avg_stop_ret_pct": avg_stop_ret,
    }


# ─── Run grid ───────────────────────────────────────────────────────
print(f"\n{'=' * 110}")
print(f"  STOP-LOSS VALIDATION — {len(PERIODS)} periods × {len(STOPS)} stops = {len(PERIODS)*len(STOPS)} variants")
print(f"{'=' * 110}")

results = []
for pname, start, end in PERIODS:
    print(f"\n  Running period: {pname}  [{start} → {end}]")
    for stop in STOPS:
        r = run_one(pname, start, end, stop)
        results.append(r)
        print(f"    stop={int(stop*100):>3}%  CAGR={r['cagr_pct']:>6.2f}%  "
              f"Sh={r['sharpe']:>5.2f}  DD={r['max_dd_pct']:>+6.1f}%  "
              f"Cal={r['calmar']:>4.2f}  trades={r['n_trades']:>3}  "
              f"stops={r['n_stops']:>2}({r['stop_hit_pct']:>4.1f}%)")

# ─── Pretty matrix ──────────────────────────────────────────────────
df = pd.DataFrame(results)

print(f"\n{'=' * 110}")
print(f"  MATRIX: CAGR by (period × stop)")
print(f"{'=' * 110}")
pivot_cagr = df.pivot(index="period", columns="stop_pct", values="cagr_pct")
# preserve PERIODS order
pivot_cagr = pivot_cagr.reindex([p[0] for p in PERIODS])
print(pivot_cagr.round(2).to_string())

print(f"\n  MATRIX: Sharpe by (period × stop)")
pivot_sh = df.pivot(index="period", columns="stop_pct", values="sharpe")
pivot_sh = pivot_sh.reindex([p[0] for p in PERIODS])
print(pivot_sh.round(2).to_string())

print(f"\n  MATRIX: MaxDD by (period × stop)")
pivot_dd = df.pivot(index="period", columns="stop_pct", values="max_dd_pct")
pivot_dd = pivot_dd.reindex([p[0] for p in PERIODS])
print(pivot_dd.round(1).to_string())

print(f"\n  MATRIX: Calmar by (period × stop)")
pivot_cal = df.pivot(index="period", columns="stop_pct", values="calmar")
pivot_cal = pivot_cal.reindex([p[0] for p in PERIODS])
print(pivot_cal.round(2).to_string())

# ─── Best stop per period ───────────────────────────────────────────
print(f"\n{'=' * 110}")
print(f"  BEST STOP PER PERIOD (by metric)")
print(f"{'=' * 110}")
print(f"\n  {'Period':<28}  {'best CAGR':>15}  {'best Sharpe':>15}  {'best Calmar':>15}  {'best DD':>15}")
for pname, _, _ in PERIODS:
    sub = df[df["period"] == pname]
    if sub.empty:
        continue
    bc = sub.loc[sub["cagr_pct"].idxmax()]
    bs = sub.loc[sub["sharpe"].idxmax()]
    bcal = sub.loc[sub["calmar"].idxmax()]
    bd = sub.loc[sub["max_dd_pct"].idxmax()]  # least negative
    print(f"  {pname:<28}  {int(bc['stop_pct']):>3}% ({bc['cagr_pct']:>5.2f}%)  "
          f"{int(bs['stop_pct']):>3}% ({bs['sharpe']:>5.2f})   "
          f"{int(bcal['stop_pct']):>3}% ({bcal['calmar']:>5.2f})   "
          f"{int(bd['stop_pct']):>3}% ({bd['max_dd_pct']:>+5.1f}%)")

# ─── Stop -25% vs -20% delta per period ─────────────────────────────
print(f"\n{'=' * 110}")
print(f"  Δ STOP -25% vs -20% (production baseline) — per period")
print(f"{'=' * 110}")
print(f"\n  {'Period':<28}  {'ΔCAGR':>10}  {'ΔSharpe':>10}  {'ΔDD':>10}  {'ΔCalmar':>10}  {'-20% DD':>10}  {'-25% DD':>10}")
for pname, _, _ in PERIODS:
    s20 = df[(df["period"] == pname) & (df["stop_pct"] == -20)]
    s25 = df[(df["period"] == pname) & (df["stop_pct"] == -25)]
    if s20.empty or s25.empty:
        continue
    s20 = s20.iloc[0]
    s25 = s25.iloc[0]
    print(f"  {pname:<28}  {s25['cagr_pct'] - s20['cagr_pct']:>+9.2f}pp  "
          f"{s25['sharpe'] - s20['sharpe']:>+9.2f}  "
          f"{s25['max_dd_pct'] - s20['max_dd_pct']:>+9.1f}pp  "
          f"{s25['calmar'] - s20['calmar']:>+9.2f}  "
          f"{s20['max_dd_pct']:>+9.1f}%  {s25['max_dd_pct']:>+9.1f}%")

# ─── Save ───────────────────────────────────────────────────────────
out_path = os.path.join(WORKDIR, "data/stop_validation_results.csv")
df.to_csv(out_path, index=False)
print(f"\n  Saved: {out_path}")
