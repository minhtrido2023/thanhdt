#!/usr/bin/env python3
"""Package BA-system v11 production files into a deployable zip.

Cross-platform (Windows + Linux). Uses Python's zipfile, no external 'zip' command needed.

Usage:
    python package_for_deploy.py [output_filename.zip]
"""
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path


# File tiers — see PRODUCTION_FILES.md
TIER1_RUNTIME = [
    "recommend_holistic.py",
    "telegram_recommend.py",
    "simulate_holistic_nav.py",
    "signal_v10_sql.py",
    "requirements.txt",
    "data/fundamental_rating_all.csv",
]

TIER2_CONFIG = [
    "telegram_config.template.json",
    ".gitignore",
]

TIER3_VALIDATION = [
    "test_state_var_with_p3.py",
    "quarterly_walkforward.py",
    "export_journal_v6_extended.py",
    "test_etf_parking.py",
    "test_fresh_q_filter.py",
    "test_v2g_vs_baseline.py",
]

TIER4_DOCS = [
    "DEPLOYMENT.md",
    "README.md",
    "PRODUCTION_FILES.md",
    "BA_SYSTEM_WORKFLOW.md",
    "TELEGRAM_SETUP.md",
]

TIER5_DEPLOY = [
    "deploy_linux.sh",
    "deploy_windows.ps1",
    "telegram_register_task.ps1",
    "telegram_fix_wake.ps1",
]

REQUIRED = (TIER1_RUNTIME + ["telegram_config.template.json",
                              "DEPLOYMENT.md", "README.md"])


def main():
    here = Path(__file__).parent.resolve()
    out_name = (sys.argv[1] if len(sys.argv) > 1
                else f"ba-system-v11-{datetime.now():%Y%m%d}.zip")
    out_path = here / out_name

    print(f"Packaging from: {here}")
    print(f"Output zip    : {out_path}")
    print()

    all_files = (TIER1_RUNTIME + TIER2_CONFIG + TIER3_VALIDATION
                 + TIER4_DOCS + TIER5_DEPLOY)
    missing = []
    included = []

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in all_files:
            src = here / fname
            if src.exists():
                # Place inside ba-system/ subdir for cleaner unzip
                zf.write(src, arcname=f"ba-system/{fname}")
                included.append(fname)
            else:
                missing.append(fname)

    # Check critical files
    missing_required = [f for f in REQUIRED if f in missing]
    if missing_required:
        print(f"ERROR -- missing REQUIRED files: {missing_required}")
        out_path.unlink(missing_ok=True)
        sys.exit(1)

    # Display report
    size_kb = out_path.stat().st_size / 1024
    print(f"OK Package built: {out_path.name} ({size_kb:.1f} KB)")
    print()
    print(f"Included {len(included)} files:")
    for f in included:
        size = (here / f).stat().st_size
        print(f"  {size:>8} bytes  {f}")

    if missing:
        print()
        print(f"Optional files SKIPPED (not present in source):")
        for f in missing:
            print(f"  {f}")

    print()
    print("Deploy steps:")
    print(f"  1. Upload to server:")
    print(f"     scp {out_name} user@server:~/")
    print(f"  2. SSH in, unzip, run deploy script:")
    print(f"     ssh user@server")
    print(f"     unzip {out_name} && cd ba-system")
    print(f"     # Linux:   bash deploy_linux.sh")
    print(f"     # Windows: powershell -ExecutionPolicy Bypass -File deploy_windows.ps1")


if __name__ == "__main__":
    main()
