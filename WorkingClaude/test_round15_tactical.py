"""Round 15 — Tactical refinements + Forward holdout + F-system mix + Stress test."""
import os, sys, numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE, END_DATE

# v10 SQL
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

print("Loading data...")
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


# ── PART A: Tactical refinements ──────────────────────────────────────
print("\n" + "=" * 95)
print("  PART A — TACTICAL REFINEMENTS (BAL_Fin4 50B)")
print("=" * 95)

# Filter signals: skip July months
sig_no_july = sig[sig["time"].dt.month != 7].copy()
print(f"  Signals: full={len(sig):,}, no-July={len(sig_no_july):,} (-{len(sig)-len(sig_no_july):,})")

# Filter: only Tue-Thu entries
sig_tue_thu = sig[sig["time"].dt.dayofweek.isin([1, 2, 3])].copy()
print(f"  Signals: Tue-Thu only={len(sig_tue_thu):,}")

# Combined: Tue-Thu + no-July
sig_combo = sig[sig["time"].dt.dayofweek.isin([1,2,3]) & (sig["time"].dt.month != 7)].copy()
print(f"  Signals: Tue-Thu + no-July={len(sig_combo):,}")

VARIANTS_A = [
    ("baseline (BL20 stop -20%)", sig, {}),
    ("stop -25%", sig, {"stop_loss":-0.25}),
    ("skip July", sig_no_july, {}),
    ("Tue-Thu only", sig_tue_thu, {}),
    ("skip July + stop -25%", sig_no_july, {"stop_loss":-0.25}),
    ("Tue-Thu + skip July", sig_combo, {}),
    ("Tue-Thu + skip July + stop -25%", sig_combo, {"stop_loss":-0.25}),
]

print(f"\n  {'Variant':40} | {'CAGR':>7} {'Sh':>6} {'DD':>7} {'Cal':>5} {'trades':>7}")
results_a = []
for name, sig_d, extra in VARIANTS_A:
    prc_d = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_d.groupby("ticker")}
    liq_d = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_d.iterrows()}
    LIQ_d = {**LIQ, "liquidity_lookup": liq_d}
    base = dict(allowed_tiers=TIER_BAL, max_positions=10, hold_days=45,
                stop_loss=-0.20, min_hold=2, slippage=0.001, init_nav=50e9,
                sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **LIQ_d)
    base.update(extra)
    nav_df, _ = simulate(sig_d, prc_d, vni_dates, **base)
    m = metrics(nav_df, pd.DataFrame(), name)
    results_a.append({"variant": name, **m})
    print(f"  {name:40} | {m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
          f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f} {m['n_trades']:>7d}")


# ── PART B: Forward holdout test (Jan 2024 - Jan 2026) ────────────────
print("\n" + "=" * 95)
print("  PART B — FORWARD HOLDOUT (Jan 2024 - Jan 2026, 24 months)")
print("=" * 95)
print("  Trains on 2014-2023, holds out 2024-2026 as forward test")

# Sim only on holdout period
holdout_dates = [d for d in vni_dates if pd.Timestamp("2024-01-01") <= d <= pd.Timestamp("2026-01-16")]
print(f"\n  Holdout: {len(holdout_dates)} days, {holdout_dates[0].date()} → {holdout_dates[-1].date()}")

print(f"\n  {'Strat':40} | {'CAGR':>7} {'Sh':>6} {'DD':>7} {'Cal':>5}")
holdout_results = []
for name, tiers, mp, h, sl, base_extra in [
    ("BAL_Fin4 50B baseline", TIER_BAL, 10, 45, -0.20, {"sector_limit_per_sector":{8:4}, "ticker_sector_map":sec_map}),
    ("BAL_Fin4 50B + tactical", TIER_BAL, 10, 45, -0.25, {"sector_limit_per_sector":{8:4}, "ticker_sector_map":sec_map}),
]:
    nav_df, _ = simulate(sig, prices, holdout_dates,
        allowed_tiers=tiers, max_positions=mp, hold_days=h, stop_loss=sl,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ, **base_extra)
    m = metrics(nav_df, pd.DataFrame(), name)
    holdout_results.append({"strat": name, **m})
    print(f"  {name:40} | {m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
          f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f}")

# VNINDEX during holdout
vni_h = vni[(vni["time"] >= pd.Timestamp("2024-01-01")) &
            (vni["time"] <= pd.Timestamp("2026-01-16"))].copy()
