#!/usr/bin/env python3
"""Selfcheck for bin/retro_precollect.py using an isolated sandbox."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "retro_precollect.py")


def main() -> int:
    fails: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(("PASS " if cond else "FAIL ") + name + (f" ({detail})" if detail and not cond else ""))
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        day = "2026-11-26"
        inc_dir = os.path.join(tmp, "kb", "incidents", "2026-11")
        inbox_dir = os.path.join(tmp, "bus", "inbox")
        os.makedirs(inc_dir, exist_ok=True)
        os.makedirs(inbox_dir, exist_ok=True)
        os.makedirs(os.path.join(tmp, "bin"), exist_ok=True)
        with open(os.path.join(tmp, "bin", "real_tool.py"), "w", encoding="utf-8") as f:
            f.write("# ok\n")

        subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp, check=True)
        subprocess.run(["git", "add", "bin/real_tool.py"], cwd=tmp, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=tmp, check=True)
        sha = subprocess.run(["git", "rev-parse", "--short=7", "HEAD"], cwd=tmp, capture_output=True, text=True, check=True).stdout.strip()

        with open(os.path.join(inc_dir, f"{day}-sample-bug.md"), "w", encoding="utf-8") as f:
            f.write(f"Fixed bin/real_tool.py in {sha}, broken ref bin/ghost_missing.py deadbeef.\n")

        with open(os.path.join(inbox_dir, "Wags.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"ts": f"{day}T01:00:00Z", "agent": "Wags", "event_type": "finding", "topic": "sample-find", "payload": {"file": "bin/real_tool.py"}}) + "\n")
            f.write(json.dumps({"ts": "2026-11-25T23:00:00Z", "agent": "Wags", "event_type": "finding", "topic": "yesterday-ignore", "payload": {}}) + "\n")

        r = subprocess.run([sys.executable, SCRIPT, "--root", tmp, "--day", day], capture_output=True, text=True)
        out = r.stdout
        check("1_rc_zero", r.returncode == 0)
        check("2_incident_found", f"kb/incidents/2026-11/{day}-sample-bug.md" in out, out)
        check("3_bus_day_filter", "sample-find" in out and "yesterday-ignore" not in out, out)
        check("4_file_check", "ok=1 missing=1" in out and "bin/ghost_missing.py" in out, out)
        check("5_commit_check", "ok=1 missing=1" in out and "deadbeef" in out, out)

    print("ALL PASS" if not fails else f"{len(fails)} FAIL: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
