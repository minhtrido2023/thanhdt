#!/usr/bin/env python3
"""
test_ba_v11_lagged_v2.py — LAGGED integration on REAL BA v11 production stack
================================================================================
Baseline: BA v11 = SIGNAL_V11_UNIFIED + P3 overheat + V6 ETF + 50/50 BAL+VN30
Confirmed: 19.42% CAGR 12y (vs previously reported 15.46% which was wrong v10)

Variants tested:
  BASELINE : no LAGGED modification (= production 19.42%)
  BONUS    : ta += 5 if prior_avg_post_good ≥ 8% AND prior_n_good ≥ 4
  BLACK    : drop rows where prior_avg_post_good < 0 AND prior_n_good ≥ 4
  BOTH     : bonus + black combined
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq

# Extract SQL from sim_v11_for_analyzer.py
with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
SIGNAL_V11_UNIFIED = _extract("SIGNAL_V11_UNIFIED")
VNI_QUERY_UNIFIED  = _extract("VNI_QUERY_UNIFIED")

START_DATE = "2014-01-01"; END_DATE = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
DEPOSIT = 0.01; ETF_STATES = {3: 0.7}
OOS_START = pd.Timestamp("2024-01-01")

BONUS_PTS = 5
BLACK_THR = 0.0
N_GOOD_MIN = 4

print("="*100)
print(f"  BA V11 + LAGGED FACTOR — 12y test on PRODUCTION baseline (19.42%)")
print("="*100)

# ─── 1. Load v11 signals (from cache) ────────────────────────────────────
sig_cache = "data/ba_v11_unified_12y_sig.pkl"
with open(sig_cache, "rb") as f: sig = pickle.load(f)
print(f"[1] Loaded V11 signals: {len(sig):,} rows")

# ─── 2. Apply P3 overheat filter (same as production) ────────────────────
print("[2] Applying P3 COMPOSITE overheat filter ...")
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
state5 = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state5["time"] = pd.to_datetime(state5["time"])
vni_full = vni_full.merge(state5, on="time", how="left")
vni_full["state"] = vni_full["state"].ffill()
vni_full["overheat"] = ((vni_full["Close"]/vni_full["MA200"] > 1.30)
                        & ((vni_full["state"] == 5) | (vni_full["D_RSI"] > 0.75)))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
mask = sig["time"].isin(overheat_dates) & sig["play_type"].isin(BUY_TIERS_V11)
sig.loc[mask, "play_type"] = "AVOID_overheated"
print(f"  Blocked {mask.sum():,} signals via P3")

# ─── 3. Build rolling LAGGED profile + merge ─────────────────────────────
print("\n[3] Building rolling LAGGED profile (no lookahead) ...")
ev = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["prior_n_good"] = 0; ev["prior_avg_post_good"] = np.nan
for tk, g in ev.groupby("ticker"):
    pre_n_good = 0; pre_sum_post = 0.0
    for row_idx in g.index.tolist():
        row = ev.loc[row_idx]
        ev.at[row_idx, "prior_n_good"] = pre_n_good
        if pre_n_good > 0:
            ev.at[row_idx, "prior_avg_post_good"] = pre_sum_post / pre_n_good
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15:
            pre_n_good += 1
            pre_sum_post += row["post_ret"]

ev_lookup = ev[["ticker","Release_Date","prior_n_good","prior_avg_post_good"]].rename(columns={"Release_Date":"time"})
sig_sorted = sig.sort_values(["time","ticker"]).reset_index(drop=True)
ev_lookup_sorted = ev_lookup.sort_values(["time","ticker"]).reset_index(drop=True)
sig_merged = pd.merge_asof(sig_sorted, ev_lookup_sorted, on="time", by="ticker", direction="backward")
print(f"  Signals merged: {len(sig_merged):,}  | with prior data: {sig_merged['prior_n_good'].notna().sum():,}")

# ─── 4. Shared data ──────────────────────────────────────────────────────
vni = bq(VNI_QUERY_UNIFIED.format(start=START_DATE, end=END_DATE))
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

state_by_date = dict(zip(state5["time"], state5["state"]))
state_by_date_ff = {}
last_state = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_state = s
    state_by_date_ff[d] = last_state

def apply_variant(sig_in, variant):
    s = sig_in.copy()
    if variant == "BASELINE": return s
    has_prior = (s["prior_n_good"] >= N_GOOD_MIN) & s["prior_avg_post_good"].notna()
    is_good = has_prior & (s["prior_avg_post_good"] >= 8.0)
    is_bad  = has_prior & (s["prior_avg_post_good"] < BLACK_THR)
    if variant in ("BONUS","BOTH"):
        s.loc[is_good, "ta"] = s.loc[is_good, "ta"] + BONUS_PTS
    if variant in ("BLACK","BOTH"):
        s = s[~is_bad].copy()
    return s

def run_variant(variant):
    print(f"\n{'='*70}\n  RUN: {variant}\n{'='*70}", flush=True)
    s = apply_variant(sig_merged, variant)
    if variant in ("BONUS","BOTH"):
        b = ((s["prior_n_good"] >= N_GOOD_MIN) & (s["prior_avg_post_good"] >= 8.0)).sum()
        print(f"  Bonus applied: {b:,} rows")
    if variant in ("BLACK","BOTH"):
        print(f"  Black filtered: {len(sig_merged)-len(s):,} rows")
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in s.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in s.iterrows()}

    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    print("  Running BOOK A — BAL+Fin/RE-max-4 25B + V6 ETF ...", flush=True)
    nav_bal, trades_bal = simulate(s, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
        **LIQ_FULL, name="BAL")
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    print("  Running BOOK B — VN30_BAL 25B + V6 ETF ...", flush=True)
    s_vn30 = s[s["ticker"].isin(top30)].copy()
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, trades_vn30 = simulate(s_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
        **LIQ_VN30, name="VN30")
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    nav_bal_s = nav_bal.set_index("time")["nav"]
    nav_vn30_s = nav_vn30.set_index("time")["nav"]
    common = nav_bal_s.index.intersection(nav_vn30_s.index)
    nav_total = nav_bal_s.loc[common] + nav_vn30_s.loc[common]
    nav_norm = nav_total / TOTAL_NAV
    print(f"  Final NAV: {nav_total.iloc[-1]/1e9:.2f}B  | Trades BAL/VN30: {len(trades_bal)}/{len(trades_vn30)}")
    return nav_norm, len(trades_bal), len(trades_vn30)

# ─── 5. Run 4 variants ───────────────────────────────────────────────────
results = {}
trade_counts = {}
for v in ["BASELINE", "BONUS", "BLACK", "BOTH"]:
    nav, tb, tv = run_variant(v)
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
    ("FULL 2014-2026",  results["BASELINE"].index.min(),    results["BASELINE"].index.max()),
    ("OOS 2024-2026",   OOS_START,                          results["BASELINE"].index.max()),
    ("Pre-OOS 2014-19", pd.Timestamp("2014-01-01"),         pd.Timestamp("2019-12-31")),
    ("Mid 2018-2023",   pd.Timestamp("2018-01-01"),         pd.Timestamp("2023-12-31")),
    ("Y2022",           pd.Timestamp("2022-01-01"),         pd.Timestamp("2022-12-31")),
    ("Q1 2026",         pd.Timestamp("2025-12-30"),         results["BASELINE"].index.max()),
]

print("\n" + "="*135)
print("  BA v11 PRODUCTION + LAGGED FACTOR INTEGRATION TEST")
print("="*135)
print(f"  Trade counts (BAL/VN30): " + " | ".join(f"{v}={tb}/{tv}" for v,(tb,tv) in trade_counts.items()))
print()
print(f"  {'Period':<22}{'Variant':<12}{'CAGR%':>9}{'Sharpe':>9}{'MaxDD%':>10}{'Calmar':>9}{'Wealth':>9}{'Δ CAGR':>10}")
print("  " + "-"*110)
for label, st, en in periods:
    base_m = window_metrics(results["BASELINE"], st, en)
    vni_m  = vni_metrics_window(vni, st, en)
    for v in ["BASELINE","BONUS","BLACK","BOTH"]:
        m = window_metrics(results[v], st, en)
        if not m: continue
        dlt = m["cagr"] - base_m["cagr"] if v != "BASELINE" else 0.0
        print(f"  {label:<22}{v:<12}{m['cagr']:>+8.2f}{m['sharpe']:>+9.2f}{m['mdd']:>+9.2f}{m['calmar']:>+9.2f}{m['wealth']:>+9.2f}{dlt:>+9.2f}")
    if vni_m:
        print(f"  {label:<22}{'VNI':<12}{vni_m['cagr']:>+8.2f}{vni_m['sharpe']:>+9.2f}{vni_m['mdd']:>+9.2f}{vni_m['calmar']:>+9.2f}{vni_m['wealth']:>+9.2f}")
    print()

combo = pd.DataFrame({v: results[v] for v in ["BASELINE","BONUS","BLACK","BOTH"]})
combo.to_csv("data/ba_v11_production_lagged_nav.csv")
print("Saved: ba_v11_production_lagged_nav.csv")
