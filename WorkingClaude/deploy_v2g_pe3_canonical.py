# -*- coding: utf-8 -*-
"""
deploy_v2g_pe3_canonical.py
===========================
Deploy v2g_pe3c (PE composite W=0.03 + S2_bull) to all 4 canonical stores.

Pipeline:
  1. Backup canonical files + BQ table with timestamp _baseline_pre_v2g_pe3_{TS}
  2. Load v2g_pe3 history (state_v2g_pe3) + previous v2g_full history (state_raw, r_score_ema)
  3. Write canonical CSVs:
      - vnindex_5state_history.csv      (time, state, state_raw)
      - vnindex_5state.csv              (same)
      - vnindex_state_history.csv       (time, Close, VNINDEX_PE, state, state_name, r_score_ema)
  4. Load into BQ table tav2_bq.vnindex_5state (REPLACE)
  5. Verify
"""
import sys, io, os, subprocess, shutil, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd
from datetime import datetime

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ = r"bq"
PROJECT = "lithe-record-440915-m9"
DATASET = "tav2_bq"
TABLE   = "vnindex_5state"

TS = datetime.now().strftime("%Y%m%d_%H%M%S")
SUFFIX = f"_baseline_pre_v2g_pe3_{TS}"
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

# ════════════════════ 1. Load v2g_pe3 + merge state_raw + r_score_ema ════════════════════
print("Loading v2g_pe3 history ...")
pe3 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2g_pe3_history.csv"))
pe3["time"] = pd.to_datetime(pe3["time"])
pe3 = pe3.sort_values("time").reset_index(drop=True)
print(f"  pe3 rows={len(pe3)}  range={pe3['time'].min().date()} → {pe3['time'].max().date()}")

# Merge state_raw + r_score_ema from previous v2g_full history
print("Loading previous v2g_full history (for state_raw + r_score_ema) ...")
prev = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2g_full_history.csv"))
prev["time"] = pd.to_datetime(prev["time"])
merged = pe3.merge(prev[["time", "state_raw", "r_score_ema"]], on="time", how="left", suffixes=("", "_prev"))
# Use prev r_score_ema where pe3 doesn't have it
if "r_score_ema" not in pe3.columns:
    pass  # picked up from prev via merge
print(f"  merged rows={len(merged)}")

# Load VNINDEX_PE_clean for legacy schema
print("Loading vnindex_full_2000_2026.csv (for VNINDEX_PE_clean) ...")
full = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_full_2000_2026.csv"), low_memory=False)
full["time"] = pd.to_datetime(full["time"])
merged = merged.merge(full[["time", "VNINDEX_PE_clean"]], on="time", how="left")

# Final canonical state = state_v2g_pe3
merged["state"] = merged["state_v2g_pe3"]

# ════════════════════ 2. Backup canonical stores ════════════════════
print(f"\n=== STEP 1: Backup canonical stores → {SUFFIX} ===")
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
    print(f"  ✗ BQ backup FAILED: {r.stderr[:500]}")
    sys.exit(1)
print(f"  ✓ BQ backup OK")

# ════════════════════ 3. Write canonical CSVs ════════════════════
print("\n=== STEP 2: Write canonical CSVs ===")

# 3a. vnindex_5state_history.csv (time, state, state_raw)
out1 = merged[["time", "state", "state_raw"]].copy()
out1["time"] = out1["time"].dt.strftime("%Y-%m-%d")
out1["state"] = out1["state"].astype("Int64")
out1["state_raw"] = out1["state_raw"].astype("Int64")
out1.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_history.csv"), index=False)
print(f"  ✓ vnindex_5state_history.csv  ({len(out1)} rows, latest={out1['time'].iloc[-1]} state={out1['state'].iloc[-1]})")

# 3b. vnindex_5state.csv (same)
out1.to_csv(os.path.join(WORKDIR, "data/vnindex_5state.csv"), index=False)
print(f"  ✓ vnindex_5state.csv         ({len(out1)} rows)")

# 3c. vnindex_state_history.csv (legacy schema)
out3 = merged[["time", "Close", "VNINDEX_PE_clean", "state", "r_score_ema"]].copy()
out3 = out3.rename(columns={"VNINDEX_PE_clean": "VNINDEX_PE"})
out3["state_name"] = out3["state"].map(STATE_NAMES)
out3 = out3[["time", "Close", "VNINDEX_PE", "state", "state_name", "r_score_ema"]]
out3["time"] = out3["time"].dt.strftime("%Y-%m-%d")
out3["state"] = out3["state"].astype("Int64")
out3.to_csv(os.path.join(WORKDIR, "data/vnindex_state_history.csv"), index=False)
print(f"  ✓ vnindex_state_history.csv  ({len(out3)} rows)")

# ════════════════════ 4. Overwrite BQ table ════════════════════
print("\n=== STEP 3: Overwrite BQ table ===")
load_csv = os.path.join(WORKDIR, "_v2g_pe3_for_bq.csv")
out1.to_csv(load_csv, index=False)
cmd_load = (f'"{BQ}" load --replace --source_format=CSV --skip_leading_rows=1 '
            f'--project_id={PROJECT} '
            f'{DATASET}.{TABLE} "{load_csv}" '
            f'time:DATE,state:INT64,state_raw:INT64')
print(f"  Loading {len(out1)} rows ...")
r = subprocess.run(cmd_load, capture_output=True, text=True, shell=True)
if r.returncode != 0:
    print(f"  ✗ BQ load FAILED: {r.stderr[:1000]}")
    sys.exit(1)
print(f"  ✓ BQ table updated")
os.unlink(load_csv)

# ════════════════════ 5. Verify ════════════════════
print("\n=== STEP 4: Verify ===")
for fn in ["data/vnindex_5state_history.csv", "data/vnindex_5state.csv"]:
    df = pd.read_csv(os.path.join(WORKDIR, fn))
    print(f"  {fn}: {len(df)} rows, latest = {df['time'].iloc[-1]} state={df['state'].iloc[-1]}")
df3 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_state_history.csv"))
print(f"  vnindex_state_history.csv: {len(df3)} rows, latest = {df3['time'].iloc[-1]} state={df3['state'].iloc[-1]} ({df3['state_name'].iloc[-1]})")

# Check BQ
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

# State distribution comparison
print("\n=== State distribution v2g_pe3 (deployed) ===")
import numpy as np
total = len(merged)
for s in [1,2,3,4,5]:
    n = int((merged["state"]==s).sum())
    print(f"  {STATE_NAMES[s]:<8}: {n:>5} ({n/total*100:5.1f}%)")

print(f"\n✓ v2g_pe3c deployment complete. Backups suffix: {SUFFIX}")
print(f"  Rollback: copy *{SUFFIX}.csv back; BQ: bq cp -f {DATASET}.{TABLE}{SUFFIX} {DATASET}.{TABLE}")
