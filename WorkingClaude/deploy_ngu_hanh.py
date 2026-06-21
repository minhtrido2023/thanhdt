# -*- coding: utf-8 -*-
"""
deploy_ngu_hanh.py
==================
Deploy/promote 5-state "Ngũ Hành" iterations following the LIVE / STAGING / ARCHIVE convention.

Usage:
  python deploy_ngu_hanh.py --to-staging --source <state_csv> [--codename <NAME>]
      Build staging from a local state CSV (must contain time + state columns).
      Uploads to tav2_bq.vnindex_5state_staging + writes vnindex_5state_staging.csv.

  python deploy_ngu_hanh.py --promote [--archive-as <codename>]
      Promote STAGING to LIVE.
      Old LIVE → archive_<codename>. Default codename = "prev_<TS>" if not provided.

  python deploy_ngu_hanh.py --drop-staging
      Drop staging tables/CSVs (test failed, abandon candidate).

  python deploy_ngu_hanh.py --status
      Show current registry status (LIVE / STAGING / ARCHIVE).

  python deploy_ngu_hanh.py --rollback-to <codename>
      Restore archived version as LIVE.
"""
import sys, io, os, subprocess, shutil, tempfile, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd
from datetime import datetime

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
BQ = r"bq"
PROJECT = "lithe-record-440915-m9"
DATASET = "tav2_bq"
LIVE_TABLE = "vnindex_5state"
STAGING_TABLE = "vnindex_5state_staging"
STATE_NAMES = {1:"CRISIS", 2:"BEAR", 3:"NEUTRAL", 4:"BULL", 5:"EX-BULL"}

def bq_run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, shell=True)

def list_tables():
    cmd = f'"{BQ}" ls --max_results=100 --project_id={PROJECT} {DATASET}'
    r = bq_run(cmd)
    return [line.split()[0] for line in r.stdout.splitlines()
            if line.strip().startswith("vnindex_5state")]

def show_status():
    print("=" * 70)
    print("Ngũ Hành 5-state Registry Status")
    print("=" * 70)
    tables = list_tables()
    live = [t for t in tables if t == LIVE_TABLE]
    staging = [t for t in tables if t == STAGING_TABLE]
    archives = [t for t in tables if t.startswith("vnindex_5state_archive_")]
    print("\n🟢 LIVE:")
    for t in live: print(f"  tav2_bq.{t}")
    if not live: print("  (none)")
    print("\n🟡 STAGING:")
    for t in staging: print(f"  tav2_bq.{t}")
    if not staging: print("  (none)")
    print("\n📦 ARCHIVE:")
    for t in archives: print(f"  tav2_bq.{t}")
    if not archives: print("  (none)")
    # latest live state
    if live:
        with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False, encoding="utf-8") as f:
            f.write(f"SELECT MAX(s.time) AS max_t, (SELECT s2.state FROM {DATASET}.{LIVE_TABLE} AS s2 ORDER BY s2.time DESC LIMIT 1) AS latest_state FROM {DATASET}.{LIVE_TABLE} AS s")
            qp = f.name
        cmd = f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=1 < "{qp}"'
        r = bq_run(cmd); os.unlink(qp)
        if r.returncode == 0:
            lines = r.stdout.strip().splitlines()
            if len(lines) >= 2:
                print(f"\nLIVE latest row: {lines[1]}")

