# -*- coding: utf-8 -*-
"""
analyze_us_vn_linkage.py
========================
Quantify US market shock → VN contagion. Identify which US signals best predict
VN drawdowns (esp. 2008 GFC, 2020 COVID, 2022 rate hikes).

Tested US shock signals:
  - SPX 60d return < -X%
  - SPX 1Y drawdown < -X%
  - VIX > X
  - VIX / VIX_252d_MA ratio > X

Output: us_shock_signal_analysis.csv + console report on predictive power.
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
import numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

print("="*70); print("US-VN Linkage Analysis"); print("="*70)

# Load
us = pd.read_csv(os.path.join(WORKDIR, "us_market_history.csv"))
us["time"] = pd.to_datetime(us["time"])
vni = pd.read_pickle(os.path.join(WORKDIR, "_cache_vnindex_2000_now.pkl"))
vni["time"] = pd.to_datetime(vni["time"])

print(f"\n[1] Data: US {len(us)} rows | VN {len(vni)} rows")

# Align by date (VN has fewer trading days due to TET etc.)
# Match VN day to most-recent US day (US might be ahead due to time zone)
us_idx = us.set_index("time")
vn_join = vni[["time", "Close"]].copy().rename(columns={"Close":"vni_close"})
vn_join["vni_close"] = pd.to_numeric(vn_join["vni_close"], errors="coerce")
vn_join = vn_join.sort_values("time").reset_index(drop=True)

# For each VN date, use the most recent US date ≤ VN date - 1 (US closes before VN open next day)
us_dates = sorted(us["time"].tolist())
def nearest_us(t):
    target = t - pd.Timedelta(days=1)
    # binary search
    import bisect
    idx = bisect.bisect_right(us_dates, target)
    if idx == 0: return None
    return us_dates[idx-1]
vn_join["us_date"] = vn_join["time"].apply(nearest_us)
vn_join = vn_join.merge(us, left_on="us_date", right_on="time", how="left", suffixes=("","_us"))
vn_join = vn_join.drop(columns=["time_us", "us_date"]).rename(columns={"time":"time"})

# VN drawdown 60d
vn_join["vni_ret_60d"] = vn_join["vni_close"] / vn_join["vni_close"].shift(60) - 1
vn_join["vni_max_1y"] = vn_join["vni_close"].rolling(252, min_periods=60).max()
vn_join["vni_dd_1y"] = vn_join["vni_close"] / vn_join["vni_max_1y"] - 1

print(f"  After merge: {len(vn_join)} VN days with US data")

# ─────────────────────────────────────────────────────────────────────
# [2] Notable historical US shocks
# ─────────────────────────────────────────────────────────────────────
print("\n[2] Notable US shock episodes (VIX > 30 OR SPX_DD_1Y < -15%)")
shocks = vn_join[(vn_join["vix"] > 30) | (vn_join["spx_dd_1y"] < -0.15)].copy()
shocks["regime"] = "unknown"
shocks.loc[(shocks["time"] >= "2008-01-01") & (shocks["time"] <= "2009-06-30"), "regime"] = "2008_GFC"
shocks.loc[(shocks["time"] >= "2011-06-01") & (shocks["time"] <= "2011-12-31"), "regime"] = "2011_euro"
shocks.loc[(shocks["time"] >= "2015-08-01") & (shocks["time"] <= "2016-02-29"), "regime"] = "2015_China"
shocks.loc[(shocks["time"] >= "2018-10-01") & (shocks["time"] <= "2019-01-31"), "regime"] = "2018_trade_war"
shocks.loc[(shocks["time"] >= "2020-02-15") & (shocks["time"] <= "2020-06-30"), "regime"] = "2020_COVID"
shocks.loc[(shocks["time"] >= "2022-01-01") & (shocks["time"] <= "2022-12-31"), "regime"] = "2022_rate_hike"
print(f"  Total US-shock days: {len(shocks)}")
print(f"  By regime:")
regimes = shocks.groupby("regime").size().sort_values(ascending=False)
for r, c in regimes.items():
    print(f"    {r:<18}: {c:>4} days")

# ─────────────────────────────────────────────────────────────────────
# [3] US shock → VN drawdown correlation
# ─────────────────────────────────────────────────────────────────────
print("\n[3] During US-shock episodes, what happened to VN?")
for regime in ["2008_GFC", "2011_euro", "2015_China", "2018_trade_war", "2020_COVID", "2022_rate_hike"]:
    s = shocks[shocks["regime"] == regime]
    if len(s) == 0: continue
    # VN performance during the shock window
    start_date = s["time"].min(); end_date = s["time"].max()
    vn_window = vn_join[(vn_join["time"] >= start_date) & (vn_join["time"] <= end_date)]
    if len(vn_window) == 0: continue
    vn_total_ret = vn_window["vni_close"].iloc[-1] / vn_window["vni_close"].iloc[0] - 1
    vn_dd_window = ((vn_window["vni_close"] - vn_window["vni_close"].cummax()) / vn_window["vni_close"].cummax()).min()
    spx_total = s["spx_close"].iloc[-1] / s["spx_close"].iloc[0] - 1
    vix_peak = s["vix"].max()
    print(f"  {regime}: {start_date.date()} → {end_date.date()} ({len(s)} shock days, {len(vn_window)} VN sessions)")
    print(f"    SPX: {spx_total*100:+.1f}%  VIX peak: {vix_peak:.1f}  →  VN: {vn_total_ret*100:+.1f}%, VN DD {vn_dd_window*100:.1f}%")

# ─────────────────────────────────────────────────────────────────────
# [4] Predictive signals — IC vs VN forward 20d return
# ─────────────────────────────────────────────────────────────────────
print("\n[4] Predictive power of US signals → VN forward 20d return")
vn_join["vni_fwd20"] = vn_join["vni_close"].shift(-20) / vn_join["vni_close"] - 1

signals = {
    "spx_ret_20d":     vn_join["spx_ret_20d"],
    "spx_ret_60d":     vn_join["spx_ret_60d"],
    "spx_dd_1y":       vn_join["spx_dd_1y"],
    "spx_ma200_dev":   vn_join["spx_ma200_dev"],
    "vix":             vn_join["vix"],
    "vix_above_ma252": vn_join["vix"] - vn_join["vix_ma252"],
}

print(f"  {'Signal':<20} {'IC (Spearman)':>15} {'IC vs forward 20d VN ret':<25}")
for name, sig in signals.items():
    m = sig.notna() & vn_join["vni_fwd20"].notna()
    if m.sum() < 200: continue
    # Use rank correlation
    ic = sig[m].rank().corr(vn_join.loc[m, "vni_fwd20"].rank())
    print(f"  {name:<20} {ic:>+14.3f}")

# ─────────────────────────────────────────────────────────────────────
# [5] Threshold-based shock detection — false-BULL day check
# ─────────────────────────────────────────────────────────────────────
print("\n[5] Tam Quan failure days (2008-08-18-19) — what did US look like?")
target = vn_join[vn_join["time"].isin([pd.Timestamp("2008-08-18"), pd.Timestamp("2008-08-19")])]
for _, r in target.iterrows():
    print(f"  {r['time'].date()}: VNI {r['vni_close']:.1f}  |  "
          f"SPX 1Y DD {r['spx_dd_1y']*100:+.1f}%  60d ret {r['spx_ret_60d']*100:+.1f}%  VIX {r['vix']:.1f}")

# ─────────────────────────────────────────────────────────────────────
# [6] Proposed override rule — count fires per year
# ─────────────────────────────────────────────────────────────────────
print("\n[6] Proposed override rules — fire frequency per year")
# 3 levels
vn_join["lvl1_cap_NEUTRAL"] = (vn_join["spx_dd_1y"] < -0.10) & (vn_join["vix"] > 20)
vn_join["lvl2_cap_BEAR"]    = (vn_join["spx_dd_1y"] < -0.15) & (vn_join["vix"] > 25)
vn_join["lvl3_cap_CRISIS"]  = (vn_join["spx_dd_1y"] < -0.25) | (vn_join["vix"] > 35)

# Simplest single rule (for production)
vn_join["us_shock_bear_cap"] = (vn_join["spx_dd_1y"] < -0.15) | (vn_join["vix"] > 30)

vn_join["year"] = vn_join["time"].dt.year
print(f"  {'Year':<6} {'lvl1':>8} {'lvl2':>8} {'lvl3':>8} {'simple_bear_cap':>18}")
for y in sorted(vn_join["year"].dropna().unique()):
    sub = vn_join[vn_join["year"] == y]
    if len(sub) == 0: continue
    n_lvl1 = sub["lvl1_cap_NEUTRAL"].sum()
    n_lvl2 = sub["lvl2_cap_BEAR"].sum()
    n_lvl3 = sub["lvl3_cap_CRISIS"].sum()
    n_simple = sub["us_shock_bear_cap"].sum()
    print(f"  {int(y):<6} {n_lvl1:>8d} {n_lvl2:>8d} {n_lvl3:>8d} {n_simple:>18d}")

# Save artifact
out_path = os.path.join(WORKDIR, "us_shock_signal_analysis.csv")
vn_join[["time","vni_close","spx_close","vix","spx_ret_20d","spx_ret_60d","spx_dd_1y",
         "spx_ma200_dev","vix_ma252","vni_dd_1y",
         "lvl1_cap_NEUTRAL","lvl2_cap_BEAR","lvl3_cap_CRISIS","us_shock_bear_cap"]].to_csv(out_path, index=False)
print(f"\nSaved → {out_path}")

print("\n" + "="*70)
print("PROPOSED OVERRIDE for Tam Quan v3.1")
print("="*70)
print("Simple rule:")
print("  IF SPX 1Y drawdown < -15% OR VIX > 30:")
print("    → cap Tam Quan state at BEAR(2)")
print("Detailed rule (3 levels):")
print("  Level 1: SPX_DD_1Y<-10% AND VIX>20 → cap at NEUTRAL(3)")
print("  Level 2: SPX_DD_1Y<-15% AND VIX>25 → cap at BEAR(2)")
print("  Level 3: SPX_DD_1Y<-25% OR VIX>35  → cap at CRISIS(1)")
