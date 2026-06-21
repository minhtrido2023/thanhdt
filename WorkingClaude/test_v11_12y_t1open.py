# -*- coding: utf-8 -*-
"""Validate V11 (V4 SV_TIGHT + P3) with T+1 Open execution on FULL 12-year backtest.

Compares:
  A) OLD timing: T+1 Close entry, T Close exit (look-ahead bias)
  B) NEW timing: T+1 Open entry + T+1 Open exit (no bias, realistic)

Period: 2014-01-01 → 2026-03-30
Stack: V11 = v10 score + SV_TIGHT Fresh-Q + P3 overheat + 50/50 BAL+VN30 + V6 ETF
"""
import os
import sys
import io

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY
from signal_v10_sql import SIGNAL_V10

START_DATE = "2014-01-01"
END_DATE = "2026-03-30"
TOTAL_NAV = 50e9
BOOK_NAV = 25e9

# Sub-periods for window analysis
PERIODS = [
    ("FULL 2014-2026",   "2014-01-01", "2026-03-30"),
    ("Pre-OOS 2014-19",  "2014-01-01", "2019-12-31"),
    ("Mid 2018-2023",    "2018-01-01", "2023-12-31"),
    ("OOS 2024-2026",    "2024-01-01", "2026-03-30"),
]

BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]

print("=" * 100)
print(f"  V11 12-year validation — OLD vs NEW (T+1 Open) timing")
print(f"  Period: {START_DATE} → {END_DATE}")
print("=" * 100)

# ─── 1. Load signals (v10 score, no V11 filters yet) ────────────────────
print("\n[1/9] Loading v10 signals (12y)…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows")

# ─── 2. Load Release_Date for SV_TIGHT ──────────────────────────────────
print("\n[2/9] Computing days_since_release…")
releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY tf.ticker, tf.Release_Date""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = releases.sort_values(["ticker", "Release_Date"]).groupby("ticker")["Release_Date"].apply(list).to_dict()

import bisect
ds = np.empty(len(sig))
ticker_arr = sig["ticker"].values
time_arr = sig["time"].values
for i in range(len(sig)):
    arr = release_by_ticker.get(ticker_arr[i])
    if not arr:
        ds[i] = np.nan; continue
    idx = bisect.bisect_right(arr, pd.Timestamp(time_arr[i]))
    if idx == 0:
        ds[i] = np.nan; continue
    ds[i] = (pd.Timestamp(time_arr[i]) - arr[idx-1]).days
sig["days_since_release"] = ds
print(f"  done")

# ─── 3. Load 5-state + overheat dates ───────────────────────────────────
print("\n[3/9] Loading 5-state + overheat dates…")
state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
vni_full["ratio"] = vni_full["Close"] / vni_full["MA200"]
vni_full["state"] = vni_full["time"].map(state_by_date)
vni_full["overheat"] = ((vni_full["ratio"] > 1.30)
                        & ((vni_full["state"] == 5) | (vni_full["D_RSI"] > 0.75)))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
print(f"  Overheat days: {len(overheat_dates)}")

# ─── 4. Apply V11 SV_TIGHT + P3 filters ─────────────────────────────────
print("\n[4/9] Applying V11 SV_TIGHT (state-conditional Fresh-Q) + P3 (overheat block)…")
sig["state"] = sig["time"].map(state_by_date)

# SV_TIGHT thresholds: state 1: 30d, state 2/3: 60d, state 4/5: no filter
def sv_tight_keep(row):
    s = row["state"]
    days = row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4, 5): return True  # no filter
    if s == 1:
        return pd.notna(days) and days <= 30
    if s in (2, 3):
        return pd.notna(days) and days <= 60
    return True

# Apply only to BA-core tiers
mask_bacore = sig["play_type"].isin(BUY_TIERS_V11)
mask_keep = mask_bacore.apply(lambda x: True) if not mask_bacore.any() else \
            (~mask_bacore) | sig.apply(sv_tight_keep, axis=1)
n_filtered = (mask_bacore & ~sig.apply(sv_tight_keep, axis=1)).sum()
sig_filtered = sig[mask_keep].copy()
print(f"  SV_TIGHT filtered {n_filtered:,} signals")

# P3 overheat
mask_p3 = sig_filtered["time"].isin(overheat_dates) & sig_filtered["play_type"].isin(BUY_TIERS_V11)
n_p3 = mask_p3.sum()
sig_filtered.loc[mask_p3, "play_type"] = "AVOID_overheated"
print(f"  P3 blocked {n_p3:,} signals")

# ─── 5. Load Open prices ─────────────────────────────────────────────────
print("\n[5/9] Loading Open prices (12y)…")
OPEN_SQL = f"""
SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL
"""
opens_df = bq(OPEN_SQL)
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"]))
               for tk, g in opens_df.groupby("ticker")}
print(f"  {len(opens_df):,} Open prices loaded")

# Compute true overnight gap stats (correctly)
def compute_overnight_gap():
    """Properly compute overnight gaps using sequential dates per ticker."""
    df = sig_filtered[["ticker", "time", "Close"]].copy()
    df["open"] = df.apply(lambda r: open_prices.get(r["ticker"], {}).get(r["time"]), axis=1)
    df = df.dropna(subset=["open"]).sort_values(["ticker", "time"])
    df["prev_close"] = df.groupby("ticker")["Close"].shift(1)
    df["gap"] = (df["open"] / df["prev_close"] - 1) * 100
    return df[df["gap"].notna()]["gap"]

