#!/usr/bin/env python3
"""
test_dual_v1_v11_3variants.py
=============================
Run BA V11 production stack 12y backtest on 3 dual-system α variants
+ LIVE Tinh Tế baseline for comparison.

Adapted from test_ba_v11_production_12y.py — only difference is the
state source: instead of always reading tav2_bq.vnindex_5state, we loop
through {LIVE, α=0.4 CSV, α=0.5 CSV, α=0.6 CSV}.

Each variant uses its own state for BOTH:
  - ETF parking decision (state==3 → 70% cash → VN30 ETF)
  - P3 overheat filter (state==5 OR D_RSI>0.75 with Close/MA200>1.30)

Stack: SIGNAL_V11_UNIFIED + P3 overheat + V6 ETF + TIER_BAL + 50/50 BAL+VN30
Period: 2014-01-01 → 2026-05-15
Init: 50B (25B + 25B)
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, re, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq

with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
SIGNAL_V11_UNIFIED = _extract("SIGNAL_V11_UNIFIED")
VNI_QUERY_UNIFIED  = _extract("VNI_QUERY_UNIFIED")
assert SIGNAL_V11_UNIFIED and VNI_QUERY_UNIFIED

START_DATE = "2014-01-01"
END_DATE   = "2026-05-15"
TOTAL_NAV  = 50_000_000_000
BOOK_NAV   = TOTAL_NAV / 2
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
DEPOSIT = 0.01
ETF_STATES = {3: 0.7}
OOS_START = pd.Timestamp("2024-01-01")

# Variants to test
VARIANTS = [
    ("LIVE Tinh Tế",   "BQ"),
    ("Dual α=0.40",    "data/vnindex_5state_dual_a40_staging.csv"),
    ("Dual α=0.50",    "data/vnindex_5state_dual_a50_staging.csv"),
    ("Dual α=0.60",    "data/vnindex_5state_dual_a60_staging.csv"),
]

print("="*100)
print(f"  V11 — 4-variant test: LIVE Tinh Tế vs Dual α=0.40/0.50/0.60")
print(f"  Period: {START_DATE} → {END_DATE} | NAV: {TOTAL_NAV/1e9:.0f}B")
print("="*100)

# ─── Shared data: signals (cached) + VNI prices + sec_map + top30 ─────────
sig_cache = "data/ba_v11_unified_12y_sig.pkl"
if os.path.exists(sig_cache):
    with open(sig_cache, "rb") as f: sig = pickle.load(f)
    print(f"[shared] Loaded signal cache: {len(sig):,} rows")
else:
    print("[shared] Loading SIGNAL_V11_UNIFIED (5-10 min) ...")
    sig = bq(SIGNAL_V11_UNIFIED.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    with open(sig_cache, "wb") as f: pickle.dump(sig, f)
    print(f"  Cached: {len(sig):,} rows")

prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY_UNIFIED.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
vn30_underlying = dict(zip(vni["time"], vni["Close"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

# ─── Helper: window metrics ───────────────────────────────────────────────
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
    ("FULL 2014-2026",  pd.Timestamp("2014-01-01"), pd.Timestamp(END_DATE)),
    ("OOS 2024-2026",   OOS_START,                  pd.Timestamp(END_DATE)),
    ("Pre-OOS 2014-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-2023",   pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2022",           pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1 2026",         pd.Timestamp("2025-12-30"), pd.Timestamp(END_DATE)),
]

# ─── Run each variant ─────────────────────────────────────────────────────
results = {}

for vname, vsource in VARIANTS:
    print("\n" + "="*100)
    print(f"  VARIANT: {vname}  ({vsource})")
    print("="*100)
    # Load state for this variant
    if vsource == "BQ":
        state5 = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
        state5["time"] = pd.to_datetime(state5["time"])
    else:
        state5 = pd.read_csv(os.path.join(WORKDIR, vsource))
        state5["time"] = pd.to_datetime(state5["time"])
        state5 = state5[(state5["time"]>=START_DATE) & (state5["time"]<=END_DATE)][["time","state"]]
    print(f"  State rows: {len(state5)}")

    # State by date forward-fill
    state_by_date = dict(zip(state5["time"], state5["state"]))
    state_by_date_ff = {}
    last_state = None
    for d in vni_dates:
        s = state_by_date.get(d)
        if s is not None: last_state = s
        state_by_date_ff[d] = last_state

    # P3 overheat filter — uses THIS variant's state
    v = vni_full.merge(state5, on="time", how="left")
    v["state"] = v["state"].ffill()
    v["overheat"] = ((v["Close"]/v["MA200"] > 1.30)
                     & ((v["state"] == 5) | (v["D_RSI"] > 0.75)))
    overheat_dates = set(v[v["overheat"]]["time"])
    sig_v = sig.copy()
    mask = sig_v["time"].isin(overheat_dates) & sig_v["play_type"].isin(BUY_TIERS_V11)
    n_blocked = mask.sum()
    sig_v.loc[mask, "play_type"] = "AVOID_overheated"
    print(f"  Overheat days: {len(overheat_dates)} | Blocked signals: {n_blocked:,}")

    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    print("  Running BOOK A (BAL 25B) ...")
    nav_bal, trades_bal = simulate(sig_v, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
        **LIQ_FULL, name="BAL")
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    print("  Running BOOK B (VN30 25B) ...")
    sig_vn30 = sig_v[sig_v["ticker"].isin(top30)].copy()
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

    nav_bal_s  = nav_bal.set_index("time")["nav"]
    nav_vn30_s = nav_vn30.set_index("time")["nav"]
    common = nav_bal_s.index.intersection(nav_vn30_s.index)
    nav_total = nav_bal_s.loc[common] + nav_vn30_s.loc[common]
    nav_norm = nav_total / TOTAL_NAV
    final_b = nav_total.iloc[-1] / 1e9
    print(f"  Final NAV: {final_b:.2f}B  →  wealth × {nav_norm.iloc[-1]:.2f}")
    results[vname] = {
        "nav": nav_norm, "trades_bal": len(trades_bal), "trades_vn30": len(trades_vn30),
        "overheat_days": len(overheat_dates),
    }
    safe_name = vname.lower().replace(" ", "_").replace("=", "").replace(".", "").replace("ế","e").replace("ử","u").replace("ọ","o").replace("đ","d").replace("ị","i").replace("í","i").replace("ô","o").replace("ầ","a")
    out_csv = os.path.join(WORKDIR, f"v11_nav_{safe_name}.csv")
    nav_norm.to_csv(out_csv)

# ─── Comparison table ────────────────────────────────────────────────────
print("\n\n" + "="*120)
print("  COMPARISON: V11 production stack — LIVE vs Dual α=0.40/0.50/0.60")
print("="*120)
for label, st, en in periods:
    print(f"\n  ── {label} ──")
    print(f"    {'Variant':<18} {'CAGR%':>8} {'Sharpe':>8} {'MaxDD%':>9} {'Calmar':>8} {'Wealth':>8} {'Trades':>8} {'Overheat':>9}")
    vm = vni_metrics_window(vni, st, en)
    if vm:
        print(f"    {'VNI B&H':<18} {vm['cagr']:>+7.2f} {vm['sharpe']:>+8.2f} {vm['mdd']:>+8.2f} {vm['calmar']:>+7.2f} {vm['wealth']:>+8.2f}")
    for vname, _ in VARIANTS:
        m = window_metrics(results[vname]["nav"], st, en)
        if not m: continue
        tr = results[vname]["trades_bal"] + results[vname]["trades_vn30"]
        oh = results[vname]["overheat_days"]
        print(f"    {vname:<18} {m['cagr']:>+7.2f} {m['sharpe']:>+8.2f} {m['mdd']:>+8.2f} {m['calmar']:>+7.2f} {m['wealth']:>+8.2f} {tr:>8} {oh:>9}")
print("\n" + "="*120)
print("DONE.")
