#!/usr/bin/env python3
"""wags_bus_question_pending.py <root> <agent> <topic>

Exit 0 if <agent>/<topic> is a currently PENDING bus question (per
bus_question_audit.py's canonical resolver algorithm — an open question with no
answer/decision resolver yet); exit 1 otherwise (never existed, or already resolved).

Why this exists (arch-review coord-2026-09-19 round-2 audit, required_change #5): the
round-2-escalation dedup in wags_autofix.sh originally used `mike_json.py has-event-prefix`,
which only checks EVENT EXISTENCE, not resolution state. That silently suppresses a real
re-escalation: escalate → human answers/closes it → Wags fixes → next round is STILL
NEEDS_CHANGES (same streak, first_ts unchanged, no CONFIRMED to reset it) → the old
existence check found the earlier (now-closed) question and skipped re-opening one, so the
recurrence got no distinct escalation. Checking "still pending" via the same resolver
bus_question_audit.py already uses (answer/decision/rollup semantics — see the
bus-question-closure skill) fixes that: closed means "not pending" regardless of whether the
event still exists on the append-only bus.

Thin argv wrapper on purpose — callers should never embed untrusted topic text inside a
Python -c source string (word-split / quote-injection risk already documented at length in
append_event.sh's own history).
"""
import json
import os
import subprocess
import sys


def main():
    if len(sys.argv) != 4:
        print("usage: wags_bus_question_pending.py <root> <agent> <topic>", file=sys.stderr)
        return 2
    root, agent, topic = sys.argv[1], sys.argv[2], sys.argv[3]
    env = dict(os.environ)
    env["BUS_AUDIT_ROOT"] = root
    audit = os.path.join(root, "bin", "bus_question_audit.py")
    try:
        r = subprocess.run([sys.executable, audit, "--json"], env=env,
                            capture_output=True, text=True, timeout=30)
        pending = json.loads(r.stdout).get("pending", [])
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError, ValueError):
        # Không đọc được audit ⇒ KHÔNG có bằng chứng "đang pending" ⇒ fail-closed như
        # "không pending" (để caller đi nhánh escalate/mở mới thay vì im lặng nuốt mất một
        # sự cố thật vì audit tạm thời lỗi — cùng nguyên tắc bus im lặng = không có bằng
        # chứng đã dùng ở WAGS_VERDICT_RECONCILE).
        return 1
    for q in pending:
        if q.get("agent") == agent and q.get("topic") == topic:
            return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
