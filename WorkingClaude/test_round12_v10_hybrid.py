"""Round 12 — v10 Fin/RE-D bonus + VN30/small-mid hybrid + combined split."""
import os, sys, numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE, END_DATE

# v10 SQL: original SIGNAL_QUERY but with Fin/RE FA-D bonus +10 / FA-A penalty -10 in TA score
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
    t.Volume_3M_P50 * t.Close AS liq
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
  ta, liq
FROM classified
WHERE liq >= 1e9
"""

print("Loading v10 signals (with Fin/RE-D bonus)...")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} rows")
vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
TIER_HC  = ["MEGA","MOMENTUM","MOMENTUM_N"]
LIQ = {"liquidity_volume_pct":0.20, "max_fill_days":5, "liquidity_lookup":liq_map,
       "exit_slippage_tiered":True}


# ─── A) v10 vs v9 at 50B ───────────────────────────────────────────
print("\n" + "=" * 95)
print("  PART A — v10 (Fin/RE-D bonus) vs v9 baseline at 50B")
print("=" * 95)

# Reload v9 signals (without bonus)
print("  Loading v9 signals for comparison...")
from simulate_holistic_nav import SIGNAL_QUERY
sig_v9 = bq(SIGNAL_QUERY.format(start=START_DATE, end=END_DATE))
sig_v9["time"] = pd.to_datetime(sig_v9["time"])
prices_v9 = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_v9.groupby("ticker")}
liq_v9 = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_v9.iterrows()}
LIQ_v9 = {"liquidity_volume_pct":0.20, "max_fill_days":5, "liquidity_lookup":liq_v9,
          "exit_slippage_tiered":True}

results_a = []
for label, sig_d, prc_d, liq_d in [("v9 baseline", sig_v9, prices_v9, LIQ_v9),
                                    ("v10 Fin/RE-D bonus", sig, prices, LIQ)]:
    nav_df, trades_df = simulate(sig_d, prc_d, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **liq_d)
    m = metrics(nav_df, trades_df, label)
    results_a.append({"label":label, **m})
    print(f"  {label:25}: CAGR={m['cagr_pct']:.2f}% Sh={m['sharpe']:.2f} "
          f"DD={m['max_dd_pct']:.1f}% Cal={m['calmar']:.2f} trades={m['n_trades']}")


# ─── B) VN30 + small-mid hybrid ────────────────────────────────────
print("\n" + "=" * 95)
print("  PART B — VN30 + small-mid HYBRID at 50B and 100B")
print("=" * 95)

sig_vn30 = sig[sig["ticker"].isin(top30)]
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
sig_smid = sig[~sig["ticker"].isin(top30)]
prices_smid = {tk: prices[tk] for tk in prices if tk not in top30}
liq_smid = {k: v for k, v in liq_map.items() if k[0] not in top30}
LIQ_VN30 = {**LIQ, "liquidity_lookup": liq_vn30}
LIQ_SMID = {**LIQ, "liquidity_lookup": liq_smid}

print(f"  Universe: VN30={len(top30)}, small-mid={len(prices_smid)}")
print(f"  Signals: VN30={len(sig_vn30):,}, small-mid={len(sig_smid):,}")

results_b = {}
for label, sig_d, prc_d, liq_dd in [
    ("VN30_BAL", sig_vn30, prices_vn30, LIQ_VN30),
    ("smid_BAL", sig_smid, prices_smid, LIQ_SMID),
    ("FULL_BAL", sig, prices, LIQ),
]:
    for nav_lvl in [50e9, 100e9]:
        nav_df, _ = simulate(sig_d, prc_d, vni_dates,
            allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
            min_hold=2, slippage=0.001, init_nav=nav_lvl, **liq_dd)
        nav_df["time"] = pd.to_datetime(nav_df["time"])
        results_b[(label, nav_lvl)] = nav_df.set_index("time")["nav"] / nav_lvl

# Compute hybrid mixes
common_idx = results_b[("VN30_BAL", 50e9)].index.intersection(
    results_b[("smid_BAL", 50e9)].index)


def metrics_from_nav(nav, name):
    rets = nav.pct_change().dropna()
    n_yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets) / n_yrs
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1/n_yrs) - 1
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = (nav - nav.cummax()) / nav.cummax()
    return {"name":name, "cagr_pct":cagr*100, "sharpe":sharpe,
            "max_dd_pct":dd.min()*100,
            "calmar":cagr/abs(dd.min()) if dd.min()<0 else 0,
            "wealth_x":nav.iloc[-1]}


print(f"\n  Hybrid mixes at 50B:")
print(f"  {'Mix':30} | {'CAGR':>7} {'Sh':>6} {'DD':>7} {'Cal':>5} {'Wealth':>7}")
hybrid_50b = []
for vn_w, smid_w in [(1.0,0.0), (0.7,0.3), (0.5,0.5), (0.3,0.7), (0.0,1.0)]:
    n_vn = results_b[("VN30_BAL", 50e9)].loc[common_idx]
    n_sm = results_b[("smid_BAL", 50e9)].loc[common_idx]
    combined = vn_w * n_vn + smid_w * n_sm
    name = f"VN30_{int(vn_w*100)}_smid_{int(smid_w*100)}"
    m = metrics_from_nav(combined, name)
    hybrid_50b.append(m)
    print(f"  {name:30} | {m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
          f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f} {m['wealth_x']:>6.2f}×")

# Add full reference
n_full = results_b[("FULL_BAL", 50e9)].loc[common_idx]
m = metrics_from_nav(n_full, "FULL_BAL_ref")
hybrid_50b.append(m)
print(f"  {'FULL_BAL (reference)':30} | {m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
      f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f} {m['wealth_x']:>6.2f}×")


# ─── C) Combined split: BAL_Fin4 + VN30_BAL ───────────────────────
print("\n" + "=" * 95)
print("  PART C — COMBINED SPLIT: BAL+Fin/RE-max-4 + VN30_BAL at 50B")
print("=" * 95)

# Run BAL+Fin/RE-max-4 (full universe)
nav_bw_full, _ = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **LIQ)
nav_bw_full["time"] = pd.to_datetime(nav_bw_full["time"])
nav_bw_full_n = nav_bw_full.set_index("time")["nav"] / 50e9

# Already have VN30_BAL_50B from results_b
nav_vn30 = results_b[("VN30_BAL", 50e9)]

common2 = nav_bw_full_n.index.intersection(nav_vn30.index)
nav_bw_full_n = nav_bw_full_n.loc[common2]
nav_vn30 = nav_vn30.loc[common2]

print(f"\n  Combined splits at 50B:")
print(f"  {'Mix':30} | {'CAGR':>7} {'Sh':>6} {'DD':>7} {'Cal':>5}")
combined = []
for bw_w, vn_w in [(1.0,0.0), (0.7,0.3), (0.5,0.5), (0.3,0.7), (0.0,1.0)]:
    nav = bw_w * nav_bw_full_n + vn_w * nav_vn30
    name = f"BAL_Fin4_{int(bw_w*100)}_VN30_{int(vn_w*100)}"
    m = metrics_from_nav(nav, name)
    combined.append(m)
    print(f"  {name:30} | {m['cagr_pct']:>6.2f}% {m['sharpe']:>6.2f} "
          f"{m['max_dd_pct']:>6.1f}% {m['calmar']:>5.2f}")

pd.DataFrame(results_a).to_csv(os.path.join(WORKDIR, "round12_v10.csv"), index=False)
pd.DataFrame(hybrid_50b).to_csv(os.path.join(WORKDIR, "round12_hybrid.csv"), index=False)
pd.DataFrame(combined).to_csv(os.path.join(WORKDIR, "round12_combined.csv"), index=False)
print("\n  Saved: round12_*.csv")
