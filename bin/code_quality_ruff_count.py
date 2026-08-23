#!/usr/bin/env python3
"""code_quality_ruff_count.py — chạy ruff (rule set hẹp, cấu hình ở WorkingClaude/pyproject.toml)
trên một danh sách file .py và in ra JSON {relpath_tu_WorkingClaude: so_loi}.

Dùng bởi bin/code_quality_gate.sh (ratchet per-file) và bin/code_quality_baseline_build.py
(build/refresh toàn baseline). Luôn chạy ruff với cwd = WorkingClaude root để pyproject.toml
(exclude test_*.py/exp_*/probe_*/stress_*/agents/*/research/archive/wc_venv) được áp dụng.
"""
import json
import subprocess
import sys
from pathlib import Path

WC_ROOT = Path(__file__).resolve().parents[2]
RUFF = "/home/trido/thanhdt/wc_venv/bin/ruff"


def count_errors(paths):
    abs_paths = []
    rel_paths = []
    for p in paths:
        ap = Path(p).resolve()
        if not ap.is_file():
            continue
        abs_paths.append(str(ap))
        rel_paths.append(str(ap.relative_to(WC_ROOT)))
    counts = {rp: 0 for rp in rel_paths}
    if not abs_paths:
        return counts
    proc = subprocess.run(
        [RUFF, "check", "--no-cache", "--output-format=json", *abs_paths],
        cwd=str(WC_ROOT),
        capture_output=True,
        text=True,
    )
    # ruff exits 1 when findings exist — that's expected, not an error.
    if proc.returncode not in (0, 1):
        print(f"FATAL: ruff exited {proc.returncode}: {proc.stderr}", file=sys.stderr)
        sys.exit(2)
    findings = json.loads(proc.stdout or "[]")
    for f in findings:
        rp = str(Path(f["filename"]).resolve().relative_to(WC_ROOT))
        if rp in counts:
            counts[rp] += 1
    return counts


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: code_quality_ruff_count.py <file.py> [...]", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(count_errors(sys.argv[1:]), ensure_ascii=False, indent=2))
