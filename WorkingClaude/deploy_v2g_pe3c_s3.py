# -*- coding: utf-8 -*-
"""
deploy_v2g_pe3c_s3.py
=====================
Deploy D_pe3c_s3 (v2g_pe3c states + rolling_mode(3) + min_stay_filter(2)) as new canonical.

Justification (V11 integrated 12y backtest 50B NAV):
  vs baseline:  FULL CAGR +1.42pp (17.86 vs 16.44), Wealth +16% (×7.63 vs ×6.57),
                Mid 18-23 tied (-0.21pp), OOS +4.43pp, Sharpe -0.01 (tied),
                DD -5.9pp worse (-23.3 vs -17.4) — accepted trade-off
  vs v2g_pe3c:  FULL CAGR +0.52pp, Mid 18-23 +2.36pp (rescues volatile-period weakness),
                Pre-OOS -0.60pp, OOS -1.06pp, DD -2.8pp worse

Pipeline:
  1. Backup current 4 canonical stores with timestamp _baseline_pre_pe3c_s3_{TS}
  2. Load smoothed states from local generated file (or BQ temp table)
  3. Write 3 local CSVs + REPLACE BQ table tav2_bq.vnindex_5state
  4. Verify
"""
import sys, io, os, subprocess, shutil, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd
from datetime import datetime

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ = r"bq"
PROJECT = "lithe-record-440915-m9"
DATASET = "tav2_bq"
TABLE   = "vnindex_5state"
SOURCE_TABLE = "vnindex_5state_v2g_pe3c_s3"  # the temp table generated earlier

TS = datetime.now().strftime("%Y%m%d_%H%M%S")
SUFFIX = f"_baseline_pre_pe3c_s3_{TS}"
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

# ════════════════════ 1. Build state series in-memory (so we can write all 4 stores) ════════════════════
print("Building D_pe3c_s3 state series from local v2g_pe3c + smoothing ...")
pe3 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2g_pe3_history.csv"))
pe3["time"] = pd.to_datetime(pe3["time"])
pe3 = pe3.sort_values("time").reset_index(drop=True)
state_raw_v2g_pe3 = pe3["state_v2g_pe3"].values.astype(int)

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

state_s3 = rolling_mode(state_raw_v2g_pe3, 3)
state_s3 = min_stay_filter(state_s3, 2)
n_trans = int((np.diff(state_s3) != 0).sum())
print(f"  {len(state_s3)} rows, {n_trans} transitions after s3 smoothing")
for s in [1,2,3,4,5]:
    n = int((state_s3==s).sum())
    print(f"    state {s}: {n} ({n/len(state_s3)*100:.1f}%)")

# Load state_raw from previous canonical for the 3-col schema
canonical_prev = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_history.csv"))
canonical_prev["time"] = pd.to_datetime(canonical_prev["time"])
state_raw_by_t = dict(zip(canonical_prev["time"], canonical_prev["state_raw"]))
state_raw_arr = pe3["time"].map(state_raw_by_t).fillna(3).astype(int).values

# Load PE_clean + r_score_ema for legacy schema
full = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_full_2000_2026.csv"), low_memory=False)
full["time"] = pd.to_datetime(full["time"])
pe_by_t = dict(zip(full["time"], full["VNINDEX_PE_clean"]))
v2g_full = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2g_full_history.csv"))
v2g_full["time"] = pd.to_datetime(v2g_full["time"])
rscore_by_t = dict(zip(v2g_full["time"], v2g_full["r_score_ema"]))
close_by_t = dict(zip(pe3["time"], pe3["Close"]))

# ════════════════════ 2. Backup ════════════════════
print(f"\n=== STEP 1: Backup current canonical → {SUFFIX} ===")
for fn in ["data/vnindex_5state_history.csv", "data/vnindex_5state.csv", "data/vnindex_state_history.csv"]:
    p = os.path.join(WORKDIR, fn)
    if os.path.exists(p):
        bak = p.replace(".csv", f"{SUFFIX}.csv")
        shutil.copy2(p, bak)
        print(f"  ✓ {fn} → {os.path.basename(bak)}")

