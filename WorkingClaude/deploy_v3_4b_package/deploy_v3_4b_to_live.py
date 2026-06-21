# -*- coding: utf-8 -*-
"""
deploy_v3_4b_to_live.py
=======================
ONE-TIME DEPLOY: Replace LIVE 5-state table with v3.4b "Định Tâm".

Pipeline:
  1. Backup current `tav2_bq.vnindex_5state` → `vnindex_5state_archive_tinh_te_{TS}`
  2. Upload `vnindex_5state_tam_quan_v3_4b_full_history.csv` to
     `tav2_bq.vnindex_5state` (replace)
  3. Verify row count + last 5 rows

No production code change needed — `recommend_holistic.py` reads from
the same BQ table name, just gets new state values.

Usage:
  python deploy_v3_4b_to_live.py
  python deploy_v3_4b_to_live.py --dry-run    # show plan, don't execute
"""
import sys, io, os, subprocess, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from datetime import datetime

WORKDIR = os.environ.get("STATE_WORKDIR", os.path.dirname(os.path.abspath(__file__)))
PROJECT = "lithe-record-440915-m9"
DATASET = "tav2_bq"
LIVE_TABLE = "vnindex_5state"
SOURCE_CSV = "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"

TS = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_TABLE = f"vnindex_5state_archive_tinh_te_{TS}"

def run(cmd, capture=False):
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0:
        err = result.stderr if capture else "(see above)"
        raise RuntimeError(f"Command failed (exit {result.returncode}): {err}")
    return result.stdout if capture else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    args = ap.parse_args()

    csv_path = os.path.join(WORKDIR, SOURCE_CSV)
    if not os.path.exists(csv_path):
        sys.exit(f"❌ CSV not found: {csv_path}\n   Run daily_refresh_v3_4b.sh first to generate fresh state series.")

    print("="*70)
    print(f"DEPLOY v3.4b 'Định Tâm' → LIVE  ({'DRY-RUN' if args.dry_run else 'EXECUTE'})")
    print("="*70)
    print(f"Source CSV:    {csv_path}")
    print(f"Target table:  {PROJECT}:{DATASET}.{LIVE_TABLE}")
    print(f"Backup table:  {PROJECT}:{DATASET}.{BACKUP_TABLE}")
    print()

    if args.dry_run:
        print("Plan:")
        print(f"  1. CREATE TABLE {DATASET}.{BACKUP_TABLE} AS SELECT * FROM {DATASET}.{LIVE_TABLE}")
        print(f"  2. bq load --replace {DATASET}.{LIVE_TABLE} {SOURCE_CSV}")
        print(f"  3. Verify row count + last 5 rows")
        return

    print("--- STEP 1: Backup current LIVE ---")
    backup_sql = f"CREATE TABLE `{PROJECT}.{DATASET}.{BACKUP_TABLE}` AS SELECT * FROM `{PROJECT}.{DATASET}.{LIVE_TABLE}`"
    run(f'bq query --use_legacy_sql=false --project_id={PROJECT} "{backup_sql}"')
    print(f"  ✓ Backed up to {BACKUP_TABLE}")

    print("\n--- STEP 2: Replace LIVE with v3.4b ---")
    run(f'bq load --replace --source_format=CSV --skip_leading_rows=1 --location=asia-southeast1 '
        f'--schema=time:DATE,state:INT64,state_raw:INT64 '
        f'{PROJECT}:{DATASET}.{LIVE_TABLE} "{csv_path}"')
    print(f"  ✓ Replaced {LIVE_TABLE} with v3.4b values")

    print("\n--- STEP 3: Verify ---")
    verify_sql = f"SELECT COUNT(*) AS n, MIN(time) AS first_d, MAX(time) AS last_d FROM `{PROJECT}.{DATASET}.{LIVE_TABLE}`"
    out = run(f'bq query --use_legacy_sql=false --project_id={PROJECT} --format=csv "{verify_sql}"', capture=True)
    print(out)
    last5_sql = f"SELECT s.time, s.state, s.state_raw FROM `{PROJECT}.{DATASET}.{LIVE_TABLE}` AS s ORDER BY s.time DESC LIMIT 5"
    out = run(f'bq query --use_legacy_sql=false --project_id={PROJECT} --format=csv "{last5_sql}"', capture=True)
    print("Last 5 rows:")
    print(out)

    print("="*70)
    print("✅ DEPLOY COMPLETE")
    print(f"   Backup: {DATASET}.{BACKUP_TABLE}")
    print(f"   LIVE now serves v3.4b 'Định Tâm' state values")
    print(f"   recommend_holistic.py needs NO code change — reads same table name")
    print("="*70)
    print()
    print("⚠ ROLLBACK (if needed):")
    print(f"   bq cp {DATASET}.{BACKUP_TABLE} {DATASET}.{LIVE_TABLE}")

if __name__ == "__main__":
    main()
