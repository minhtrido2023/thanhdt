#!/usr/bin/env python3
"""Nightly BQ snapshot builder.

Pulls SIGNAL_V11 + VNI_QUERY from BigQuery (full 2014-01-01 → today range)
and saves them as parquet files in data/snapshots/. Subsequent experiment runs
can load from parquet instead of hitting BQ each time.

Usage:
    python scripts/build_snapshot.py [--dry-run]

Outputs:
    data/snapshots/signal_YYYYMMDD.parquet  — signal/classification rows
    data/snapshots/vni_YYYYMMDD.parquet     — VNINDEX close prices
    data/snapshots/latest_date.txt          — today's date (YYYY-MM-DD)
"""
import os
import sys
import time
import subprocess
import tempfile
from datetime import date, datetime
from io import StringIO

import pandas as pd

# ── paths ──────────────────────────────────────────────────────────────────
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
SNAPSHOT_DIR = os.path.join(WORKDIR, "data", "snapshots")
PROJECT = "lithe-record-440915-m9"
BQ_BIN = "bq"

START_DATE = "2014-01-01"

# ── SQL: import the canonical production signal query ──────────────────────
sys.path.insert(0, WORKDIR)
from signal_v11_sql import SIGNAL_V11 as SIGNAL_QUERY  # noqa: E402

# Unused legacy SIGNAL_QUERY was simulate_holistic_nav.py's standalone main()
# query (referenced t.VNINDEX_RSI_Max3M which does NOT exist in tav2_bq.ticker).
# pt_v23_audit_2014.py and all production scripts use SIGNAL_V11, so we snapshot
# SIGNAL_V11 here.  Variable alias kept as SIGNAL_QUERY so downstream code
# references (signal_sql = SIGNAL_QUERY.format(...)) remain unchanged.

VNI_QUERY = """
SELECT t.time, t.Close
FROM tav2_bq.ticker AS t
WHERE t.ticker = 'VNINDEX'
  AND t.time BETWEEN DATE '{start}' AND DATE '{end}'
ORDER BY t.time
"""


def _bq_run(sql: str) -> pd.DataFrame:
    """Execute a BQ SQL query and return result as DataFrame."""
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql)
        sql_path = f.name
    try:
        cmd = (f'{BQ_BIN} query --use_legacy_sql=false --project_id={PROJECT} '
               f'--format=csv --max_rows=5000000 < "{sql_path}"')
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
    finally:
        os.unlink(sql_path)
    if not out.stdout or not out.stdout.strip():
        return pd.DataFrame()
    return pd.read_csv(StringIO(out.stdout))


def _dry_run_estimate(sql: str, label: str) -> None:
    """Print bytes-processed estimate for a query without running it."""
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql)
        sql_path = f.name
    try:
        cmd = (f'{BQ_BIN} query --use_legacy_sql=false --dry_run --project_id={PROJECT} '
               f'< "{sql_path}"')
        out = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    finally:
        os.unlink(sql_path)
    # dry-run output goes to stderr
    stderr = out.stderr or ""
    stdout = out.stdout or ""
    combined = stderr + stdout
    for line in combined.splitlines():
        if "bytes" in line.lower() or "processed" in line.lower():
            print(f"  [{label} dry-run] {line.strip()}")
            return
    # fallback: print last non-empty line
    lines = [l for l in combined.splitlines() if l.strip()]
    if lines:
        print(f"  [{label} dry-run] {lines[-1].strip()}")


