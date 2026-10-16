#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Đối chiếu CHỈ-ĐỌC sổ đơn vị đã chốt với mốc ngoài kho (kb/fund_ledger_anchors.txt, mốc MỚI NHẤT mỗi TK).

Gọi `nav_unit_ledger.py --verify-anchor` cho từng tài khoản. rc=0 mọi TK khớp · rc=1 có TK lệch/lỗi ·
rc=3 file mốc thiếu/trống. Không ghi gì. Cron bọc bằng fund_bench_cron.sh ⇒ rc≠0 báo Trading Daily
(cảnh báo, KHÔNG chặn báo cáo — user duyệt 2026-10-14). Selfcheck: ledger_anchor_check_selfcheck.py.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHORS = os.environ.get("LEDGER_ANCHORS_FILE", os.path.join(ROOT, "kb", "fund_ledger_anchors.txt"))
LEDGER_DIR = os.environ.get("LEDGER_DIR", "/home/trido/thanhdt/WorkingClaude/data/execution_logs")
CLI = os.environ.get("NAV_UNIT_LEDGER_CLI", os.path.join(ROOT, "bin", "nav_unit_ledger.py"))
LINE = re.compile(r"^SEAL_MD5 (\S+) ([0-9a-f]{32}) ([0-9a-f]{32})\s*$")


def latest_anchors(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for ln in f:
            m = LINE.match(ln.strip())
            if m:
                out[m.group(1)] = m.group(0).strip()   # dòng sau đè dòng trước ⇒ mốc mới nhất
    return out


def main() -> int:
    try:
        anchors = latest_anchors(ANCHORS)
    except OSError as exc:
        print(f"LỖI ledger_anchor_check: không đọc được {ANCHORS}: {type(exc).__name__} ({exc})", file=sys.stderr)
        return 3
    if not anchors:
        print(f"LỖI ledger_anchor_check: {ANCHORS} không có dòng SEAL_MD5 nào", file=sys.stderr)
        return 3
    bad = 0
    env = {k: v for k, v in os.environ.items() if k != "WC_ROOT"}
    for acct, line in sorted(anchors.items()):
        r = subprocess.run([sys.executable, CLI, "--account", acct, "--ledger-dir", LEDGER_DIR,
                            "--verify-anchor", line], capture_output=True, text=True, env=env, timeout=300)
        tail = " | ".join(x for x in (r.stdout + r.stderr).strip().splitlines() if x and not x[0].isdigit())[-400:]
        if r.returncode == 0:
            print(f"OK {acct}: {tail}")
        else:
            bad += 1
            print(f"LỆCH {acct} rc={r.returncode}: {tail}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
