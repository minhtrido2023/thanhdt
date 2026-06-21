# -*- coding: utf-8 -*-
"""
deploy_v2g_canonical.py
=======================
Overwrite the 4 canonical state stores with v2g states:
  1. vnindex_5state_history.csv  (time, state, state_raw)
  2. vnindex_5state.csv          (time, state, state_raw)
  3. vnindex_state_history.csv   (time, Close, VNINDEX_PE, state, state_name, r_score_ema)
  4. tav2_bq.vnindex_5state      BigQuery table (time, state, state_raw)

All originals backed up to *_baseline_pre_v2g_{timestamp}.csv before overwrite.
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
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

# ── Load v2g source ──
print("Loading v2g source ...")
src = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_v2g_full_history.csv"))
src["time"] = pd.to_datetime(src["time"])
src = src.sort_values("time").reset_index(drop=True)
print(f"  v2g source: {len(src)} rows, {src['time'].min().date()} → {src['time'].max().date()}")

# ════════════════════════════════════════════════════════
# 1. Backup all canonical files
# ════════════════════════════════════════════════════════
print("\n=== STEP 1: Backup canonical files ===")
files_to_backup = ["vnindex_5state_history.csv", "vnindex_5state.csv", "vnindex_state_history.csv"]
for fn in files_to_backup:
    src_p = os.path.join(WORKDIR, fn)
    if os.path.exists(src_p):
        bak = src_p.replace(".csv", f"_baseline_pre_v2g_{TS}.csv")
        shutil.copy2(src_p, bak)
        print(f"  ✓ {fn} → {os.path.basename(bak)}")
    else:
        print(f"  - {fn}: not found, skipping backup")

# BQ table backup: copy to vnindex_5state_baseline_pre_v2g_TS
print(f"\nBackup BQ table {DATASET}.{TABLE} → {DATASET}.{TABLE}_baseline_pre_v2g_{TS} ...")
cmd_bak = f'"{BQ}" cp -f --project_id={PROJECT} {DATASET}.{TABLE} {DATASET}.{TABLE}_baseline_pre_v2g_{TS}'
r = subprocess.run(cmd_bak, capture_output=True, text=True, shell=True)
if r.returncode == 0:
    print(f"  ✓ BQ backup OK: {DATASET}.{TABLE}_baseline_pre_v2g_{TS}")
else:
    print(f"  ✗ BQ backup FAILED: {r.stderr[:500]}")
    sys.exit(1)

# ════════════════════════════════════════════════════════
# 2. Write canonical CSVs (3 schemas)
# ════════════════════════════════════════════════════════
print("\n=== STEP 2: Write canonical CSVs ===")

# 2a. vnindex_5state_history.csv (time, state, state_raw) — full 2000-now
out1 = src[["time", "state_v2g", "state_raw"]].rename(columns={"state_v2g":"state"})
out1["time"] = out1["time"].dt.strftime("%Y-%m-%d")
out1.to_csv(os.path.join(WORKDIR, "vnindex_5state_history.csv"), index=False)
print(f"  ✓ vnindex_5state_history.csv  ({len(out1)} rows, {out1['time'].iloc[0]} → {out1['time'].iloc[-1]})")

# 2b. vnindex_5state.csv (time, state, state_raw) — full
out2 = out1.copy()
out2.to_csv(os.path.join(WORKDIR, "vnindex_5state.csv"), index=False)
print(f"  ✓ vnindex_5state.csv          ({len(out2)} rows)")

# 2c. vnindex_state_history.csv (time, Close, VNINDEX_PE, state, state_name, r_score_ema)
#     Original schema includes Close + PE; pull PE from cached full
full = pd.read_csv(os.path.join(WORKDIR, "vnindex_full_2000_2026.csv"))
full["time"] = pd.to_datetime(full["time"])
m = src[["time","Close","state_v2g","r_score_ema"]].merge(
    full[["time","VNINDEX_PE"]], on="time", how="left")
m = m.rename(columns={"state_v2g":"state"})
m["state_name"] = m["state"].map(STATE_NAMES)
m = m[["time","Close","VNINDEX_PE","state","state_name","r_score_ema"]]
m["time"] = m["time"].dt.strftime("%Y-%m-%d")
m.to_csv(os.path.join(WORKDIR, "vnindex_state_history.csv"), index=False)
print(f"  ✓ vnindex_state_history.csv   ({len(m)} rows)")

# ════════════════════════════════════════════════════════
# 3. Overwrite BQ table
# ════════════════════════════════════════════════════════
print("\n=== STEP 3: Overwrite BQ table ===")
load_csv = os.path.join(WORKDIR, "_v2g_for_bq.csv")
out1.to_csv(load_csv, index=False)

# bq load --replace
cmd_load = (f'"{BQ}" load --replace --source_format=CSV --skip_leading_rows=1 '
            f'--project_id={PROJECT} '
            f'{DATASET}.{TABLE} "{load_csv}" '
            f'time:DATE,state:INT64,state_raw:INT64')
print(f"  Loading {len(out1)} rows ...")
r = subprocess.run(cmd_load, capture_output=True, text=True, shell=True)
if r.returncode == 0:
    print(f"  ✓ BQ table updated")
else:
    print(f"  ✗ BQ load failed: {r.stderr[:1000]}")
    sys.exit(1)
os.unlink(load_csv)

# ════════════════════════════════════════════════════════
# 4. Verify
# ════════════════════════════════════════════════════════
print("\n=== STEP 4: Verify ===")
# Verify local CSVs
for fn in ["vnindex_5state_history.csv", "vnindex_5state.csv"]:
    df = pd.read_csv(os.path.join(WORKDIR, fn))
    print(f"  {fn}: {len(df)} rows, latest = {df['time'].iloc[-1]} state={df['state'].iloc[-1]}")

df3 = pd.read_csv(os.path.join(WORKDIR, "vnindex_state_history.csv"))
print(f"  vnindex_state_history.csv: {len(df3)} rows, latest = {df3['time'].iloc[-1]} state={df3['state'].iloc[-1]} ({df3['state_name'].iloc[-1]})")

# Verify BQ table
print(f"  Querying BQ table ...")
with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
    f.write(f"SELECT MIN(s.time) as min_t, MAX(s.time) as max_t, COUNT(*) as n, "
            f"(SELECT s2.state FROM {DATASET}.{TABLE} AS s2 ORDER BY s2.time DESC LIMIT 1) as latest_state "
            f"FROM {DATASET}.{TABLE} AS s")
    qp = f.name
cmd_q = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=1 < "{qp}"'
r = subprocess.run(cmd_q, capture_output=True, text=True, shell=True)
os.unlink(qp)
print(f"  BQ verify:")
for line in r.stdout.strip().splitlines()[-3:]:
    print(f"    {line}")

print(f"\n✓ Deployment complete. Backups retained with suffix _baseline_pre_v2g_{TS}")
print(f"  Rollback: copy backup files back; restore BQ via: bq cp -f {DATASET}.{TABLE}_baseline_pre_v2g_{TS} {DATASET}.{TABLE}")
