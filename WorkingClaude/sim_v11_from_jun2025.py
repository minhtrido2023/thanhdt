#!/usr/bin/env python3
"""
sim_v11_from_jun2025.py
========================
Run BA v11 simulation from 2025-06-09 to latest (2026-05-14).
Init NAV = 50B VND. Output: detailed trade log + cash balance tracking.

V11 spec applied:
  - SV_TIGHT Fresh-Q: 30d state 1, 60d state 2-3, no filter state 4-5
  - P3 COMPOSITE: VNI/MA200 > 1.30 AND (state5==5 OR D_RSI > 0.75) → block buys
  - Strategy: BAL+Fin/RE-max-4 (50B), max_pos=10, hold=45d, stop=-20%
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
from test_round14_stability import SIGNAL_V10

START = "2025-06-09"
END   = "2026-05-15"
INIT_NAV = 50e9
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
FRESH_Q_BY_STATE = {1: 30, 2: 60, 3: 60}
P3_VNI_MA200_THRESHOLD = 1.30
P3_VNI_RSI_THRESHOLD = 0.75

# ─── Load data ──────────────────────────────────────────────────────────
print(f"Loading signals from {START} to {END} ...")
# Need extra history for days_since_release — pull from 2024-06 to capture quarterly cycle
sig = bq(SIGNAL_V10.format(start="2024-01-01", end=END))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} raw signal rows")

print("Loading Release_Date ...")
releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '2023-01-01' AND DATE '{END}'""")
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
              WHERE s.time BETWEEN DATE '2024-01-01' AND DATE '{END}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.D_RSI, t.MA200 FROM tav2_bq.ticker AS t
              WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '2023-01-01' AND DATE '{END}'""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full = vni_full.sort_values("time").reset_index(drop=True)
if vni_full["MA200"].isna().all():
    vni_full["MA200"] = vni_full["Close"].rolling(200, min_periods=200).mean()
vni_full["ratio"] = vni_full["Close"] / vni_full["MA200"]
vni_ratio_today = dict(zip(vni_full["time"], vni_full["ratio"]))
vni_rsi_today = dict(zip(vni_full["time"], vni_full["D_RSI"]))

# ─── Apply V11 filters to signals ─────────────────────────────────────
def apply_v11(s):
    s = s.copy()
    s["state"] = s["time"].map(state_by_date)
    s["vni_ratio"] = s["time"].map(vni_ratio_today)
    s["vni_rsi"] = s["time"].map(vni_rsi_today)

    # SV_TIGHT: state-conditional Fresh-Q
    keep = s["state"].isin([4, 5])  # BULL: no filter
    has_release = s["days_since_release"].notna()
    keep |= (s["state"] == 1) & has_release & (s["days_since_release"] <= 30)
    keep |= (s["state"].isin([2, 3])) & has_release & (s["days_since_release"] <= 60)
    s = s[keep].copy()

    # P3 COMPOSITE: block buys if overheat + regime confirmation
    overheat = (s["vni_ratio"] > P3_VNI_MA200_THRESHOLD).fillna(False)
    regime = ((s["state"] == 5) | (s["vni_rsi"] > P3_VNI_RSI_THRESHOLD)).fillna(False)
    block = overheat & regime & s["play_type"].isin(BUY_TIERS)
    s.loc[block, "play_type"] = "AVOID_overheated"

    n_overheat = block.sum()
    if n_overheat > 0:
        print(f"  V11 P3 COMPOSITE blocked {n_overheat:,} buy signals on overheated days")
    return s

sig_v11 = apply_v11(sig)
print(f"  V11-filtered signals: {len(sig_v11):,}")

# ─── Filter to actual sim window (keep prior days for entry context) ──
sig_in_window = sig_v11[sig_v11["time"] >= pd.Timestamp(START)].copy()
print(f"  Signals in sim window {START}+: {len(sig_in_window):,}")

# Build prices, liq_map
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

