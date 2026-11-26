#!/usr/bin/env python3
"""Selfcheck for bin/job_handoff_digest.py using synthetic transcript and bus records."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "job_handoff_digest.py")


def _assistant(blocks: list[dict]) -> str:
    return json.dumps({"type": "assistant", "message": {"role": "assistant", "content": blocks}}, ensure_ascii=False) + "\n"


def main() -> int:
    fails: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(("PASS " if cond else "FAIL ") + name + (f" ({detail})" if detail and not cond else ""))
        if not cond:
            fails.append(name)

    sid1 = "11111111-1111-4111-8111-111111111111"
    sid2 = "22222222-2222-4222-8222-222222222222"

    with tempfile.TemporaryDirectory() as tmp:
        claude_dir = os.path.join(tmp, "claude")
        proj_dir = os.path.join(claude_dir, "projects", "-workspace-test")
        jobs_dir = os.path.join(tmp, "bus", "jobs")
        inbox_dir = os.path.join(tmp, "bus", "inbox")
        os.makedirs(proj_dir, exist_ok=True)
        os.makedirs(jobs_dir, exist_ok=True)
        os.makedirs(inbox_dir, exist_ok=True)

        with open(os.path.join(proj_dir, f"{sid2}.jsonl"), "w", encoding="utf-8") as f:
            f.write(_assistant([
                {"type": "tool_use", "name": "Read", "input": {"file_path": "/repo/a.py"}},
                {"type": "tool_use", "name": "Edit", "input": {"file_path": "/repo/b.py"}},
                {"type": "tool_use", "name": "Write", "input": {"file_path": "/repo/c.py"}},
                {"type": "tool_use", "name": "Edit", "input": {"file_path": "/repo/b.py"}},
                {"type": "tool_use", "name": "Bash", "input": {"command": "pytest tests/test_b.py -q"}},
                {"type": "text", "text": "Edited b.py and c.py; pytest is pending final assert fix."},
            ]))

        with open(os.path.join(jobs_dir, "Taylor_20261126_010000.json"), "w", encoding="utf-8") as f:
            json.dump({"job_id": "Taylor_20261126_010000", "session_id": f"{sid1},{sid2}"}, f)

        with open(os.path.join(inbox_dir, "Taylor.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({
                "agent": "Taylor",
                "event_type": "progress",
                "topic": "partial-b-py",
                "trace_id": "Taylor_20261126_010000",
            }) + "\n")

        env = dict(os.environ, MIKE_ROOT=tmp, CLAUDE_CONFIG_DIR=claude_dir)

        r1 = subprocess.run([sys.executable, SCRIPT, "--session-id", f"{sid1},{sid2}"], env=env, capture_output=True, text=True)
        check("1_session_id_digest", r1.returncode == 0 and "/repo/b.py" in r1.stdout and "/repo/c.py" in r1.stdout and "pytest tests/test_b.py" in r1.stdout, r1.stdout)
        check("2_dedup_edited_files", r1.stdout.count("/repo/b.py") == 1, r1.stdout)

        r2 = subprocess.run([sys.executable, SCRIPT, "--job", "Taylor_20261126_010000", "--max-chars", "1200"], env=env, capture_output=True, text=True)
        check("3_job_lookup_and_bus_trace", r2.returncode == 0 and "partial-b-py" in r2.stdout and len(r2.stdout) <= 1205, r2.stdout)

        r3 = subprocess.run([sys.executable, SCRIPT, "--session-id", "bad-uuid", "--job", "missing"], env=env, capture_output=True, text=True)
        check("4_fail_open_missing", r3.returncode == 0 and r3.stdout == "", repr(r3.stdout))

    print("ALL PASS" if not fails else f"{len(fails)} FAIL: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