def to_staging(source_csv, codename=None):
    print(f"=== Build STAGING from {source_csv} ===")
    df = pd.read_csv(source_csv)
    if "time" not in df.columns:
        print("ERROR: source CSV must have 'time' column"); sys.exit(1)
    state_col = None
    for c in ["state","state_v2g_pe3","state_v2g","state_smoothed"]:
        if c in df.columns: state_col = c; break
    if state_col is None:
        print("ERROR: no state column found"); sys.exit(1)
    df["time"] = pd.to_datetime(df["time"]).dt.strftime("%Y-%m-%d")
    raw_col = "state_raw" if "state_raw" in df.columns else None
    out = pd.DataFrame({"time": df["time"], "state": df[state_col].astype(int)})
    if raw_col is None:
        # fetch state_raw from existing LIVE
        canonical = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_history.csv"))
        canonical["time"] = pd.to_datetime(canonical["time"]).dt.strftime("%Y-%m-%d")
        raw_map = dict(zip(canonical["time"], canonical["state_raw"]))
        out["state_raw"] = out["time"].map(raw_map).fillna(3).astype(int)
    else:
        out["state_raw"] = df[raw_col].astype(int)
    # Local CSV
    out_local = os.path.join(WORKDIR, "data/vnindex_5state_staging.csv")
    out.to_csv(out_local, index=False)
    print(f"  Wrote local: {out_local} ({len(out)} rows)")
    # BQ upload
    load_csv = os.path.join(WORKDIR, "_staging_load.csv")
    out.to_csv(load_csv, index=False)
    cmd = (f'"{BQ}" load --replace --source_format=CSV --skip_leading_rows=1 '
           f'--project_id={PROJECT} {DATASET}.{STAGING_TABLE} "{load_csv}" '
           f'time:DATE,state:INT64,state_raw:INT64')
    r = bq_run(cmd); os.unlink(load_csv)
    if r.returncode == 0:
        print(f"  Uploaded → tav2_bq.{STAGING_TABLE}")
    else:
        print(f"  Upload FAILED: {r.stderr[:300]}")
        sys.exit(1)
    if codename:
        print(f"  Codename: {codename}")

def promote(archive_as=None):
    print("=== Promote STAGING → LIVE ===")
    # Check staging exists
    cmd = f'"{BQ}" show --project_id={PROJECT} {DATASET}.{STAGING_TABLE}'
    r = bq_run(cmd)
    if r.returncode != 0:
        print(f"ERROR: staging table {DATASET}.{STAGING_TABLE} does not exist")
        sys.exit(1)

    if archive_as is None:
        TS = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_as = f"prev_{TS}"
    archive_table = f"vnindex_5state_archive_{archive_as}"

    # 1. Archive current LIVE
    print(f"  Archive current LIVE → tav2_bq.{archive_table}")
    cmd = f'"{BQ}" cp -f --project_id={PROJECT} {DATASET}.{LIVE_TABLE} {DATASET}.{archive_table}'
    r = bq_run(cmd)
    if r.returncode != 0:
        print(f"  ✗ archive FAILED: {r.stderr[:200]}"); sys.exit(1)
    print("    BQ archived")
    # Local backup
    for fn in ["data/vnindex_5state.csv", "data/vnindex_5state_history.csv", "data/vnindex_state_history.csv"]:
        src = os.path.join(WORKDIR, fn)
        if os.path.exists(src):
            ext = "_archive_" + archive_as
            dst = src.replace(".csv", f"{ext}.csv")
            shutil.copy2(src, dst)
            print(f"    {fn} → {os.path.basename(dst)}")

    # 2. Copy staging → LIVE
    print(f"  Promote staging → LIVE")
    cmd = f'"{BQ}" cp -f --project_id={PROJECT} {DATASET}.{STAGING_TABLE} {DATASET}.{LIVE_TABLE}'
    r = bq_run(cmd)
    if r.returncode != 0:
        print(f"  ✗ promote FAILED: {r.stderr[:200]}"); sys.exit(1)
    print("    BQ live updated")
    # Local: staging.csv → live CSVs
    staging_csv = os.path.join(WORKDIR, "data/vnindex_5state_staging.csv")
    if os.path.exists(staging_csv):
        df = pd.read_csv(staging_csv)
        df.to_csv(os.path.join(WORKDIR, "data/vnindex_5state.csv"), index=False)
        df.to_csv(os.path.join(WORKDIR, "data/vnindex_5state_history.csv"), index=False)
        # Legacy schema (recompute Close + PE + r_score_ema from cached data if available)
        try:
            pe3 = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2g_pe3_history.csv"))
            full = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_full_2000_2026.csv"), low_memory=False)
            v2gf = pd.read_csv(os.path.join(WORKDIR, "data/vnindex_5state_v2g_full_history.csv"))
            pe3["time"] = pd.to_datetime(pe3["time"])
            full["time"] = pd.to_datetime(full["time"])
            v2gf["time"] = pd.to_datetime(v2gf["time"])
            df["time"] = pd.to_datetime(df["time"])
            close_map = dict(zip(pe3["time"], pe3["Close"]))
            pe_map = dict(zip(full["time"], full["VNINDEX_PE_clean"]))
            rs_map = dict(zip(v2gf["time"], v2gf["r_score_ema"]))
            df["Close"] = df["time"].map(close_map)
            df["VNINDEX_PE"] = df["time"].map(pe_map)
            df["state_name"] = df["state"].map(STATE_NAMES)
            df["r_score_ema"] = df["time"].map(rs_map)
            out3 = df[["time","Close","VNINDEX_PE","state","state_name","r_score_ema"]]
            out3["time"] = out3["time"].dt.strftime("%Y-%m-%d")
            out3.to_csv(os.path.join(WORKDIR, "data/vnindex_state_history.csv"), index=False)
        except Exception as e:
            print(f"  warning: legacy schema rebuild skipped ({e})")
        print(f"    Local CSVs updated from staging")
    # 3. Drop staging
    cmd = f'"{BQ}" rm -f -t --project_id={PROJECT} {DATASET}.{STAGING_TABLE}'
    bq_run(cmd)
    if os.path.exists(staging_csv): os.unlink(staging_csv)
    print(f"  Staging dropped")
    print(f"\n✓ Promoted. Old LIVE archived as: {archive_table}")

