# -*- coding: utf-8 -*-
"""exp8_isoos_metrics.py — FULL / IS(2014-19) / OOS(2020-now) core metrics from an audit CSV.
Reuses simulate_holistic_nav.metrics() so Sharpe/MaxDD/Calmar are byte-identical to the script's
own FULL print (Sharpe uses actual sessions/year, not fixed 252). Usage: python exp8_isoos_metrics.py <audit.csv> [label]
"""
import sys, os
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
os.chdir("/home/trido/thanhdt/WorkingClaude")
import pandas as pd
from simulate_holistic_nav import metrics

path = sys.argv[1]
label = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(path)
df = pd.read_csv(path, low_memory=False)
d = df[df["combined_nav"].notna() & df["ymd"].notna()].copy()
d["ymd"] = pd.to_datetime(d["ymd"], errors="coerce")
d = d.dropna(subset=["ymd"]).sort_values("ymd")
nav = d.groupby("ymd")["combined_nav"].last().astype(float)

def block(name, s):
    s = s.dropna()
    nav_df = pd.DataFrame({"time": s.index, "nav": s.values})
    m = metrics(nav_df, pd.DataFrame(), name)
    print(f"  {name:10s} CAGR {m['cagr_pct']:6.2f}%  Sharpe {m['sharpe']:.2f}  "
          f"MaxDD {m['max_dd_pct']:6.1f}%  Calmar {m['calmar']:.2f}  ({m['n_yrs']:.2f}y)")
    return m

print(f"== {label} ==")
block("FULL", nav)
block("IS_14_19", nav[nav.index <= "2019-12-31"])
block("OOS_20_now", nav[nav.index >= "2020-01-01"])
