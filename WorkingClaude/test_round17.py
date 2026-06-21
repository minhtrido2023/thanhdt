# -*- coding: utf-8 -*-
"""Round 17 — Exit logic optimization: state-transition exit + profit-target exit.

Two new exit rules untried in rounds 1-16:

(1) State-transition exit — close positions when 5-state regime degrades to
    BEAR (state=2) or CRISIS (state=1), bypassing 45d hold and -20% stop.
    Targets known weakness: 2026-Q1 -8.08% loss when system held into BEAR.

(2) Profit-target exit — close at +30% / +35% / +40% gain, recycle capital.
    Different from PARTIAL (round-5 reject) — full close + redeploy.

Test universe: BAL+Fin/RE-max-4 single-book at 50B with v10 SQL.
Period EXTENDED to 2026-03-30 (was 2026-01-16) to include recent BEAR
(2026-03-17 → 2026-04-08, 23 sessions) AND 2025-Q4 CRISIS (Sep-Dec 2025, 64 sessions).
"""
import os
import sys
import io

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY
from test_round14_stability import SIGNAL_V10

# EXTENDED test period — include recent BEAR + 2025-Q4 CRISIS
START_DATE = "2014-01-01"
END_DATE = "2026-03-30"

print("=" * 100)
print("  ROUND 17 — Exit logic: state-transition + profit-target")
print(f"  Period: {START_DATE} → {END_DATE} (EXTENDED to include 2025-Q4 CRISIS + 2026-Q1 BEAR)")
print("=" * 100)