def drop_staging():
    print("=== Drop STAGING ===")
    cmd = f'"{BQ}" rm -f -t --project_id={PROJECT} {DATASET}.{STAGING_TABLE}'
    r = bq_run(cmd)
    print(f"  BQ: {'OK' if r.returncode==0 else 'FAIL'}")
    staging_csv = os.path.join(WORKDIR, "data/vnindex_5state_staging.csv")
    if os.path.exists(staging_csv):
        os.unlink(staging_csv); print(f"  Local: dropped")

def rollback_to(codename):
    archive_table = f"vnindex_5state_archive_{codename}"
    print(f"=== Rollback LIVE ← {archive_table} ===")
    cmd = f'"{BQ}" show --project_id={PROJECT} {DATASET}.{archive_table}'
    r = bq_run(cmd)
    if r.returncode != 0:
        print(f"ERROR: archive table {archive_table} does not exist"); sys.exit(1)
    # Archive current live before overwriting
    TS = datetime.now().strftime("%Y%m%d_%H%M%S")
    safety_archive = f"vnindex_5state_archive_pre_rollback_{TS}"
    print(f"  Safety archive current LIVE → tav2_bq.{safety_archive}")
    bq_run(f'"{BQ}" cp -f --project_id={PROJECT} {DATASET}.{LIVE_TABLE} {DATASET}.{safety_archive}')
    # Restore
    print(f"  Restore: cp {archive_table} → {LIVE_TABLE}")
    r = bq_run(f'"{BQ}" cp -f --project_id={PROJECT} {DATASET}.{archive_table} {DATASET}.{LIVE_TABLE}')
    if r.returncode == 0:
        print(f"  ✓ BQ rollback OK")
    else:
        print(f"  ✗ rollback FAILED: {r.stderr[:200]}")
    # Local: restore from corresponding local archive if exists
    local_archive = os.path.join(WORKDIR, f"vnindex_5state_archive_{codename}.csv")
    if os.path.exists(local_archive):
        shutil.copy2(local_archive, os.path.join(WORKDIR, "data/vnindex_5state.csv"))
        shutil.copy2(local_archive, os.path.join(WORKDIR, "data/vnindex_5state_history.csv"))
        h = os.path.join(WORKDIR, f"vnindex_state_history_archive_{codename}.csv")
        if os.path.exists(h):
            shutil.copy2(h, os.path.join(WORKDIR, "data/vnindex_state_history.csv"))
        print(f"  ✓ Local CSVs restored from {local_archive}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--to-staging", action="store_true", help="Build staging from --source CSV")
    parser.add_argument("--source", help="Source CSV with 'time' + state column")
    parser.add_argument("--codename", help="Codename for staging (informational)")
    parser.add_argument("--promote", action="store_true", help="Promote STAGING → LIVE")
    parser.add_argument("--archive-as", help="Codename for archived old-LIVE (default: prev_<TS>)")
    parser.add_argument("--drop-staging", action="store_true", help="Drop staging without promote")
    parser.add_argument("--status", action="store_true", help="Show registry status")
    parser.add_argument("--rollback-to", help="Rollback LIVE to archive_<codename>")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.to_staging:
        if not args.source: print("ERROR: --to-staging requires --source"); sys.exit(1)
        to_staging(args.source, args.codename)
    elif args.promote:
        promote(args.archive_as)
    elif args.drop_staging:
        drop_staging()
    elif args.rollback_to:
        rollback_to(args.rollback_to)
    else:
        parser.print_help()