vni_nav = vni_h["Close"] / vni_h["Close"].iloc[0]
n_yrs = (vni_h["time"].iloc[-1] - vni_h["time"].iloc[0]).days / 365.25
vni_cagr = (vni_nav.iloc[-1] / vni_nav.iloc[0]) ** (1/n_yrs) - 1
print(f"  {'VNINDEX_BH':40} | {vni_cagr*100:>6.2f}%   ---   ---")


# ── PART D: Stress test — 2× drawdown scenarios ────────────────────────
print("\n" + "=" * 95)
print("  PART D — STRESS TEST (apply hypothetical -25% / -40% market shocks)")
print("=" * 95)

# Run baseline
nav_base, _ = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **LIQ)
nav_base["time"] = pd.to_datetime(nav_base["time"])
nav_b = nav_base.set_index("time")["nav"]

# Apply hypothetical shock during 2022 (already crashed -33% VNI)
# Stress: amplify NAV drawdown if portfolio holds positions during simulated crash
print("\n  Hypothetical shocks at peak periods:")
def apply_shock(nav, shock_date, shock_pct, recovery_days=120):
    nav2 = nav.copy()
    if shock_date not in nav.index:
        nav2 = nav.copy()
        return nav2
    idx = nav.index.get_loc(shock_date)
    # Shock happens over 30 days
    shock_days = 30
    end_shock_idx = min(idx + shock_days, len(nav) - 1)
    end_recov_idx = min(idx + recovery_days, len(nav) - 1)
    pre_shock = nav.iloc[idx]
    trough = pre_shock * (1 + shock_pct)
    # Linear decline from idx to end_shock
    for i in range(idx, end_shock_idx + 1):
        ratio = (i - idx) / shock_days
        nav2.iloc[i] = pre_shock * (1 + shock_pct * ratio)
    # Recovery: linear back to pre-shock level
    for i in range(end_shock_idx, end_recov_idx + 1):
        recover_ratio = (i - end_shock_idx) / max(1, end_recov_idx - end_shock_idx)
        nav2.iloc[i] = trough + (pre_shock - trough) * recover_ratio * 0.7  # only 70% recovery
    # After end_recov_idx: scale post-shock by ratio
    if end_recov_idx + 1 < len(nav):
        scale = nav2.iloc[end_recov_idx] / nav.iloc[end_recov_idx]
        for i in range(end_recov_idx + 1, len(nav)):
            nav2.iloc[i] = nav.iloc[i] * scale
    return nav2


def metrics_from_nav(nav, name):
    rets = nav.pct_change().dropna()
    n_yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets) / n_yrs if n_yrs > 0 else 252
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1/n_yrs) - 1 if n_yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (nav - nav.cummax()) / nav.cummax()
    return {"name":name, "cagr_pct":cagr*100, "sharpe":sharpe,
            "max_dd_pct":dd.min()*100,
            "calmar":cagr/abs(dd.min()) if dd.min()<0 else 0}


# Find peak NAV date
peak_date = nav_b.idxmax()
print(f"  Peak NAV at {peak_date.date()} (NAV={nav_b.loc[peak_date]/1e9:.0f}B)")

# Apply shocks at peak
m_base = metrics_from_nav(nav_b, "Baseline (no shock)")
m_25 = metrics_from_nav(apply_shock(nav_b, peak_date, -0.25), "Shock -25% at peak")
m_40 = metrics_from_nav(apply_shock(nav_b, peak_date, -0.40), "Shock -40% at peak")
m_60 = metrics_from_nav(apply_shock(nav_b, peak_date, -0.60), "Shock -60% at peak (Black Swan)")

print(f"\n  {'Scenario':40} | {'CAGR':>7} {'Sh':>6} {'DD':>7} {'Cal':>5}")
for m in [m_base, m_25, m_40, m_60]:
    print(f"  {m['name']:40} | {m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
          f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f}")

# Year stability (worst year analysis)
print("\n  Yearly returns under each scenario:")
yr_table = pd.DataFrame()
for name, nav in [("base", nav_b), ("shock-25", apply_shock(nav_b, peak_date, -0.25)),
                   ("shock-40", apply_shock(nav_b, peak_date, -0.40))]:
    yr_chg = nav.groupby(nav.index.year).agg(lambda x: x.iloc[-1]/x.iloc[0] - 1) * 100
    yr_table[name] = yr_chg
print(yr_table.round(2).to_string())


pd.DataFrame(results_a).to_csv(os.path.join(WORKDIR, "data/round15_tactical.csv"), index=False)
pd.DataFrame(holdout_results).to_csv(os.path.join(WORKDIR, "data/round15_holdout.csv"), index=False)
print("\n  Saved: round15_*.csv")
