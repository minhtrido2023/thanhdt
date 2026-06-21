"""Round 13 — ULTIMATE multi-NAV + Rolling window + v11 + Deep-dive."""
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
    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier="A" THEN -10 ELSE 0 END
    -- v11 extensions:
    + CASE WHEN {V11_M_D} CAST(FLOOR(t.ICB_Code/1000) AS INT64)=1 AND fa.fa_tier="D" THEN 8 ELSE 0 END
    + CASE WHEN {V11_C_D} CAST(FLOOR(t.ICB_Code/1000) AS INT64)=3 AND fa.fa_tier="D" THEN 8 ELSE 0 END) AS ta,
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

print("Loading v10 signals...")
v10_sql = SIGNAL_V10.format(start=START_DATE, end=END_DATE, V11_M_D="FALSE AND", V11_C_D="FALSE AND")
sig_v10 = bq(v10_sql)
sig_v10["time"] = pd.to_datetime(sig_v10["time"])
prices_v10 = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_v10.groupby("ticker")}
liq_v10 = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_v10.iterrows()}
print(f"  v10: {len(sig_v10):,} signals")

print("Loading v11 signals (Mat-D + ConsGoods-D bonus)...")
v11_sql = SIGNAL_V10.format(start=START_DATE, end=END_DATE, V11_M_D="TRUE AND", V11_C_D="TRUE AND")
sig_v11 = bq(v11_sql)
sig_v11["time"] = pd.to_datetime(sig_v11["time"])
prices_v11 = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_v11.groupby("ticker")}
liq_v11 = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_v11.iterrows()}
print(f"  v11: {len(sig_v11):,} signals")

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
LIQ_v10 = {"liquidity_volume_pct":0.20, "max_fill_days":5, "liquidity_lookup":liq_v10,
           "exit_slippage_tiered":True}
LIQ_v11 = {"liquidity_volume_pct":0.20, "max_fill_days":5, "liquidity_lookup":liq_v11,
           "exit_slippage_tiered":True}


def metrics_from_nav(nav, name):
    rets = nav.pct_change().dropna()
    n_yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets) / n_yrs if n_yrs > 0 else 252
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1/n_yrs) - 1 if n_yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (nav - nav.cummax()) / nav.cummax()
    return {"name":name, "cagr_pct":cagr*100, "sharpe":sharpe,
            "max_dd_pct":dd.min()*100,
            "calmar":cagr/abs(dd.min()) if dd.min()<0 else 0,
            "wealth_x":nav.iloc[-1]}


# ── A: ULTIMATE 50/50 multi-NAV ──────────────────────────────────────
print("\n" + "="*95)
print("  PART A — ULTIMATE 50/50 BAL_Fin4(v10) + VN30_BAL at multi-NAV")
print("="*95)
results_a = []
for nav_lvl in [1e9, 30e9, 50e9, 100e9, 200e9]:
    print(f"\n  NAV={nav_lvl/1e9:.0f}B...")
    # BAL+Fin/RE-max-4 with v10
    nav_bw, _ = simulate(sig_v10, prices_v10, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=nav_lvl,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **LIQ_v10)
    nav_bw["time"] = pd.to_datetime(nav_bw["time"])
    nav_bw_n = nav_bw.set_index("time")["nav"] / nav_lvl

    # VN30_BAL with v10
    sig_vn30 = sig_v10[sig_v10["ticker"].isin(top30)]
    prices_vn30 = {tk: prices_v10[tk] for tk in top30 if tk in prices_v10}
    liq_vn30 = {k: v for k, v in liq_v10.items() if k[0] in top30}
    LIQ_vn30 = {**LIQ_v10, "liquidity_lookup": liq_vn30}
    nav_v30, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=nav_lvl, **LIQ_vn30)
    nav_v30["time"] = pd.to_datetime(nav_v30["time"])
    nav_v30_n = nav_v30.set_index("time")["nav"] / nav_lvl

    common = nav_bw_n.index.intersection(nav_v30_n.index)
    nav_bw_n = nav_bw_n.loc[common]
    nav_v30_n = nav_v30_n.loc[common]

    # 50/50 combined
    combined = 0.5 * nav_bw_n + 0.5 * nav_v30_n
    m_combo = metrics_from_nav(combined, f"50/50_{nav_lvl/1e9:.0f}B")
    m_bw = metrics_from_nav(nav_bw_n, f"BAL_Fin4_{nav_lvl/1e9:.0f}B")
    m_v30 = metrics_from_nav(nav_v30_n, f"VN30_{nav_lvl/1e9:.0f}B")
    m_combo["nav_B"] = nav_lvl/1e9
    m_combo["bw_cagr"] = m_bw["cagr_pct"]
    m_combo["v30_cagr"] = m_v30["cagr_pct"]
    results_a.append(m_combo)
    print(f"    BAL_Fin4: CAGR={m_bw['cagr_pct']:.2f}% Sh={m_bw['sharpe']:.2f}")
    print(f"    VN30:     CAGR={m_v30['cagr_pct']:.2f}% Sh={m_v30['sharpe']:.2f}")
    print(f"    🏆 50/50: CAGR={m_combo['cagr_pct']:.2f}% Sh={m_combo['sharpe']:.2f} "
          f"DD={m_combo['max_dd_pct']:.1f}% Cal={m_combo['calmar']:.2f}")


