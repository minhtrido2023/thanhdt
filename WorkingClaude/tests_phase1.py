#!/usr/bin/env python3
"""
tests_phase1.py
===============
Three cheap diagnostic tests on Hybrid v11 (BA v11 + LH gated):
  1) Capital allocation grid (BA-tilt 70/30 ... LH-tilt 30/70)
  2) BA-LH rolling correlation (1Y rolling)
  3) Black-swan stress test (-30%/-40% one-day shock at NAV peak)
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics

INIT_NAV = 50e9

# Load NAVs
print("Loading NAVs ...")
ba = pd.read_csv("data/ba_v11_nav.csv", parse_dates=["time"]).sort_values("time").set_index("time")["BA_v11"]
lh_g = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
               refresh_mode="staggered", crisis_gate=True)["nav"]["nav"]
vn = pd.read_csv("data/vnindex_lh.csv", parse_dates=["time"])
vn = vn[vn["Close"] > 100].sort_values("time").set_index("time")["Close"]

common_start = max(ba.index.min(), lh_g.index.min(), vn.index.min())
common_end = min(ba.index.max(), lh_g.index.max(), vn.index.max())
ba_n = (ba.loc[common_start:common_end] / ba.loc[ba.index >= common_start].iloc[0])
lh_n = (lh_g.loc[common_start:common_end] / lh_g.loc[lh_g.index >= common_start].iloc[0])
vn_n = (vn.loc[common_start:common_end] / vn.loc[vn.index >= common_start].iloc[0])

# Align to BA index
common_idx = ba_n.index.intersection(lh_n.index).intersection(vn_n.index)
ba_n = ba_n.reindex(common_idx).ffill()
lh_n = lh_n.reindex(common_idx).ffill()
vn_n = vn_n.reindex(common_idx).ffill()

def hybrid_qtrly(s1, s2, w1):
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

def metrics_window(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    nav_v = INIT_NAV * s / s.iloc[0]
    return compute_metrics(nav_v, start, end)

print("\n" + "="*120)
print("TEST 1 — Capital allocation grid (BA tilt → LH tilt)")
print("="*120)

WEIGHTS = [
    ("LH-tilt 30/70",  0.30),
    ("LH-tilt 40/60",  0.40),
    ("Balanced 50/50", 0.50),
    ("BA-tilt 60/40",  0.60),
    ("BA-tilt 70/30",  0.70),
    ("BA-only 100/0",  1.00),
    ("LH-only 0/100",  0.00),
]

periods = [
    ("FULL 2014-2026",   common_start, common_end),
    ("PRE_2024",         common_start, pd.Timestamp("2023-12-31")),
    ("OOS_2024+",        pd.Timestamp("2024-01-01"), common_end),
    ("Y2022_crash",      pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026_BEAR",     pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]

grid_rows = []
hybrid_navs = {}
for label, w_ba in WEIGHTS:
    if w_ba == 1.0: nav = ba_n
    elif w_ba == 0.0: nav = lh_n
    else: nav = hybrid_qtrly(ba_n, lh_n, w_ba)
    hybrid_navs[label] = nav
    for pname, ps, pe in periods:
        m = metrics_window(nav, ps, pe)
        if m is None: continue
        # Compute alpha vs VNI for same window
        vm = metrics_window(vn_n, ps, pe)
        alpha = m["CAGR"] - vm["CAGR"] if vm else np.nan
        grid_rows.append({"weight":label, "period":pname, **m, "alpha_vs_vni":alpha})

# Pretty print pivot: weights × metrics for FULL period
grid_df = pd.DataFrame(grid_rows)
print("\n--- FULL 2014-2026 ---")
full_df = grid_df[grid_df["period"]=="FULL 2014-2026"].copy()
print(full_df[["weight","CAGR","Sharpe","MaxDD","Calmar","alpha_vs_vni"]].to_string(
    index=False, float_format=lambda x: f"{x:+.4f}" if isinstance(x,(int,float,np.floating)) else str(x)))

print("\n--- Other periods (CAGR / Sharpe / MaxDD) ---")
for pname in ["PRE_2024", "OOS_2024+", "Y2022_crash", "Q1_2026_BEAR"]:
    sub = grid_df[grid_df["period"]==pname]
    if len(sub) == 0: continue
    print(f"\n{pname}:")
    for _, r in sub.iterrows():
        print(f"  {r['weight']:<22}  CAGR={r['CAGR']:>+7.2%}  Sh={r['Sharpe']:>+5.2f}  DD={r['MaxDD']:>+6.2%}  alpha={r['alpha_vs_vni']:>+6.2%}")

grid_df.to_csv("data/phase1_capital_allocation.csv", index=False)

print("\n" + "="*120)
print("TEST 2 — Rolling 1Y correlation BA v11 vs LH gated (daily returns)")
print("="*120)

ba_ret = ba_n.pct_change().dropna()
lh_ret = lh_n.pct_change().dropna()
common_ret = ba_ret.index.intersection(lh_ret.index)
ba_ret = ba_ret.reindex(common_ret); lh_ret = lh_ret.reindex(common_ret)
roll_corr = ba_ret.rolling(252).corr(lh_ret).dropna()

# Sample at quarter-ends
print(f"\nRolling 252-day correlation BA v11 ↔ LH_gated (lower = better diversification):")
print(f"  Full-period correlation: {ba_ret.corr(lh_ret):+.4f}")
print(f"  Min rolling 1Y corr: {roll_corr.min():+.4f} on {roll_corr.idxmin().date()}")
print(f"  Max rolling 1Y corr: {roll_corr.max():+.4f} on {roll_corr.idxmax().date()}")
print(f"  Mean / Median: {roll_corr.mean():+.4f} / {roll_corr.median():+.4f}")

# Sample selected dates
print("\n--- Rolling 1Y corr at quarter-ends (last 5y) ---")
qe = pd.date_range("2021-01-01", common_end, freq="QE")
for q in qe:
    if q not in roll_corr.index:
        nearest = roll_corr.index[roll_corr.index <= q]
        if len(nearest) == 0: continue
        q = nearest[-1]
    print(f"  {q.date()}  corr = {roll_corr.loc[q]:+.4f}")

# Stress-period correlation
print("\n--- Correlation during stress events ---")
stress_periods = [
    ("COVID 2020-Q1", "2020-01-01", "2020-04-30"),
    ("2022_crash", "2022-01-01", "2022-12-31"),
    ("Q1_2026 BEAR", "2025-12-30", "2026-03-30"),
]
for label, s, e in stress_periods:
    sub_ba = ba_ret[(ba_ret.index >= s) & (ba_ret.index <= e)]
    sub_lh = lh_ret[(lh_ret.index >= s) & (lh_ret.index <= e)]
    c = sub_ba.corr(sub_lh)
    print(f"  {label:<20} ({s} → {e}, N={len(sub_ba)}): corr = {c:+.4f}")

roll_corr.to_csv("data/phase1_rolling_corr.csv", header=["corr_BA_LH"])

print("\n" + "="*120)
print("TEST 3 — Black-swan stress test on hybrid 50/50 (BA v11 + LH gated, qtrly)")
print("="*120)

hybrid = hybrid_navs["Balanced 50/50"]

# Find local maxima (peak dates) and apply -30%/-40% one-day shock
shocks = [-0.30, -0.40]
# Pick peak dates at year-end of strong bull years
peak_dates = ["2017-12-29", "2021-12-31", "2024-12-31", "2025-12-31"]

print(f"\nBaseline Hybrid 50/50 metrics (full): CAGR={metrics_window(hybrid, common_start, common_end)['CAGR']:+.2%}, "
      f"Sharpe={metrics_window(hybrid, common_start, common_end)['Sharpe']:+.2f}")

for shock in shocks:
    print(f"\n--- Shock = {shock:+.0%} applied at peak ---")
    print(f"  {'Peak date':<14}{'NAV_before':>14}{'CAGR_post_shock':>20}{'Δ vs no_shock':>18}{'Recovery_days':>18}")
    for pd_str in peak_dates:
        peak_dt = pd.Timestamp(pd_str)
        if peak_dt not in hybrid.index:
            nearest = hybrid.index[hybrid.index <= peak_dt]
            if len(nearest) == 0: continue
            peak_dt = nearest[-1]
        # Apply shock: new NAV from peak onwards scaled by (1+shock)
        nav_shocked = hybrid.copy()
        mask = nav_shocked.index >= peak_dt
        nav_shocked.loc[mask] = nav_shocked.loc[mask] * (1 + shock)
        # Recompute full metrics
        m_post = metrics_window(nav_shocked, common_start, common_end)
        m_base = metrics_window(hybrid, common_start, common_end)
        delta = m_post["CAGR"] - m_base["CAGR"]
        # Recovery: days until NAV returns to pre-shock level
        post_shock = nav_shocked.loc[peak_dt:]
        target = hybrid.loc[peak_dt]
        recovered = post_shock[post_shock >= target]
        if len(recovered) > 0:
            recov_days = (recovered.index[0] - peak_dt).days
        else:
            recov_days = "not recovered"
        print(f"  {peak_dt.date()}    {hybrid.loc[peak_dt]:>13.3f}x  {m_post['CAGR']:>+18.2%}  {delta:>+17.2%}    {recov_days}")

print("\n--- Done. Files: phase1_capital_allocation.csv, phase1_rolling_corr.csv ---")