def build_snapshot(dry_run: bool = False) -> None:
    today_str = date.today().strftime("%Y%m%d")
    today_iso = date.today().isoformat()
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    signal_path = os.path.join(SNAPSHOT_DIR, f"signal_{today_str}.parquet")
    vni_path = os.path.join(SNAPSHOT_DIR, f"vni_{today_str}.parquet")
    latest_path = os.path.join(SNAPSHOT_DIR, "latest_date.txt")

    signal_sql = SIGNAL_QUERY.format(start=START_DATE, end=today_iso)
    vni_sql = VNI_QUERY.format(start=START_DATE, end=today_iso)

    t0_total = time.time()

    # ── dry-run estimate first ──────────────────────────────────────────────
    print(f"[build_snapshot] date={today_iso}  start={START_DATE}")
    print("  Estimating query sizes (dry-run)...")
    _dry_run_estimate(signal_sql, "SIGNAL")
    _dry_run_estimate(vni_sql, "VNI")

    if dry_run:
        print("[build_snapshot] --dry-run: stopping after cost estimate.")
        return

    # ── SIGNAL_QUERY ───────────────────────────────────────────────────────
    print(f"\n  Pulling SIGNAL_QUERY ({START_DATE} → {today_iso})...")
    t0 = time.time()
    sig_df = _bq_run(signal_sql)
    elapsed_sig = time.time() - t0
    print(f"  -> {len(sig_df):,} rows in {elapsed_sig:.1f}s")

    if sig_df.empty:
        print("  WARNING: SIGNAL_QUERY returned 0 rows — snapshot aborted.")
        sys.exit(1)

    # parse date column
    sig_df["time"] = pd.to_datetime(sig_df["time"])

    print(f"  Saving to {signal_path} ...")
    sig_df.to_parquet(signal_path, index=False, engine="pyarrow")
    sig_size_mb = os.path.getsize(signal_path) / 1024 / 1024
    print(f"  -> {sig_size_mb:.1f} MB written")

    # ── VNI_QUERY ──────────────────────────────────────────────────────────
    print(f"\n  Pulling VNI_QUERY ({START_DATE} → {today_iso})...")
    t0 = time.time()
    vni_df = _bq_run(vni_sql)
    elapsed_vni = time.time() - t0
    print(f"  -> {len(vni_df):,} rows in {elapsed_vni:.1f}s")

    if vni_df.empty:
        print("  WARNING: VNI_QUERY returned 0 rows.")
    else:
        vni_df["time"] = pd.to_datetime(vni_df["time"])
        print(f"  Saving to {vni_path} ...")
        vni_df.to_parquet(vni_path, index=False, engine="pyarrow")
        vni_size_mb = os.path.getsize(vni_path) / 1024 / 1024
        print(f"  -> {vni_size_mb:.1f} MB written")

    # ── latest_date.txt ────────────────────────────────────────────────────
    with open(latest_path, "w") as f:
        f.write(today_iso + "\n")
    print(f"\n  latest_date.txt -> {today_iso}")

    # ── summary ────────────────────────────────────────────────────────────
    total_elapsed = time.time() - t0_total
    total_mb = sig_size_mb + (vni_size_mb if not vni_df.empty else 0)
    print("\n" + "=" * 60)
    print("  BQ SNAPSHOT SUMMARY")
    print("=" * 60)
    print(f"  date          : {today_iso}")
    print(f"  signal rows   : {len(sig_df):,}")
    print(f"  vni rows      : {len(vni_df):,}")
    print(f"  signal file   : {signal_path}  ({sig_size_mb:.1f} MB)")
    if not vni_df.empty:
        print(f"  vni file      : {vni_path}  ({vni_size_mb:.1f} MB)")
    print(f"  total size    : {total_mb:.1f} MB")
    print(f"  total time    : {total_elapsed:.1f}s")
    print("=" * 60)

    # ── prune old snapshots (keep last 7 days) ─────────────────────────────
    _prune_old_snapshots(keep=7)


def _prune_old_snapshots(keep: int = 7) -> None:
    """Remove parquet files older than `keep` most-recent date-stamped sets."""
    import glob
    signal_files = sorted(glob.glob(os.path.join(SNAPSHOT_DIR, "signal_*.parquet")))
    vni_files = sorted(glob.glob(os.path.join(SNAPSHOT_DIR, "vni_*.parquet")))

    for flist in (signal_files, vni_files):
        to_delete = flist[:-keep] if len(flist) > keep else []
        for f in to_delete:
            os.remove(f)
            print(f"  pruned old snapshot: {os.path.basename(f)}")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    build_snapshot(dry_run=dry)
