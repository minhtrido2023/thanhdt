#!/usr/bin/env python3
"""
test_release_date_advanced.py
==============================
Deep exploration of Release_Date impact on BA-45d sim.

Current production F1 (60d, recommend_holistic.py) was validated on BAL leg only.
This script tests advanced variants on FULL canonical 50/50 BAL+VN30 config.

Variants tested:
  F0: no filter (canonical baseline)
  F1_30: very tight (30d max stale)
  F1_45: medium tight (45d)
  F1_60: current production (60d)
  F1_90: loose (90d)
  TIER_VAR: MEGA/MOMENTUM 30d, others 60d (tier-stratified)
  STATE_VAR: 60d only in state 1,2,3 (BEAR/NEUTRAL); no filter in 4,5 (BULL)
  EARN_SEASON: F1 60d, but only when in earnings season (Apr-May, Jul-Aug, Oct-Nov, Jan-Feb)
  TONEXT: filter on days_to_NEXT release (entered just before quarterly catalyst)

Compare: CAGR, Sharpe, MaxDD, Calmar at FULL 2014-2026 + OOS 2024-2026.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE, END_DATE
from test_round14_stability import SIGNAL_V10

TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
OOS_START = pd.Timestamp("2024-01-01")

# ─── Load signals + Release_Date data ──────────────────────────────────
print("Loading signals ...")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} signal rows")

print("Loading Release_Date per ticker ...")
releases = bq(f"""
SELECT tf.ticker, tf.Release_Date
FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY tf.ticker, tf.Release_Date
""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = releases.groupby("ticker")["Release_Date"].apply(sorted).to_dict()
print(f"  {len(releases):,} release dates across {len(release_by_ticker):,} tickers")

# For each signal row, compute:
# (a) days_since_release = days since most recent release on or before signal date
# (b) days_to_next_release = days until next upcoming release
import bisect
def time_release_info(ticker, signal_ts):
    arr = release_by_ticker.get(ticker)
    if not arr: return (np.nan, np.nan)
    # bisect to find most recent past release and next future release
    idx = bisect.bisect_right(arr, signal_ts)
    past = arr[idx-1] if idx > 0 else None
    nxt = arr[idx] if idx < len(arr) else None
    days_since = (signal_ts - past).days if past else np.nan
    days_to_next = (nxt - signal_ts).days if nxt else np.nan
    return (days_since, days_to_next)

print("Computing days_since/to_next per signal row (~1 min) ...")
ds = np.empty(len(sig)); dn = np.empty(len(sig))
ticker_arr = sig["ticker"].values
time_arr = sig["time"].values
for i in range(len(sig)):
    a, b = time_release_info(ticker_arr[i], pd.Timestamp(time_arr[i]))
    ds[i] = a; dn[i] = b
sig["days_since_release"] = ds
sig["days_to_next_release"] = dn
print(f"  Days_since stats: median={sig['days_since_release'].median():.0f}, "
      f"p25={sig['days_since_release'].quantile(0.25):.0f}, "
      f"p75={sig['days_since_release'].quantile(0.75):.0f}, "
      f"p90={sig['days_since_release'].quantile(0.90):.0f}")
print(f"  Days_to_next stats: median={sig['days_to_next_release'].median():.0f}, "
      f"p25={sig['days_to_next_release'].quantile(0.25):.0f}, "
      f"p75={sig['days_to_next_release'].quantile(0.75):.0f}")

