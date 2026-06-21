#!/usr/bin/env python3
"""
sim_v11_pre2014_clean.py
========================
Pre-2014 stress test for C3_clean (NO SV_TIGHT at all).

User insight: SV_TIGHT was for immature pre-2014 market dominated by
psychology. Modern market (post-2014) doesn't need this filter.
Empirical test: does removing SVT entirely also work pre-2014?

Variants compared:
  V_PROD       — SVT s1=30, s2=60, s3=60 (current production)
  C3_safer     — SVT s3=60→90 (single change, validated)
  C3_clean     — NO SVT at all (full removal)
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, bisect
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq, VNI_QUERY

START = "2007-01-01"; END = "2013-12-31"
INIT_NAV = 1e9
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}

# Reuse the signal SQL from sim_v11_pre2014_c3test.py
SIGNAL_SQL = """
WITH fa_union AS (
  SELECT f.ticker, f.time, f.tier FROM tav2_bq.fa_ratings AS f
  UNION ALL
  SELECT f.ticker, f.time, f.tier FROM tav2_bq.fa_ratings_pre2014 AS f
),
fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM fa_union AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
),
vni_rsi AS (
  SELECT t.time, t.D_RSI AS vni_rsi,
    MAX(t.D_RSI) OVER (ORDER BY t.time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS vni_rsi_max3m
  FROM tav2_bq.ticker AS t WHERE t.ticker = 'VNINDEX'
    AND t.time BETWEEN DATE '{start}' AND DATE '{end}'
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
    + CASE WHEN vr.vni_rsi_max3m > 0.65 THEN 10 ELSE 0 END
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
  LEFT JOIN vni_rsi AS vr ON vr.time = t.time
  WHERE t.time BETWEEN DATE '{start}' AND DATE '{end}'
    AND t.ticker != 'VNINDEX' AND t.MA200 IS NOT NULL
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
  END AS play_type, ta, liq, sec
FROM classified WHERE liq >= 1e8
"""

print("="*100)
print(f"  PRE-2014: V_PROD vs C3_safer vs C3_clean  ({START} -> {END})")
print("="*100)

print(f"\n[1] Load signals...")
sig = bq(SIGNAL_SQL.format(start="2006-01-01", end=END))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows")

print(f"[2] Compute days_since_release...")
releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '2005-01-01' AND DATE '{END}'""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = releases.groupby("ticker")["Release_Date"].apply(sorted).to_dict()
ds = np.empty(len(sig))
ticker_arr = sig["ticker"].values; time_arr = sig["time"].values
for i in range(len(sig)):
    arr = release_by_ticker.get(ticker_arr[i])
    if not arr: ds[i] = np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(time_arr[i]))
    if idx == 0: ds[i] = np.nan; continue
    ds[i] = (pd.Timestamp(time_arr[i]) - arr[idx-1]).days
sig["days_since_release"] = ds

print(f"[3] Load state5, VNI metrics...")
state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
              WHERE s.time BETWEEN DATE '2006-01-01' AND DATE '{END}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.D_RSI, t.MA200 FROM tav2_bq.ticker AS t
              WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '2005-01-01' AND DATE '{END}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full = vni_full.sort_values("time").reset_index(drop=True)
if vni_full["MA200"].isna().all():
    vni_full["MA200"] = vni_full["Close"].rolling(200, min_periods=200).mean()
vni_full["ratio"] = vni_full["Close"] / vni_full["MA200"]
vni_ratio_today = dict(zip(vni_full["time"], vni_full["ratio"]))
vni_rsi_today = dict(zip(vni_full["time"], vni_full["D_RSI"]))

# How many state==3 days in 2007-2013 with buy signals?
sig_with_state = sig.copy()
sig_with_state["state"] = sig_with_state["time"].map(state_by_date)
state3_buy = sig_with_state[(sig_with_state["state"]==3) & sig_with_state["play_type"].isin(BUY_TIERS)]
print(f"\n  State-3 buy signal rows (pre-2014): {len(state3_buy):,}")
print(f"  Total buy signal rows: {sig_with_state['play_type'].isin(BUY_TIERS).sum():,}")
print(f"  State-3 fraction of all buys: {len(state3_buy) / max(sig_with_state['play_type'].isin(BUY_TIERS).sum(),1) * 100:.1f}%")

# Filter functions
def apply_filters(sig_src, svt_mode="prod", overheat_ma=1.30, overheat_rsi=0.75):
    """svt_mode: 'prod' (s1=30,s2=60,s3=60), 'safer' (s3=90), 'clean' (no SVT)"""
    s = sig_src.copy()
    s["state"] = s["time"].map(state_by_date)
    s["vni_ratio"] = s["time"].map(vni_ratio_today)
    s["vni_rsi"] = s["time"].map(vni_rsi_today)

    if svt_mode == "prod":
        keep = s["state"].isin([4, 5])
        has_release = s["days_since_release"].notna()
        keep |= (s["state"] == 1) & has_release & (s["days_since_release"] <= 30)
        keep |= (s["state"].isin([2, 3])) & has_release & (s["days_since_release"] <= 60)
        s = s[keep].copy()
    elif svt_mode == "safer":
        keep = s["state"].isin([4, 5])
        has_release = s["days_since_release"].notna()
        keep |= (s["state"] == 1) & has_release & (s["days_since_release"] <= 30)
        keep |= (s["state"] == 2) & has_release & (s["days_since_release"] <= 60)
        keep |= (s["state"] == 3) & has_release & (s["days_since_release"] <= 90)
        s = s[keep].copy()
    elif svt_mode == "clean":
        pass  # NO SVT filter

    overheat = (s["vni_ratio"] > overheat_ma).fillna(False)
    regime = ((s["state"] == 5) | (s["vni_rsi"] > overheat_rsi)).fillna(False)
    block = overheat & regime & s["play_type"].isin(BUY_TIERS)
    s.loc[block, "play_type"] = "AVOID_overheated"
    return s

sig_vprod = apply_filters(sig, svt_mode="prod")
sig_safer = apply_filters(sig, svt_mode="safer")
sig_clean = apply_filters(sig, svt_mode="clean")
print(f"  V_PROD filtered: {len(sig_vprod):,}")
print(f"  C3_safer filtered: {len(sig_safer):,}")
print(f"  C3_clean filtered: {len(sig_clean):,}")

# Build prices, liq
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
vni_dates_query = bq(VNI_QUERY.format(start=START, end=END))
vni_dates_query["time"] = pd.to_datetime(vni_dates_query["time"])
vni_dates = sorted(vni_dates_query["time"].unique())
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ_FULL = {"liquidity_volume_pct":0.20, "max_fill_days":5,
            "liquidity_lookup":liq_map, "exit_slippage_tiered":True}

def run_sim(sig_in, label):
    print(f"\n  Running {label}...", flush=True)
    nav_df, trades_df = simulate(sig_in, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=INIT_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        state_by_date={pd.Timestamp(k): int(v) for k,v in state_by_date.items()},
        **LIQ_FULL)
    nav_df["time"] = pd.to_datetime(nav_df["time"])
    return nav_df, trades_df

print("\n[4] Run sims...")
nav_vprod, tr_vprod = run_sim(sig_vprod, "V_PROD")
nav_safer, tr_safer = run_sim(sig_safer, "C3_safer (s3=90)")
nav_clean, tr_clean = run_sim(sig_clean, "C3_clean (no SVT)")

def metrics(nav_df):
    nav_w = nav_df[(nav_df["time"]>=pd.Timestamp(START)) & (nav_df["time"]<=pd.Timestamp(END))]
    if len(nav_w) < 2: return None
    final = nav_w["nav"].iloc[-1]
    yrs = (nav_w["time"].iloc[-1] - nav_w["time"].iloc[0]).days / 365.25
    cagr = (final/INIT_NAV)**(1/yrs) - 1
    rets = nav_w["nav"].pct_change().dropna()
    sharpe = rets.mean()/rets.std()*np.sqrt(252) if rets.std() > 0 else 0
    dd = ((nav_w["nav"] - nav_w["nav"].cummax()) / nav_w["nav"].cummax()).min()
    return {"final":final/1e9, "cagr":cagr*100, "sharpe":sharpe, "dd":dd*100}

m_p = metrics(nav_vprod); m_s = metrics(nav_safer); m_c = metrics(nav_clean)

print("\n" + "="*100)
print(f"  PRE-2014 RESULTS (2007-2013, init {INIT_NAV/1e9:.0f}B)")
print("="*100)
print(f"\n  {'Variant':<24} {'Final':>9} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'n_trades':>9}")
print(f"  {'V_PROD':<24} {m_p['final']:>8.3f}B {m_p['cagr']:>+6.2f}% {m_p['sharpe']:>7.2f} {m_p['dd']:>+6.1f}% {len(tr_vprod):>8}")
print(f"  {'C3_safer (s3=90)':<24} {m_s['final']:>8.3f}B {m_s['cagr']:>+6.2f}% {m_s['sharpe']:>7.2f} {m_s['dd']:>+6.1f}% {len(tr_safer):>8}")
print(f"  {'C3_clean (no SVT)':<24} {m_c['final']:>8.3f}B {m_c['cagr']:>+6.2f}% {m_c['sharpe']:>7.2f} {m_c['dd']:>+6.1f}% {len(tr_clean):>8}")

# Per-year
print("\n  Per-year CAGR:")
print(f"  {'Year':<6} {'V_PROD':>8} {'C3_safer':>9} {'C3_clean':>9}")
for yr in range(2007, 2014):
    parts = []
    for nav_df in [nav_vprod, nav_safer, nav_clean]:
        yrm = nav_df[(nav_df["time"].dt.year==yr) & (nav_df["time"]>=pd.Timestamp(START))]
        if len(yrm) < 5:
            parts.append(None)
        else:
            parts.append((yrm["nav"].iloc[-1]/yrm["nav"].iloc[0] - 1) * 100)
    print(f"  {yr:<6}", end="")
    for p in parts:
        print(f" {p:>+7.1f}%" if p is not None else f" {'-':>8}", end="")
    print()

# 2008 GFC peak-trough
print("\n  2008 GFC peak-trough drawdown:")
for nav_df, name in [(nav_vprod,"V_PROD"), (nav_safer,"C3_safer"), (nav_clean,"C3_clean")]:
    sub = nav_df[(nav_df["time"]>=pd.Timestamp("2007-01-01")) & (nav_df["time"]<=pd.Timestamp("2009-06-30"))]
    if len(sub) < 5: continue
    rm = sub["nav"].cummax()
    dd = (sub["nav"] - rm) / rm
    worst = dd.min()*100
    worst_t = sub.loc[dd.idxmin(), "time"]
    print(f"    {name:<10}: MaxDD={worst:+.1f}% at {worst_t.date()}")
