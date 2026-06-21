#!/usr/bin/env python3
"""
sim_v5_pre2014.py
=================
Z2: Pre-2014 V5 stress test (TQ34b vs DT_10_25_25 with ETF_KELLY).

V5 = ETF_KELLY (100% in NEUTRAL state). 2008 GFC potentially catastrophic if:
- During state 2/3 transitions, ETF held during VNI -65% crash
- DT might amplify or mitigate this depending on regime timing

Compare:
  V5_TQ_KELLY pre-2014  (canonical for 2007-2013)
  V5_DT_KELLY pre-2014  (state smoothing — does it help or hurt 2008 GFC?)

Both use same V_PROD filters (don't combine with C3_clean here to isolate state effect).
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
ETF_KELLY = {3: 1.0}

# Use the signal SQL from sim_v11_pre2014_c3test.py
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
    fa.fa_tier,
    SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy, fin.Revenue_YoY_P0 AS rev_yoy,
    (t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0) AS pe_z,
    (t.D_RSI > 0.90 OR (t.MA20 > 0 AND t.Close / t.MA20 > 1.25)) AS warn_ext,
    t.Volume_3M_P50 * t.Close AS liq, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec
  FROM tav2_bq.ticker AS t
  LEFT JOIN fa_dated AS fa ON fa.ticker = t.ticker AND t.time >= fa.f_time
       AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
  LEFT JOIN fin_dated AS fin ON fin.ticker = t.ticker AND t.time >= fin.fin_time
       AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
  LEFT JOIN vni_rsi AS vr ON vr.time = t.time
  WHERE t.time BETWEEN DATE '{start}' AND DATE '{end}'
    AND t.ticker != 'VNINDEX' AND t.MA200 IS NOT NULL
)
SELECT ticker, time, Close, ta, fa_tier, np_yoy, rev_yoy, pe_z, warn_ext, liq, sec
FROM classified WHERE liq >= 1e8
"""

print("="*100)
print(f"  Z2: V5 PRE-2014 STRESS TEST  ({START} -> {END}, ETF_KELLY=100% in NEUTRAL)")
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

print(f"[3] Load state series + VNI metrics...")
state_dfs = {}
for name, csv in [("TQ34b","vnindex_5state_tam_quan_v3_4b_full_history.csv"),
                  ("DT","vnindex_5state_dt_10_25_25.csv")]:
    sdf = pd.read_csv(csv)
    sdf["time"] = pd.to_datetime(sdf["time"])
    sdf = sdf[(sdf["time"]>=pd.Timestamp("2006-01-01")) & (sdf["time"]<=pd.Timestamp(END))][["time","state"]]
    state_dfs[name] = sdf

