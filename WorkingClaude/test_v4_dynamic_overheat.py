#!/usr/bin/env python3
"""
test_v4_dynamic_overheat.py
============================
V4 (SV_TIGHT 30/60/60 + P3 1.30) is current best. Test if DYNAMIC overheated
threshold beats static 1.30.

Variants:
  V4_BASE: static 1.30 (current best)
  V4_PERC90: 90th percentile rolling 5Y of VNI/MA200
  V4_PERC95: 95th percentile rolling 5Y
  V4_STATE_AWARE: 1.20 in state 5, 1.30 in state 4, no filter elsewhere
  V4_GRADIENT: 1.20-1.30 block 50% of weak picks; >1.30 block all
  V4_TREND: block only when ratio still rising (5d slope > 0) AND > 1.30
  V4_HIGHER: 1.40 (tighter — let market run longer)
  V4_LOWER: 1.25 (looser — defensive earlier)
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

CACHE_FILE = "data/test_state_p3_cache.pkl"
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
OOS_START = pd.Timestamp("2024-01-01")

# Load cache (from previous V4 test)
print("Loading cache ...")
with open(CACHE_FILE, "rb") as f:
    cache = pickle.load(f)
sig = cache["sig"]; vni = cache["vni"]; sec_map = cache["sec_map"]
top30 = cache["top30"]; state_by_date = cache["state_by_date"]
overheated_dates_130 = cache["overheated_dates"]

print(f"  signals={len(sig):,}, overheated 1.30 days={len(overheated_dates_130)}")

# ─── Compute dynamic VNI/MA200 ratios ──────────────────────────────────
vni_sorted = vni.sort_values("time").reset_index(drop=True)
vni_sorted["MA200"] = vni_sorted["Close"].rolling(200, min_periods=200).mean()
vni_sorted["ratio"] = vni_sorted["Close"] / vni_sorted["MA200"]

# Rolling 5Y percentiles of ratio (1260 trading days ≈ 5Y)
vni_sorted["ratio_p90_5Y"] = vni_sorted["ratio"].rolling(1260, min_periods=500).quantile(0.90)
vni_sorted["ratio_p95_5Y"] = vni_sorted["ratio"].rolling(1260, min_periods=500).quantile(0.95)

# 5-day slope: is ratio rising?
vni_sorted["ratio_5d_ago"] = vni_sorted["ratio"].shift(5)
vni_sorted["ratio_rising"] = vni_sorted["ratio"] > vni_sorted["ratio_5d_ago"]

# Build date → ratio lookup
ratio_today = dict(zip(vni_sorted["time"], vni_sorted["ratio"]))
ratio_p90 = dict(zip(vni_sorted["time"], vni_sorted["ratio_p90_5Y"]))
ratio_p95 = dict(zip(vni_sorted["time"], vni_sorted["ratio_p95_5Y"]))
ratio_rising = dict(zip(vni_sorted["time"], vni_sorted["ratio_rising"]))

# Dynamic threshold sets
def overheat_set_perc(p_col, ratio_col):
    overheat = vni_sorted[
        (vni_sorted["ratio"] > vni_sorted[p_col]) & vni_sorted[p_col].notna()
    ]["time"]
    return set(overheat)

OH_PERC90 = overheat_set_perc("ratio_p90_5Y", "ratio")
OH_PERC95 = overheat_set_perc("ratio_p95_5Y", "ratio")
OH_140 = set(vni_sorted[vni_sorted["ratio"] > 1.40]["time"])
OH_125 = set(vni_sorted[vni_sorted["ratio"] > 1.25]["time"])
OH_120 = set(vni_sorted[vni_sorted["ratio"] > 1.20]["time"])

# State-aware: combine ratio threshold with state
def overheat_state_aware(date):
    state = state_by_date.get(date)
    r = ratio_today.get(date)
    if r is None or state is None: return False
    if state == 5 and r > 1.20: return True
    if state == 4 and r > 1.30: return True
    return False

OH_STATE_AWARE = {d for d in ratio_today if overheat_state_aware(d)}

# Trend-aware: rising AND > 1.30
OH_TREND = {d for d in ratio_today
            if ratio_today.get(d, 0) > 1.30 and ratio_rising.get(d, False)}

# Gradient: yellow (1.20-1.30 — block 50% weakest), red (>1.30 — block all)
OH_YELLOW = {d for d in ratio_today if 1.20 < ratio_today.get(d, 0) <= 1.30}

print(f"\nOverheat date counts:")
print(f"  1.30 (V4 base):        {len(overheated_dates_130)}")
print(f"  1.40 (HIGHER):         {len(OH_140)}")
print(f"  1.25 (LOWER):          {len(OH_125)}")
print(f"  1.20 (LOWER-2):        {len(OH_120)}")
print(f"  PERC90 rolling 5Y:     {len(OH_PERC90)}")
print(f"  PERC95 rolling 5Y:     {len(OH_PERC95)}")
print(f"  STATE_AWARE:           {len(OH_STATE_AWARE)}")
print(f"  TREND_RISING + >1.30:  {len(OH_TREND)}")
print(f"  GRADIENT YELLOW band:  {len(OH_YELLOW)}")

# ─── Build variants ──────────────────────────────────────────────────────
BUY_PLAY_TYPES = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                   "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}

def apply_state_var(s):
    """SV_TIGHT(30/60/60): 30d state 1, 60d state 2-3, no filter state 4-5."""
    s = s.copy()
    s["state"] = s["time"].map(state_by_date)
    keep = s["state"].isin([4, 5])  # BULL: no filter
    has_release = s["days_since_release"].notna()
    keep |= (s["state"] == 1) & has_release & (s["days_since_release"] <= 30)
    keep |= (s["state"].isin([2, 3])) & has_release & (s["days_since_release"] <= 60)
    return s[keep].copy()

def apply_p3_static(s, overheat_set):
    s = s.copy()
    mask = s["time"].isin(overheat_set) & s["play_type"].isin(BUY_PLAY_TYPES)
    s.loc[mask, "play_type"] = "AVOID_overheated"
    return s

def apply_p3_gradient(s):
    """Yellow band: block bottom 50% by ta score; Red band: block all."""
    s = s.copy()
    # Red zone (>1.30): block all
    red_mask = s["time"].isin(overheated_dates_130) & s["play_type"].isin(BUY_PLAY_TYPES)
    s.loc[red_mask, "play_type"] = "AVOID_overheated_red"
    # Yellow zone (1.20-1.30): block bottom 50% by ta
    s["is_yellow"] = s["time"].isin(OH_YELLOW)
    yellow_buys = s[s["is_yellow"] & s["play_type"].isin(BUY_PLAY_TYPES)].copy()
    if len(yellow_buys) > 0:
        # Per day, rank by ta and block bottom half
        yellow_buys["ta_rank"] = yellow_buys.groupby("time")["ta"].rank(pct=True, na_option="bottom")
        block_idx = yellow_buys[yellow_buys["ta_rank"] < 0.5].index
        s.loc[block_idx, "play_type"] = "AVOID_overheated_yellow"
    s = s.drop(columns=["is_yellow"])
    return s

VARIANTS = {
    "V4_BASE (1.30 static)":      lambda s: apply_p3_static(apply_state_var(s), overheated_dates_130),
    "V4_HIGHER (1.40)":           lambda s: apply_p3_static(apply_state_var(s), OH_140),
    "V4_LOWER (1.25)":            lambda s: apply_p3_static(apply_state_var(s), OH_125),
    "V4_LOWER-2 (1.20)":          lambda s: apply_p3_static(apply_state_var(s), OH_120),
    "V4_PERC90_5Y":               lambda s: apply_p3_static(apply_state_var(s), OH_PERC90),
    "V4_PERC95_5Y":               lambda s: apply_p3_static(apply_state_var(s), OH_PERC95),
    "V4_STATE_AWARE":             lambda s: apply_p3_static(apply_state_var(s), OH_STATE_AWARE),
    "V4_TREND_RISING+>1.30":      lambda s: apply_p3_static(apply_state_var(s), OH_TREND),
    "V4_GRADIENT":                lambda s: apply_p3_gradient(apply_state_var(s)),
}

# ─── Run sim per variant ────────────────────────────────────────────────
vni_dates = sorted(vni["time"].unique())
results = {}
for label, fn in VARIANTS.items():
    print(f"\n{'='*60}\n  {label}\n{'='*60}")
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
print("  V4 BASE vs DYNAMIC OVERHEATED THRESHOLD")
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
pd.DataFrame({k: v[0] for k, v in results.items()}).to_csv("data/ba_v4_dynamic_overheat.csv")
print("\nSaved ba_v4_dynamic_overheat.csv")
