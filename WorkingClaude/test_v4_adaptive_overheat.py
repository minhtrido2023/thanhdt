#!/usr/bin/env python3
"""
test_v4_adaptive_overheat.py
=============================
Address overfit concern: test SELF-ADAPTING overheat detection mechanisms
that adjust to changing market structure WITHOUT manual re-tuning.

Approaches:
  V4_ZSCORE_2SD:  Trailing 3Y rolling mean + 2 SD (adapt to volatility regime)
  V4_ZSCORE_1.5SD: trailing 3Y mean + 1.5 SD (more sensitive)
  V4_ENSEMBLE:    Fire if ≥2 of [VNI/MA200>1.25, VNI/MA50>1.15, ratio rising 30d]
  V4_COMPOSITE:   VNI/MA200>1.30 AND (state5=5 OR RSI>75)
  V4_STATE5_BUNDLE: Use state5 transitions instead of raw ratio
                  - Block when state was 5 AND just dropped to 4 (regime weakening)
  V4_WALK_FORWARD: Recompute optimal threshold every year on trailing 5Y
                  - Mean reverts to historical optimum
  V4_BASE: static 1.30 (reference)
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE, END_DATE

CACHE_FILE = "test_state_p3_cache.pkl"
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
OOS_START = pd.Timestamp("2024-01-01")

print("Loading cache ...")
with open(CACHE_FILE, "rb") as f:
    cache = pickle.load(f)
sig = cache["sig"]; vni = cache["vni"]; sec_map = cache["sec_map"]
top30 = cache["top30"]; state_by_date = cache["state_by_date"]

# ─── Compute VNI metrics ───────────────────────────────────────────────
vni_sorted = vni.sort_values("time").reset_index(drop=True)
vni_sorted["MA200"] = vni_sorted["Close"].rolling(200, min_periods=200).mean()
vni_sorted["MA50"] = vni_sorted["Close"].rolling(50, min_periods=50).mean()
vni_sorted["ratio_200"] = vni_sorted["Close"] / vni_sorted["MA200"]
vni_sorted["ratio_50"] = vni_sorted["Close"] / vni_sorted["MA50"]

# Z-score: trailing 3Y mean + N*SD
vni_sorted["ratio_mean_3Y"] = vni_sorted["ratio_200"].rolling(750, min_periods=400).mean()
vni_sorted["ratio_sd_3Y"] = vni_sorted["ratio_200"].rolling(750, min_periods=400).std()
vni_sorted["z_score"] = (vni_sorted["ratio_200"] - vni_sorted["ratio_mean_3Y"]) / vni_sorted["ratio_sd_3Y"]
vni_sorted["thresh_1_5SD"] = vni_sorted["ratio_mean_3Y"] + 1.5 * vni_sorted["ratio_sd_3Y"]
vni_sorted["thresh_2SD"] = vni_sorted["ratio_mean_3Y"] + 2.0 * vni_sorted["ratio_sd_3Y"]

# Ratio rising 30d
vni_sorted["ratio_30d_ago"] = vni_sorted["ratio_200"].shift(30)
vni_sorted["ratio_rising_30d"] = vni_sorted["ratio_200"] > vni_sorted["ratio_30d_ago"]

# VNI RSI 14-day (Wilder)
delta = vni_sorted["Close"].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss.replace(0, np.nan)
vni_sorted["RSI"] = 100 - 100/(1+rs)

# State at each date
vni_sorted["state"] = vni_sorted["time"].map(state_by_date)
vni_sorted["state_prev"] = vni_sorted["state"].shift(1)
vni_sorted["state_was_5_now_4"] = (vni_sorted["state_prev"] == 5) & (vni_sorted["state"] <= 4)

# Walk-forward optimal threshold (yearly recalibration)
# At each year-end, find threshold in (1.20, 1.40, step 0.01) that maximizes
# "# days flagged & in top 5% of forward return drawdowns" over trailing 5Y
# (Too complex — use simplified: threshold = trailing 5Y 95th percentile)
vni_sorted["thresh_walkfwd"] = vni_sorted["ratio_200"].rolling(1260, min_periods=750).quantile(0.95)

# Build overheat date sets
OH_BASE_130 = set(vni_sorted[vni_sorted["ratio_200"] > 1.30]["time"])

OH_ZSCORE_2SD = set(vni_sorted[
    vni_sorted["thresh_2SD"].notna() & (vni_sorted["ratio_200"] > vni_sorted["thresh_2SD"])
]["time"])
OH_ZSCORE_1_5SD = set(vni_sorted[
    vni_sorted["thresh_1_5SD"].notna() & (vni_sorted["ratio_200"] > vni_sorted["thresh_1_5SD"])
]["time"])

# Ensemble: fire if ≥2 of 3 signals
vni_sorted["sig_a"] = vni_sorted["ratio_200"] > 1.25
vni_sorted["sig_b"] = vni_sorted["ratio_50"] > 1.15
vni_sorted["sig_c"] = vni_sorted["ratio_rising_30d"].fillna(False) & (vni_sorted["ratio_200"] > 1.20)
vni_sorted["n_signals"] = vni_sorted["sig_a"].astype(int) + vni_sorted["sig_b"].astype(int) + vni_sorted["sig_c"].astype(int)
OH_ENSEMBLE = set(vni_sorted[vni_sorted["n_signals"] >= 2]["time"])

# Composite: VNI/MA200 > 1.30 AND (state=5 OR RSI>75)
OH_COMPOSITE = set(vni_sorted[
    (vni_sorted["ratio_200"] > 1.30) &
    ((vni_sorted["state"] == 5) | (vni_sorted["RSI"] > 75))
]["time"])

# State5 transition: just dropped from state 5 to 4 (regime weakening from peak)
OH_STATE5_BUNDLE = set(vni_sorted[vni_sorted["state_was_5_now_4"].fillna(False)]["time"])

# Walk-forward (5Y rolling p95)
OH_WALKFWD = set(vni_sorted[
    vni_sorted["thresh_walkfwd"].notna() &
    (vni_sorted["ratio_200"] > vni_sorted["thresh_walkfwd"])
]["time"])

print(f"\nOverheat date counts (12y data):")
print(f"  V4_BASE 1.30 static:          {len(OH_BASE_130)}")
print(f"  V4_ZSCORE_2SD:                {len(OH_ZSCORE_2SD)}")
print(f"  V4_ZSCORE_1.5SD:              {len(OH_ZSCORE_1_5SD)}")
print(f"  V4_ENSEMBLE (≥2 of 3):        {len(OH_ENSEMBLE)}")
print(f"  V4_COMPOSITE (1.30 + state5 or RSI>75): {len(OH_COMPOSITE)}")
print(f"  V4_STATE5_BUNDLE (5→4 drop):  {len(OH_STATE5_BUNDLE)}")
print(f"  V4_WALK_FORWARD (5Y p95):     {len(OH_WALKFWD)}")

# ─── STATE_VAR + dynamic P3 ────────────────────────────────────────────
BUY_PLAY_TYPES = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                   "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}

def apply_state_var(s):
    s = s.copy()
    s["state"] = s["time"].map(state_by_date)
    keep = s["state"].isin([4, 5])
    has_release = s["days_since_release"].notna()
    keep |= (s["state"] == 1) & has_release & (s["days_since_release"] <= 30)
    keep |= (s["state"].isin([2, 3])) & has_release & (s["days_since_release"] <= 60)
    return s[keep].copy()

def apply_p3(s, overheat_set):
    s = s.copy()
    mask = s["time"].isin(overheat_set) & s["play_type"].isin(BUY_PLAY_TYPES)
    s.loc[mask, "play_type"] = "AVOID_overheated"
    return s

VARIANTS = {
    "V4_BASE (1.30 static)":     lambda s: apply_p3(apply_state_var(s), OH_BASE_130),
    "V4_ZSCORE_2SD (adaptive)":  lambda s: apply_p3(apply_state_var(s), OH_ZSCORE_2SD),
    "V4_ZSCORE_1.5SD (adaptive)":lambda s: apply_p3(apply_state_var(s), OH_ZSCORE_1_5SD),
    "V4_ENSEMBLE (2of3 signals)":lambda s: apply_p3(apply_state_var(s), OH_ENSEMBLE),
    "V4_COMPOSITE (1.30+regime)":lambda s: apply_p3(apply_state_var(s), OH_COMPOSITE),
    "V4_STATE5_BUNDLE (5→4)":    lambda s: apply_p3(apply_state_var(s), OH_STATE5_BUNDLE),
    "V4_WALKFWD (5Y p95 adap)":  lambda s: apply_p3(apply_state_var(s), OH_WALKFWD),
}

# ─── Run sim ────────────────────────────────────────────────────────────
vni_dates = sorted(vni["time"].unique())
results = {}
for label, fn in VARIANTS.items():
    print(f"\n{'='*60}\n  {label}\n{'='*60}", flush=True)
    s = fn(sig)
    print(f"  signals after filter: {len(s):,}")

    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in s.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in s.iterrows()}
    LIQ = {"liquidity_volume_pct":0.20, "max_fill_days":5,
           "liquidity_lookup":liq_map, "exit_slippage_tiered":True}

    nav_bal, trades_bal = simulate(s, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **LIQ)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    sig_vn30 = s[s["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k:v for k,v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ, "liquidity_lookup": liq_vn30}
    nav_vn30, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_V30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    results[label] = (ba_nav, len(trades_bal))

# ─── Report ─────────────────────────────────────────────────────────────
def window_metrics(nav, start, end):
    sub = nav[(nav.index >= start) & (nav.index <= end)]
    if len(sub) < 30: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((sub - sub.cummax()) / sub.cummax()).min()
    return {"cagr":cagr*100, "sharpe":sharpe, "mdd":dd*100,
            "calmar":cagr/abs(dd) if dd<0 else 0, "wealth":sub.iloc[-1]/sub.iloc[0]}

periods = [
    ("FULL 2014-2026",  pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)),
    ("OOS 2024-2026",   OOS_START,                 pd.Timestamp(END_DATE)),
    ("Pre-OOS 2014-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-2023",   pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
]

print("\n" + "═"*100)
print("  ADAPTIVE OVERHEAT DETECTION vs V4_BASE static 1.30")
print("═"*100)
base_label = "V4_BASE (1.30 static)"
for plabel, st, en in periods:
    print(f"\n{'='*64}\n  {plabel}\n{'='*64}")
    print(f"  {'Variant':<32}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Trades':>8}")
    print("  " + "-"*73)
    base_m = window_metrics(results[base_label][0], st, en)
    for label, (nav, ntr) in results.items():
        m = window_metrics(nav, st, en)
        if not m: continue
        delta = ""
        if label != base_label and base_m:
            delta = f"  Δ={m['cagr']-base_m['cagr']:+.2f}/{m['sharpe']-base_m['sharpe']:+.2f}"
        print(f"  {label:<32}{m['cagr']:>8.2f}{m['sharpe']:>8.2f}{m['mdd']:>9.1f}"
              f"{m['calmar']:>8.2f}{ntr:>8d}{delta}")

# Save NAVs
pd.DataFrame({k: v[0] for k, v in results.items()}).to_csv("ba_v4_adaptive_overheat.csv")
print("\nSaved ba_v4_adaptive_overheat.csv")
