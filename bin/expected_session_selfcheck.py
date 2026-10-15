#!/usr/bin/env python3
"""Selfcheck expected_session.py — chạy dưới `env -u TZ` và TZ lạ đều phải ra cùng kết quả (§16)."""
import os
import subprocess
import sys

H = os.path.dirname(os.path.abspath(__file__)) + "/expected_session.py"
CASES = [  # (now ICT, session, next)
    ("2026-10-15T07:30:00", "2026-10-14", "2026-10-15"),  # sáng T5 -> phiên T4, plan cho hôm nay
    ("2026-10-14T18:30:00", "2026-10-14", "2026-10-15"),  # tối T4 -> phiên hôm nay (hành vi cron cũ)
    ("2026-10-14T16:59:00", "2026-10-13", "2026-10-14"),  # chưa tới cutoff
    ("2026-10-14T17:00:00", "2026-10-14", "2026-10-15"),  # đúng cutoff
    ("2026-10-12T08:00:00", "2026-10-09", "2026-10-12"),  # sáng T2 -> phiên T6
    ("2026-10-17T10:00:00", "2026-10-16", "2026-10-19"),  # T7 -> phiên T6
    ("2026-10-16T19:00:00", "2026-10-16", "2026-10-19"),  # tối T6 -> T2
]
bad = 0
for tzenv in (None, "America/New_York", "UTC"):
    env = {k: v for k, v in os.environ.items() if k != "TZ"}
    if tzenv:
        env["TZ"] = tzenv
    for now, es, en in CASES:
        env["MIKE_NOW_ICT"] = now
        out = subprocess.run([sys.executable, H], env=env, capture_output=True, text=True).stdout.split()
        ok = out == [es, en]
        bad += not ok
        print(("OK  " if ok else "FAIL"), tzenv or "-unset-", now, out, "want", [es, en])
print("selfcheck:", "PASS" if not bad else f"FAIL ({bad})")
sys.exit(1 if bad else 0)
