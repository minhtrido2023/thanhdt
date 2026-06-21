# -*- coding: utf-8 -*-
"""F-system + BA-system mix backtest.

Question: does combining BA-system (stock momentum/value) with F-system (VN30F
derivatives, LONG/SHORT) improve risk-adjusted returns?

Approach:
  1. F-system: import f_system_backtest.py to get F_Balanced + F_HAdapted NAVs
     (state-based position maps on VN30 underlying, TC=0.03%, T+0).
  2. BA-system: run simulate_holistic_nav at 50B with v10 config
     (50% BAL+Fin/RE-max-4 + 50% VN30_BAL).
  3. Align both NAVs on common date range, normalize start=1.0, mix at various
     weights, compare CAGR/Sharpe/MaxDD.

Note: F-system trades VN30 futures (margin instrument) and BA-system trades
spot stocks. In practice they would use separate capital pools — this script
backtests them as a pseudo-portfolio mix to assess hypothetical synergy.
"""
import os
import sys
import io

import numpy as np
import pandas as pd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)

# ─── 1) Build F-system NAVs from BQ 5-state + VN30 returns (self-contained) ──
print("=" * 90)
print("  STEP 1 — Building F-system NAVs from 5-state regime + VN30 returns")
print("=" * 90)

from simulate_holistic_nav import bq

print("  Loading 5-state regime + VN30 returns from BQ…")
F_DATA_SQL = """
SELECT s5.time, s5.state, t.Close AS vnindex_close, vn30.Close AS vn30_close
FROM tav2_bq.vnindex_5state AS s5
LEFT JOIN tav2_bq.ticker AS t ON t.time = s5.time AND t.ticker = 'VNINDEX'
LEFT JOIN tav2_bq.ticker AS vn30 ON vn30.time = s5.time AND vn30.ticker = 'VN30'
WHERE s5.time >= DATE '2014-01-01'
ORDER BY s5.time
"""
fdf = bq(F_DATA_SQL)
fdf["time"] = pd.to_datetime(fdf["time"])
fdf = fdf.sort_values("time").reset_index(drop=True)
# Use VN30 underlying when available, else fallback to VNINDEX
fdf["underlying"] = fdf["vn30_close"].fillna(fdf["vnindex_close"])
fdf["underlying"] = fdf["underlying"].ffill()
fdf = fdf.dropna(subset=["underlying", "state"]).reset_index(drop=True)
print(f"  {len(fdf):,} sessions, {fdf['time'].iloc[0].date()} → {fdf['time'].iloc[-1].date()}")

# F-system position maps (from f_system_backtest.py F_MAPS)
F_MAPS = {
    "F_Balanced":     {1: -1.00, 2: -0.30, 3:  0.00, 4: +1.00, 5: +1.50},
    "F_HAdapted":     {1: -1.00, 2: -0.20, 3: +0.70, 4: +1.00, 5: +1.30},
    "F_Conservative": {1: -0.50, 2: -0.20, 3:  0.00, 4: +1.00, 5: +1.30},
}

TC_F = 0.0003       # 0.03% per |Δposition|
ROLL_C = 0.012      # 1.2%/yr roll cost on |position|
SPY_F = 252         # approx sessions/yr for VN30


def simulate_f(fdf, pos_map, init=1e9):
    """Run F-system NAV simulation. Returns Series indexed by time."""
    n = len(fdf)
    pv = np.zeros(n); pv[0] = init
    pos = pos_map[3]  # neutral start
    underlying = fdf["underlying"].values
    state = fdf["state"].astype(int).values
    for t in range(1, n):
        target = pos_map[int(state[t-1])]  # T+1: state from yesterday → today's position
        diff = target - pos
        pos_new = target  # T+0 snap
        rm = underlying[t] / underlying[t-1] - 1 if underlying[t-1] > 0 else 0.0
        pnl_pos = pos_new * rm
        cost_tc = abs(diff) * TC_F
        cost_roll = abs(pos_new) * (ROLL_C / SPY_F)
        pv[t] = pv[t-1] * (1.0 + pnl_pos - cost_tc - cost_roll)
        pos = pos_new
    return pd.Series(pv, index=fdf["time"])


print("  Simulating F_Balanced, F_HAdapted, F_Conservative…")
f_balanced_nav = simulate_f(fdf, F_MAPS["F_Balanced"])
f_hadapted_nav = simulate_f(fdf, F_MAPS["F_HAdapted"])
f_conserv_nav = simulate_f(fdf, F_MAPS["F_Conservative"])

# B&H VN30 reference
n = len(fdf)
underlying = fdf["underlying"].values
bh = np.zeros(n); bh[0] = 1e9
for t in range(1, n):
    bh[t] = bh[t-1] * (underlying[t] / underlying[t-1] if underlying[t-1] > 0 else 1.0)
bh_nav = pd.Series(bh, index=fdf["time"])

