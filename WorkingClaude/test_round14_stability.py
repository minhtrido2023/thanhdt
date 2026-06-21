"""Round 14 stability tests — sector evolution + day/month patterns + PM variants."""
import os, sys, numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE, END_DATE

# v10 SQL (same as round 12/13)
# Note: ticker.VNINDEX_RSI_Max3M no longer exists in schema; computed from VNINDEX D_RSI rolling MAX
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
-- Compute VNINDEX_RSI_Max3M from raw VNI D_RSI rolling MAX over 60 sessions
vni_history AS (
  SELECT t.time, t.D_RSI
  FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
),
vni_max3m AS (
  SELECT time,
    MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m
  FROM vni_history
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
    + CASE WHEN vmax.rsi_max3m > 0.65 THEN 10 ELSE 0 END
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
  LEFT JOIN vni_max3m AS vmax ON vmax.time = t.time
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

print("Loading data + signals...")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
LIQ = {"liquidity_volume_pct":0.20, "max_fill_days":5, "liquidity_lookup":liq_map,
       "exit_slippage_tiered":True}

# Run BAL_Fin4(v10) at 50B with default BL20 → reference trade log
print("\nRunning BAL_Fin4(v10) at 50B (reference) ...")
nav_ref, trades_ref = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **LIQ)
trades_ref["entry_date"] = pd.to_datetime(trades_ref["entry_date"])
trades_ref["exit_date"] = pd.to_datetime(trades_ref["exit_date"])
trades_ref["sector_top"] = trades_ref["ticker"].map(sec_map).fillna(-1).astype(int)
trades_ref["yr"] = trades_ref["entry_date"].dt.year

# ── A) Sector evolution year-by-year ──────────────────────────────────
print("\n" + "=" * 95)
print("  PART A — SECTOR EVOLUTION YEAR-BY-YEAR (BAL_Fin4 50B)")
print("=" * 95)
sec_names = {0:"Misc/Oil", 1:"Materials", 2:"Industrials", 3:"ConsGoods",
             4:"Health", 5:"ConsServ", 7:"Utilities", 8:"Fin/RE", 9:"Tech/Tel"}

print(f"\n  {'Year':>6}{'n':>6}", end="")
for sec in sorted(sec_names.keys()):
    print(f"{sec_names[sec][:8]:>10}", end="")
print()
print("  " + "-" * 100)
for yr in sorted(trades_ref["yr"].unique()):
    sub = trades_ref[trades_ref["yr"] == yr]
    n_total = len(sub)
    print(f"  {yr:>6}{n_total:>6}", end="")
    for sec in sorted(sec_names.keys()):
        n_sec = (sub["sector_top"] == sec).sum()
        pct = n_sec / n_total * 100 if n_total else 0
        print(f"   {n_sec:>3}({pct:>3.0f}%)", end="")
    print()

# Per-sector avg returns by year
print("\n  Per-sector AVG NET RETURN per year (in S145+ pool):")
print(f"  {'Year':>6}", end="")
for sec in sorted(sec_names.keys()):
    print(f"{sec_names[sec][:8]:>10}", end="")
print()
for yr in sorted(trades_ref["yr"].unique()):
    sub = trades_ref[trades_ref["yr"] == yr]
    print(f"  {yr:>6}", end="")
    for sec in sorted(sec_names.keys()):
        s_sub = sub[sub["sector_top"] == sec]
        if len(s_sub) >= 2:
            avg = s_sub["ret_net"].mean() * 100
            print(f"  {avg:>+7.1f}%", end="")
        else:
            print("       n/a", end="")
    print()

# ── B) Day-of-week + month patterns ──────────────────────────────────
print("\n" + "=" * 95)
print("  PART B — DAY-OF-WEEK + MONTH PATTERNS")
print("=" * 95)
trades_ref["entry_dow"] = trades_ref["entry_date"].dt.day_name()
trades_ref["entry_month"] = trades_ref["entry_date"].dt.month
trades_ref["entry_qtr"] = trades_ref["entry_date"].dt.quarter

print("\n  Returns by entry day-of-week:")
dow_stats = trades_ref.groupby("entry_dow").agg(
    n=("ret_net", "count"),
    avg_ret=("ret_net", lambda x: x.mean()*100),
    median_ret=("ret_net", lambda x: x.median()*100),
    win=("ret_net", lambda x: (x > 0).mean()*100),
).reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
print(dow_stats.round(2).to_string())

print("\n  Returns by entry month:")
month_stats = trades_ref.groupby("entry_month").agg(
    n=("ret_net", "count"),
    avg_ret=("ret_net", lambda x: x.mean()*100),
    median_ret=("ret_net", lambda x: x.median()*100),
    win=("ret_net", lambda x: (x > 0).mean()*100),
)
print(month_stats.round(2).to_string())

print("\n  Returns by entry quarter:")
qtr_stats = trades_ref.groupby("entry_qtr").agg(
    n=("ret_net", "count"),
    avg_ret=("ret_net", lambda x: x.mean()*100),
    win=("ret_net", lambda x: (x > 0).mean()*100),
)
print(qtr_stats.round(2).to_string())

# ── C) Position management variants on ULTIMATE 50/50 ──────────────
print("\n" + "=" * 95)
print("  PART C — POSITION MANAGEMENT VARIANTS (BAL_Fin4 50B)")
print("=" * 95)

PM_TESTS = [
    ("baseline (BL20)", {}),
    ("BL10", {"reentry_blacklist_days": 10}),
    ("BL30", {"reentry_blacklist_days": 30}),
    ("BL40", {"reentry_blacklist_days": 40}),
    ("BL20+trail_tight", {"trailing_stop_activate":0.10, "trailing_stop_pct":0.06}),
    ("BL20+trail_loose", {"trailing_stop_activate":0.15, "trailing_stop_pct":0.10}),
    ("BL20+sec_lim_2_global", {"sector_limit": 2, "ticker_sector_map": sec_map}),
    ("BL20+sec_lim_3_global", {"sector_limit": 3, "ticker_sector_map": sec_map}),
    ("hold_30d", {"hold_days_override": 30}),
    ("hold_60d", {"hold_days_override": 60}),
    ("hold_90d", {"hold_days_override": 90}),
    ("stop_-15%", {"stop_loss_override": -0.15}),
    ("stop_-25%", {"stop_loss_override": -0.25}),
]

print(f"\n  {'PM Variant':30} | {'CAGR':>7} {'Sh':>6} {'DD':>7} {'Cal':>5} {'trades':>7}")
pm_results = []
for name, params in PM_TESTS:
    base_args = dict(allowed_tiers=TIER_BAL, max_positions=10, hold_days=45,
                     stop_loss=-0.20, min_hold=2, slippage=0.001, init_nav=50e9,
                     sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **LIQ)
    if "hold_days_override" in params:
        base_args["hold_days"] = params.pop("hold_days_override")
    if "stop_loss_override" in params:
        base_args["stop_loss"] = params.pop("stop_loss_override")
    base_args.update(params)
    nav_df, _ = simulate(sig, prices, vni_dates, **base_args)
    m = metrics(nav_df, pd.DataFrame(), name)
    pm_results.append({"variant": name, **m})
    print(f"  {name:30} | {m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
          f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f} "
          f"{m['n_trades']:>7d}")

trades_ref.to_csv(os.path.join(WORKDIR, "round14_trades.csv"), index=False)
pd.DataFrame(pm_results).to_csv(os.path.join(WORKDIR, "round14_pm.csv"), index=False)
print("\n  Saved: round14_*.csv")
