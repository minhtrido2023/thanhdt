#!/usr/bin/env python3
"""
test_state_var_with_p3.py
==========================
Combine STATE_VAR (Fresh-Q in BEAR/NEUTRAL only) with P3 (VNI overheated filter)
and other variants to find the BEST production stack.

Variants:
  V0: baseline (no filter, no P3)
  V1: STATE_VAR only (Fresh-Q 60d in state 1/2/3)
  V2: P3 only (skip bull buys when VNI/MA200 > 1.30)
  V3: STATE_VAR + P3 (both)
  V4: STATE_VAR_TIGHT_BEAR (30d in state 1, 60d in state 2/3) + P3
  V5: STATE_VAR + P3 + DD-cap exit (-15% trailing portfolio DD → reduce to 0)

Test on canonical 50/50 BAL+VN30 sim, 2014-2026.
Periods: FULL, OOS 2024-2026, Pre-OOS 2014-19.
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
from signal_v10_sql import SIGNAL_V10  # pure SQL constant (no side effects)

CACHE_FILE = "data/test_state_p3_cache.pkl"
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
OOS_START = pd.Timestamp("2024-01-01")

# ─── Load signals + Release_Date data (with cache) ────────────────────
if os.path.exists(CACHE_FILE):
    print("Loading cached signals + Release_Date ...")
    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)
    sig = cache["sig"]; vni = cache["vni"]; sec_map = cache["sec_map"]; top30 = cache["top30"]
    state_by_date = cache["state_by_date"]
    overheated_dates = cache["overheated_dates"]
else:
    print("Loading signals from BQ ...")
    sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} signal rows")

    print("Loading Release_Date ...")
    releases = bq(f"""
SELECT tf.ticker, tf.Release_Date
FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY tf.ticker, tf.Release_Date
""")
    releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
    release_by_ticker = releases.groupby("ticker")["Release_Date"].apply(sorted).to_dict()

    import bisect
    print("Computing days_since_release per signal row ...")
    ds = np.empty(len(sig))
    ticker_arr = sig["ticker"].values
    time_arr = sig["time"].values
    for i in range(len(sig)):
        arr = release_by_ticker.get(ticker_arr[i])
        if not arr: ds[i] = np.nan; continue
        idx = bisect.bisect_right(arr, pd.Timestamp(time_arr[i]))
        if idx == 0: ds[i] = np.nan; continue
        ds[i] = (pd.Timestamp(time_arr[i]) - arr[idx-1]).days
    sig["days_since_release"] = ds

    print("Loading VNI + computing overheated dates ...")
    vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_sorted = vni.sort_values("time").reset_index(drop=True)
    vni_sorted["MA200"] = vni_sorted["Close"].rolling(200, min_periods=200).mean()
    vni_sorted["ratio"] = vni_sorted["Close"] / vni_sorted["MA200"]
    overheated_dates = set(vni_sorted[vni_sorted["ratio"] > 1.30]["time"])
    print(f"  Overheated days: {len(overheated_dates)}")

    sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                    FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
                    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                """).set_index("ticker")["s"].to_dict()
    top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
                    WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
                    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                    GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

    print("Loading state5 ...")
    state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
                    WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
    state_df["time"] = pd.to_datetime(state_df["time"])
    state_by_date = dict(zip(state_df["time"], state_df["state"]))

    print(f"Caching → {CACHE_FILE}")
    with open(CACHE_FILE, "wb") as f:
        pickle.dump({"sig":sig, "vni":vni, "sec_map":sec_map, "top30":top30,
                     "state_by_date":state_by_date, "overheated_dates":overheated_dates}, f)

vni_dates = sorted(vni["time"].unique())

# ─── Variants ────────────────────────────────────────────────────────────
BUY_PLAY_TYPES = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                   "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}