print("\n[6/9] Overnight gap statistics (sanity check)…")
gaps = compute_overnight_gap()
print(f"  Sample size: {len(gaps):,}")
print(f"  Mean: {gaps.mean():+.3f}%, Median: {gaps.median():+.3f}%")
print(f"  P5={gaps.quantile(0.05):+.2f}%, P95={gaps.quantile(0.95):+.2f}%")
print(f"  % positive: {(gaps > 0).mean()*100:.1f}%")

# ─── 7. Common data ─────────────────────────────────────────────────────
print("\n[7/9] Loading universe…")
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_filtered.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_filtered.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
vn30_underlying = dict(zip(vni["time"], vni["Close"]))

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

state_ff = {}
last_s = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_s = s
    state_ff[d] = last_s

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# ─── 8. Run BOTH variants ───────────────────────────────────────────────
def run_combo(label, t1_mode):
    sig_vn30 = sig_filtered[sig_filtered["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}

    nav_b, _ = simulate(sig_filtered, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        open_prices=open_prices if t1_mode else None,
        t1_open_exec=t1_mode,
        **LIQ_FULL, name=f"{label}_BAL")

    nav_v, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        deposit_annual=0.01, state_by_date=state_ff,
        cash_etf_states={3: 0.7}, vn30_underlying=vn30_underlying,
        open_prices=open_prices if t1_mode else None,
        t1_open_exec=t1_mode,
        **LIQ_V30, name=f"{label}_VN30")

    nav_b["time"] = pd.to_datetime(nav_b["time"])
    nav_v["time"] = pd.to_datetime(nav_v["time"])
    nav_b_s = nav_b.set_index("time")["nav"]
    nav_v_s = nav_v.set_index("time")["nav"]
    common = nav_b_s.index.intersection(nav_v_s.index)
    return nav_b_s.loc[common] + nav_v_s.loc[common]


print("\n[8/9] Running A (OLD timing)…")
nav_A = run_combo("OLD", t1_mode=False)
print("        Running B (NEW T+1 Open timing)…")
nav_B = run_combo("NEW", t1_mode=True)

# ─── 9. Window metrics ──────────────────────────────────────────────────
def window_metrics(nav, label):
    rets = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets)/yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs) - 1 if yrs > 0 else 0
    sh = rets.mean()/rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((nav - nav.cummax())/nav.cummax()).min()
    cal = cagr/abs(dd) if dd < 0 else 0
    return {"label": label, "cagr_pct": cagr*100, "sharpe": sh,
            "max_dd_pct": dd*100, "calmar": cal,
            "wealth_x": nav.iloc[-1]/nav.iloc[0]}


print("\n" + "=" * 100)
print(f"  📊 12-YEAR RESULTS — V11 (V4 SV_TIGHT + P3) — OLD vs NEW")
print("=" * 100)

results = []
for plabel, ps, pe in PERIODS:
    ps_ts = pd.Timestamp(ps); pe_ts = pd.Timestamp(pe)
    sub_A = nav_A[(nav_A.index >= ps_ts) & (nav_A.index <= pe_ts)]
    sub_B = nav_B[(nav_B.index >= ps_ts) & (nav_B.index <= pe_ts)]
    if len(sub_A) < 30:
        continue
    mA = window_metrics(sub_A, f"{plabel} OLD")
    mB = window_metrics(sub_B, f"{plabel} NEW")
    results.append({"period": plabel, "A": mA, "B": mB})

print()
print(f"  {'Period':<22} {'Variant':<8} {'CAGR':>8} {'Sharpe':>7} {'DD':>8} {'Calmar':>7} {'Wealth':>9}")
print(f"  {'-'*22} {'-'*8} {'-'*8} {'-'*7} {'-'*8} {'-'*7} {'-'*9}")
for r in results:
    p = r["period"]; mA = r["A"]; mB = r["B"]
    print(f"  {p:<22} {'A) OLD':<8} {mA['cagr_pct']:>+7.2f}% {mA['sharpe']:>+7.2f} "
          f"{mA['max_dd_pct']:>+7.1f}% {mA['calmar']:>+7.2f} {mA['wealth_x']:>+7.2f}×")
    print(f"  {'':<22} {'B) NEW':<8} {mB['cagr_pct']:>+7.2f}% {mB['sharpe']:>+7.2f} "
          f"{mB['max_dd_pct']:>+7.1f}% {mB['calmar']:>+7.2f} {mB['wealth_x']:>+7.2f}×")
    dc = mB['cagr_pct'] - mA['cagr_pct']
    ds = mB['sharpe'] - mA['sharpe']
    print(f"  {'':<22} {'Δ NEW-OLD':<10} ΔCAGR {dc:+.2f}pp  ΔSharpe {ds:+.2f}  "
          f"ΔDD {mB['max_dd_pct']-mA['max_dd_pct']:+.1f}pp")
    print()

# Save
df_out = pd.DataFrame([{"period": r["period"],
                         "A_cagr": r["A"]["cagr_pct"], "A_sharpe": r["A"]["sharpe"],
                         "A_dd": r["A"]["max_dd_pct"], "A_wealth": r["A"]["wealth_x"],
                         "B_cagr": r["B"]["cagr_pct"], "B_sharpe": r["B"]["sharpe"],
                         "B_dd": r["B"]["max_dd_pct"], "B_wealth": r["B"]["wealth_x"]}
                        for r in results])
df_out.to_csv(os.path.join(WORKDIR, "data/v11_12y_t1open_validation.csv"), index=False)
print(f"  Saved: v11_12y_t1open_validation.csv")