print(f"\nBackup BQ table → {DATASET}.{TABLE}{SUFFIX} ...")
cmd = f'"{BQ}" cp -f --project_id={PROJECT} {DATASET}.{TABLE} {DATASET}.{TABLE}{SUFFIX}'
r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
if r.returncode != 0:
    print(f"  ✗ BQ backup FAILED: {r.stderr[:500]}"); sys.exit(1)
print(f"  ✓ BQ backup OK")

# ════════════════════ 3. Write canonical CSVs ════════════════════
print("\n=== STEP 2: Write canonical CSVs ===")

out1 = pd.DataFrame({
    "time": pe3["time"].dt.strftime("%Y-%m-%d"),
    "state": state_s3.astype(int),
    "state_raw": state_raw_arr.astype(int),
})
out1.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_history.csv"), index=False)
print(f"  ✓ vnindex_5state_history.csv  ({len(out1)} rows, latest={out1['time'].iloc[-1]} state={out1['state'].iloc[-1]})")

out1.to_csv(os.path.join(WORKDIR, "data/vnindex_5state.csv"), index=False)
print(f"  ✓ vnindex_5state.csv         ({len(out1)} rows)")

# Legacy schema
out3 = pd.DataFrame({
    "time": pe3["time"].dt.strftime("%Y-%m-%d"),
    "Close": pe3["Close"].values,
    "VNINDEX_PE": pe3["time"].map(pe_by_t).values,
    "state": state_s3.astype(int),
    "state_name": pd.Series(state_s3).map(STATE_NAMES).values,
    "r_score_ema": pe3["time"].map(rscore_by_t).values,
})
out3.to_csv(os.path.join(WORKDIR, "data/vnindex_state_history.csv"), index=False)
print(f"  ✓ vnindex_state_history.csv  ({len(out3)} rows)")

# ════════════════════ 4. Overwrite BQ table ════════════════════
print("\n=== STEP 3: Overwrite BQ table ===")
load_csv = os.path.join(WORKDIR, "_pe3c_s3_for_bq.csv")
out1.to_csv(load_csv, index=False)
cmd_load = (f'"{BQ}" load --replace --source_format=CSV --skip_leading_rows=1 '
            f'--project_id={PROJECT} '
            f'{DATASET}.{TABLE} "{load_csv}" '
            f'time:DATE,state:INT64,state_raw:INT64')
print(f"  Loading {len(out1)} rows ...")
r = subprocess.run(cmd_load, capture_output=True, text=True, shell=True)
if r.returncode != 0:
    print(f"  ✗ BQ load FAILED: {r.stderr[:1000]}"); sys.exit(1)
print(f"  ✓ BQ table updated")
os.unlink(load_csv)

# ════════════════════ 5. Verify ════════════════════
print("\n=== STEP 4: Verify ===")
for fn in ["data/vnindex_5state_history.csv", "data/vnindex_5state.csv"]:
    df = pd.read_csv(os.path.join(WORKDIR, fn))
    print(f"  {fn}: {len(df)} rows, latest = {df['time'].iloc[-1]} state={df['state'].iloc[-1]}")
df3 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_state_history.csv"))
print(f"  vnindex_state_history.csv: {len(df3)} rows, latest = {df3['time'].iloc[-1]} state={df3['state'].iloc[-1]} ({df3['state_name'].iloc[-1]})")

print(f"  Querying BQ table ...")
with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
    f.write(f"SELECT MIN(s.time) as min_t, MAX(s.time) as max_t, COUNT(*) as n, "
            f"(SELECT s2.state FROM {DATASET}.{TABLE} AS s2 ORDER BY s2.time DESC LIMIT 1) as latest_state "
            f"FROM {DATASET}.{TABLE} AS s")
    qp = f.name
cmd_q = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=1 < "{qp}"'
r = subprocess.run(cmd_q, capture_output=True, text=True, shell=True)
os.unlink(qp)
for line in r.stdout.strip().splitlines()[-3:]:
    print(f"    {line}")

print(f"\n✓ pe3c_s3 deployment complete. Backups suffix: {SUFFIX}")
print(f"  Rollback: copy backup files; BQ: bq cp -f {DATASET}.{TABLE}{SUFFIX} {DATASET}.{TABLE}")