print("\nLoading v10 signals…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
print(f"  {len(sig):,} rows")
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

print("Loading 5-state series…")
state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state_df["time"] = pd.to_datetime(state_df["time"])
state_by_date = dict(zip(state_df["time"], state_df["state"]))
print(f"  {len(state_by_date):,} state observations")

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
       "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

BASE_KW = dict(
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
)


def run(label, **extra):
    nav_df, trades_df = simulate(sig, prices, vni_dates, **BASE_KW, **LIQ,
                                  **extra, name=label)
    m = metrics(nav_df, trades_df, label)
    return m, trades_df


# ─── Variants ────────────────────────────────────────────────────────────────
variants = [
    ("v10 baseline", {}),
    # State-transition exit variants
    ("ST: exit on BEAR", {"state_by_date": state_by_date,
                           "state_exit_map": {2: 1.0, 1: 1.0}}),
    ("ST: exit on CRISIS only", {"state_by_date": state_by_date,
                                   "state_exit_map": {1: 1.0}}),
    ("ST: halve NEUTRAL + close BEAR", {"state_by_date": state_by_date,
                                          "state_exit_map": {3: 0.5, 2: 1.0, 1: 1.0}}),
    # Profit-target variants
    ("PT: +25% close-redeploy", {"profit_target": 0.25}),
    ("PT: +30% close-redeploy", {"profit_target": 0.30}),
    ("PT: +35% close-redeploy", {"profit_target": 0.35}),
    ("PT: +40% close-redeploy", {"profit_target": 0.40}),
    ("PT: +30% + BL10", {"profit_target": 0.30, "pt_blacklist_days": 10}),
    # Combined: best ST + best PT
    ("ST+PT: BEAR-exit + +30%", {"state_by_date": state_by_date,
                                   "state_exit_map": {2: 1.0, 1: 1.0},
                                   "profit_target": 0.30}),
    ("ST+PT: BEAR-exit + +35%", {"state_by_date": state_by_date,
                                   "state_exit_map": {2: 1.0, 1: 1.0},
                                   "profit_target": 0.35}),
]

print(f"\nRunning {len(variants)} variants…\n")
print(f"  {'Variant':<40} {'CAGR':>8} {'Sharpe':>8} {'MaxDD':>8} {'Calmar':>8} {'trades':>8}")
print(f"  {'-'*40} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

results = []
trades_by_variant = {}
for label, extra in variants:
    m, trades_df = run(label, **extra)
    results.append({"variant": label, **m})
    trades_by_variant[label] = trades_df
    print(f"  {label:<40} {m['cagr_pct']:>+7.2f}% {m['sharpe']:>+8.2f} "
          f"{m['max_dd_pct']:>+7.1f}% {m['calmar']:>+8.2f} {m['n_trades']:>8d}")

df = pd.DataFrame(results)

# ─── Δ vs baseline ───────────────────────────────────────────────────────────
base = df[df["variant"] == "v10 baseline"].iloc[0]
print(f"\n{'=' * 100}")
print(f"  Δ vs baseline (CAGR={base['cagr_pct']:.2f}% Sh={base['sharpe']:.2f} "
      f"DD={base['max_dd_pct']:.1f}% Cal={base['calmar']:.2f})")
print(f"{'=' * 100}")
print(f"\n  {'Variant':<40} {'ΔCAGR':>10} {'ΔSharpe':>10} {'ΔDD':>10} {'ΔCalmar':>10}")
for _, r in df.iterrows():
    if r["variant"] == "v10 baseline":
        continue
    print(f"  {r['variant']:<40} {r['cagr_pct']-base['cagr_pct']:>+9.2f}pp "
          f"{r['sharpe']-base['sharpe']:>+9.2f} "
          f"{r['max_dd_pct']-base['max_dd_pct']:>+9.1f}pp "
          f"{r['calmar']-base['calmar']:>+9.2f}")

# ─── Exit reason breakdown ───────────────────────────────────────────────────
print(f"\n{'=' * 100}")
print(f"  EXIT REASON BREAKDOWN")
print(f"{'=' * 100}")
for label in ["v10 baseline", "ST: exit on BEAR", "PT: +30% close-redeploy",
              "ST+PT: BEAR-exit + +30%"]:
    tdf = trades_by_variant.get(label)
    if tdf is None or tdf.empty:
        continue
    counts = tdf["reason"].value_counts()
    avg_ret = tdf.groupby("reason")["ret_net"].mean() * 100
    print(f"\n  {label}")
    print(f"  {'reason':<22} {'n':>6} {'%':>6} {'avg ret':>10}")
    total = len(tdf)
    for r, n in counts.items():
        ar = avg_ret[r]
        print(f"  {r:<22} {n:>6d} {n/total*100:>5.1f}% {ar:>+9.2f}%")

# ─── 2026-Q1 specific behavior (key test of state-transition exit) ───────────
print(f"\n{'=' * 100}")
print(f"  2026-Q1 BEHAVIOR (Jan 1 - Mar 30) — known weakness period")
print(f"{'=' * 100}")
print(f"  Recent BEAR: 2026-03-17 → 2026-03-30 (in test data)")
print()
for label in ["v10 baseline", "ST: exit on BEAR", "ST+PT: BEAR-exit + +30%"]:
    tdf = trades_by_variant.get(label)
    if tdf is None:
        continue
    tdf["entry_date"] = pd.to_datetime(tdf["entry_date"])
    tdf["exit_date"] = pd.to_datetime(tdf["exit_date"])
    q1_2026 = tdf[(tdf["exit_date"] >= "2026-01-01") &
                   (tdf["exit_date"] <= "2026-03-30")]
    if not q1_2026.empty:
        print(f"  {label}: {len(q1_2026)} exits in 2026-Q1, "
              f"avg ret {q1_2026['ret_net'].mean()*100:+.2f}%, "
              f"win {(q1_2026['ret_net']>0).mean()*100:.1f}%")

# ─── Save ────────────────────────────────────────────────────────────────────
out_path = os.path.join(WORKDIR, "data/round17_results.csv")
df.to_csv(out_path, index=False)
print(f"\n  Saved: {out_path}")

# Save trades for top 3 variants
for label in ["v10 baseline", "ST: exit on BEAR", "ST+PT: BEAR-exit + +30%"]:
    safe_label = label.replace(":", "").replace(" ", "_").replace("+", "p")
    trades_by_variant[label].to_csv(
        os.path.join(WORKDIR, f"round17_trades_{safe_label}.csv"), index=False)
print(f"  Trade logs saved for 3 variants")
