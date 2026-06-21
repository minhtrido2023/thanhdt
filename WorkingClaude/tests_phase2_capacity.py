#!/usr/bin/env python3
"""
tests_phase2_capacity.py
========================
Capacity scaling for Hybrid v11 at multiple NAV sizes.

Tests: 1B / 50B / 100B / 200B / 500B
  - BA v11 (BA v10 + P3): rerun BAL + VN30 sims at each size
  - LH gated: rerun at each size (uses same liquidity caps in simulate_lh_nav)
  - Hybrid 50/50 and 60/40 BA-tilt combinations

Shows where liquidity caps + ADV constraints start to bite.
Goal: confirm production-grade performance at 100B+ NAV.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)

import simulate_holistic_nav as shn
shn.END_DATE = "2026-05-13"
from simulate_holistic_nav import simulate, bq, VNI_QUERY, START_DATE
from simulate_lh_nav import run_lh, compute_metrics, _CACHE

END_DATE = shn.END_DATE
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]

# ─── LOAD CACHE FROM PHASE 1 ─────────────────────────────────────────────
CACHE_FILE = "ba_patches_signal_cache.pkl"
if not os.path.exists(CACHE_FILE):
    print(f"ERROR: {CACHE_FILE} not found. Run backtest_ba_patches.py first."); sys.exit(1)

print(f"Loading cached BA signals ...", flush=True)
with open(CACHE_FILE, "rb") as f:
    cache = pickle.load(f)
sig = cache["sig"]; vni = cache["vni"]; sec_map = cache["sec_map"]; top30 = cache["top30"]
print(f"  {len(sig):,} signal rows", flush=True)

vni_sorted = vni.sort_values("time").reset_index(drop=True)
vni_sorted["MA200"] = vni_sorted["Close"].rolling(200, min_periods=200).mean()
overheated_dates = set(vni_sorted[vni_sorted["Close"] / vni_sorted["MA200"] > 1.30]["time"])

# Apply P3 patch (block overheated days)
sig_p3 = sig.copy()
mask = sig_p3["time"].isin(overheated_dates) & (sig_p3["play_type"].isin(
    ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","DEEP_VALUE_RECOVERY","S_PRO","S","MOMENTUM_A"]))
sig_p3.loc[mask, "play_type"] = "AVOID_overheated"

prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_p3.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_p3.iterrows()}
vni_dates = sorted(vni["time"].unique())

# VN30 setup
sig_vn30 = sig_p3[sig_p3["ticker"].isin(top30)]
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}
LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}

# ─── RUN BA v11 + LH AT MULTIPLE NAV SIZES ───────────────────────────────
NAV_SIZES = [1e9, 50e9, 100e9, 200e9, 500e9]

print("\n" + "="*80)
print("PHASE 2 — Capacity scaling for Hybrid v11")
print("="*80)

ba_navs = {}
lh_navs = {}

for nav_size in NAV_SIZES:
    nav_label = f"{int(nav_size/1e9)}B"
    print(f"\n--- NAV = {nav_label} VND ---", flush=True)

    # BA BAL
    print(f"  BA BAL ...", flush=True)
    nav_bal, _ = simulate(sig_p3, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=nav_size,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    # BA VN30
    print(f"  BA VN30 ...", flush=True)
    nav_vn30, _ = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=nav_size, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    # 50/50 BA combined
    nav_bal_s = nav_bal.set_index("time")["nav"] / nav_size
    nav_vn30_s = nav_vn30.set_index("time")["nav"] / nav_size
    common = nav_bal_s.index.intersection(nav_vn30_s.index)
    ba_navs[nav_label] = 0.5 * nav_bal_s.loc[common] + 0.5 * nav_vn30_s.loc[common]

    # LH gated at this NAV
    print(f"  LH gated ...", flush=True)
    lh_res = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                     refresh_mode="staggered", crisis_gate=True, init_nav=nav_size)
    lh_navs[nav_label] = lh_res["nav"]["nav"] / lh_res["nav"]["nav"].iloc[0]

# ─── COMPUTE METRICS ─────────────────────────────────────────────────────
print("\n" + "="*120)
print("CAPACITY SCALING RESULTS — Hybrid v11 (50/50 BA + LH gated, qtrly rebal)")
print("="*120)

def hybrid_qtrly(s1, s2, w1=0.5):
    common = s1.index.intersection(s2.index)
    s1 = s1.reindex(common).ffill(); s2 = s2.reindex(common).ffill()
    out = pd.Series(1.0, index=common); r1 = s1.pct_change().fillna(0); r2 = s2.pct_change().fillna(0)
    w = w1; cur = 1.0; last_q = (common[0].year, (common[0].month-1)//3)
    for i in range(1, len(common)):
        dt = common[i]; ret = w*r1.iloc[i] + (1-w)*r2.iloc[i]; cur *= (1+ret)
        this_q = (dt.year, (dt.month-1)//3)
        if this_q != last_q: w = w1; last_q = this_q
        elif (1+ret) != 0: w = w * (1+r1.iloc[i]) / (1+ret)
        out.iloc[i] = cur
    return out

def metrics_window(nav, start, end, nav_size=50e9):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    nav_v = nav_size * s / s.iloc[0]
    return compute_metrics(nav_v, start, end)

vn_df = pd.read_csv("vnindex_lh.csv", parse_dates=["time"])
vn_df = vn_df[vn_df["Close"] > 100].sort_values("time").set_index("time")["Close"]

periods = [
    ("FULL", pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Q1_2026", pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]

rows = []
for pname, ps, pe in periods:
    print(f"\n─── {pname} ({ps.date()} → {pe.date()}) ───")
    print(f"  {'NAV':<6}{'BA CAGR':>10}{'LH CAGR':>10}{'H50/50 CAGR':>14}{'H60/40 CAGR':>14}{'H50/50 Sh':>11}{'H50/50 DD':>11}{'H50/50 Cal':>12}")
    for nav_label in [f"{int(n/1e9)}B" for n in NAV_SIZES]:
        ba_n = ba_navs[nav_label]; lh_n = lh_navs[nav_label]
        h50 = hybrid_qtrly(ba_n, lh_n, 0.5)
        h60 = hybrid_qtrly(ba_n, lh_n, 0.6)

        m_ba = metrics_window(ba_n, ps, pe)
        m_lh = metrics_window(lh_n, ps, pe)
        m_50 = metrics_window(h50, ps, pe)
        m_60 = metrics_window(h60, ps, pe)
        if m_50 is None: continue
        print(f"  {nav_label:<6}{m_ba['CAGR']:>+10.2%}{m_lh['CAGR']:>+10.2%}{m_50['CAGR']:>+14.2%}{m_60['CAGR']:>+14.2%}"
              f"{m_50['Sharpe']:>+11.2f}{m_50['MaxDD']:>+11.2%}{m_50['Calmar']:>+12.2f}")
        rows.append({"period":pname,"nav":nav_label,
                     "BA_CAGR":m_ba["CAGR"],"LH_CAGR":m_lh["CAGR"],
                     "H50_CAGR":m_50["CAGR"],"H50_Sharpe":m_50["Sharpe"],"H50_MaxDD":m_50["MaxDD"],"H50_Calmar":m_50["Calmar"],
                     "H60_CAGR":m_60["CAGR"],"H60_Sharpe":m_60["Sharpe"],"H60_MaxDD":m_60["MaxDD"],"H60_Calmar":m_60["Calmar"]})

# Save
pd.DataFrame(rows).to_csv("phase2_capacity_results.csv", index=False)
# Save NAVs
out = {"BA_"+k: v for k,v in ba_navs.items()}
out.update({"LH_"+k: v for k,v in lh_navs.items()})
pd.DataFrame(out).to_csv("phase2_navs.csv")
print("\nSaved: phase2_capacity_results.csv, phase2_navs.csv")
