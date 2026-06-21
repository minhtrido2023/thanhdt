#!/usr/bin/env python3
"""
sim_v11_pre2014.py
==================
BA v11 stress test on pre-2014 era (2007-01-01 → 2013-12-31).
Tests V11 (state-conditional Fresh-Q + P3 overheated guard) against v10 baseline
on 2008 GFC crash, 2011 inflation crisis, 2012-2013 sideways recovery.

Adaptations vs production SIGNAL_V10:
  - fa_ratings: UNION fa_ratings + fa_ratings_pre2014 (just-built table)
  - ticker_prune filter: dropped (table empty pre-2014) — use full ticker universe
                         + liq filter ≥ 100M VND
  - VNINDEX_RSI_Max3M: compute from VNINDEX D_RSI rolling MAX(60) inside SQL
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, bisect
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY

START = "2007-01-01"
END   = "2013-12-31"
INIT_NAV = 1e9  # 1B for pre-2014 (smaller market)
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}

# V11 spec
FRESH_Q_BY_STATE = {1: 30, 2: 60, 3: 60}
P3_VNI_MA200_THRESHOLD = 1.30
P3_VNI_RSI_THRESHOLD = 0.75

SIGNAL_V10_PRE2014 = """
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
  FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX'
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
    AND t.ticker != 'VNINDEX'
    AND t.MA200 IS NOT NULL  -- quality gate (replaces ticker_prune)
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
FROM classified WHERE liq >= 1e8  -- 100M VND (relaxed from 1B for thin pre-2014 market)
"""

# ─── Load data ──────────────────────────────────────────────────────────
print(f"Loading signals from {START} to {END} ...")
sig = bq(SIGNAL_V10_PRE2014.format(start="2006-01-01", end=END))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} raw signal rows")
print(f"  play_type distribution:\n{sig['play_type'].value_counts().head(15)}")

print("\nLoading Release_Date ...")
releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '2005-01-01' AND DATE '{END}'""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = releases.groupby("ticker")["Release_Date"].apply(sorted).to_dict()

print("Computing days_since_release per signal row ...")
ds = np.empty(len(sig))
ticker_arr = sig["ticker"].values; time_arr = sig["time"].values
for i in range(len(sig)):
    arr = release_by_ticker.get(ticker_arr[i])
    if not arr: ds[i] = np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(time_arr[i]))
    if idx == 0: ds[i] = np.nan; continue
    ds[i] = (pd.Timestamp(time_arr[i]) - arr[idx-1]).days
sig["days_since_release"] = ds

print("Loading state5 + VNI metrics ...")
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


def apply_v11(s):
    s = s.copy()
    s["state"] = s["time"].map(state_by_date)
    s["vni_ratio"] = s["time"].map(vni_ratio_today)
    s["vni_rsi"] = s["time"].map(vni_rsi_today)

    keep = s["state"].isin([4, 5])
    has_release = s["days_since_release"].notna()
    keep |= (s["state"] == 1) & has_release & (s["days_since_release"] <= 30)
    keep |= (s["state"].isin([2, 3])) & has_release & (s["days_since_release"] <= 60)
    s = s[keep].copy()

    overheat = (s["vni_ratio"] > P3_VNI_MA200_THRESHOLD).fillna(False)
    regime = ((s["state"] == 5) | (s["vni_rsi"] > P3_VNI_RSI_THRESHOLD)).fillna(False)
    block = overheat & regime & s["play_type"].isin(BUY_TIERS)
    s.loc[block, "play_type"] = "AVOID_overheated"

    n_blocked = block.sum()
    if n_blocked > 0:
        print(f"  V11 P3 COMPOSITE blocked {n_blocked:,} buy signals on overheated days")
    return s


sig_v10 = sig.copy()  # baseline: no V11 filter
sig_v11 = apply_v11(sig)
print(f"  V11-filtered signals: {len(sig_v11):,} (baseline {len(sig_v10):,})")

# Build prices, liq_map
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni_dates_query = bq(VNI_QUERY.format(start=START, end=END))
vni_dates_query["time"] = pd.to_datetime(vni_dates_query["time"])
vni_dates = sorted(vni_dates_query["time"].unique())

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
            """).set_index("ticker")["s"].to_dict()

LIQ_FULL = {"liquidity_volume_pct":0.20, "max_fill_days":5,
            "liquidity_lookup":liq_map, "exit_slippage_tiered":True}

# ─── Run sims ────────────────────────────────────────────────────────
def run_sim(sig_in, label):
    print(f"\nRunning {label} ...", flush=True)
    nav_df, trades_df = simulate(sig_in, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=INIT_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        state_by_date={pd.Timestamp(k): int(v) for k,v in state_by_date.items()},
        **LIQ_FULL)
    nav_df["time"] = pd.to_datetime(nav_df["time"])
    trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"])
    trades_df = trades_df[trades_df["entry_date"] >= pd.Timestamp(START)].copy()
    return nav_df, trades_df

nav_v10, trades_v10 = run_sim(sig_v10, "BA v10 baseline (no V11 patches)")
nav_v11, trades_v11 = run_sim(sig_v11, "BA v11 (SV_TIGHT + P3 COMPOSITE)")

