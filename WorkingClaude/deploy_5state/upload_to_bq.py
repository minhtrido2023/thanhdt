# -*- coding: utf-8 -*-
"""Upload vnindex_5state_history.csv → tav2_bq.vnindex_5state (OVERWRITE).

This is the table that `recommend_holistic.py` reads via LEFT JOIN to get the
current market regime state for each historical day.

Schema: time:DATE, state:INT64, state_raw:INT64

Run AFTER vnindex_5state_system.py daily.

Usage:
  python upload_to_bq.py                # overwrite full table
  python upload_to_bq.py --dry-run      # show what would happen
"""
import argparse
import io
import os
import subprocess
import sys

import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

WORKDIR = os.environ.get("BAVN_WORKDIR",
                          os.path.dirname(os.path.abspath(__file__)))
PROJECT = "lithe-record-440915-m9"
DATASET = "tav2_bq"
TABLE   = "vnindex_5state"


def _find_bq():
    import shutil as _sh
    for cand in [os.environ.get("BQ_BIN"),
                 _sh.which("bq"), _sh.which("bq.cmd"),
                 "/usr/local/google-cloud-sdk/bin/bq",
                 os.path.expanduser("~/google-cloud-sdk/bin/bq"),
                 r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd",
                 r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd",
                 os.path.expanduser(r"~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd")]:
        if cand and os.path.exists(cand):
            return cand
    raise RuntimeError("bq CLI not found. Install Google Cloud SDK or set BQ_BIN env var.")

BQ = _find_bq()


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    src = os.path.join(WORKDIR, "data/vnindex_5state_history.csv")
    if not os.path.exists(src):
        print(f"ERROR: {src} not found. Run vnindex_5state_system.py first.",
              file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(src)
    df["time"] = pd.to_datetime(df["time"]).dt.strftime("%Y-%m-%d")
    print(f"=== Upload to BQ: {DATASET}.{TABLE} ===")
    print(f"   Source: {src}")
    print(f"   Rows:   {len(df):,}")
    print(f"   Latest: {df['time'].iloc[-1]} state={df['state'].iloc[-1]} "
          f"(state_raw={df['state_raw'].iloc[-1]})")

    if args.dry_run:
        print("\n[dry-run] Would execute:")
        print(f"   bq load --replace --source_format=CSV --skip_leading_rows=1 \\")
        print(f"      --project_id={PROJECT} \\")
        print(f"      {DATASET}.{TABLE} <csv> \\")
        print(f"      time:DATE,state:INT64,state_raw:INT64")
        sys.exit(0)

    # Save as a clean CSV with just (time, state, state_raw)
    clean = os.path.join(WORKDIR, "_5state_for_bq.csv")
    df[["time", "state", "state_raw"]].to_csv(clean, index=False)

    cmd = (f'"{BQ}" load --replace --source_format=CSV --skip_leading_rows=1 '
           f'--project_id={PROJECT} '
           f'{DATASET}.{TABLE} "{clean}" '
           f'time:DATE,state:INT64,state_raw:INT64')
    print(f"\nLoading ...")
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    try:
        os.unlink(clean)
    except OSError:
        pass

    if r.returncode == 0:
        print(f"✓ BQ table updated ({DATASET}.{TABLE})")
    else:
        print(f"✗ BQ load FAILED:")
        print(r.stderr[:2000])
        sys.exit(1)

    # Quick verify
    print("\nVerifying ...")
    verify_sql = (f'SELECT COUNT(*) AS n, MAX(time) AS latest_date '
                  f'FROM `{PROJECT}.{DATASET}.{TABLE}`')
    cmd = (f'"{BQ}" query --use_legacy_sql=false --project_id={PROJECT} '
           f'--format=csv "{verify_sql}"')
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if r.returncode == 0:
        from io import StringIO
        v = pd.read_csv(StringIO(r.stdout))
        print(f"   Table now has {v['n'].iloc[0]:,} rows, latest={v['latest_date'].iloc[0]}")


if __name__ == "__main__":
    main()