# VNI for dates
vni_dates_query = bq(VNI_QUERY.format(start=START, end=END))
vni_dates_query["time"] = pd.to_datetime(vni_dates_query["time"])
vni_dates = sorted(vni_dates_query["time"].unique())

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
            """).set_index("ticker")["s"].to_dict()

LIQ_FULL = {"liquidity_volume_pct":0.20, "max_fill_days":5,
            "liquidity_lookup":liq_map, "exit_slippage_tiered":True}

# ─── Run sim ──────────────────────────────────────────────────────────
print(f"\nRunning BA v11 sim from {START} to {END} ...")
nav_log = []
nav_df, trades_df = simulate(sig_v11, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=INIT_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    state_by_date={pd.Timestamp(k): int(v) for k,v in state_by_date.items()},
    nav_log_extra=nav_log,
    **LIQ_FULL)
nav_df["time"] = pd.to_datetime(nav_df["time"])

# Filter trades to those starting in sim window
trades_df = trades_df[pd.to_datetime(trades_df["entry_date"]) >= pd.Timestamp(START)].copy()

# ─── Detailed trade log ───────────────────────────────────────────────
print("\n" + "═"*120)
print(f"  BA V11 SIMULATION — {START} → {END}  |  Init NAV: {INIT_NAV/1e9:.0f}B VND  |  Strategy: BAL+Fin/RE-max-4")
print("═"*120)

print(f"\n📊 TRADE LOG ({len(trades_df)} trades):")
print(f"{'#':<3}{'Ticker':<7}{'Entry':<12}{'Exit':<12}{'Days':>4}{'EntryPx':>10}{'ExitPx':>10}"
      f"{'Cost(B)':>10}{'Proceeds(B)':>13}{'Ret%':>8}{'Reason':<10}{'PlayType':<22}")
print("-"*135)

# Add cost/proceeds columns
trades_df = trades_df.sort_values("entry_date").reset_index(drop=True)
trades_df["entry_date"] = pd.to_datetime(trades_df["entry_date"])
trades_df["exit_date"] = pd.to_datetime(trades_df["exit_date"])
for i, r in trades_df.iterrows():
    # Reconstruct cost from ret_net and exit value
    ret_net = r.get("ret_net", r.get("ret", 0))
    days = int(r["days_held"])
    # Position size = round-trip from ret_net (proceeds/cost - 1)
    # Without explicit cost, estimate: assume target_value at entry based on average position
    # Use entry_price × shares; shares not in trades_df. Approximate by checking NAV log.
    # For display purposes, just show ret_net %
    print(f"{i+1:<3}{r['ticker']:<7}{str(r['entry_date'].date()):<12}{str(r['exit_date'].date()):<12}"
          f"{days:>4}{r['entry_price']:>9.0f}{r['exit_price']:>9.0f}"
          f"{'?':>10}{'?':>13}"
          f"{ret_net*100:>+7.2f}%{r['reason']:<10}{r['play_type']:<22}")

# ─── Cash + NAV tracking through time ─────────────────────────────────
# nav_log captures (date, cash, n_pos, deployed_pct, state)
print(f"\n💰 NAV / CASH TRACKING (sampled monthly):")
print(f"{'Date':<12}{'NAV(B)':>10}{'Cash(B)':>10}{'Deployed%':>11}{'#Pos':>6}{'State':>8}{'Δ NAV(B)':>11}")
print("-"*70)

if nav_log:
    log_df = pd.DataFrame(nav_log, columns=["time","cash","n_pos","deployed_pct","state"])
    log_df["time"] = pd.to_datetime(log_df["time"])
    log_df = log_df.merge(nav_df[["time","nav"]], on="time", how="left")
    log_df = log_df.sort_values("time").reset_index(drop=True)
    log_df["delta_nav"] = log_df["nav"] - INIT_NAV

    # Sample: month-end + first day + last day
    log_df["yr_mo"] = log_df["time"].dt.to_period("M")
    monthly = log_df.groupby("yr_mo").tail(1)
    # Always include first day
    if len(log_df) > 0:
        sample = pd.concat([log_df.iloc[[0]], monthly]).drop_duplicates("time").sort_values("time")
    for _, r in sample.iterrows():
        print(f"{str(r['time'].date()):<12}{r['nav']/1e9:>9.3f}{r['cash']/1e9:>9.3f}"
              f"{r['deployed_pct']*100:>10.1f}%{int(r['n_pos']):>6}{int(r['state']) if pd.notna(r['state']) else '-':>8}"
              f"{r['delta_nav']/1e9:>+10.3f}")

# ─── Summary metrics ──────────────────────────────────────────────────
print(f"\n📈 SUMMARY METRICS:")
nav_in_window = nav_df[(nav_df["time"]>=pd.Timestamp(START)) & (nav_df["time"]<=pd.Timestamp(END))]
if len(nav_in_window) > 1:
    final_nav = nav_in_window["nav"].iloc[-1]
    total_ret = (final_nav / INIT_NAV - 1) * 100
    n_days = (nav_in_window["time"].iloc[-1] - nav_in_window["time"].iloc[0]).days
    yrs = n_days / 365.25
    cagr = (final_nav / INIT_NAV) ** (1/yrs) - 1 if yrs > 0 else 0
    rets = nav_in_window["nav"].pct_change().dropna()
    sharpe = rets.mean()/rets.std() * np.sqrt(252) if rets.std() > 0 else 0
    dd = ((nav_in_window["nav"] - nav_in_window["nav"].cummax()) / nav_in_window["nav"].cummax()).min()

    print(f"  Period: {nav_in_window['time'].iloc[0].date()} → {nav_in_window['time'].iloc[-1].date()} ({n_days} days)")
    print(f"  Init NAV:   {INIT_NAV/1e9:>10.3f} tỷ VND")
    print(f"  Final NAV:  {final_nav/1e9:>10.3f} tỷ VND")
    print(f"  Total Ret:  {total_ret:>+10.2f}%")
    print(f"  Annualized: {cagr*100:>+10.2f}% CAGR")
    print(f"  Sharpe:     {sharpe:>10.2f}")
    print(f"  Max DD:     {dd*100:>+10.2f}%")
    print(f"  Trades:     {len(trades_df):>10d}")
    if len(trades_df) > 0:
        wr = (trades_df["ret_net"] > 0).mean()*100 if "ret_net" in trades_df.columns else (trades_df["ret"]>0).mean()*100
        avg_ret = trades_df.get("ret_net", trades_df.get("ret", pd.Series([0]))).mean()*100
        avg_hold = trades_df["days_held"].mean()
        print(f"  Win Rate:   {wr:>10.1f}%")
        print(f"  Avg Trade:  {avg_ret:>+10.2f}%")
        print(f"  Avg Hold:   {avg_hold:>10.1f} days")

# Save outputs
trades_df.to_csv("data/sim_v11_jun2025_trades.csv", index=False)
nav_df.to_csv("data/sim_v11_jun2025_nav.csv", index=False)
if nav_log:
    pd.DataFrame(nav_log).to_csv("sim_v11_jun2025_navlog.csv", index=False)
print(f"\n💾 Saved: sim_v11_jun2025_trades.csv, sim_v11_jun2025_nav.csv, sim_v11_jun2025_navlog.csv")