vni_full = bq(f"""SELECT t.time, t.Close, t.D_RSI, t.MA200 FROM tav2_bq.ticker AS t
              WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '2005-01-01' AND DATE '{END}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full = vni_full.sort_values("time").reset_index(drop=True)
if vni_full["MA200"].isna().all():
    vni_full["MA200"] = vni_full["Close"].rolling(200, min_periods=200).mean()
vni_full["ratio"] = vni_full["Close"] / vni_full["MA200"]
vni_ratio_today = dict(zip(vni_full["time"], vni_full["ratio"]))
vni_rsi_today = dict(zip(vni_full["time"], vni_full["D_RSI"]))
vn30_underlying = dict(zip(vni_full["time"], vni_full["Close"]))  # VNI proxy

# Classify play_type per state series
def classify_play_type(sig_src, state_df):
    s = sig_src.copy()
    state_by_date = dict(zip(state_df["time"], state_df["state"]))
    s["state5"] = s["time"].map(state_by_date)

    # Apply play_type SQL CASE logic in Python
    def py_play_type(row):
        state = row["state5"]; ta = row["ta"]; fa = row.get("fa_tier")
        pe_z = row.get("pe_z"); warn = row.get("warn_ext", False)
        npy = row.get("np_yoy"); rvy = row.get("rev_yoy")
        if pd.isna(state) or state in (1, 2):
            if fa == "E": return "AVOID_faE"
            return "AVOID_bear" if not pd.isna(state) and state in (1,2) else "PASS"
        if fa == "E": return "AVOID_faE"
        if ta >= 170 and state in (4,5) and fa in ("C","D"): return "MEGA"
        if ta >= 170 and state in (4,5): return "S_PRO"
        if ta >= 155 and state in (4,5) and fa in ("C","D"): return "MOMENTUM"
        if ta >= 155 and state in (4,5) and fa in ("A","B"): return "MOMENTUM_QUALITY"
        if ta >= 155 and state == 3 and fa in ("C","D"): return "MOMENTUM_N"
        if fa in ("A","B") and pd.notna(pe_z) and pe_z < -0.5 and ta >= 95 and state in (3,4,5) and not warn: return "COMPOUNDER_BUY"
        if fa == "C" and ta >= 100 and state in (4,5) and ((pd.notna(npy) and npy > 0.20) or (pd.notna(rvy) and rvy > 0.20)): return "DEEP_VALUE_RECOVERY"
        if ta >= 140 and state in (4,5): return "MOMENTUM_S"
        if ta >= 125 and state in (4,5): return "MOMENTUM_A"
        if ta >= 140 and state == 3: return "MOMENTUM_S_N"
        if fa in ("A","B") and 70 <= ta < 130: return "COMPOUNDER_HOLD"
        if fa in ("A","B"): return "WAIT"
        return "PASS"
    s["play_type"] = s.apply(py_play_type, axis=1)
    return s

# Apply V_PROD filters: SV_TIGHT + overheat
def apply_filters_v5(sig_src):
    s = sig_src.copy()
    s["vni_ratio"] = s["time"].map(vni_ratio_today)
    s["vni_rsi"] = s["time"].map(vni_rsi_today)
    # SV_TIGHT
    keep = s["state5"].isin([4, 5])
    has_release = s["days_since_release"].notna()
    keep |= (s["state5"] == 1) & has_release & (s["days_since_release"] <= 30)
    keep |= (s["state5"].isin([2, 3])) & has_release & (s["days_since_release"] <= 60)
    s = s[keep].copy()
    # Overheat
    overheat = (s["vni_ratio"] > 1.30).fillna(False)
    regime = ((s["state5"] == 5) | (s["vni_rsi"] > 0.75)).fillna(False)
    block = overheat & regime & s["play_type"].isin(BUY_TIERS)
    s.loc[block, "play_type"] = "AVOID_overheated"
    return s

prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
vni_dates_query = bq(VNI_QUERY.format(start=START, end=END))
vni_dates_query["time"] = pd.to_datetime(vni_dates_query["time"])
vni_dates = sorted(vni_dates_query["time"].unique())
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ_FULL = {"liquidity_volume_pct":0.20, "max_fill_days":5,
            "liquidity_lookup":liq_map, "exit_slippage_tiered":True}

def run_v5_pre2014(state_name):
    sdf = state_dfs[state_name]
    state_by_date = dict(zip(sdf["time"], sdf["state"]))
    sig_classified = classify_play_type(sig, sdf)
    sig_filtered = apply_filters_v5(sig_classified)
    print(f"  {state_name}: classified={len(sig_classified):,}, after filter={len(sig_filtered):,}, buy={(sig_filtered['play_type'].isin(BUY_TIERS)).sum():,}")
    nav_df, trades_df = simulate(sig_filtered, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=INIT_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        state_by_date={pd.Timestamp(k): int(v) for k,v in state_by_date.items()},
        cash_etf_states=ETF_KELLY, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        **LIQ_FULL)
    nav_df["time"] = pd.to_datetime(nav_df["time"])
    return nav_df, trades_df

print("\n[4] Run V5_TQ_KELLY pre-2014...")
nav_tq, tr_tq = run_v5_pre2014("TQ34b")
print("[5] Run V5_DT_KELLY pre-2014...")
nav_dt, tr_dt = run_v5_pre2014("DT")

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

m_tq = metrics(nav_tq); m_dt = metrics(nav_dt)
print("\n" + "="*100)
print(f"  Z2 PRE-2014 V5 RESULTS (2007-2013, init {INIT_NAV/1e9:.0f}B)")
print("="*100)
print(f"\n  {'Variant':<22} {'Final':>9} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'n_trades':>9}")
print(f"  {'V5_TQ34b_KELLY':<22} {m_tq['final']:>8.3f}B {m_tq['cagr']:>+6.2f}% {m_tq['sharpe']:>7.2f} {m_tq['dd']:>+6.1f}% {len(tr_tq):>8}")
print(f"  {'V5_DT_KELLY':<22} {m_dt['final']:>8.3f}B {m_dt['cagr']:>+6.2f}% {m_dt['sharpe']:>7.2f} {m_dt['dd']:>+6.1f}% {len(tr_dt):>8}")

# Per-year
print("\n  Per-year CAGR:")
print(f"  {'Year':<6} {'TQ_KELLY':>10} {'DT_KELLY':>10} {'Δ':>9}")
for yr in range(2007, 2014):
    rets = {}
    for nav_df, name in [(nav_tq,"TQ"), (nav_dt,"DT")]:
        yrm = nav_df[(nav_df["time"].dt.year==yr) & (nav_df["time"]>=pd.Timestamp(START))]
        if len(yrm) < 5: rets[name] = None
        else: rets[name] = (yrm["nav"].iloc[-1]/yrm["nav"].iloc[0] - 1) * 100
    line = f"  {yr:<6}"
    line += f" {rets['TQ']:>+8.1f}%" if rets['TQ'] is not None else f" {'-':>9}"
    line += f" {rets['DT']:>+8.1f}%" if rets['DT'] is not None else f" {'-':>9}"
    if rets['TQ'] is not None and rets['DT'] is not None:
        line += f" {rets['DT'] - rets['TQ']:>+7.1f}pp"
    print(line)

# 2008 GFC
print("\n  2008 GFC peak-trough drawdown:")
for nav_df, name in [(nav_tq,"V5_TQ_KELLY"), (nav_dt,"V5_DT_KELLY")]:
    sub = nav_df[(nav_df["time"]>=pd.Timestamp("2007-01-01")) & (nav_df["time"]<=pd.Timestamp("2009-06-30"))]
    if len(sub) < 5: continue
    rm = sub["nav"].cummax()
    dd = (sub["nav"] - rm) / rm
    worst = dd.min()*100
    worst_t = sub.loc[dd.idxmin(), "time"]
    print(f"    {name:<15}: MaxDD={worst:+.1f}% at {worst_t.date()}")

# 2011 inflation
print("\n  2011 inflation crisis drawdown:")
for nav_df, name in [(nav_tq,"V5_TQ_KELLY"), (nav_dt,"V5_DT_KELLY")]:
    sub = nav_df[(nav_df["time"]>=pd.Timestamp("2010-12-01")) & (nav_df["time"]<=pd.Timestamp("2012-01-31"))]
    if len(sub) < 5: continue
    rm = sub["nav"].cummax()
    dd = (sub["nav"] - rm) / rm
    worst = dd.min()*100
    print(f"    {name:<15}: 2011 worst DD={worst:+.1f}%")
