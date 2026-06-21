#!/usr/bin/env python3
"""
test_tam_quan_stress_2007_2013.py
=================================
Pre-2014 STRESS TEST: BA v11 stack with LIVE Tinh Tế vs Tam Quan v3 state.
Period: 2007-01-01 → 2013-12-31 (1B init, matches memory baseline).
Covers: 2008 GFC + 2009-10 recovery + 2011 inflation crisis + 2012-13 sideways.

Adapted from sim_v11_pre2014.py — parameterized to test both state sources.
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
FRESH_Q_BY_STATE = {1: 30, 2: 60, 3: 60}
P3_VNI_MA200_THRESHOLD = 1.30; P3_VNI_RSI_THRESHOLD = 0.75

VARIANTS = [
    ("LIVE Tinh Tế",  "tav2_bq.vnindex_5state"),
    ("Tam Quan v3",    "tav2_bq.vnindex_5state_tam_quan_stress"),
]

# Parameterize SIGNAL SQL by state table name
def make_signal_sql(state_table):
    return f"""
WITH fa_union AS (
  SELECT f.ticker, f.time, f.tier FROM tav2_bq.fa_ratings AS f
  UNION ALL SELECT f.ticker, f.time, f.tier FROM tav2_bq.fa_ratings_pre2014 AS f
),
fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM fa_union AS f),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f),
vni_rsi AS (
  SELECT t.time, t.D_RSI AS vni_rsi,
    MAX(t.D_RSI) OVER (ORDER BY t.time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS vni_rsi_max3m
  FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{{start}}' AND DATE '{{end}}'),
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
  LEFT JOIN {state_table} AS s5 ON s5.time = t.time
  LEFT JOIN fa_dated AS fa ON fa.ticker = t.ticker AND t.time >= fa.f_time
       AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
  LEFT JOIN fin_dated AS fin ON fin.ticker = t.ticker AND t.time >= fin.fin_time
       AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
  LEFT JOIN vni_rsi AS vr ON vr.time = t.time
  WHERE t.time BETWEEN DATE '{{start}}' AND DATE '{{end}}'
    AND t.ticker != 'VNINDEX' AND t.MA200 IS NOT NULL)
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
FROM classified WHERE liq >= 1e8
"""

# ─── Pre-load shared data ──────────────────────────────────────
print("="*100); print(f"  PRE-2014 STRESS TEST: BA v11 — LIVE Tinh Tế vs Tam Quan v3"); print(f"  Period: {START} → {END} | Init: 1B"); print("="*100)

print("\nLoading Release_Date (shared)...")
releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '2005-01-01' AND DATE '{END}'""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = releases.groupby("ticker")["Release_Date"].apply(sorted).to_dict()

vni_full = bq(f"""SELECT t.time, t.Close, t.D_RSI, t.MA200 FROM tav2_bq.ticker AS t
              WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '2005-01-01' AND DATE '{END}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full = vni_full.sort_values("time").reset_index(drop=True)
if vni_full["MA200"].isna().all():
    vni_full["MA200"] = vni_full["Close"].rolling(200, min_periods=200).mean()
vni_full["ratio"] = vni_full["Close"] / vni_full["MA200"]
vni_ratio_today = dict(zip(vni_full["time"], vni_full["ratio"]))
vni_rsi_today = dict(zip(vni_full["time"], vni_full["D_RSI"]))

vni_dates_query = bq(VNI_QUERY.format(start=START, end=END))
vni_dates_query["time"] = pd.to_datetime(vni_dates_query["time"])
vni_dates = sorted(vni_dates_query["time"].unique())

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
            """).set_index("ticker")["s"].to_dict()

def run_variant(name, state_table):
    print("\n" + "="*100); print(f"  VARIANT: {name}  (state from {state_table})"); print("="*100)
    SIGNAL_SQL = make_signal_sql(state_table)
    print(f"  Loading signals ({state_table})...")
    sig = bq(SIGNAL_SQL.format(start="2006-01-01", end=END))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} raw signal rows")
    play_dist = sig['play_type'].value_counts().head(8)
    print(f"  Top play_types:\n{play_dist.to_string()}")

    # days_since_release
    ds = np.empty(len(sig))
    ticker_arr = sig["ticker"].values; time_arr = sig["time"].values
    for i in range(len(sig)):
        arr = release_by_ticker.get(ticker_arr[i])
        if not arr: ds[i] = np.nan; continue
        idx = bisect.bisect_right(arr, pd.Timestamp(time_arr[i]))
        if idx == 0: ds[i] = np.nan; continue
        ds[i] = (pd.Timestamp(time_arr[i]) - arr[idx-1]).days
    sig["days_since_release"] = ds

    # State
    state_df = bq(f"""SELECT s.time, s.state FROM {state_table} AS s
                  WHERE s.time BETWEEN DATE '2006-01-01' AND DATE '{END}' ORDER BY s.time""")
    state_df["time"] = pd.to_datetime(state_df["time"])
    state_by_date = dict(zip(state_df["time"], state_df["state"]))

    # V11 filter
    s = sig.copy()
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
    print(f"  After V11 filter: {len(s):,} signals (blocked {block.sum()} overheat)")

    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

    print("  Running sim...")
    nav_df, trades_df = simulate(s, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=INIT_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        state_by_date={pd.Timestamp(k): int(v) for k,v in state_by_date.items()},
        liquidity_volume_pct=0.20, max_fill_days=5, liquidity_lookup=liq_map,
        exit_slippage_tiered=True)
    nav_df["time"] = pd.to_datetime(nav_df["time"])
    trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"])
    trades_df = trades_df[trades_df["entry_date"] >= pd.Timestamp(START)].copy()
    return nav_df, trades_df

results = {}
for name, st in VARIANTS:
    nav, trades = run_variant(name, st)
    results[name] = (nav, trades)

# ─── Metrics ─────────────────────────────────────
def metrics(nav_df, trades_df):
    nav_w = nav_df[(nav_df["time"]>=pd.Timestamp(START)) & (nav_df["time"]<=pd.Timestamp(END))]
    if len(nav_w) < 2: return None
    final = nav_w["nav"].iloc[-1]
    yrs = (nav_w["time"].iloc[-1] - nav_w["time"].iloc[0]).days / 365.25
    cagr = (final/INIT_NAV)**(1/yrs) - 1 if yrs > 0 else 0
    rets = nav_w["nav"].pct_change().dropna()
    sharpe = rets.mean()/rets.std() * np.sqrt(252) if rets.std() > 0 else 0
    dd = ((nav_w["nav"] - nav_w["nav"].cummax()) / nav_w["nav"].cummax()).min()
    return {"final_nav":final,"cagr":cagr*100,"sharpe":sharpe,"dd":dd*100,
            "calmar":(cagr*100)/abs(dd*100) if dd!=0 else 0,
            "ntr":len(trades_df),"wr":(trades_df["ret_net"]>0).mean()*100 if len(trades_df)>0 else 0}

# VNI buy & hold
vni_w = vni_full[(vni_full["time"]>=pd.Timestamp(START)) & (vni_full["time"]<=pd.Timestamp(END))]
vni_yrs = (vni_w["time"].iloc[-1] - vni_w["time"].iloc[0]).days / 365.25
vni_cagr = (vni_w["Close"].iloc[-1]/vni_w["Close"].iloc[0])**(1/vni_yrs) - 1
vni_rets = vni_w["Close"].pct_change().dropna()
vni_sharpe = vni_rets.mean()/vni_rets.std()*np.sqrt(252) if vni_rets.std()>0 else 0
vni_dd = ((vni_w["Close"] - vni_w["Close"].cummax())/vni_w["Close"].cummax()).min()

print("\n\n" + "="*100); print(f"  STRESS TEST RESULTS  ({START} → {END}, init 1B)"); print("="*100)
print(f"\n  {'Variant':<22}{'Final':>9}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>10}{'Calmar':>9}{'Trades':>9}{'WR':>7}")
print("  " + "-"*85)
print(f"  {'VNI buy&hold':<22}{vni_w['Close'].iloc[-1]/vni_w['Close'].iloc[0]:>8.3f}x{vni_cagr*100:>+8.2f}%{vni_sharpe:>+9.2f}{vni_dd*100:>+9.2f}%{vni_cagr*100/abs(vni_dd*100):>+8.2f}")
for name, _ in VARIANTS:
    nav, trades = results[name]
    m = metrics(nav, trades)
    if m is None: continue
    print(f"  {name:<22}{m['final_nav']/1e9:>8.3f}B{m['cagr']:>+8.2f}%{m['sharpe']:>+9.2f}{m['dd']:>+9.2f}%{m['calmar']:>+8.2f}{m['ntr']:>9d}{m['wr']:>+6.1f}%")

# Year by year
print(f"\n  📅 Year-by-year:")
print(f"  {'Year':<6}{'Tinh Tế YoY%':>15}{'Tam Quan YoY%':>17}{'Δ':>9}")
for yr in range(2007, 2014):
    nav_l = results["LIVE Tinh Tế"][0]
    nav_t = results["Tam Quan v3"][0]
    sl = nav_l[(nav_l["time"]>=f"{yr}-01-01") & (nav_l["time"]<=f"{yr}-12-31")]
    st_ = nav_t[(nav_t["time"]>=f"{yr}-01-01") & (nav_t["time"]<=f"{yr}-12-31")]
    if len(sl)<2 or len(st_)<2: continue
    yoy_l = (sl["nav"].iloc[-1]/sl["nav"].iloc[0] - 1)*100
    yoy_t = (st_["nav"].iloc[-1]/st_["nav"].iloc[0] - 1)*100
    print(f"  {yr:<6}{yoy_l:>+14.1f}%{yoy_t:>+16.1f}%{yoy_t-yoy_l:>+8.1f}pp")

# Save
for name, _ in VARIANTS:
    nav, trades = results[name]
    safe = name.lower().replace(" ", "_").replace("ế","e").replace("ử","u")
    nav.to_csv(f"stress_pre2014_{safe}_nav.csv", index=False)
    trades.to_csv(f"stress_pre2014_{safe}_trades.csv", index=False)
print(f"\n💾 Saved NAV+trades CSVs")
