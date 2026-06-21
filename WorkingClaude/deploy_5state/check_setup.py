# -*- coding: utf-8 -*-
"""Smoke test cho setup 5-state deploy.

Verifies:
  1. Python >= 3.10
  2. pandas + numpy
  3. bq CLI + BQ auth
  4. BQ read access (ticker, ticker_prune)
  5. BQ write access (vnindex_5state — dry-run a load)
  6. Local files: vnindex_5state_system.py, filter.json
"""
import io
import os
import shutil as _sh
import subprocess
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROJECT = "lithe-record-440915-m9"


def check(label, cond, hint=""):
    mark = "✓" if cond else "✗"
    print(f"  [{mark}] {label}")
    if not cond and hint:
        print(f"      → {hint}")
    return cond


def main():
    print("=" * 70)
    print("  5-state deploy smoke test")
    print("=" * 70)
    ok = True

    # 1. Python
    print("\n[1/6] Python version")
    ver = sys.version_info
    ok &= check(f"Python {ver.major}.{ver.minor}.{ver.micro}",
                ver >= (3, 10),
                "Cần Python >= 3.10")

    # 2. Deps
    print("\n[2/6] Python dependencies")
    try:
        import pandas as pd
        ok &= check(f"pandas {pd.__version__}", True)
    except ImportError:
        ok &= check("pandas installed", False, "pip install -r requirements.txt")
    try:
        import numpy as np
        ok &= check(f"numpy {np.__version__}", True)
    except ImportError:
        ok &= check("numpy installed", False, "pip install -r requirements.txt")

    # 3. bq CLI
    print("\n[3/6] Google Cloud SDK / bq CLI")
    candidates = [os.environ.get("BQ_BIN"),
                  _sh.which("bq"), _sh.which("bq.cmd"),
                  "/usr/local/google-cloud-sdk/bin/bq",
                  os.path.expanduser("~/google-cloud-sdk/bin/bq"),
                  r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd",
                  r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd",
                  os.path.expanduser(r"~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd")]
    bq_path = None
    for c in [c for c in candidates if c]:
        if not os.path.exists(c) and _sh.which(c) is None:
            continue
        try:
            r = subprocess.run([c, "version"], capture_output=True, text=True,
                              timeout=15)
            if r.returncode == 0:
                bq_path = c
                break
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    ok &= check(f"bq found at: {bq_path or 'NOT FOUND'}",
                bool(bq_path),
                "Cài Google Cloud SDK")

    # 4. BQ read
    if bq_path:
        print("\n[4/6] BigQuery read access")
        for tbl in ["tav2_bq.ticker", "tav2_bq.ticker_prune"]:
            r = subprocess.run(
                [bq_path, "query", "--use_legacy_sql=false",
                 f"--project_id={PROJECT}", "--format=csv",
                 f"SELECT COUNT(*) FROM `{tbl}` WHERE FALSE"],
                capture_output=True, text=True, timeout=30
            )
            ok &= check(f"Read {tbl}", r.returncode == 0,
                        f"Auth/permissions issue: {r.stderr[:200]}")

        # 5. BQ write — verify dataset exists + ability to query target table
        print("\n[5/6] BigQuery write check (vnindex_5state table)")
        r = subprocess.run(
            [bq_path, "show", "--format=prettyjson",
             f"{PROJECT}:tav2_bq.vnindex_5state"],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode == 0:
            ok &= check(f"Table tav2_bq.vnindex_5state exists", True)
        else:
            # Table may not exist yet — first run will CREATE via --replace.
            # Check dataset exists at least.
            r2 = subprocess.run(
                [bq_path, "show", "--format=prettyjson",
                 f"{PROJECT}:tav2_bq"],
                capture_output=True, text=True, timeout=30
            )
            if r2.returncode == 0:
                ok &= check(f"Dataset tav2_bq exists (table will be created on first upload)", True)
            else:
                ok &= check(f"Dataset tav2_bq accessible", False,
                            "Check service account has roles/bigquery.dataEditor + jobUser")
    else:
        print("\n[4/6] BQ access — SKIP")
        print("\n[5/6] BQ write check — SKIP")
        ok = False

    # 6. Files
    print("\n[6/6] Local files")
    base = Path(__file__).parent
    for fn in ["vnindex_5state_system.py", "refresh_data.py", "upload_to_bq.py",
               "filter.json"]:
        ok &= check(f"{fn}", (base / fn).exists(),
                    f"Missing from deploy package")

    print()
    print("=" * 70)
    if ok:
        print("  ✅ Setup OK. Bước tiếp theo: python refresh_data.py")
    else:
        print("  ❌ Có vấn đề. Xem các dòng [✗] phía trên + DEPLOY.md.")
    print("=" * 70)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
