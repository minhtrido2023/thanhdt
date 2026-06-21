#!/usr/bin/env python3
"""
qwf_hybrid.py
=============
Quarterly walk-forward (QWF) validation for the Hybrid 50/50 BA+LH_gated system.

Run at any date; outputs:
  - Trailing 1Y/3Y/5Y CAGR/Sharpe/MaxDD/Calmar
  - Rolling table: same metrics computed at each quarter-end over last 5 years
  - Traffic-light GREEN/YELLOW/RED vs baseline expectations
  - Comparison to BA-only, LH_gated-only, VNINDEX_BH for the same windows

Baselines (Hybrid 50/50 qtrly + GATED, validated 2014-2026):
  CAGR 19.33%, Sharpe 1.44, MaxDD -16.4%, Calmar 1.18
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics

INIT_NAV = 50e9

BASELINE = {
    "CAGR": 0.1933, "Sharpe": 1.44, "MaxDD": -0.164, "Calmar": 1.18,
}
GREEN_BAND = {"CAGR": 0.05, "Sharpe": 0.30, "MaxDD": 0.05, "Calmar": 0.30}
YELLOW_BAND = {"CAGR": 0.10, "Sharpe": 0.50, "MaxDD": 0.10, "Calmar": 0.50}

def status(metric, val, baseline):
    if pd.isna(val): return "N/A"
    diff = abs(val - baseline) if metric != "MaxDD" else (baseline - val)  # for DD, worse=more negative
    if metric == "MaxDD":
        # val=-0.20, baseline=-0.164. val is worse → diff = baseline - val = -0.164 - (-0.20) = 0.036 (positive = worse)
        diff = baseline - val  # positive=worse
    green = GREEN_BAND[metric]; yellow = YELLOW_BAND[metric]
    if metric in ("MaxDD",):
        if diff <= green: return "GREEN"
        if diff <= yellow: return "YELLOW"
        return "RED"
    # symmetric bands for CAGR/Sharpe/Calmar (worse = below baseline)
    diff = baseline - val  # positive=underperform
    if diff <= green: return "GREEN"
    if diff <= yellow: return "YELLOW"
    return "RED"

def hybrid_rebal_qtrly(s1, s2, w1=0.5):
    """Quarterly rebalance to w1/(1-w1). Returns NAV series starting at 1.0."""
    common = s1.index.intersection(s2.index)
    s1 = s1.reindex(common).ffill(); s2 = s2.reindex(common).ffill()
    out = pd.Series(1.0, index=common)
    r1 = s1.pct_change().fillna(0); r2 = s2.pct_change().fillna(0)
    w = w1; cur = 1.0
    last_q = (common[0].year, (common[0].month-1)//3)
    for i in range(1, len(common)):
        dt = common[i]
        ret = w*r1.iloc[i] + (1-w)*r2.iloc[i]
        cur *= (1 + ret)
        this_q = (dt.year, (dt.month-1)//3)
        if this_q != last_q:
            w = w1; last_q = this_q
        else:
            if (1+ret) != 0:
                w = w * (1+r1.iloc[i]) / (1+ret)
        out.iloc[i] = cur
    return out

def slice_metrics(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    return compute_metrics(INIT_NAV * s / s.iloc[0], start, end)

def fmt(v, kind="float", baseline=None, metric=None):
    if pd.isna(v): return "  N/A"
    if kind == "pct": s = f"{v:+7.2%}"
    elif kind == "sharpe": s = f"{v:+6.2f}"
    else: s = f"{v:+7.3f}"
    if baseline is not None and metric is not None:
        st = status(metric, v, baseline)
        col = {"GREEN":"🟢","YELLOW":"🟡","RED":"🔴","N/A":"⚪"}[st]
        return f"{s} {col}"
    return s

# ---- Build series ----
print("Loading BA NAV ...")
ba_traces = pd.read_csv("data/f_ba_mix_nav_traces.csv", parse_dates=["time"]).sort_values("time").set_index("time")
ba_nav = ba_traces["BA_50_50"]

print("Running LH_gated ...")
lh_gated = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                   refresh_mode="staggered", crisis_gate=True)
lh_g_nav = lh_gated["nav"]["nav"]

print("Loading VNINDEX ...")
vn_df = pd.read_csv("data/vnindex_lh.csv", parse_dates=["time"])
vn_df = vn_df[vn_df["Close"] > 100].sort_values("time").set_index("time")["Close"]

# Common range
common_start = max(ba_nav.index.min(), lh_g_nav.index.min(), vn_df.index.min())
common_end = min(ba_nav.index.max(), lh_g_nav.index.max(), vn_df.index.max())
print(f"\nCommon range: {common_start.date()} -> {common_end.date()}")

ba_n = (ba_nav / ba_nav[ba_nav.index >= common_start].iloc[0]).loc[common_start:common_end]
lh_n = (lh_g_nav / lh_g_nav[lh_g_nav.index >= common_start].iloc[0]).loc[common_start:common_end]
vn_n = (vn_df / vn_df[vn_df.index >= common_start].iloc[0]).loc[common_start:common_end]

hybrid = hybrid_rebal_qtrly(ba_n, lh_n, w1=0.5)

# ---- Snapshot date ----
snap_dt = sys.argv[1] if len(sys.argv) > 1 else common_end.strftime("%Y-%m-%d")
snap_dt = pd.Timestamp(snap_dt)
print(f"\nSnapshot: {snap_dt.date()}")

# ---- Trailing windows ----
print("\n" + "="*100)
print(f"HYBRID QWF SNAPSHOT @ {snap_dt.date()}  |  baseline CAGR 19.33% Sh 1.44 DD -16.4% Cal 1.18")
print("="*100)

windows = [("Latest Q (3M)", 90), ("Trailing 1Y", 365), ("Trailing 3Y", 365*3),
           ("Trailing 5Y", 365*5), ("Full since 2014", 365*15)]
print(f"\n{'Window':<18}{'CAGR':>14}{'Sharpe':>14}{'MaxDD':>14}{'Calmar':>14}{'wealth×':>10}")
qwf_rows = []
for label, days in windows:
    start = snap_dt - pd.Timedelta(days=days)
    start = max(start, common_start)
    m = slice_metrics(hybrid, start, snap_dt)
    if m is None: continue
    wealth = (hybrid.loc[:snap_dt].iloc[-1] / hybrid.loc[hybrid.index >= start].iloc[0])
    print(f"{label:<18}"
          f"{fmt(m['CAGR'],'pct',BASELINE['CAGR'],'CAGR'):>14}"
          f"{fmt(m['Sharpe'],'sharpe',BASELINE['Sharpe'],'Sharpe'):>14}"
          f"{fmt(m['MaxDD'],'pct',BASELINE['MaxDD'],'MaxDD'):>14}"
          f"{fmt(m['Calmar'],'float',BASELINE['Calmar'],'Calmar'):>14}"
          f"{wealth:>10.3f}")
    qwf_rows.append({"window":label,"start":start.date(),"end":snap_dt.date(),
                     "CAGR":m["CAGR"],"Sharpe":m["Sharpe"],"MaxDD":m["MaxDD"],"Calmar":m["Calmar"],"wealth_x":wealth})

# ---- Compare same windows for components ----
print("\n" + "="*100)
print("COMPONENT COMPARISON (same windows)")
print("="*100)
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

# ---- Rolling QWF: trailing-3Y at each quarter end ----
print("\n" + "="*100)
print("ROLLING QWF: trailing-3Y metrics at each quarter-end since 2019")
print("="*100)
quarter_ends = pd.date_range(start="2019-03-31", end=common_end, freq="QE")
quarter_ends = [q for q in quarter_ends if q <= common_end]
print(f"\n{'Q-end':<12}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}{'BA CAGR':>10}{'LH CAGR':>10}{'VNI CAGR':>10}")
roll_rows = []
for qe in quarter_ends:
    start = qe - pd.Timedelta(days=365*3)
    start = max(start, common_start)
    if (qe - start).days < 365*2: continue
    mh = slice_metrics(hybrid, start, qe)
    mb = slice_metrics(ba_n, start, qe)
    ml = slice_metrics(lh_n, start, qe)
    mv = slice_metrics(vn_n, start, qe)
    if mh is None: continue
    cagr_status = status("CAGR", mh["CAGR"], BASELINE["CAGR"])
    flag = {"GREEN":"🟢","YELLOW":"🟡","RED":"🔴"}[cagr_status]
    print(f"{qe.date()}  {mh['CAGR']:>+8.2%} {flag}"
          f" {mh['Sharpe']:>+8.2f}"
          f" {mh['MaxDD']:>+9.2%}"
          f" {mh['Calmar']:>+9.2f}"
          f" {mb['CAGR']:>+9.2%}"
          f" {ml['CAGR']:>+9.2%}"
          f" {mv['CAGR']:>+9.2%}")
    roll_rows.append({"qend":qe.date(),"hybrid_CAGR":mh["CAGR"],"hybrid_Sharpe":mh["Sharpe"],
                      "hybrid_MaxDD":mh["MaxDD"],"hybrid_Calmar":mh["Calmar"],"status":cagr_status,
                      "ba_CAGR":mb["CAGR"],"lh_CAGR":ml["CAGR"],"vni_CAGR":mv["CAGR"]})

# ---- Rolling 1Y (more sensitive) ----
print("\n" + "="*100)
print("ROLLING QWF: trailing-1Y CAGR at each quarter-end since 2019")
print("="*100)
print(f"\n{'Q-end':<12}{'Hyb 1Y':>10}{'BA 1Y':>10}{'LH 1Y':>10}{'VNI 1Y':>10}{'Hyb-VNI':>10}")
roll1y = []
for qe in quarter_ends:
    start = qe - pd.Timedelta(days=365)
    start = max(start, common_start)
    if (qe - start).days < 300: continue
    mh = slice_metrics(hybrid, start, qe); mb = slice_metrics(ba_n, start, qe)
    ml = slice_metrics(lh_n, start, qe); mv = slice_metrics(vn_n, start, qe)
    if mh is None: continue
    alpha = mh["CAGR"] - mv["CAGR"]
    print(f"{qe.date()}  {mh['CAGR']:>+8.2%} {mb['CAGR']:>+9.2%} {ml['CAGR']:>+9.2%} {mv['CAGR']:>+9.2%} {alpha:>+9.2%}")
    roll1y.append({"qend":qe.date(),"hybrid":mh["CAGR"],"ba":mb["CAGR"],"lh":ml["CAGR"],"vni":mv["CAGR"],"alpha_vs_vni":alpha})

# ---- Save ----
pd.DataFrame(qwf_rows).to_csv(f"qwf_hybrid_snapshot_{snap_dt.date()}.csv", index=False)
pd.DataFrame(roll_rows).to_csv(f"qwf_hybrid_rolling3y_{snap_dt.date()}.csv", index=False)
pd.DataFrame(roll1y).to_csv(f"qwf_hybrid_rolling1y_{snap_dt.date()}.csv", index=False)

# ---- Append to tracking log ----
log_row = {"date": snap_dt.date(), "system": "Hybrid_50_50_qtrly_gated"}
for r in qwf_rows:
    if r["window"] == "Trailing 3Y":
        log_row.update({"trail3Y_CAGR":r["CAGR"], "trail3Y_Sharpe":r["Sharpe"],
                         "trail3Y_MaxDD":r["MaxDD"], "trail3Y_Calmar":r["Calmar"]})
    elif r["window"] == "Trailing 1Y":
        log_row.update({"trail1Y_CAGR":r["CAGR"], "trail1Y_Sharpe":r["Sharpe"]})
log_df = pd.DataFrame([log_row])
log_file = "data/qwf_hybrid_tracking_log.csv"
import os
if os.path.exists(log_file):
    log_df.to_csv(log_file, mode="a", header=False, index=False)
else:
    log_df.to_csv(log_file, index=False)

# ---- Verdict ----
print("\n" + "="*100)
red_count = sum(1 for r in qwf_rows if status("CAGR", r["CAGR"], BASELINE["CAGR"])=="RED")
yellow_count = sum(1 for r in qwf_rows if status("CAGR", r["CAGR"], BASELINE["CAGR"])=="YELLOW")
green_count = sum(1 for r in qwf_rows if status("CAGR", r["CAGR"], BASELINE["CAGR"])=="GREEN")
overall = "GREEN" if red_count==0 and yellow_count<=1 else ("YELLOW" if red_count<=1 else "RED")
print(f"VERDICT: {overall} — Green {green_count} | Yellow {yellow_count} | Red {red_count}")
print(f"Saved: qwf_hybrid_snapshot_{snap_dt.date()}.csv, qwf_hybrid_rolling3y_{snap_dt.date()}.csv, qwf_hybrid_rolling1y_{snap_dt.date()}.csv")
