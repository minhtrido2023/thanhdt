# -*- coding: utf-8 -*-
"""
build_dt_variants_csv.py
========================
Generate state CSVs for the asymmetric causal confirmation variants,
formatted identical to vnindex_5state_tam_quan_v3_4b_full_history.csv
so they can be drop-in substitutes in BA v11 prod-spec runner.
"""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

def min_stay_causal_asym(states, default_min, target_state_min):
    out = states.copy()
    committed = states[0]
    pending_state = states[0]
    pending_run = 1
    out[0] = committed
    for t in range(1, len(states)):
        s = states[t]
        if s == pending_state: pending_run += 1
        else: pending_state = s; pending_run = 1
        need = target_state_min.get(pending_state, default_min)
        if pending_run >= need and pending_state != committed:
            committed = pending_state
        out[t] = committed
    return out

tq = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
state_base = tq["state"].values.astype(int)
state_raw  = tq["state_raw"].values.astype(int) if "state_raw" in tq.columns else state_base.copy()

variants = {
    "dt_10_25_25":  (10, {1: 25, 5: 25}),
    "dt_15_30_25":  (15, {1: 30, 5: 25}),
    "dt_15_25_30":  (15, {1: 25, 5: 30}),
    "dt_15_35_25":  (15, {1: 35, 5: 25}),
    "dt_7_20_20":   ( 7, {1: 20, 5: 20}),
    "dt_5_15_15":   ( 5, {1: 15, 5: 15}),
}

for name, (d_min, target_min) in variants.items():
    s = min_stay_causal_asym(state_base, d_min, target_min)
    out = pd.DataFrame({
        "time":  tq["time"].dt.strftime("%Y-%m-%d"),
        "state": s.astype(int),
        "state_raw": state_raw.astype(int),
    })
    fp = os.path.join(WORKDIR, f"vnindex_5state_{name}.csv")
    out.to_csv(fp, index=False)
    print(f"  Wrote {fp} ({len(out)} rows)")
print("Done.")
