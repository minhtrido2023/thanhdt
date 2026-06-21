# -*- coding: utf-8 -*-
"""Head-to-head: Tinh Te (live) vs v3.4b vs DT_10_25_25 on the pure-VNINDEX money sim."""
import sys, io, os
import numpy as np, pandas as pd
from simulate_state_timing import simulate_timing, print_result

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

SERIES = {
    "Tinh_Te":     "vnindex_5state.csv",
    "v3.4b":       "_cmp_v34b.csv",
    "DT_10_25_25": "vnindex_5state_dt_10_25_25.csv",
}

def n_transitions(df, start=None):
    d = df.copy()
    d["time"] = pd.to_datetime(d["time"])
    if start: d = d[d["time"] >= start]
    s = d.sort_values("time")["state"].astype(int).values
    return int((s[1:] != s[:-1]).sum())

def state_dist(df, start=None):
    d = df.copy(); d["time"] = pd.to_datetime(d["time"])
    if start: d = d[d["time"] >= start]
    vc = d["state"].astype(int).value_counts(normalize=True).sort_index()
    return {int(k): round(v*100,1) for k,v in vc.items()}

dfs = {k: pd.read_csv(os.path.join(WORKDIR, v)) for k,v in SERIES.items()}

for period_label, start in [("FULL 2000-2026", None), ("MODERN 2014-2026", "2014-01-01")]:
    print("="*92)
    print(f"  {period_label}   (pure VNINDEX allocation sim, 1B VND, T+1, TC0.1%, dep6%/bor10%)")
    print("="*92)
    # benchmark B&H
    bh = pd.DataFrame({"time": dfs["v3.4b"]["time"], "state": 4})
    res_bh = simulate_timing(bh, start_date=start)
    print_result("Buy&Hold (100% VNI)", res_bh)
    print(f"  {'':25} transitions={'n/a':>5}")
    rows = []
    for name, df in dfs.items():
        res = simulate_timing(df, start_date=start)
        nt = n_transitions(df, start)
        print_result(name, res, ref=res_bh)
        # money-per-transition efficiency: final NAV per transition
        print(f"  {'':25} transitions={nt:>5}   dist={state_dist(df,start)}")
        rows.append((name, res, nt))
    print()