# ─── Shared infrastructure ──────────────────────────────────────────────
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
            """).set_index("ticker")["s"].to_dict()

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
                WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# State 5 for state-conditional variant
state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
                WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))

def run_canonical(label, sig_filt):
    """Run canonical 50/50 BAL+VN30 sim with given (filtered) signals."""
    n_orig = len(sig)
    n_filt = len(sig_filt)
    pct_skip = (n_orig - n_filt) / n_orig * 100
    print(f"\n--- {label}  signals: {n_filt:,}  (skipped {n_orig-n_filt:,} = {pct_skip:.1f}%) ---")

    prices_f = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_filt.groupby("ticker")}
    liq_map_f = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_filt.iterrows()}
    LIQ_F = {**LIQ_FULL, "liquidity_lookup": liq_map_f}

    nav_bal, trades_bal = simulate(sig_filt, prices_f, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_F)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    sig_vn30 = sig_filt[sig_filt["ticker"].isin(top30)]
    prices_vn30 = {tk: prices_f[tk] for tk in top30 if tk in prices_f}
    liq_vn30 = {k:v for k,v in liq_map_f.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
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
    return {"cagr": cagr*100, "sharpe": sharpe, "mdd": dd*100,
            "calmar": cagr/abs(dd) if dd<0 else 0, "wealth": sub.iloc[-1]/sub.iloc[0]}


# ─── Variants ────────────────────────────────────────────────────────────
# Tier-stratified F1: MEGA/MOMENTUM tighter (30d), others loose (60d)
def tier_stratified_filter(s):
    mega_tight = ["MEGA","MOMENTUM","MOMENTUM_N"]
    mask = pd.Series(True, index=s.index)
    has_release = s["days_since_release"].notna()
    is_strict = s["play_type"].isin(mega_tight)
    # MEGA/MOMENTUM: ≤30d freshness required
    strict_ok = is_strict & has_release & (s["days_since_release"] <= 30)
    # Other tiers: ≤60d freshness required
    loose_ok = (~is_strict) & has_release & (s["days_since_release"] <= 60)
    # AVOID_* and PASS/WAIT: always pass (they don't generate buys anyway)
    non_buy = ~s["play_type"].isin(["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                                     "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY"])
    return s[strict_ok | loose_ok | non_buy].copy()

# State-conditional: F1 60d only in state 1,2,3 (BEAR/NEUTRAL)
def state_conditional_filter(s):
    s = s.copy()
    s["state_at_signal"] = s["time"].map(state_by_date)
    # In state 4,5 (BULL): no filter
    # In state 1,2,3: F1 60d
    in_bull = s["state_at_signal"].isin([4, 5])
    in_other = ~in_bull
    has_release = s["days_since_release"].notna()
    fresh = has_release & (s["days_since_release"] <= 60)
    return s[in_bull | (in_other & fresh)].copy()

# Earnings-season-only F1: 60d filter only in Apr-May, Jul-Aug, Oct-Nov, Jan-Feb
def earnings_season_filter(s):
    s = s.copy()
    s["month"] = s["time"].dt.month
    earnings_months = [1,2,4,5,7,8,10,11]
    in_season = s["month"].isin(earnings_months)
    has_release = s["days_since_release"].notna()
    fresh = has_release & (s["days_since_release"] <= 60)
    return s[(~in_season) | fresh].copy()

# To-next variant: ≤30d to next release (enter just before catalyst)
def to_next_filter(s, max_days):
    has_release = s["days_to_next_release"].notna()
    return s[has_release & (s["days_to_next_release"] <= max_days)].copy()

# ─── Run all variants ───────────────────────────────────────────────────
print("\n" + "="*100)
print("RUNNING VARIANTS (canonical 50/50 BAL+VN30)")
print("="*100)

variants = {
    "F0 baseline (no filter)":  lambda s: s,
    "F1_30 tight":              lambda s: s[s["days_since_release"].notna() & (s["days_since_release"]<=30)].copy(),
    "F1_45 medium":             lambda s: s[s["days_since_release"].notna() & (s["days_since_release"]<=45)].copy(),
    "F1_60 (prod)":             lambda s: s[s["days_since_release"].notna() & (s["days_since_release"]<=60)].copy(),
    "F1_90 loose":              lambda s: s[s["days_since_release"].notna() & (s["days_since_release"]<=90)].copy(),
    "TIER_VAR (30/60 split)":   tier_stratified_filter,
    "STATE_VAR (filter in BEAR/NEUTRAL only)": state_conditional_filter,
    "EARN_SEASON (filter in earning months only)": earnings_season_filter,
    "TONEXT_30 (≤30d to next release)": lambda s: to_next_filter(s, 30),
    "TONEXT_60 (≤60d to next release)": lambda s: to_next_filter(s, 60),
}

results = {}
for label, fn in variants.items():
    sig_f = fn(sig)
    ba_nav, n_trades = run_canonical(label, sig_f)
    results[label] = (ba_nav, n_trades)

# ─── Compare ────────────────────────────────────────────────────────────
periods = [
    ("FULL 2014-2026",  pd.Timestamp(START_DATE), pd.Timestamp(END_DATE)),
    ("OOS 2024-2026",   OOS_START,                 pd.Timestamp(END_DATE)),
    ("Pre-OOS 2014-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
]

baseline_label = "F0 baseline (no filter)"
print("\n" + "═"*100)
print("  RESULTS BY PERIOD (canonical 50/50 BAL+VN30)")
print("═"*100)

for plabel, st, en in periods:
    print(f"\n{'='*70}\n  {plabel}\n{'='*70}")
    print(f"  {'Variant':<46}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Trades':>8}")
    print("  " + "-"*87)
    base_m = window_metrics(results[baseline_label][0], st, en)
    for label, (nav, n) in results.items():
        m = window_metrics(nav, st, en)
        if not m: continue
        delta_str = ""
        if label != baseline_label and base_m:
            delta_str = f"  ΔCAGR={m['cagr']-base_m['cagr']:+.2f}, ΔSh={m['sharpe']-base_m['sharpe']:+.2f}"
        print(f"  {label:<46}{m['cagr']:>8.2f}{m['sharpe']:>8.2f}{m['mdd']:>9.1f}"
              f"{m['calmar']:>8.2f}{n:>8d}{delta_str}")

# Save
pd.DataFrame({k: v[0] for k, v in results.items()}).to_csv("ba_release_date_nav.csv")
print("\nSaved ba_release_date_nav.csv")
