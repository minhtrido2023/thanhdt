# -*- coding: utf-8 -*-
"""
generate_smoothed_v2g_pe3c.py
=============================
Generate smoothed variants of v2g_pe3c states for integrated V11 testing.

Variants:
  s3:  rolling_mode(3) + min_stay_filter(2)
  s5:  rolling_mode(5) + min_stay_filter(3)   ← main candidate (light smoothing)
  s10: rolling_mode(10) + min_stay_filter(5)  ← medium smoothing
  s15: rolling_mode(15) + min_stay_filter(7)  ← same as baseline (heavy)

Upload each to tav2_bq.vnindex_5state_v2g_pe3c_s{N} for V11 sim comparison.
"""
import os, sys, io, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ = r"bq"

# Load v2g_pe3c states
print("Loading v2g_pe3c history ...")
df = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2g_pe3_history.csv"))
df["time"] = pd.to_datetime(df["time"])
df = df.sort_values("time").reset_index(drop=True)
state_v2g_pe3 = df["state_v2g_pe3"].values.astype(int)
n = len(state_v2g_pe3)
print(f"  {n} rows, range {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}")

def rolling_mode(states, window):
    if window <= 1: return states.copy()
    out = states.copy()
    for t in range(window-1, len(states)):
        win = states[t-window+1:t+1]
        vals, counts = np.unique(win, return_counts=True)
        mc = counts.max(); cand = vals[counts==mc]
        for v in reversed(win):
            if v in cand:
                out[t] = v; break
    return out

def min_stay_filter(states, min_days):
    if min_days <= 1: return states.copy()
    out = states.copy(); changed = True
    while changed:
        changed = False; i = 0
        while i < len(out):
            j = i+1
            while j<len(out) and out[j]==out[i]: j += 1
            if (j-i) < min_days:
                fill = out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j] = fill; changed = True
            i = j
    return out

VARIANTS = [
    ("s3",  3, 2),
    ("s5",  5, 3),
    ("s10", 10, 5),
    ("s15", 15, 7),
]

# Also fetch state_raw from existing data (use the same for all variants since it's pre-smoothing)
# state_raw doesn't exist in pe3 history — but we need it for the canonical 3-col output
# Solution: read from previously deployed canonical file
canonical = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_history.csv"))
canonical["time"] = pd.to_datetime(canonical["time"])
state_raw_by_t = dict(zip(canonical["time"], canonical["state_raw"]))

state_raw_arr = df["time"].map(state_raw_by_t).fillna(3).astype(int).values

print("\nGenerating + uploading variants ...")
for label, mw, ms in VARIANTS:
    print(f"\n--- {label} (mode={mw}, min_stay={ms}) ---")
    smoothed = rolling_mode(state_v2g_pe3, mw)
    smoothed = min_stay_filter(smoothed, ms)
    # count transitions
    trans = int((np.diff(smoothed) != 0).sum())
    print(f"  transitions: {trans} (vs original {(np.diff(state_v2g_pe3) != 0).sum()})")
    # state distribution
    for s in [1,2,3,4,5]:
        n_s = int((smoothed==s).sum())
        print(f"    state {s}: {n_s} ({n_s/n*100:.1f}%)")

    # Save local
    out = pd.DataFrame({
        "time": df["time"].dt.strftime("%Y-%m-%d"),
        "state": smoothed.astype(int),
        "state_raw": state_raw_arr.astype(int),
    })
    csv_path = os.path.join(WORKDIR, f"_v2g_pe3c_{label}_for_bq.csv")
    out.to_csv(csv_path, index=False)

    # Upload to BQ
    table_name = f"vnindex_5state_v2g_pe3c_{label}"
    cmd = (f'"{BQ}" load --replace --source_format=CSV --skip_leading_rows=1 '
           f'--project_id=lithe-record-440915-m9 '
           f'tav2_bq.{table_name} "{csv_path}" '
           f'time:DATE,state:INT64,state_raw:INT64')
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if r.returncode == 0:
        print(f"  uploaded -> tav2_bq.{table_name}")
    else:
        print(f"  UPLOAD FAILED: {r.stderr[:300]}")
    os.unlink(csv_path)

print("\nDone. Tables created:")
for label, _, _ in VARIANTS:
    print(f"  tav2_bq.vnindex_5state_v2g_pe3c_{label}")