# Pseudo H-system (simple long-only state map) for comparison
H_MAP = {1: 0.0, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
h_system_nav = simulate_f(fdf, H_MAP)

print(f"  Final F_Balanced wealth: {f_balanced_nav.iloc[-1]/1e9:.2f}× "
      f"| F_HAdapted: {f_hadapted_nav.iloc[-1]/1e9:.2f}× "
      f"| B&H: {bh_nav.iloc[-1]/1e9:.2f}×")

# ─── 2) Run BA-system simulation at 50B (v10) ────────────────────────────────
print("\n" + "=" * 90)
print("  STEP 2 — Running BA-system 50B (50% BAL+Fin/RE-max-4 + 50% VN30_BAL)…")
print("=" * 90)

from simulate_holistic_nav import simulate, metrics, bq, VNI_QUERY, START_DATE, END_DATE
# Use v10 SQL — same as test_round12_v10_hybrid.py / test_round14_stability.py
from test_round14_stability import SIGNAL_V10  # reuse SQL constant

print("  Loading v10 signals…")
sig = bq(SIGNAL_V10.format(start=START_DATE, end=END_DATE))
sig["time"] = pd.to_datetime(sig["time"])
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

TIER_BAL = ["MEGA", "MOMENTUM", "MOMENTUM_N", "MOMENTUM_S", "DEEP_VALUE_RECOVERY"]
LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

print("  Running BAL+Fin/RE-max-4 (full universe) at 50B…")
nav_bal, _ = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map, **LIQ_FULL)
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
nav_bal_s = nav_bal.set_index("time")["nav"]

print("  Running VN30_BAL at 50B…")
sig_vn30 = sig[sig["ticker"].isin(top30)]
prices_vn30 = {tk: prices[tk] for tk in top30 if tk in prices}
liq_vn30 = {k: v for k, v in liq_map.items() if k[0] in top30}
LIQ_VN30 = {**LIQ_FULL, "liquidity_lookup": liq_vn30}

nav_vn30, _ = simulate(sig_vn30, prices_vn30, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=50e9, **LIQ_VN30)
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
nav_vn30_s = nav_vn30.set_index("time")["nav"]

# Combine 50/50 BAL_Fin4 + VN30_BAL → BA-system NAV
common = nav_bal_s.index.intersection(nav_vn30_s.index)
ba_nav_norm = (0.5 * (nav_bal_s.loc[common] / 50e9)
               + 0.5 * (nav_vn30_s.loc[common] / 50e9))
print(f"  BA-system 50/50 NAV: {len(ba_nav_norm)} sessions, "
      f"final {ba_nav_norm.iloc[-1]:.2f}× (started 1.0×)")

# ─── 3) Align F-system + BA-system on common dates, normalize ────────────────
print("\n" + "=" * 90)
print("  STEP 3 — Aligning + mixing")
print("=" * 90)

aligned_dates = ba_nav_norm.index.intersection(f_balanced_nav.index)
ba_n = (ba_nav_norm.loc[aligned_dates] / ba_nav_norm.loc[aligned_dates].iloc[0])
fb_n = (f_balanced_nav.loc[aligned_dates] / f_balanced_nav.loc[aligned_dates].iloc[0])
fh_n = (f_hadapted_nav.loc[aligned_dates] / f_hadapted_nav.loc[aligned_dates].iloc[0])
fc_n = (f_conserv_nav.loc[aligned_dates] / f_conserv_nav.loc[aligned_dates].iloc[0])
bh_n = (bh_nav.loc[aligned_dates] / bh_nav.loc[aligned_dates].iloc[0])
h_n = (h_system_nav.loc[aligned_dates] / h_system_nav.loc[aligned_dates].iloc[0])

print(f"  Common range: {aligned_dates[0].date()} → {aligned_dates[-1].date()} "
      f"({len(aligned_dates)} sessions)")

# ─── 4) Metrics function ─────────────────────────────────────────────────────
def m(nav, name=""):
    rets = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1] / nav.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    down = rets[rets < 0]
    sortino = rets.mean() * spy / (down.std() * np.sqrt(spy)) if len(down) and down.std() > 0 else 0
    rm = nav.cummax()
    dd = (nav - rm) / rm
    mdd = dd.min()
    cal = cagr / abs(mdd) if mdd < 0 else 0
    return {"name": name, "cagr_pct": cagr * 100, "sharpe": sharpe, "sortino": sortino,
            "mdd_pct": mdd * 100, "calmar": cal, "wealth_x": nav.iloc[-1]}

print("\n  Standalone NAVs (full common period):")
print(f"  {'System':<28} {'CAGR':>7} {'Sharpe':>7} {'Sortino':>7} {'MaxDD':>7} {'Calmar':>7} {'Wealth':>7}")
print(f"  {'-'*28} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7} {'-'*7}")
for nav, label in [(ba_n, "BA-system 50/50"),
                   (fb_n, "F_Balanced (futures)"),
                   (fh_n, "F_HAdapted (futures)"),
                   (fc_n, "F_Conservative"),
                   (h_n, "H-system (cash market)"),
                   (bh_n, "B&H (VNINDEX/VN30)")]:
    mt = m(nav, label)
    print(f"  {label:<28} {mt['cagr_pct']:>+6.2f}% {mt['sharpe']:>+7.2f} {mt['sortino']:>+7.2f} "
          f"{mt['mdd_pct']:>+6.1f}% {mt['calmar']:>+7.2f} {mt['wealth_x']:>+6.2f}×")