# ── C: v11 — extend Fin/RE-D pattern to Materials + Cons Goods ──────
print("\n" + "="*95)
print("  PART C — v11: Extend FA-D bonus to Materials + Cons Goods")
print("="*95)
print(f"\n  v10 vs v11 at 50B BAL+Fin/RE-max-4...")
results_c = []
for label, sigd, prcd, liqd in [("v10", sig_v10, prices_v10, LIQ_v10),
                                  ("v11", sig_v11, prices_v11, LIQ_v11)]:
    nav_df, _ = simulate(sigd, prcd, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **liqd)
    m = metrics(nav_df, pd.DataFrame(), label)
    results_c.append({"version":label, **m})
    print(f"  {label:10}: CAGR={m['cagr_pct']:.2f}% Sh={m['sharpe']:.2f} "
          f"DD={m['max_dd_pct']:.1f}% Cal={m['calmar']:.2f}")


# ── B: Quarterly rolling re-tune — quick stability check using v10 ULTIMATE ──
print("\n" + "="*95)
print("  PART B — ROLLING QUARTERLY STABILITY (50/50 ULTIMATE at 50B)")
print("="*95)
# Reuse 50B 50/50 NAV from PART A
combo_50b = next(r for r in results_a if r["nav_B"]==50)
print(f"\n  50B ULTIMATE: full-period CAGR={combo_50b['cagr_pct']:.2f}% Sh={combo_50b['sharpe']:.2f}")
print("  Computing quarterly returns of 50/50 combined NAV...")
# Re-run 50B
nav_bw_50, _ = simulate(sig_v10, prices_v10, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **LIQ_v10)
nav_bw_50["time"] = pd.to_datetime(nav_bw_50["time"])
nav_bw_50_n = nav_bw_50.set_index("time")["nav"] / 50e9
sig_vn30_50 = sig_v10[sig_v10["ticker"].isin(top30)]
liq_vn30_50 = {k: v for k, v in liq_v10.items() if k[0] in top30}
nav_v30_50, _ = simulate(sig_vn30_50, {tk: prices_v10[tk] for tk in top30 if tk in prices_v10},
    vni_dates, allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9, **{**LIQ_v10, "liquidity_lookup":liq_vn30_50})
nav_v30_50["time"] = pd.to_datetime(nav_v30_50["time"])
nav_v30_50_n = nav_v30_50.set_index("time")["nav"] / 50e9
common = nav_bw_50_n.index.intersection(nav_v30_50_n.index)
ultimate_50b = 0.5 * nav_bw_50_n.loc[common] + 0.5 * nav_v30_50_n.loc[common]
qrets = ultimate_50b.resample("QE").last().pct_change().dropna() * 100
print(f"\n  Quarterly returns (n={len(qrets)}):")
print(f"    Mean: {qrets.mean():.2f}%, Median: {qrets.median():.2f}%, Std: {qrets.std():.2f}%")
print(f"    Win rate: {(qrets > 0).mean()*100:.1f}%, Best: {qrets.max():.2f}%, Worst: {qrets.min():.2f}%")
print(f"  Worst 5 quarters:")
for q, r in qrets.nsmallest(5).items():
    print(f"    {q.to_period('Q')}: {r:+.2f}%")


# ── D: ULTIMATE deep-dive — drawdown periods ────────────────────────
print("\n" + "="*95)
print("  PART D — ULTIMATE 50/50 50B DEEP-DIVE: Drawdown periods")
print("="*95)
nav = ultimate_50b
peak = nav.cummax()
dd = (nav - peak) / peak
in_dd = dd < -0.05
dd_periods = []
i = 0
while i < len(dd):
    if dd.iloc[i] < -0.05:
        start = i
        peak_idx = i
        while peak_idx > 0 and nav.iloc[peak_idx-1] >= nav.iloc[start]:
            peak_idx -= 1
        end = i
        peak_val = peak.iloc[i]
        while end < len(dd) and nav.iloc[end] < peak_val:
            end += 1
        max_dd_val = dd.iloc[start:min(end+1, len(dd))].min()
        max_dd_idx = start + np.argmin(dd.iloc[start:min(end+1, len(dd))].values)
        dd_periods.append({
            "peak_date": nav.index[peak_idx].date(),
            "trough_date": nav.index[max_dd_idx].date(),
            "recovery_date": nav.index[end].date() if end < len(nav) else "ongoing",
            "max_dd_pct": max_dd_val * 100,
            "to_trough_d": max_dd_idx - peak_idx,
            "recovery_d": end - max_dd_idx if end < len(nav) else None,
        })
        i = end + 1
    else:
        i += 1
df_dd = pd.DataFrame(dd_periods).sort_values("max_dd_pct").head(5)
print("  Top 5 drawdowns:")
print(df_dd.to_string(index=False))

# Yearly NAV
print("\n  Year-by-year NAV (1B start):")
yr_nav = ultimate_50b.groupby(ultimate_50b.index.year).last()
print((yr_nav).to_string())

pd.DataFrame(results_a).to_csv(os.path.join(WORKDIR, "round13_multi_nav.csv"), index=False)
pd.DataFrame(results_c).to_csv(os.path.join(WORKDIR, "round13_v11.csv"), index=False)
df_dd.to_csv(os.path.join(WORKDIR, "round13_dd_periods.csv"), index=False)
print("\n  Saved: round13_*.csv")
