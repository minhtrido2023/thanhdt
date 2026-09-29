#!/usr/bin/env python3
"""code_quality_ruff_count.py — chạy ruff (rule set hẹp, cấu hình ở WorkingClaude/pyproject.toml)
trên một danh sách file .py và in ra JSON {abs_path: so_loi}.

Dùng bởi bin/code_quality_gate.sh (ratchet per-file) và bin/code_quality_baseline_build.py
(build/refresh toàn baseline). Key là ĐƯỜNG DẪN TUYỆT ĐỐI, không tự suy ra baseline-key — việc
map abs-path -> baseline-key (chuẩn hoá worktree, loại "mike/agents/wt-*/") là việc của caller,
vì chỉ caller biết ngữ cảnh commit đang chạy trong repo/worktree nào.

Luôn chạy ruff với cwd = WC_ROOT (mặc định /home/trido/thanhdt/WorkingClaude, override bằng
env CODE_QUALITY_WC_ROOT) để pyproject.toml (exclude test_*.py/exp_*/probe_*/stress_*/
agents/*/research/archive/wc_venv) được áp dụng; `--force-exclude` để ruff tự loại trừ ngay cả
khi path được truyền TƯỜNG MINH trên command line (mặc định ruff chỉ áp exclude khi tự walk
thư mục, không áp cho file truyền thẳng — đã đo thật 2026-08-23, xem finding
code-quality-tier1-ruff-gate + arch-review job Wags_20260823_071251).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

WC_ROOT = Path(os.environ.get("CODE_QUALITY_WC_ROOT", "/home/trido/thanhdt/WorkingClaude"))
RUFF = os.environ.get("CODE_QUALITY_RUFF", "/home/trido/thanhdt/wc_venv/bin/ruff")


def count_errors(paths):
    abs_paths = []
    for p in paths:
        ap = Path(p).resolve()
        if ap.is_file():
            abs_paths.append(str(ap))
    counts = {ap: 0 for ap in abs_paths}
    if not abs_paths:
        return counts
    proc = subprocess.run(
        [RUFF, "check", "--no-cache", "--force-exclude", "--output-format=json", *abs_paths],
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
        ap = str(Path(f["filename"]).resolve())
        if ap in counts:
            counts[ap] += 1
    return counts


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: code_quality_ruff_count.py <file.py> [...]", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(count_errors(sys.argv[1:]), ensure_ascii=False, indent=2))
