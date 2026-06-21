#!/usr/bin/env python3
"""
sim_v11_pre2014_c3test.py
=========================
Pre-2014 stress test: V_PROD vs C3_cons (filter re-tune).

Critical question: does cash_etf {2:0.5} destroy NAV in 2008 GFC?

Adapts sim_v11_pre2014.py by adding:
  - V_PROD variant: current production filters (SVT s3=60, cash_etf=None)
  - C3_cons variant: SVT s3=90, cash_etf={2:0.5, 3:0.7}

Uses VNINDEX as vn30_underlying proxy (no real ETF existed pre-2014).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, bisect, io
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

print("="*100)
print(f"  PRE-2014 STRESS TEST: V_PROD vs C3_cons  ({START} -> {END})")
print("="*100)

# Re-use the SQL + signal logic from sim_v11_pre2014.py via import (it executes module-level)
# Cleaner: define inline what we need
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

# Use VNINDEX as ETF proxy
vn30_underlying = dict(zip(vni_full["time"], vni_full["Close"]))

# Filter functions
def apply_filters(sig_src, svt_s3, overheat_ma=1.30, overheat_rsi=0.75):
    s = sig_src.copy()
    s["state"] = s["time"].map(state_by_date)
    s["vni_ratio"] = s["time"].map(vni_ratio_today)
    s["vni_rsi"] = s["time"].map(vni_rsi_today)

    # SV_TIGHT
    keep = s["state"].isin([4, 5])
    has_release = s["days_since_release"].notna()
    keep |= (s["state"] == 1) & has_release & (s["days_since_release"] <= 30)
    keep |= (s["state"] == 2) & has_release & (s["days_since_release"] <= 60)
    keep |= (s["state"] == 3) & has_release & (s["days_since_release"] <= svt_s3)
    s = s[keep].copy()

    # Overheat (state 5 only for both)
    overheat = (s["vni_ratio"] > overheat_ma).fillna(False)
    regime = ((s["state"] == 5) | (s["vni_rsi"] > overheat_rsi)).fillna(False)
    block = overheat & regime & s["play_type"].isin(BUY_TIERS)
    s.loc[block, "play_type"] = "AVOID_overheated"
    return s

sig_vprod = apply_filters(sig, svt_s3=60)
sig_c3    = apply_filters(sig, svt_s3=90)
print(f"  V_PROD filtered: {len(sig_vprod):,} | C3_cons filtered: {len(sig_c3):,}")

# Build prices, liq, sectors
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
vni_dates_query = bq(VNI_QUERY.format(start=START, end=END))
vni_dates_query["time"] = pd.to_datetime(vni_dates_query["time"])
vni_dates = sorted(vni_dates_query["time"].unique())
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ_FULL = {"liquidity_volume_pct":0.20, "max_fill_days":5,
            "liquidity_lookup":liq_map, "exit_slippage_tiered":True}

# Run sims
def run_sim(sig_in, label, cash_etf=None):
    print(f"\n  Running {label} (cash_etf={cash_etf})...", flush=True)
    kwargs = dict(allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=INIT_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        state_by_date={pd.Timestamp(k): int(v) for k,v in state_by_date.items()},
        **LIQ_FULL)
    if cash_etf is not None:
        kwargs["cash_etf_states"] = cash_etf
        kwargs["vn30_underlying"]  = vn30_underlying
        kwargs["etf_mgmt_fee_annual"] = 0.0
        kwargs["etf_tracking_drag_annual"] = 0.0
        kwargs["etf_rebalance_friction"] = 0.0015
    nav_df, trades_df = simulate(sig_in, prices, vni_dates, **kwargs)
    nav_df["time"] = pd.to_datetime(nav_df["time"])
    return nav_df, trades_df

print("\n[4] Running V_PROD baseline (current production)...")
nav_vprod, trades_vprod = run_sim(sig_vprod, "V_PROD", cash_etf=None)

print("\n[5] Running C3_cons (SVT s3=90 + cash_etf {2:0.5, 3:0.7})...")
nav_c3, trades_c3 = run_sim(sig_c3, "C3_cons", cash_etf={2: 0.5, 3: 0.7})

print("\n[6] Running C3_safer (SVT s3=90 ONLY, no cash_etf change)...")
nav_c3safe, trades_c3safe = run_sim(sig_c3, "C3_safer", cash_etf=None)

# Metrics
def metrics(nav_df, label):
    nav_w = nav_df[(nav_df["time"]>=pd.Timestamp(START)) & (nav_df["time"]<=pd.Timestamp(END))]
    if len(nav_w) < 2: return None
    final = nav_w["nav"].iloc[-1]
    tot = (final/INIT_NAV - 1)*100
    yrs = (nav_w["time"].iloc[-1] - nav_w["time"].iloc[0]).days / 365.25
    cagr = (final/INIT_NAV)**(1/yrs) - 1
    rets = nav_w["nav"].pct_change().dropna()
    sharpe = rets.mean()/rets.std()*np.sqrt(252) if rets.std() > 0 else 0
    dd = ((nav_w["nav"] - nav_w["nav"].cummax()) / nav_w["nav"].cummax()).min()
    return {"label":label, "final":final/1e9, "cagr":cagr*100, "sharpe":sharpe, "dd":dd*100}

mp = metrics(nav_vprod, "V_PROD")
mc = metrics(nav_c3, "C3_cons")
ms = metrics(nav_c3safe, "C3_safer")

print("\n" + "="*100)
print(f"  PRE-2014 RESULTS (2007-2013, init {INIT_NAV/1e9:.0f}B)")
print("="*100)
print(f"\n  {'Variant':<14} {'Final':>9} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7}")
for m in [mp, mc, ms]:
    if m: print(f"  {m['label']:<14} {m['final']:>8.3f}B {m['cagr']:>+6.2f}% {m['sharpe']:>7.2f} {m['dd']:>+6.1f}%")

# VNI buy & hold ref
vni_df = vni_full[(vni_full["time"]>=pd.Timestamp(START)) & (vni_full["time"]<=pd.Timestamp(END))]
vni_first = vni_df["Close"].iloc[0]; vni_last = vni_df["Close"].iloc[-1]
yrs = (vni_df["time"].iloc[-1] - vni_df["time"].iloc[0]).days / 365.25
vni_cagr = (vni_last/vni_first)**(1/yrs) - 1
vni_dd = ((vni_df["Close"] - vni_df["Close"].cummax())/vni_df["Close"].cummax()).min()
print(f"  {'B&H VNINDEX':<14} {'-':>9} {vni_cagr*100:>+6.2f}% {'-':>7} {vni_dd*100:>+6.1f}%")

# Per-year breakdown
print("\n  Per-year CAGR:")
print(f"  {'Year':<6} {'V_PROD':>9} {'C3_cons':>9} {'C3_safer':>9} {'VNI':>8} {'Δcons-PROD':>10} {'Δsafer-PROD':>11}")
for yr in range(2007, 2014):
    masks = {}
    rets = {}
    for nav_df, name in [(nav_vprod,"V_PROD"), (nav_c3,"C3_cons"), (nav_c3safe,"C3_safer")]:
        yrm = nav_df[(nav_df["time"].dt.year==yr) & (nav_df["time"]>=pd.Timestamp(START))]
        if len(yrm) < 5: rets[name] = None; continue
        rets[name] = (yrm["nav"].iloc[-1]/yrm["nav"].iloc[0] - 1) * 100
    vni_yr = vni_df[vni_df["time"].dt.year==yr]
    vni_ret = (vni_yr["Close"].iloc[-1]/vni_yr["Close"].iloc[0] - 1) * 100 if len(vni_yr) >= 5 else None
    line = f"  {yr:<6}"
    for n in ["V_PROD","C3_cons","C3_safer"]:
        line += f" {rets[n]:>+7.1f}%" if rets[n] is not None else f" {'-':>8}"
    line += f" {vni_ret:>+7.1f}%" if vni_ret is not None else f" {'-':>7}"
    if rets["C3_cons"] is not None and rets["V_PROD"] is not None:
        line += f"  {rets['C3_cons']-rets['V_PROD']:>+8.1f}pp"
    if rets["C3_safer"] is not None and rets["V_PROD"] is not None:
        line += f"  {rets['C3_safer']-rets['V_PROD']:>+9.1f}pp"
    print(line)

# Critical: 2008 GFC DD
print("\n  2008 GFC peak-trough drawdown:")
for nav_df, name in [(nav_vprod,"V_PROD"), (nav_c3,"C3_cons"), (nav_c3safe,"C3_safer")]:
    sub = nav_df[(nav_df["time"]>=pd.Timestamp("2007-01-01")) & (nav_df["time"]<=pd.Timestamp("2009-06-30"))]
    if len(sub) < 5: continue
    rm = sub["nav"].cummax()
    dd = (sub["nav"] - rm) / rm
    worst = dd.min()*100
    worst_t = sub.loc[dd.idxmin(), "time"]
    print(f"    {name:<10}: MaxDD={worst:+.1f}% at {worst_t.date()}")
