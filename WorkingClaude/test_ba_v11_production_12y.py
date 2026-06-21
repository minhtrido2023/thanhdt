#!/usr/bin/env python3
"""
test_ba_v11_production_12y.py — Re-run BA v11 production stack on 12y backtest

Stack (matching sim_v11_for_analyzer.py production config):
  - SIGNAL_V11_UNIFIED (SV_TIGHT Fresh-Q built-in)
  - P3 COMPOSITE overheat filter (block buys when state=5 OR VNI/MA200>1.30)
  - TIER_BAL = MEGA, MOMENTUM, MOMENTUM_N, MOMENTUM_S, DEEP_VALUE_RECOVERY
  - 50/50 split: 25B BAL book + 25B VN30 book
  - V6 ETF parking (70% cash → VN30 in NEUTRAL state 3)
  - max_pos=10, hold=45d, stop=-20%, slip=0.1%, sec_lim Fin/RE max=4
  - T+1 realistic open execution (default in simulate_holistic_nav)

Period: 2014-01-01 → 2026-05-15 (full 12y+)
Init NAV: 50B (25B per book)
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq
# Extract SIGNAL_V11_UNIFIED + VNI_QUERY_UNIFIED from sim_v11_for_analyzer (without running it)
import re
with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
SIGNAL_V11_UNIFIED = _extract("SIGNAL_V11_UNIFIED")
VNI_QUERY_UNIFIED  = _extract("VNI_QUERY_UNIFIED")
assert SIGNAL_V11_UNIFIED and VNI_QUERY_UNIFIED, "Failed to extract SQL constants"

START_DATE = "2014-01-01"
END_DATE   = "2026-05-15"
TOTAL_NAV  = 50_000_000_000
BOOK_NAV   = TOTAL_NAV / 2

TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
DEPOSIT = 0.01
ETF_STATES = {3: 0.7}  # 70% idle cash → VN30 ETF in NEUTRAL state
OOS_START = pd.Timestamp("2024-01-01")

print("="*100)
print(f"  V11 PRODUCTION STACK — 12y backtest")
print(f"  Period: {START_DATE} → {END_DATE} | NAV: {TOTAL_NAV/1e9:.0f}B (25B+25B books)")
print(f"  Stack: SIGNAL_V11_UNIFIED + P3 overheat + V6 ETF + TIER_BAL")
print("="*100)

# ─── 1. Load signals ─────────────────────────────────────────────────────
import pickle
sig_cache = "ba_v11_unified_12y_sig.pkl"
if os.path.exists(sig_cache):
    with open(sig_cache, "rb") as f: sig = pickle.load(f)
    print(f"[1] Loaded signal cache: {len(sig):,} rows")
else:
    print("[1] Loading SIGNAL_V11_UNIFIED (will take 3-5 min for 12y)...")
    sig = bq(SIGNAL_V11_UNIFIED.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    with open(sig_cache, "wb") as f: pickle.dump(sig, f)
    print(f"  Pulled + cached: {len(sig):,} rows ({sig['time'].min().date()} → {sig['time'].max().date()})")

# Tier distribution check
print(f"  Play_type distribution (top 10):")
print(sig["play_type"].value_counts().head(10).to_string())

# ─── 2. P3 COMPOSITE overheat filter ─────────────────────────────────────
print("\n[2] Computing P3 COMPOSITE overheat dates ...")
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
# Join state5
state5 = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state5["time"] = pd.to_datetime(state5["time"])
vni_full = vni_full.merge(state5, on="time", how="left")
vni_full["state"] = vni_full["state"].ffill()
vni_full["overheat"] = ((vni_full["Close"]/vni_full["MA200"] > 1.30)
                        & ((vni_full["state"] == 5) | (vni_full["D_RSI"] > 0.75)))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
print(f"  Overheat days: {len(overheat_dates)}")

# Apply P3 — block BUY tiers on overheat dates
mask = sig["time"].isin(overheat_dates) & sig["play_type"].isin(BUY_TIERS_V11)
n_blocked = mask.sum()
sig.loc[mask, "play_type"] = "AVOID_overheated"
print(f"  Blocked {n_blocked:,} signals via P3 overheat filter")

# ─── 3. Common data ──────────────────────────────────────────────────────
print("\n[3] Loading prices + universe + state ...")
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY_UNIFIED.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
vn30_underlying = dict(zip(vni["time"], vni["Close"]))
print(f"  {len(vni_dates)} trading sessions")

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

# Forward-fill state
state_by_date = dict(zip(state5["time"], state5["state"]))
state_by_date_ff = {}
last_state = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_state = s
    state_by_date_ff[d] = last_state

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# ─── 4. BOOK A — BAL+Fin/RE-max-4 25B with V6 ETF ────────────────────────
print("\n[4] Running BOOK A — BAL+Fin/RE-max-4 (25B) + V6 ETF (70% cash → VN30 in NEUTRAL) ...")
nav_bal, trades_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    **LIQ_FULL, name="BAL")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
print(f"  Closed trades: {len(trades_bal)}")

# ─── 5. BOOK B — VN30_BAL 25B with V6 ETF ────────────────────────────────
print("\n[5] Running BOOK B — VN30_BAL (25B) + V6 ETF ...")
sig_vn30 = sig[sig["ticker"].isin(top30)].copy()
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    **LIQ_VN30, name="VN30")
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
print(f"  Closed trades: {len(trades_vn30)}")

# ─── 6. Combine + metrics ────────────────────────────────────────────────
print("\n[6] Computing metrics ...")
nav_bal_s = nav_bal.set_index("time")["nav"]
nav_vn30_s = nav_vn30.set_index("time")["nav"]
common = nav_bal_s.index.intersection(nav_vn30_s.index)
nav_total = nav_bal_s.loc[common] + nav_vn30_s.loc[common]
nav_norm = nav_total / TOTAL_NAV  # normalize starting at 1.0
nav_norm.to_csv("ba_v11_production_12y_nav.csv")
print(f"  Final NAV: {nav_total.iloc[-1]/1e9:.2f}B (start 50B)  →  Wealth multiple: {nav_norm.iloc[-1]:.2f}x")

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
    ("FULL 2014-2026",  nav_norm.index.min(),    nav_norm.index.max()),
    ("OOS 2024-2026",   OOS_START,                nav_norm.index.max()),
    ("Pre-OOS 2014-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-2023",   pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2022",           pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1 2026",         pd.Timestamp("2025-12-30"), nav_norm.index.max()),
]

print("\n" + "="*120)
print("  BA V11 PRODUCTION STACK — 12y CANONICAL")
print("="*120)
print(f"  Trade counts: BAL={len(trades_bal)} / VN30={len(trades_vn30)}")
print()
hdr = f"  {'Period':<22}{'Source':<12}{'CAGR%':>9}{'Sharpe':>9}{'MaxDD%':>10}{'Calmar':>9}{'Wealth':>9}"
print(hdr); print("  " + "-"*len(hdr))
for label, st, en in periods:
    m = window_metrics(nav_norm, st, en)
    vm = vni_metrics_window(vni, st, en)
    if not m: continue
    print(f"  {label:<22}{'BA v11':<12}{m['cagr']:>+8.2f}{m['sharpe']:>+9.2f}{m['mdd']:>+9.2f}{m['calmar']:>+9.2f}{m['wealth']:>+9.2f}")
    if vm:
        print(f"  {label:<22}{'VNI B&H':<12}{vm['cagr']:>+8.2f}{vm['sharpe']:>+9.2f}{vm['mdd']:>+9.2f}{vm['calmar']:>+9.2f}{vm['wealth']:>+9.2f}")
        print(f"  {label:<22}{'Alpha':<12}{m['cagr']-vm['cagr']:>+8.2f}pp")
    print()

print("Saved: ba_v11_production_12y_nav.csv")
