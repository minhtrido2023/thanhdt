# -*- coding: utf-8 -*-
"""
reorganize_5state_tables.py
===========================
Rename BQ vnindex_5state archive tables to codename convention,
drop temp tables that are no longer needed.

After this:
  LIVE     : tav2_bq.vnindex_5state               (= Ngũ Hành — Tinh Tế)
  STAGING  : tav2_bq.vnindex_5state_staging       (created on demand)
  ARCHIVE  : tav2_bq.vnindex_5state_archive_co_dien      (= original baseline)
             tav2_bq.vnindex_5state_archive_pe3c_raw    (= v2g_pe3c without smoothing)
             tav2_bq.vnindex_5state_archive_v2g          (= v2g 2026-05-12 archive)
"""
import os, sys, io, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BQ = r"bq"
PROJECT = "lithe-record-440915-m9"
DATASET = "tav2_bq"

# Rename map: source → target (codename)
RENAME = [
    ("vnindex_5state_baseline_pre_v2g_20260517_144254",       "vnindex_5state_archive_co_dien"),
    ("vnindex_5state_baseline_pre_pe3c_s3_20260521_021831",   "vnindex_5state_archive_pe3c_raw"),
    ("vnindex_5state_v2g_archive_20260512",                    "vnindex_5state_archive_v2g_old"),
]

# Tables to drop (no longer needed):
# - baseline_pre_v2g_pe3 = duplicate of co_dien
# - v2g_only, pe3c_s5/s10/s15 = research-only temp tables
# - v2g_pe3c_s3 = the staging that was promoted; keeps copy as archive_pe3c_raw
DROPS = [
    "vnindex_5state_baseline_pre_v2g_pe3_20260521_004032",   # dup of co_dien
    "vnindex_5state_v2g_only",                                # research temp
    "vnindex_5state_v2g_pe3c_s3",                             # already in LIVE, no need
    "vnindex_5state_v2g_pe3c_s5",
    "vnindex_5state_v2g_pe3c_s10",
    "vnindex_5state_v2g_pe3c_s15",
]

def bq_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, shell=True)

print("=" * 80)
print("REORGANIZE 5-state BQ tables → codename convention")
print("=" * 80)

print("\n--- STEP 1: Rename archives ---")
for src, dst in RENAME:
    print(f"\n  {src}")
    print(f"  → {dst}")
    cp_cmd = f'"{BQ}" cp -f --project_id={PROJECT} {DATASET}.{src} {DATASET}.{dst}'
    r = bq_cmd(cp_cmd)
    if r.returncode == 0:
        print(f"    cp OK")
        del_cmd = f'"{BQ}" rm -f -t --project_id={PROJECT} {DATASET}.{src}'
        rd = bq_cmd(del_cmd)
        if rd.returncode == 0:
            print(f"    drop original OK")
        else:
            print(f"    drop FAILED: {rd.stderr[:200]}")
    else:
        print(f"    cp FAILED: {r.stderr[:200]}")

print("\n--- STEP 2: Drop temp tables ---")
for t in DROPS:
    cmd = f'"{BQ}" rm -f -t --project_id={PROJECT} {DATASET}.{t}'
    r = bq_cmd(cmd)
    status = "OK" if r.returncode == 0 else f"FAIL: {r.stderr[:100]}"
    print(f"  drop {t}: {status}")

print("\n--- STEP 3: Verify final state ---")
cmd = f'"{BQ}" ls --max_results=100 --project_id={PROJECT} {DATASET}'
r = bq_cmd(cmd)
print("Tables remaining (filtered to vnindex_5state*):")
for line in r.stdout.splitlines():
    if "vnindex_5state" in line.lower():
        print(f"  {line.strip()}")

print("\nDone.")
