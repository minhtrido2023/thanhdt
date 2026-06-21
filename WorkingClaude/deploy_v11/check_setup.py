# -*- coding: utf-8 -*-
"""Smoke test cho setup BA-system V11.

Chạy: python check_setup.py

Sẽ verify:
  1. Python version >= 3.10
  2. pandas + numpy installed
  3. bq CLI installed + authenticated
  4. BQ project access (tav2_bq tables read)
  5. fundamental_rating_all.csv exists + readable
  6. WORKDIR + BQ_BIN paths trong recommend_holistic.py hợp lệ
"""
import io
import os
import sys
import subprocess
from pathlib import Path

# Force UTF-8 stdout (Windows defaults to cp1252 which can't render check marks)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PROJECT = "lithe-record-440915-m9"
REQUIRED_TABLES = [
    "tav2_bq.ticker",
    "tav2_bq.ticker_1m",
    "tav2_bq.ticker_financial",
    "tav2_bq.fa_ratings",
    "tav2_bq.vnindex_5state",
    "tav2_bq.ticker_prune",
]


def check(label, cond, hint=""):
    mark = "✓" if cond else "✗"
    print(f"  [{mark}] {label}")
    if not cond and hint:
        print(f"      → {hint}")
    return cond


def main():
    print("=" * 70)
    print("  BA-system V11 setup smoke test")
    print("=" * 70)
    ok = True

    # 1. Python version
    print("\n[1/6] Python version")
    ver = sys.version_info
    ok &= check(f"Python {ver.major}.{ver.minor}.{ver.micro}",
                ver >= (3, 10),
                "Cần Python >= 3.10 — xem DEPLOY.md mục 3.1")

    # 2. Dependencies
    print("\n[2/6] Python dependencies")
    try:
        import pandas as pd
        ok &= check(f"pandas {pd.__version__}", True)
    except ImportError:
        ok &= check("pandas installed", False,
                    "pip install -r requirements.txt")
    try:
        import numpy as np
        ok &= check(f"numpy {np.__version__}", True)
    except ImportError:
        ok &= check("numpy installed", False,
                    "pip install -r requirements.txt")

    # 3. bq CLI
    print("\n[3/6] Google Cloud SDK / bq CLI")
    import shutil
    bq_paths = []
    candidates = [shutil.which("bq"), shutil.which("bq.cmd"),
                  "/usr/local/google-cloud-sdk/bin/bq",
                  os.path.expanduser("~/google-cloud-sdk/bin/bq"),
                  r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd",
                  r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd",
                  os.path.expanduser(r"~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\bq.cmd")]
    for c in [c for c in candidates if c]:
        if not os.path.exists(c) and shutil.which(c) is None:
            continue
        try:
            r = subprocess.run([c, "version"], capture_output=True, text=True,
                              timeout=15, shell=False)
            if r.returncode == 0:
                bq_paths.append(c)
                break
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue
    bq_ok = bool(bq_paths)
    ok &= check(f"bq CLI found at: {bq_paths[0] if bq_paths else 'NOT FOUND'}",
                bq_ok, "Cài Google Cloud SDK — xem DEPLOY.md mục 3.2")

    # 4. BQ project access
    if bq_ok:
        print("\n[4/6] BigQuery access")
        bq = bq_paths[0]
        try:
            r = subprocess.run(
                [bq, "query", "--use_legacy_sql=false",
                 f"--project_id={PROJECT}", "--format=csv",
                 "SELECT 1 AS ok"],
                capture_output=True, text=True, timeout=30
            )
            auth_ok = r.returncode == 0 and "1" in r.stdout
            ok &= check(f"Auth + BQ query (project: {PROJECT})",
                        auth_ok,
                        "Setup credentials — xem DEPLOY.md mục 3.3")

            if auth_ok:
                # Check table access
                missing = []
                for tbl in REQUIRED_TABLES:
                    r2 = subprocess.run(
                        [bq, "query", "--use_legacy_sql=false",
                         f"--project_id={PROJECT}", "--format=csv",
                         f"SELECT COUNT(*) FROM `{tbl}` WHERE FALSE"],
                        capture_output=True, text=True, timeout=30
                    )
                    if r2.returncode != 0:
                        missing.append(tbl)
                ok &= check(f"Read access to {len(REQUIRED_TABLES)} required tables",
                            not missing,
                            f"Missing: {missing}. Liên hệ admin BQ để cấp quyền.")
        except subprocess.TimeoutExpired:
            ok &= check("BQ query timeout (>30s)", False,
                        "Network slow hoặc credentials sai")
    else:
        print("\n[4/6] BigQuery access — SKIP (bq CLI missing)")
        ok = False

    # 5. FA snapshot
    print("\n[5/6] fundamental_rating_all.csv")
    fa_path = Path(__file__).parent / "data/fundamental_rating_all.csv"
    fa_ok = fa_path.exists() and fa_path.stat().st_size > 1000
    ok &= check(f"File exists at {fa_path}",
                fa_ok,
                "Refresh: python fundamental_rating.py")
    if fa_ok:
        try:
            import pandas as pd
            df = pd.read_csv(fa_path, nrows=5)
            req_cols = ["ticker", "tier", "total_score"]
            ok &= check(f"Has required columns {req_cols}",
                        all(c in df.columns for c in req_cols),
                        f"Got: {list(df.columns)[:8]}")
        except Exception as e:
            ok &= check("Readable", False, str(e))

    # 6. Path config trong recommend_holistic.py
    print("\n[6/6] recommend_holistic.py path config")
    rec_path = Path(__file__).parent / "recommend_holistic.py"
    if rec_path.exists():
        content = rec_path.read_text(encoding="utf-8")
        workdir_line = [l for l in content.splitlines()
                        if l.strip().startswith("WORKDIR")][:1]
        bqbin_line = [l for l in content.splitlines()
                      if l.strip().startswith("BQ_BIN")][:1]
        print(f"      WORKDIR line: {workdir_line[0] if workdir_line else 'NOT FOUND'}")
        print(f"      BQ_BIN line:  {bqbin_line[0] if bqbin_line else 'NOT FOUND'}")
        print(f"      → Verify đúng path cho server này (DEPLOY.md mục 3.5)")
    else:
        ok &= check("recommend_holistic.py exists", False)

    print()
    print("=" * 70)
    if ok:
        print("  ✅ Setup OK. Thử: python recommend_holistic.py")
    else:
        print("  ❌ Có vấn đề. Xem các dòng [✗] phía trên + DEPLOY.md.")
    print("=" * 70)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
