#!/usr/bin/env python3
"""code_quality_baseline_build.py — (re)ghi mike/kb/code_quality_baseline.json toàn bộ, quét
trading_bot/*.py, bot_execute.py, mike/bin/*.py bằng ruff (rule set hẹp — xem pyproject.toml).

Đây là baseline REPORT-ONLY: KHÔNG sửa code. Chạy tay khi cần refresh toàn cục (vd sau khi
Tầng 2/3 dọn xong 1 đợt nợ); ratchet ngày-thường do bin/code_quality_gate.sh tự cập nhật
per-file, không cần chạy lại script này.

Usage: DNA_PYEXE mike/bin/code_quality_baseline_build.py
"""
import json
import subprocess
import sys
from pathlib import Path

WC_ROOT = Path(__file__).resolve().parents[2]
MIKE_ROOT = WC_ROOT / "mike"
OUT = MIKE_ROOT / "kb" / "code_quality_baseline.json"
RUFF = "/home/trido/thanhdt/wc_venv/bin/ruff"


def gather_targets():
    files = []
    files += sorted((WC_ROOT / "trading_bot").glob("*.py"))
    bot_execute = WC_ROOT / "bot_execute.py"
    if bot_execute.is_file():
        files.append(bot_execute)
    files += sorted((MIKE_ROOT / "bin").glob("*.py"))
    return files


def ruff_version():
    out = subprocess.run([RUFF, "--version"], capture_output=True, text=True).stdout.strip()
    return out


def main():
    targets = gather_targets()
    proc = subprocess.run(
        [RUFF, "check", "--no-cache", "--output-format=json", *[str(f) for f in targets]],
        cwd=str(WC_ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode not in (0, 1):
        print(f"FATAL: ruff exited {proc.returncode}: {proc.stderr}", file=sys.stderr)
        sys.exit(2)
    findings = json.loads(proc.stdout or "[]")

    per_file = {str(f.relative_to(WC_ROOT)): 0 for f in targets}
    by_rule = {}
    for f in findings:
        rp = str(Path(f["filename"]).resolve().relative_to(WC_ROOT))
        if rp in per_file:
            per_file[rp] += 1
        by_rule[f["code"]] = by_rule.get(f["code"], 0) + 1

    baseline = {
        "_comment": (
            "Baseline Tầng 1 code-quality (ruff, rule set hẹp F/E9/B006/B008 — xem "
            "pyproject.toml). Dùng bởi bin/code_quality_gate.sh (ratchet per-file, xem "
            "kb/projects/code-quality-review-plan-20260823.md §3). Đây KHÔNG phải nợ phải trả "
            "ngay — chỉ là điểm xuất phát; gate chỉ chặn khi số lỗi TĂNG so với số ở đây."
        ),
        "built_from": {
            "job": "Wags_20260823_071251",
            "date": "2026-08-23",
            "ruff_version": ruff_version(),
            "rule_set": ["F", "E9", "B006", "B008"],
            "scope": ["trading_bot/*.py", "bot_execute.py", "mike/bin/*.py"],
            "total_files": len(per_file),
            "total_errors": sum(per_file.values()),
        },
        "by_rule": dict(sorted(by_rule.items(), key=lambda kv: -kv[1])),
        "files": dict(sorted(per_file.items())),
    }
    OUT.write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {OUT} — {len(per_file)} files, {sum(per_file.values())} errors total")


if __name__ == "__main__":
    main()
