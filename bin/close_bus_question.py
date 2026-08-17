#!/usr/bin/env python3
"""Close one pending bus question by its canonical ``Agent/topic`` reference."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def pending(root: Path) -> list[dict]:
    env = dict(os.environ)
    env["BUS_AUDIT_ROOT"] = str(root)
    run = subprocess.run(
        [sys.executable, str(ROOT / "bin" / "bus_question_audit.py"), "--json"],
        env=env, capture_output=True, text=True, timeout=30,
    )
    # The audit intentionally exits with the pending count; valid JSON is the success signal.
    try:
        return json.loads(run.stdout).get("pending", [])
    except Exception as exc:
        raise RuntimeError(f"cannot read canonical pending-question audit: {exc}") from exc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("question_ref", help="canonical Agent/topic copied from bus_question_audit")
    ap.add_argument("--resolution", required=True)
    ap.add_argument("--evidence", required=True,
                    help="commit, config read-back, selfcheck, report ledger, or other artifact")
    ap.add_argument("--source-topic", default="",
                    help="different topic where the resolution was originally discussed")
    ap.add_argument("--decided-by-user", action="store_true")
    ap.add_argument("--actor", default="Mike", help="agent writing the closure event")
    ap.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    a = ap.parse_args()

    if "/" not in a.question_ref:
        ap.error("question_ref must be Agent/topic")
    q_agent, topic = a.question_ref.split("/", 1)
    q_agent, topic = q_agent.strip(), topic.strip()
    if not q_agent or not topic:
        ap.error("question_ref must contain a non-empty Agent and topic")

    matches = [q for q in pending(a.root)
               if q.get("agent") == q_agent and q.get("topic") == topic]
    if not matches:
        print(f"close_bus_question: ALREADY_CLOSED_OR_UNKNOWN {a.question_ref}")
        return 0

    payload = {
        "resolution": a.resolution,
        "evidence": a.evidence,
        "resolves": [a.question_ref],
        "closed_by": a.actor,
    }
    if a.source_topic:
        payload["source_topic"] = a.source_topic
    if a.decided_by_user:
        payload["decided_by"] = "user"

    subprocess.run(
        [str(a.root / "bin" / "append_event.sh"), a.actor, "answer", topic,
         json.dumps(payload, ensure_ascii=False)],
        check=True,
    )

    remaining = [q for q in pending(a.root)
                 if q.get("agent") == q_agent and q.get("topic") == topic]
    if remaining:
        print(f"close_bus_question: closure write did not clear {a.question_ref}", file=sys.stderr)
        return 3
    print(f"close_bus_question: CLOSED {a.question_ref}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"close_bus_question: {exc}", file=sys.stderr)
        raise SystemExit(2)
