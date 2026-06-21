#!/usr/bin/env python3
"""
compare_ba_v11_vs_v10.py
========================
BA v11 (uses v8c FA) vs v10 baseline (v4 FA) — canonical sim comparison.

Changes in SIGNAL_V11 vs SIGNAL_V10:
  1. Source FA from `tav2_bq.fa_ratings_v8c` (v8c_final ratings)
  2. REMOVE the `+10 Fin/RE-D bonus / -10 Fin/RE-A penalty` from TA score
     (v10's modifier was tuned for v4 FA distribution; v8c has different distribution)

Test design:
  - Same canonical config: SIGNAL_V10 (modified) + max_pos=10, hold=45d, stop=-20%,
    slip=0.1%, sec_lim 8:4, liq caps, 50/50 BAL+VN30, 50B init
  - Periods: FULL 2014-2026 + OOS 2024-2026 + Mid 2018-2023
  - Compare CAGR / Sharpe / MaxDD / Calmar
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

# Build SIGNAL_V11 = SIGNAL_V10 with two changes:
# 1) FA source: fa_ratings_v8c instead of fa_ratings
# 2) Drop the +10 / -10 Fin/RE modifier
SIGNAL_V11 = SIGNAL_V10.replace(
    "FROM `lithe-record-440915-m9.tav2_bq.fa_ratings` AS f",
    "FROM `lithe-record-440915-m9.tav2_bq.fa_ratings_v8c` AS f"
).replace(
    "FROM tav2_bq.fa_ratings AS f",
    "FROM tav2_bq.fa_ratings_v8c AS f"
).replace(
    '    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier="D" THEN 10 ELSE 0 END\n',
    ''
).replace(
    '    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier="A" THEN -10 ELSE 0 END',
    ''
)

# Sanity check
assert "fa_ratings_v8c" in SIGNAL_V11, "v8c table not substituted"
assert 'fa_tier="D" THEN 10' not in SIGNAL_V11, "Fin/RE-D bonus not removed"
assert 'fa_tier="A" THEN -10' not in SIGNAL_V11, "Fin/RE-A penalty not removed"

TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
OOS_START = pd.Timestamp("2024-01-01")


def run_canonical(label, query_text):
    print(f"\n{'='*70}\n  RUN: {label}\n{'='*70}")
    print("Loading signals + prices ...")
    sig = bq(query_text.format(start=START_DATE, end=END_DATE))
    sig["time"] = pd.to_datetime(sig["time"])
    print(f"  {len(sig):,} signal rows")

    # Tier composition diagnostic
    if "fa_tier" in sig.columns:
        play_dist = sig.groupby("play_type").size().sort_values(ascending=False)
        print("Play_type distribution (top 12):")
        print(play_dist.head(12).to_string())

    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

    vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
    vni["time"] = pd.to_datetime(vni["time"])
    vni_dates = sorted(vni["time"].unique())

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

    LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
                "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

    print("\n  Simulating BAL+Fin/RE-max-4 (50B) ...")
    nav_bal, trades_bal = simulate(sig, prices, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9,
        sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    print("  Simulating VN30_BAL (50B) ...")
    sig_vn30 = sig[sig["ticker"].isin(top30)]
    prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
    liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
    LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}
    nav_vn30, trades_vn30 = simulate(sig_vn30, prices_vn30, vni_dates,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])

    common = nav_bal.set_index("time").index.intersection(nav_vn30.set_index("time").index)
    ba_nav = (0.5 * (nav_bal.set_index("time")["nav"].loc[common] / 50e9)
              + 0.5 * (nav_vn30.set_index("time")["nav"].loc[common] / 50e9))
    return ba_nav, vni, len(trades_bal), len(trades_vn30)


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


# Run both
print(f"Window: {START_DATE} → {END_DATE}")
ba_v10, vni, t_v10_bal, t_v10_vn = run_canonical("v10 + v4 FA (baseline)", SIGNAL_V10)
ba_v11, _,  t_v11_bal, t_v11_vn = run_canonical("v11 + v8c FA (new)",      SIGNAL_V11)

periods = [
    ("FULL 2014-2026",  ba_v10.index.min(), ba_v10.index.max()),
    ("OOS 2024-2026",   OOS_START,           ba_v10.index.max()),
    ("Mid 2018-2023",   pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Pre-OOS 2014-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
]

print("\n" + "═"*100)
print("  BA v11 (v8c FA, no Fin/RE bonus) vs v10 (v4 FA, with Fin/RE bonus)")
print("═"*100)
print(f"  Trade counts: v10 BAL={t_v10_bal}/VN30={t_v10_vn}  v11 BAL={t_v11_bal}/VN30={t_v11_vn}")
print()
hdr = f"  {'Period':<22}{'Variant':<14}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}"
print(hdr); print("  " + "-"*len(hdr))

for label, st, en in periods:
    m10 = window_metrics(ba_v10, st, en)
    m11 = window_metrics(ba_v11, st, en)
    vm  = vni_metrics_window(vni, st, en)
    if not m10 or not m11: continue
    print(f"  {label:<22}{'v10+v4':<14}{m10['cagr']:>8.2f}{m10['sharpe']:>8.2f}"
          f"{m10['mdd']:>9.1f}{m10['calmar']:>8.2f}{m10['wealth']:>8.2f}")
    print(f"  {label:<22}{'v11+v8c':<14}{m11['cagr']:>8.2f}{m11['sharpe']:>8.2f}"
          f"{m11['mdd']:>9.1f}{m11['calmar']:>8.2f}{m11['wealth']:>8.2f}")
    print(f"  {label:<22}{'Δ (v11-v10)':<14}{m11['cagr']-m10['cagr']:>+8.2f}"
          f"{m11['sharpe']-m10['sharpe']:>+8.2f}{m11['mdd']-m10['mdd']:>+9.1f}"
          f"{m11['calmar']-m10['calmar']:>+8.2f}{m11['wealth']-m10['wealth']:>+8.2f}")
    if vm:
        print(f"  {label:<22}{'VNI B&H':<14}{vm['cagr']:>8.2f}{vm['sharpe']:>8.2f}"
              f"{vm['mdd']:>9.1f}{vm['calmar']:>8.2f}{vm['wealth']:>8.2f}")
    print()

# Save NAVs for plotting
pd.DataFrame({"v10_v4":ba_v10,"v11_v8c":ba_v11}).to_csv("ba_v11_vs_v10_nav.csv")
print("Saved ba_v11_vs_v10_nav.csv")