# ─── Compare ─────────────────────────────────────────────────────
def metrics(nav_df, trades_df, label):
    nav_w = nav_df[(nav_df["time"]>=pd.Timestamp(START)) & (nav_df["time"]<=pd.Timestamp(END))]
    if len(nav_w) < 2:
        return None
    final = nav_w["nav"].iloc[-1]
    tot = (final/INIT_NAV - 1)*100
    yrs = (nav_w["time"].iloc[-1] - nav_w["time"].iloc[0]).days / 365.25
    cagr = (final/INIT_NAV)**(1/yrs) - 1 if yrs > 0 else 0
    rets = nav_w["nav"].pct_change().dropna()
    sharpe = rets.mean()/rets.std() * np.sqrt(252) if rets.std() > 0 else 0
    dd = ((nav_w["nav"] - nav_w["nav"].cummax()) / nav_w["nav"].cummax()).min()
    calmar = (cagr*100) / abs(dd*100) if dd != 0 else 0
    ntr = len(trades_df)
    wr = (trades_df["ret_net"]>0).mean()*100 if ntr > 0 else 0
    stops = (trades_df["reason"]=="STOP").sum() if ntr > 0 else 0
    return {"label": label, "final_nav": final, "total_ret": tot, "cagr": cagr*100,
            "sharpe": sharpe, "dd": dd*100, "calmar": calmar,
            "n_trades": ntr, "wr": wr, "stops": stops}

m10 = metrics(nav_v10, trades_v10, "BA v10")
m11 = metrics(nav_v11, trades_v11, "BA v11")

# VNI buy & hold
vni_df = vni_full[(vni_full["time"]>=pd.Timestamp(START)) & (vni_full["time"]<=pd.Timestamp(END))]
vni_first = vni_df["Close"].iloc[0]; vni_last = vni_df["Close"].iloc[-1]
yrs = (vni_df["time"].iloc[-1] - vni_df["time"].iloc[0]).days / 365.25
vni_cagr = (vni_last/vni_first)**(1/yrs) - 1
vni_rets = vni_df["Close"].pct_change().dropna()
vni_sharpe = vni_rets.mean()/vni_rets.std()*np.sqrt(252)
vni_dd = ((vni_df["Close"] - vni_df["Close"].cummax())/vni_df["Close"].cummax()).min()

print("\n" + "="*100)
print(f"  PRE-2014 STRESS TEST: BA v11 vs v10  ({START} → {END}, init {INIT_NAV/1e9:.0f}B)")
print("="*100)
print(f"\n  {'Variant':<22}{'Final':>10}{'TotRet':>10}{'CAGR':>9}{'Sharpe':>8}{'MaxDD':>9}{'Calmar':>8}{'Trades':>8}{'WR':>7}{'Stops':>7}")
print("  " + "-"*94)
for m in [m10, m11]:
    if m is None: continue
    print(f"  {m['label']:<22}{m['final_nav']/1e9:>9.3f}B{m['total_ret']:>+9.1f}%{m['cagr']:>+8.2f}%"
          f"{m['sharpe']:>8.2f}{m['dd']:>+8.2f}%{m['calmar']:>8.2f}{m['n_trades']:>8d}{m['wr']:>+6.1f}%{m['stops']:>7d}")

print(f"\n  {'VNI buy&hold':<22}{vni_last/vni_first:>9.3f}x{(vni_last/vni_first-1)*100:>+9.1f}%"
      f"{vni_cagr*100:>+8.2f}%{vni_sharpe:>8.2f}{vni_dd*100:>+8.2f}%{vni_cagr*100/abs(vni_dd*100):>8.2f}")

# Δ analysis
if m10 and m11:
    print(f"\n  V11 vs v10 delta:")
    print(f"    CAGR:   {m11['cagr']-m10['cagr']:+.2f}pp")
    print(f"    Sharpe: {m11['sharpe']-m10['sharpe']:+.2f}")
    print(f"    DD:     {m11['dd']-m10['dd']:+.2f}pp")
    print(f"    Calmar: {m11['calmar']-m10['calmar']:+.2f}")

# Year-by-year breakdown
print(f"\n  📅 Year-by-year (BA v11):")
print(f"  {'Year':<6}{'Start NAV':>12}{'End NAV':>12}{'YoY%':>8}{'Trades':>8}{'StopRate':>9}")
trades_v11["yr"] = pd.to_datetime(trades_v11["entry_date"]).dt.year
for yr in range(2007, 2014):
    nav_yr = nav_v11[(nav_v11["time"]>=f"{yr}-01-01") & (nav_v11["time"]<=f"{yr}-12-31")]
    if len(nav_yr) < 2: continue
    s_nav, e_nav = nav_yr["nav"].iloc[0], nav_yr["nav"].iloc[-1]
    yoy = (e_nav/s_nav - 1)*100
    tr_yr = trades_v11[trades_v11["yr"] == yr]
    stop_rate = (tr_yr["reason"]=="STOP").mean()*100 if len(tr_yr) else 0
    print(f"  {yr:<6}{s_nav/1e9:>11.3f}B{e_nav/1e9:>11.3f}B{yoy:>+7.1f}%{len(tr_yr):>8d}{stop_rate:>+8.1f}%")

# Save
trades_v10.to_csv("data/sim_v10_pre2014_trades.csv", index=False)
trades_v11.to_csv("data/sim_v11_pre2014_trades.csv", index=False)
nav_v10.to_csv("data/sim_v10_pre2014_nav.csv", index=False)
nav_v11.to_csv("data/sim_v11_pre2014_nav.csv", index=False)
print(f"\n💾 Saved trade/nav CSVs (sim_v10_pre2014_*.csv, sim_v11_pre2014_*.csv)")