def apply_state_var(s, threshold_per_state=None):
    """STATE_VAR filter: Fresh-Q in state 1/2/3 only. Optional state-specific thresholds."""
    if threshold_per_state is None:
        threshold_per_state = {1:60, 2:60, 3:60}  # uniform 60d
    s = s.copy()
    s["state"] = s["time"].map(state_by_date)
    # In BULL (state 4,5): keep all
    keep = s["state"].isin([4, 5])
    # In state 1/2/3: require fresh quarterly
    has_release = s["days_since_release"].notna()
    for state, max_days in threshold_per_state.items():
        in_state = (s["state"] == state) & has_release & (s["days_since_release"] <= max_days)
        keep = keep | in_state
    return s[keep].copy()

def apply_p3(s):
    """P3: block new bull buys on overheated days (VNI/MA200 > 1.30)."""
    s = s.copy()
    mask = s["time"].isin(overheated_dates) & s["play_type"].isin(BUY_PLAY_TYPES)
    s.loc[mask, "play_type"] = "AVOID_overheated"
    return s


def build_variant(label, transform_fn):
    print(f"\n{'='*70}\n  Building variant: {label}\n{'='*70}", flush=True)
    s = transform_fn(sig)
    print(f"  signals after filter: {len(s):,} (orig {len(sig):,})")
    return s


def run_sim(label, sig_v):
    """Run canonical 50/50 BAL+VN30 with given signals."""
    print(f"  Running {label} ...", flush=True)
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_v.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_v.iterrows()}
    LIQ_FULL = {"liquidity_volume_pct":0.20, "max_fill_days":5,
                "liquidity_lookup":liq_map, "exit_slippage_tiered":True}

    nav_bal, trades_bal = simulate(sig_v, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    sig_vn30 = sig_v[sig_v["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k:v for k,v in liq_map.items() if k[0] in top30}
    LIQ_V30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_V30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    return ba_nav, len(trades_bal)


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

# ─── Define and run all variants ────────────────────────────────────────
VARIANTS = {
    "V0 baseline":         lambda s: s,
    "V1 STATE_VAR":        lambda s: apply_state_var(s),
    "V2 P3 only":          apply_p3,
    "V3 STATE_VAR + P3":   lambda s: apply_p3(apply_state_var(s)),
    "V4 SV_TIGHT(30/60/60)+P3": lambda s: apply_p3(apply_state_var(s, {1:30, 2:60, 3:60})),
    "V5 SV_TIGHT_ALL(30)+P3":    lambda s: apply_p3(apply_state_var(s, {1:30, 2:30, 3:30})),
    "V6 SV_LOOSE_NEUTRAL(60/60/90)+P3": lambda s: apply_p3(apply_state_var(s, {1:60, 2:60, 3:90})),
}

results = {}
for label, fn in VARIANTS.items():
    sig_v = build_variant(label, fn)
    nav, ntr = run_sim(label, sig_v)
    results[label] = (nav, ntr)

# ─── Report ─────────────────────────────────────────────────────────────
periods = [
    ("FULL 2014-2026",  pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)),
    ("OOS 2024-2026",   OOS_START,                 pd.Timestamp(END_DATE)),
    ("Pre-OOS 2014-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
]

print("\n" + "═"*100)
print("  RESULTS: STATE_VAR × P3 combinations")
print("═"*100)
for plabel, st, en in periods:
    print(f"\n{'='*60}\n  {plabel}\n{'='*60}")
    print(f"  {'Variant':<38}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Trades':>8}")
    print("  " + "-"*79)
    base_m = window_metrics(results["V0 baseline"][0], st, en)
    for label, (nav, ntr) in results.items():
        m = window_metrics(nav, st, en)
        if not m: continue
        delta = ""
        if label != "V0 baseline" and base_m:
            delta = f"  Δ={m['cagr']-base_m['cagr']:+.2f}/{m['sharpe']-base_m['sharpe']:+.2f}"
        print(f"  {label:<38}{m['cagr']:>8.2f}{m['sharpe']:>8.2f}{m['mdd']:>9.1f}"
              f"{m['calmar']:>8.2f}{ntr:>8d}{delta}")

# Save NAVs
pd.DataFrame({k: v[0] for k, v in results.items()}).to_csv("data/ba_state_p3_combinations.csv")
print("\nSaved ba_state_p3_combinations.csv")
