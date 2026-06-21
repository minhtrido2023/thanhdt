#!/usr/bin/env python3
"""
run_hybrid_lh_ba.py
===================
Combine BA-system NAV (from f_ba_mix_nav_traces.csv col BA_50_50) with LH-system NAV
(from simulate_lh_nav.py) at various sleeve weights and rebalance cadences.

Also tests CRISIS-gated LH variants.
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics, load_data

INIT_NAV = 50e9

# Load BA NAV (already normalized to 1.0 start)
ba_traces = pd.read_csv("data/f_ba_mix_nav_traces.csv", parse_dates=["time"]).sort_values("time").set_index("time")
ba_nav = ba_traces["BA_50_50"]
print(f"BA NAV range: {ba_nav.index.min().date()} -> {ba_nav.index.max().date()}, final {ba_nav.iloc[-1]:.2f}x")

# Load VNINDEX for benchmark
vn_df = pd.read_csv("data/vnindex_lh.csv", parse_dates=["time"])
vn_df = vn_df[vn_df["Close"] > 100].sort_values("time").set_index("time")["Close"]

# Run LH variants
print("\nRunning LH (no gate) ...", flush=True)
lh_nogate = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                    refresh_mode="staggered", crisis_gate=False)
lh_nav = lh_nogate["nav"]["nav"]

print("Running LH (CRISIS-gated) ...", flush=True)
lh_gated = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                   refresh_mode="staggered", crisis_gate=True)
lh_g_nav = lh_gated["nav"]["nav"]

# Align all series to common date range
common_start = max(ba_nav.index.min(), lh_nav.index.min(), lh_g_nav.index.min(), vn_df.index.min())
common_end = min(ba_nav.index.max(), lh_nav.index.max(), lh_g_nav.index.max(), vn_df.index.max())
print(f"\nCommon backtest range: {common_start.date()} -> {common_end.date()}")

def norm(s, start_dt, end_dt, base=1.0):
    s2 = s[(s.index >= start_dt) & (s.index <= end_dt)]
    return base * s2 / s2.iloc[0]

# Normalize all to 1.0 at common_start
ba_n = norm(ba_nav, common_start, common_end)
lh_n = norm(lh_nav, common_start, common_end)
lh_g_n = norm(lh_g_nav, common_start, common_end)
vn_n = norm(vn_df, common_start, common_end)

# Align to BA index (sparser) for combinations
common_idx = ba_n.index.intersection(lh_n.index).intersection(lh_g_n.index)
ba_n = ba_n.reindex(common_idx).ffill()
lh_n = lh_n.reindex(common_idx).ffill()
lh_g_n = lh_g_n.reindex(common_idx).ffill()
vn_n = vn_n.reindex(common_idx).ffill()

def hybrid_passive(s1, s2, w1=0.5):
    """No inter-sleeve rebal: each sleeve grows independently from initial weight."""
    return w1 * s1 + (1 - w1) * s2

def hybrid_rebal_annual(s1, s2, w1=0.5):
    """Annual rebalance back to w1/(1-w1) at year-end."""
    out = pd.Series(1.0, index=s1.index)
    r1 = s1.pct_change().fillna(0); r2 = s2.pct_change().fillna(0)
    w = w1
    cur = 1.0
    last_year = s1.index[0].year
    for i in range(1, len(s1.index)):
        dt = s1.index[i]
        ret = w * r1.iloc[i] + (1 - w) * r2.iloc[i]
        cur *= (1 + ret)
        if dt.year != last_year:  # year boundary: rebal
            w = w1
            last_year = dt.year
        else:
            # drift weight based on relative returns
            w_new = w * (1 + r1.iloc[i]) / (1 + ret) if (1 + ret) != 0 else w
            w = w_new
        out.iloc[i] = cur
    return out

def hybrid_rebal_quarterly(s1, s2, w1=0.5):
    """Quarterly rebalance back to w1/(1-w1)."""
    out = pd.Series(1.0, index=s1.index)
    r1 = s1.pct_change().fillna(0); r2 = s2.pct_change().fillna(0)
    w = w1
    cur = 1.0
    last_q = (s1.index[0].year, (s1.index[0].month - 1) // 3)
    for i in range(1, len(s1.index)):
        dt = s1.index[i]
        ret = w * r1.iloc[i] + (1 - w) * r2.iloc[i]
        cur *= (1 + ret)
        this_q = (dt.year, (dt.month - 1) // 3)
        if this_q != last_q:
            w = w1
            last_q = this_q
        else:
            w_new = w * (1 + r1.iloc[i]) / (1 + ret) if (1 + ret) != 0 else w
            w = w_new
        out.iloc[i] = cur
    return out

def compute_for_label(s, label, start, end):
    s2 = s[(s.index >= start) & (s.index <= end)]
    if len(s2) < 30: return None
    nav = INIT_NAV * s2 / s2.iloc[0]
    return compute_metrics(nav, start, end)

scenarios = {
    "BA_only":          ba_n,
    "LH_only":          lh_n,
    "LH_gated":         lh_g_n,
    "Hybrid_50/50_passive":          hybrid_passive(ba_n, lh_n, 0.5),
    "Hybrid_50/50_pass_gated":       hybrid_passive(ba_n, lh_g_n, 0.5),
    "Hybrid_50/50_rebal_annual":     hybrid_rebal_annual(ba_n, lh_n, 0.5),
    "Hybrid_50/50_rebal_qtrly":      hybrid_rebal_quarterly(ba_n, lh_n, 0.5),
    "Hybrid_50/50_rebal_qtrly_gated": hybrid_rebal_quarterly(ba_n, lh_g_n, 0.5),
    "Hybrid_70/30_BAtilt_qtrly":     hybrid_rebal_quarterly(ba_n, lh_n, 0.7),
    "Hybrid_30/70_LHtilt_qtrly":     hybrid_rebal_quarterly(ba_n, lh_n, 0.3),
    "VNINDEX_BH":       vn_n,
}

# Compute per-period metrics
periods = {
    "FULL (2014-04 → 2026-01)": (common_start, common_end),
    "PRE_2024 (2014-04 → 2023-12)": (common_start, pd.Timestamp("2023-12-31")),
    "OOS_2024+ (2024-01 → end)": (pd.Timestamp("2024-01-01"), common_end),
    "Y2022_crash (2022)": (pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    "Y2021_bull (2021)": (pd.Timestamp("2021-01-01"), pd.Timestamp("2021-12-31")),
}

print("\n" + "="*120)
print(f"{'Scenario':<32}{'Period':<32}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Calmar':>9}")
print("="*120)

rows = []
for period_name, (s_dt, e_dt) in periods.items():
    for name, series in scenarios.items():
        m = compute_for_label(series, name, s_dt, e_dt)
        if m is None: continue
        rows.append({"period":period_name, "scenario":name, **m})
        print(f"{name:<32}{period_name:<32}{m['CAGR']:>+9.4f}{m['Sharpe']:>+9.4f}{m['MaxDD']:>+9.4f}{m['Calmar']:>+9.4f}")
    print()

pd.DataFrame(rows).to_csv("data/hybrid_lh_ba_results.csv", index=False)

# Save nav series for plotting
nav_out = pd.DataFrame({k: INIT_NAV * v / v.iloc[0] for k, v in scenarios.items()})
nav_out.to_csv("data/hybrid_lh_ba_nav.csv")

# 2022 monthly detail for crash defense check
print("\n=== 2022 monthly returns ===")
mret_2022 = {}
for name in ["BA_only","LH_only","LH_gated","Hybrid_50/50_rebal_qtrly","Hybrid_50/50_rebal_qtrly_gated","VNINDEX_BH"]:
    s = scenarios[name]
    s22 = s["2022-01-01":"2022-12-31"]
    m = s22.resample("ME").last().pct_change()
    mret_2022[name] = m
m22df = pd.DataFrame(mret_2022)
print(m22df.to_string(float_format=lambda x: f"{x:+.2%}" if pd.notna(x) else "N/A"))
m22df.to_csv("data/hybrid_2022_monthly.csv")

print("\nWrote: hybrid_lh_ba_results.csv, hybrid_lh_ba_nav.csv, hybrid_2022_monthly.csv")
