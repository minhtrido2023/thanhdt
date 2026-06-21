#!/usr/bin/env python3
"""
test_ba_v11_lagged_factor.py — integrate LAGGED_POS factor into BA v11
======================================================================
Modify SIGNAL_V10 signals post-pull:
  BASELINE   : no change (BA v11 vanilla)
  BONUS      : ta += 5 if prior_avg_post_good ≥ 8% AND prior_n_good ≥ 4
  BLACK      : drop rows where prior_avg_post_good < 0 AND prior_n_good ≥ 4
  BOTH       : bonus + black combined

Uses simulate_holistic_nav canonical: 50/50 BAL+VN30, max_pos=10, hold=45d,
stop=-20%, slip=0.1%, sec_lim Fin/RE max=4, 50B init.

prior_avg_post_good is computed rolling (no lookahead) from earnings_events_classified.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq, VNI_QUERY, START_DATE, END_DATE
from test_round14_stability import SIGNAL_V10

TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
OOS_START = pd.Timestamp("2024-01-01")
BONUS_PTS = 5
BLACK_THR_GOOD = 0.0   # prior_avg_post_good < 0% → blacklist
N_GOOD_MIN_FOR_FILTER = 4

# ─── 1. Build rolling profile lookup (no lookahead) ──────────────────────
print("[1] Building rolling prior_avg_post_good lookup ...", flush=True)
ev = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["prior_n_good"] = 0
ev["prior_avg_post_good"] = np.nan

for tk, g in ev.groupby("ticker"):
    idxs = g.index.tolist()
    pre_n_good = 0; pre_sum_post = 0.0
    for row_idx in idxs:
        row = ev.loc[row_idx]
        ev.at[row_idx, "prior_n_good"] = pre_n_good
        if pre_n_good > 0:
            ev.at[row_idx, "prior_avg_post_good"] = pre_sum_post / pre_n_good
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15:
            pre_n_good += 1
            pre_sum_post += row["post_ret"]

print(f"  Events: {len(ev):,}")
print(f"  Events with prior_n_good >= {N_GOOD_MIN_FOR_FILTER}: {(ev['prior_n_good']>=N_GOOD_MIN_FOR_FILTER).sum():,}")

# Build forward-fill table per (ticker, date): valid from Release_Date onwards
ev_lookup = ev[["ticker","Release_Date","prior_n_good","prior_avg_post_good"]].copy()
ev_lookup = ev_lookup.rename(columns={"Release_Date":"time"})
print(f"  Lookup table: {len(ev_lookup):,} rows")

# ─── 2. Load BA v11 SIGNAL_V10 + VNI ─────────────────────────────────────
print("\n[2] Loading BA v11 signals (this may take 2-3 min) ...", flush=True)
sig_cache = "data/ba_v11_sig_cache.pkl"
if os.path.exists(sig_cache):
    with open(sig_cache, "rb") as f: sig = pickle.load(f)
    print(f"  Loaded cache: {len(sig):,} signals")
else:
    sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    with open(sig_cache, "wb") as f: pickle.dump(sig, f)
    print(f"  Pulled + cached: {len(sig):,} signals")

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

# ─── 3. Merge prior_avg_post_good into signals (as-of) ───────────────────
print("\n[3] Merging rolling profile into signals ...", flush=True)
sig = sig.sort_values(["time","ticker"]).reset_index(drop=True)
ev_lookup = ev_lookup.sort_values(["time","ticker"]).reset_index(drop=True)
sig_merged = pd.merge_asof(sig, ev_lookup, on="time", by="ticker", direction="backward")
print(f"  Signals merged: {len(sig_merged):,}, with prior data: {sig_merged['prior_n_good'].notna().sum():,}")

# ─── 4. Helper to build sec_map + top30 (shared across runs) ─────────────
sec_map = bq("""SELECT DISTINCT t.ticker,
                CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
            """).set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
                WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
                AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
                GROUP BY t.ticker
                ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

def apply_variant(sig_in, variant):
    """Return modified signals for variant: BASELINE | BONUS | BLACK | BOTH."""
    s = sig_in.copy()
    if variant == "BASELINE":
        return s
    # qualifier flags
    has_prior = (s["prior_n_good"] >= N_GOOD_MIN_FOR_FILTER) & s["prior_avg_post_good"].notna()
    is_good   = has_prior & (s["prior_avg_post_good"] >= 8.0)
    is_bad    = has_prior & (s["prior_avg_post_good"] < BLACK_THR_GOOD)
    if variant in ("BONUS","BOTH"):
        s.loc[is_good, "ta"] = s.loc[is_good, "ta"] + BONUS_PTS
    if variant in ("BLACK","BOTH"):
        s = s[~is_bad].copy()
    return s

def run_variant(variant, sig_in):
    print(f"\n{'='*70}\n  RUN: {variant}\n{'='*70}")
    s = apply_variant(sig_in, variant)
    print(f"  Signals after variant: {len(s):,}")
    if variant in ("BONUS","BOTH"):
        b = ((s["prior_n_good"] >= N_GOOD_MIN_FOR_FILTER) & (s["prior_avg_post_good"] >= 8.0)).sum()
        print(f"  Bonus applied to: {b:,} rows")
    if variant in ("BLACK","BOTH"):
        print(f"  Black filtered out: ~{len(sig_in) - len(s):,} rows")

    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in s.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in s.iterrows()}

    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    print("  Sim BAL+Fin/RE-max-4 (50B) ...", flush=True)
    nav_bal, trades_bal = simulate(s, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    print("  Sim VN30_BAL (50B) ...", flush=True)
    s_vn30 = s[s["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, trades_vn30 = simulate(s_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    return ba_nav, len(trades_bal), len(trades_vn30)

# ─── 5. Run 4 variants ───────────────────────────────────────────────────
results = {}
variants = ["BASELINE", "BONUS", "BLACK", "BOTH"]
trade_counts = {}
for v in variants:
    nav, tb, tv = run_variant(v, sig_merged)
    results[v] = nav
    trade_counts[v] = (tb, tv)

# ─── 6. Metrics ──────────────────────────────────────────────────────────
def window_metrics(nav, start, end):
    sub = nav[(nav.index >= start) & (nav.index <= end)]
    if len(sub) < 30: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((sub - sub.cummax()) / sub.cummax()).min()
    cal = cagr / abs(dd) if dd < 0 else 0
    return {"cagr": cagr*100, "sharpe": sharpe, "mdd": dd*100, "calmar": cal, "wealth": sub.iloc[-1]/sub.iloc[0]}

def vni_metrics_window(vni, start, end):
    sub = vni[(vni["time"]>=start) & (vni["time"]<=end)].copy()
    if len(sub) < 30: return None
    sub["nav"] = sub["Close"] / sub["Close"].iloc[0]
    return window_metrics(sub.set_index("time")["nav"], start, end)

periods = [
    ("FULL 2014-2026",     results["BASELINE"].index.min(), results["BASELINE"].index.max()),
    ("OOS 2024-2026",      OOS_START,                       results["BASELINE"].index.max()),
    ("Pre-OOS 2014-19",    pd.Timestamp("2014-01-01"),      pd.Timestamp("2019-12-31")),
    ("Mid 2018-2023",      pd.Timestamp("2018-01-01"),      pd.Timestamp("2023-12-31")),
    ("Y2022",              pd.Timestamp("2022-01-01"),      pd.Timestamp("2022-12-31")),
]

print("\n" + "="*120)
print("  BA v11 + LAGGED factor integration test (canonical 50/50 BAL+VN30)")
print("="*120)
print(f"  Trade counts (BAL/VN30): " + " | ".join(f"{v}={tb}/{tv}" for v,(tb,tv) in trade_counts.items()))
print()
print(f"  {'Period':<22}{'Variant':<12}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}{'Δ CAGR':>10}")
print("  " + "-"*95)
for label, st, en in periods:
    base_m = window_metrics(results["BASELINE"], st, en)
    vni_m  = vni_metrics_window(vni, st, en)
    for v in variants:
        m = window_metrics(results[v], st, en)
        if not m: continue
        dlt = m["cagr"] - base_m["cagr"] if v != "BASELINE" else 0.0
        print(f"  {label:<22}{v:<12}{m['cagr']:>+7.2f}{m['sharpe']:>+8.2f}{m['mdd']:>+8.2f}{m['calmar']:>+8.2f}{m['wealth']:>+8.2f}{dlt:>+9.2f}")
    if vni_m:
        print(f"  {label:<22}{'VNI':<12}{vni_m['cagr']:>+7.2f}{vni_m['sharpe']:>+8.2f}{vni_m['mdd']:>+8.2f}{vni_m['calmar']:>+8.2f}{vni_m['wealth']:>+8.2f}")
    print()

# Save NAVs
combo = pd.DataFrame({v: results[v] for v in variants})
combo.to_csv("data/ba_v11_lagged_factor_nav.csv")
print("Saved: ba_v11_lagged_factor_nav.csv")