# ─── 5) Mix BA + F-system at various weights ─────────────────────────────────
print("\n" + "=" * 90)
print("  STEP 5 — BA-system × F-system weight grid")
print("=" * 90)

mix_results = []
for f_variant_label, f_nav in [("F_Balanced", fb_n),
                                ("F_HAdapted", fh_n),
                                ("F_Conservative", fc_n)]:
    print(f"\n  >>> BA × {f_variant_label}")
    print(f"  {'Mix (BA / F)':<20} {'CAGR':>7} {'Sharpe':>7} {'Sortino':>7} {'MaxDD':>7} {'Calmar':>7} {'Wealth':>7}")
    for ba_w, f_w in [(1.0, 0.0), (0.9, 0.1), (0.8, 0.2), (0.7, 0.3),
                       (0.6, 0.4), (0.5, 0.5), (0.0, 1.0)]:
        mix_nav = ba_w * ba_n + f_w * f_nav
        mt = m(mix_nav, f"BA{int(ba_w*100)}_{f_variant_label}{int(f_w*100)}")
        mix_results.append({"f_variant": f_variant_label, "ba_w": ba_w, "f_w": f_w, **mt})
        label = f"BA {int(ba_w*100)}% / F {int(f_w*100)}%"
        print(f"  {label:<20} {mt['cagr_pct']:>+6.2f}% {mt['sharpe']:>+7.2f} {mt['sortino']:>+7.2f} "
              f"{mt['mdd_pct']:>+6.1f}% {mt['calmar']:>+7.2f} {mt['wealth_x']:>+6.2f}×")

# ─── 6) Find Pareto-optimal mixes ────────────────────────────────────────────
print("\n" + "=" * 90)
print("  STEP 6 — Pareto-optimal mixes (best Sharpe + best Calmar)")
print("=" * 90)
df = pd.DataFrame(mix_results)
top_sh = df.sort_values("sharpe", ascending=False).head(5)
top_cal = df.sort_values("calmar", ascending=False).head(5)
print(f"\n  Top 5 by Sharpe:")
print(top_sh[["f_variant", "ba_w", "f_w", "cagr_pct", "sharpe", "mdd_pct", "calmar"]].to_string(index=False))
print(f"\n  Top 5 by Calmar:")
print(top_cal[["f_variant", "ba_w", "f_w", "cagr_pct", "sharpe", "mdd_pct", "calmar"]].to_string(index=False))

# ─── 7) Behavior in critical periods (2022 crash, 2020 COVID) ─────────────────
print("\n" + "=" * 90)
print("  STEP 7 — Crash defense check")
print("=" * 90)
# Re-segment by year
ba_y = ba_n.resample("YE").last()
fb_y = fb_n.resample("YE").last()
print(f"\n  Year-over-year wealth multiplier:")
print(f"  {'Year':<8} {'BA-only':>10} {'F_Bal-only':>12} {'80BA/20F_Bal':>15} {'70BA/30F_Bal':>15}")
ba_prev, fb_prev, m80_prev, m70_prev = 1.0, 1.0, 1.0, 1.0
ba_n_arr = ba_n
fb_n_arr = fb_n
mix80 = 0.8 * ba_n + 0.2 * fb_n
mix70 = 0.7 * ba_n + 0.3 * fb_n
for ts in ba_y.index:
    yr = ts.year
    ba_v = ba_n_arr.loc[:ts].iloc[-1]
    fb_v = fb_n_arr.loc[:ts].iloc[-1]
    m80_v = mix80.loc[:ts].iloc[-1]
    m70_v = mix70.loc[:ts].iloc[-1]
    ba_ret = (ba_v / ba_prev - 1) * 100
    fb_ret = (fb_v / fb_prev - 1) * 100
    m80_ret = (m80_v / m80_prev - 1) * 100
    m70_ret = (m70_v / m70_prev - 1) * 100
    print(f"  {yr:<8} {ba_ret:>+8.1f}%   {fb_ret:>+9.1f}%   {m80_ret:>+12.1f}%   {m70_ret:>+12.1f}%")
    ba_prev, fb_prev, m80_prev, m70_prev = ba_v, fb_v, m80_v, m70_v

# ─── Save ────────────────────────────────────────────────────────────────────
out_path = os.path.join(WORKDIR, "data/f_ba_mix_results.csv")
df.to_csv(out_path, index=False)
print(f"\n  Saved: {out_path}")

# Also save NAV traces for further analysis
nav_traces = pd.DataFrame({
    "time": ba_n.index,
    "BA_50_50": ba_n.values,
    "F_Balanced": fb_n.values,
    "F_HAdapted": fh_n.values,
    "F_Conservative": fc_n.values,
    "H_System": h_n.values,
    "BH_VN30": bh_n.values,
    "BA80_FBal20": mix80.values,
    "BA70_FBal30": mix70.values,
})
nav_traces.to_csv(os.path.join(WORKDIR, "data/f_ba_mix_nav_traces.csv"), index=False)
print(f"  NAV traces: f_ba_mix_nav_traces.csv")
