#!/usr/bin/env python3
"""
qwf_hybrid_v2.py
================
Refreshed QWF for Hybrid 50/50 BA+LH_gated with two updates:
  1) Use refreshed BA NAV (ba_nav_refresh_2026-05.csv) if available, else fallback
  2) Primary status metric is now ALPHA vs VNINDEX (not absolute CAGR baseline)
     — fixes the RED-on-bear-regime artifact from v1

Per caveat #3 investigation: both prior REDs were 3Y windows with >35% defensive
state days where VNINDEX itself was negative. Absolute CAGR baseline 19% cannot
be met during 3Y bear regimes regardless of system quality. The system actually
delivered LARGER alpha vs VNI in bear windows (+13.3pp vs +9.7pp in COVID).
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics

INIT_NAV = 50e9

# Updated baselines (full period 19.33% CAGR / Sh 1.44 / DD -16.4% / Cal 1.18)
BASELINE = {"CAGR": 0.1933, "Sharpe": 1.44, "MaxDD": -0.164, "Calmar": 1.18}
GREEN_BAND = {"CAGR": 0.05, "Sharpe": 0.30, "MaxDD": 0.05, "Calmar": 0.30}
YELLOW_BAND = {"CAGR": 0.10, "Sharpe": 0.50, "MaxDD": 0.10, "Calmar": 0.50}

# Alpha-vs-VNI baseline (Hybrid full period beats VNI by ~9pp)
ALPHA_BASELINE = 0.05  # GREEN if alpha >= +5pp
ALPHA_YELLOW = 0.0     # YELLOW if alpha in [0, 5pp), RED if < 0

def alpha_status(alpha_pp):
    if pd.isna(alpha_pp): return "N/A"
    if alpha_pp >= ALPHA_BASELINE: return "GREEN"
    if alpha_pp >= ALPHA_YELLOW: return "YELLOW"
    return "RED"

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

def slice_metrics(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    return compute_metrics(INIT_NAV * s / s.iloc[0], start, end)

# ---- Load NAV series ----
print("Loading BA NAV ...")
if os.path.exists("ba_nav_refresh_2026-05.csv"):
    ba_df = pd.read_csv("ba_nav_refresh_2026-05.csv", parse_dates=["time"]).sort_values("time").set_index("time")
    ba_nav = ba_df["BA_50_50"]
    print(f"  Using refreshed BA NAV → range {ba_nav.index.min().date()} to {ba_nav.index.max().date()}")
else:
    ba_df = pd.read_csv("f_ba_mix_nav_traces.csv", parse_dates=["time"]).sort_values("time").set_index("time")
    ba_nav = ba_df["BA_50_50"]
    print(f"  ⚠ Using OLD BA NAV (refresh not found) → ends {ba_nav.index.max().date()}")

print("Running LH_gated ...")
lh_g = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
               refresh_mode="staggered", crisis_gate=True)["nav"]["nav"]

vn_df = pd.read_csv("vnindex_lh.csv", parse_dates=["time"])
vn_df = vn_df[vn_df["Close"] > 100].sort_values("time").set_index("time")["Close"]
state_df = pd.read_csv("vnindex_5state.csv", parse_dates=["time"]).sort_values("time").set_index("time")

common_start = max(ba_nav.index.min(), lh_g.index.min(), vn_df.index.min())
common_end = min(ba_nav.index.max(), lh_g.index.max(), vn_df.index.max())
ba_n = ba_nav.loc[common_start:common_end] / ba_nav.loc[ba_nav.index >= common_start].iloc[0]
lh_n = lh_g.loc[common_start:common_end] / lh_g.loc[lh_g.index >= common_start].iloc[0]
vn_n = vn_df.loc[common_start:common_end] / vn_df.loc[vn_df.index >= common_start].iloc[0]

hybrid = hybrid_qtrly(ba_n, lh_n, 0.5)

snap_dt = pd.Timestamp(sys.argv[1]) if len(sys.argv) > 1 else common_end
print(f"\nCommon range: {common_start.date()} → {common_end.date()}")
print(f"Snapshot: {snap_dt.date()}")

# ---- Trailing windows ----
print("\n" + "="*120)
print(f"HYBRID QWF v2 SNAPSHOT @ {snap_dt.date()}  |  PRIMARY: alpha vs VNI ≥ +5pp = GREEN")
print("="*120)

windows = [("Latest Q (3M)", 90), ("Trailing 1Y", 365), ("Trailing 3Y", 365*3),
           ("Trailing 5Y", 365*5), ("Full since 2014", 365*15)]

print(f"\n{'Window':<18}{'Hyb CAGR':>11}{'Hyb Sh':>9}{'Hyb DD':>10}{'Hyb Cal':>9}"
      f"{'VNI CAGR':>11}{'Alpha':>10}{'Status':>10}{'Regime%':>12}")
qwf_rows = []
for label, days in windows:
    start = snap_dt - pd.Timedelta(days=days)
    start = max(start, common_start)
    mh = slice_metrics(hybrid, start, snap_dt); mv = slice_metrics(vn_n, start, snap_dt)
    if mh is None or mv is None: continue
    alpha = mh["CAGR"] - mv["CAGR"]
    st = alpha_status(alpha)
    flag = {"GREEN":"🟢","YELLOW":"🟡","RED":"🔴","N/A":"⚪"}[st]
    # Regime % defensive in window
    sw = state_df[(state_df.index >= start) & (state_df.index <= snap_dt)]
    if len(sw):
        defensive_pct = (sw["state"].isin([1, 2])).mean() * 100
    else:
        defensive_pct = np.nan
    print(f"{label:<18}{mh['CAGR']:>+10.2%}{mh['Sharpe']:>+9.2f}{mh['MaxDD']:>+10.2%}{mh['Calmar']:>+9.2f}"
          f"{mv['CAGR']:>+10.2%}{alpha:>+9.2%} {flag} {st:<6}{defensive_pct:>10.1f}%")
    qwf_rows.append({"window":label,"start":start.date(),"end":snap_dt.date(),
                     "hyb_CAGR":mh["CAGR"],"hyb_Sharpe":mh["Sharpe"],"hyb_MaxDD":mh["MaxDD"],"hyb_Calmar":mh["Calmar"],
                     "vni_CAGR":mv["CAGR"],"alpha_pp":alpha,"defensive_pct":defensive_pct,"status":st})

# ---- Component breakdown ----
print("\n" + "="*120)
print("COMPONENT COMPARISON")
print("="*120)
for label, days in windows:
    start = snap_dt - pd.Timedelta(days=days)
    start = max(start, common_start)
    print(f"\n--- {label} ({start.date()} → {snap_dt.date()}) ---")
    print(f"  {'series':<24}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}")
    for name, s in [("Hybrid_50/50_gated", hybrid), ("BA_only", ba_n),
                     ("LH_gated_only", lh_n), ("VNINDEX_BH", vn_n)]:
        m = slice_metrics(s, start, snap_dt)
        if m is None: continue
        print(f"  {name:<24}{m['CAGR']:>+10.2%}{m['Sharpe']:>+10.2f}{m['MaxDD']:>+10.2%}{m['Calmar']:>+10.2f}")

# ---- Rolling 3Y alpha QWF ----
print("\n" + "="*120)
print("ROLLING QWF v2: trailing-3Y ALPHA-vs-VNI at each quarter-end")
print("="*120)
quarter_ends = pd.date_range(start="2019-03-31", end=common_end, freq="QE")
quarter_ends = [q for q in quarter_ends if q <= common_end]
print(f"\n{'Q-end':<12}{'Hyb 3Y':>10}{'VNI 3Y':>10}{'Alpha':>10}{'Status':>10}{'Defensive%':>13}")
roll_rows = []
for qe in quarter_ends:
    start = qe - pd.Timedelta(days=365*3)
    start = max(start, common_start)
    if (qe - start).days < 365*2: continue
    mh = slice_metrics(hybrid, start, qe); mv = slice_metrics(vn_n, start, qe)
    if mh is None or mv is None: continue
    alpha = mh["CAGR"] - mv["CAGR"]
    st = alpha_status(alpha)
    flag = {"GREEN":"🟢","YELLOW":"🟡","RED":"🔴","N/A":"⚪"}[st]
    sw = state_df[(state_df.index >= start) & (state_df.index <= qe)]
    def_pct = (sw["state"].isin([1, 2])).mean() * 100 if len(sw) else np.nan
    print(f"{qe.date()}  {mh['CAGR']:>+8.2%} {mv['CAGR']:>+9.2%} {alpha:>+9.2%} {flag} {st:<6} {def_pct:>10.1f}%")
    roll_rows.append({"qend":qe.date(),"hyb_CAGR":mh["CAGR"],"vni_CAGR":mv["CAGR"],"alpha_pp":alpha,
                      "status":st,"defensive_pct":def_pct})

# ---- Save ----
pd.DataFrame(qwf_rows).to_csv(f"qwf_hybrid_v2_snapshot_{snap_dt.date()}.csv", index=False)
pd.DataFrame(roll_rows).to_csv(f"qwf_hybrid_v2_rolling3y_{snap_dt.date()}.csv", index=False)

# ---- Verdict ----
red = sum(1 for r in qwf_rows if r["status"]=="RED")
yel = sum(1 for r in qwf_rows if r["status"]=="YELLOW")
grn = sum(1 for r in qwf_rows if r["status"]=="GREEN")
red_rolling = sum(1 for r in roll_rows if r["status"]=="RED")

overall = "GREEN" if red == 0 and yel <= 1 else ("YELLOW" if red <= 1 else "RED")
print("\n" + "="*120)
print(f"VERDICT v2 (alpha-based): {overall} — Snapshot {grn}G {yel}Y {red}R | Rolling 3Y: {red_rolling} RED quarters out of {len(roll_rows)}")
print(f"Saved: qwf_hybrid_v2_snapshot_{snap_dt.date()}.csv, qwf_hybrid_v2_rolling3y_{snap_dt.date()}.csv")
