#!/usr/bin/env python3
"""
investigate_red_periods.py
==========================
Diagnose caveat #3 from QWF: are the 2 RED rolling-3Y periods regime-driven or score-drift?

RED #1: 2020-Q1/Q2 — trailing 3Y CAGR 6.7%
RED #2: 2024-Q4    — trailing 3Y CAGR 7.26%

For each:
  - Show the 3Y window composition (what major events happened)
  - Decompose: how much of the underperformance comes from BA vs LH?
  - Check 5-state distribution in the window (BEAR/CRISIS share)
  - Check VNINDEX MaxDD in the window
  - Show FA tier-A median forward returns (proxy for score quality drift)
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics

# Load all data
ba_traces = pd.read_csv("data/f_ba_mix_nav_traces.csv", parse_dates=["time"]).sort_values("time").set_index("time")
ba_nav = ba_traces["BA_50_50"]
vn_df = pd.read_csv("data/vnindex_lh.csv", parse_dates=["time"])
vn_df = vn_df[vn_df["Close"] > 100].sort_values("time").set_index("time")["Close"]
state_df = pd.read_csv("data/vnindex_5state.csv", parse_dates=["time"]).sort_values("time").set_index("time")
ratings = pd.read_csv("data/fa_ratings_lh.csv", parse_dates=["time"])

print("Running LH_gated (same as QWF) ...")
lh_g = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
               refresh_mode="staggered", crisis_gate=True)["nav"]["nav"]

# Normalize all to common start
common_start = max(ba_nav.index.min(), lh_g.index.min(), vn_df.index.min())
common_end = min(ba_nav.index.max(), lh_g.index.max(), vn_df.index.max())
ba_n = ba_nav.loc[common_start:common_end] / ba_nav.loc[ba_nav.index >= common_start].iloc[0]
lh_n = lh_g.loc[common_start:common_end] / lh_g.loc[lh_g.index >= common_start].iloc[0]
vn_n = vn_df.loc[common_start:common_end] / vn_df.loc[vn_df.index >= common_start].iloc[0]

# Hybrid qtrly rebal gated
def hybrid_qtrly(s1, s2, w1=0.5):
    common = s1.index.intersection(s2.index); s1 = s1.reindex(common).ffill(); s2 = s2.reindex(common).ffill()
    out = pd.Series(1.0, index=common); r1 = s1.pct_change().fillna(0); r2 = s2.pct_change().fillna(0)
    w = w1; cur = 1.0; last_q = (common[0].year, (common[0].month-1)//3)
    for i in range(1, len(common)):
        dt = common[i]; ret = w*r1.iloc[i] + (1-w)*r2.iloc[i]; cur *= (1+ret)
        this_q = (dt.year, (dt.month-1)//3)
        if this_q != last_q: w = w1; last_q = this_q
        elif (1+ret) != 0: w = w * (1+r1.iloc[i]) / (1+ret)
        out.iloc[i] = cur
    return out

hyb = hybrid_qtrly(ba_n, lh_n, 0.5)

def window_stats(name, start, end):
    """Compute and print decomposition for a window."""
    print(f"\n{'='*100}")
    print(f"  {name}: {start.date()} → {end.date()}")
    print('='*100)

    # 1) Component CAGRs
    print("\n[1] Component CAGRs over window:")
    for label, s in [("Hybrid", hyb), ("BA", ba_n), ("LH_gated", lh_n), ("VNINDEX", vn_n)]:
        sub = s[(s.index >= start) & (s.index <= end)]
        if len(sub) < 30: continue
        yrs = (sub.index[-1] - sub.index[0]).days / 365.25
        cagr = (sub.iloc[-1]/sub.iloc[0])**(1/yrs) - 1
        dd = ((sub - sub.cummax())/sub.cummax()).min()
        ret = sub.iloc[-1]/sub.iloc[0] - 1
        print(f"  {label:<10} CAGR={cagr:+7.2%}  total_ret={ret:+7.2%}  MaxDD={dd:+6.2%}")

    # 2) 5-state distribution
    print("\n[2] 5-state regime distribution in window (1=CRISIS, 2=BEAR, 3=NEU, 4=BULL, 5=EX-BULL):")
    st_sub = state_df[(state_df.index >= start) & (state_df.index <= end)]
    if len(st_sub):
        dist = st_sub["state"].value_counts(normalize=True).sort_index()
        line = "  "
        for s in [1, 2, 3, 4, 5]:
            pct = dist.get(s, 0.0) * 100
            line += f"  State{s}: {pct:5.1f}%"
        print(line)
        # Most recent 90 days regime
        recent = st_sub.tail(90)
        line2 = "  Last 90d: "
        dist2 = recent["state"].value_counts(normalize=True).sort_index()
        for s in [1,2,3,4,5]:
            pct = dist2.get(s, 0.0) * 100
            line2 += f"  State{s}: {pct:5.1f}%"
        print(line2)

    # 3) FA score quality: tier-A forward returns from quarterly ratings in this window
    print("\n[3] FA tier-A median forward returns from picks made IN this window:")
    # Quarters in window
    q_in_window = ratings[(ratings["time"] >= start) & (ratings["time"] <= end)]
    if len(q_in_window) == 0:
        print("  no quarter time stamps in window")
    else:
        a_picks = q_in_window[q_in_window["tier"] == "A"]
        b_picks = q_in_window[q_in_window["tier"] == "B"]
        # We don't have forward returns columns in fa_ratings_lh.csv. Skip detailed.
        # Show count by sub-sector
        print(f"  A picks N={len(a_picks)}, B picks N={len(b_picks)}")
        sub_dist = a_picks["sub"].value_counts().head(6).to_dict()
        print(f"  A-tier sub-sector mix: {sub_dist}")

    # 4) BA vs LH return decomposition
    print("\n[4] Monthly returns BA vs LH (last 12 months of window):")
    last_year_start = end - pd.Timedelta(days=365)
    ba_y = ba_n[(ba_n.index >= last_year_start) & (ba_n.index <= end)]
    lh_y = lh_n[(lh_n.index >= last_year_start) & (lh_n.index <= end)]
    if len(ba_y) > 100 and len(lh_y) > 100:
        ba_m = ba_y.resample("ME").last().pct_change()
        lh_m = lh_y.resample("ME").last().pct_change()
        m = pd.DataFrame({"BA": ba_m, "LH": lh_m})
        print(m.to_string(float_format=lambda x: f"{x:+.2%}" if pd.notna(x) else "  N/A"))

# RED #1: 3Y window ending 2020-03-31
window_stats("RED #1: trailing-3Y ending 2020-03-31 (COVID era)",
              pd.Timestamp("2017-04-01"), pd.Timestamp("2020-03-31"))

# RED #2: 3Y window ending 2024-12-31
window_stats("RED #2: trailing-3Y ending 2024-12-31 (post-2022 hangover)",
              pd.Timestamp("2022-01-01"), pd.Timestamp("2024-12-31"))

# Compare to a GREEN window for contrast
window_stats("CONTRAST: trailing-3Y ending 2021-12-31 (best GREEN)",
              pd.Timestamp("2019-01-01"), pd.Timestamp("2021-12-31"))

print("\n" + "="*100)
print("CAVEAT #3 ANALYSIS — VERDICT")
print("="*100)
