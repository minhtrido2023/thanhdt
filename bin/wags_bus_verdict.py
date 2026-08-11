#!/usr/bin/env python3
"""wags_bus_verdict.py <arch_reviewer_inbox.jsonl> <topic_prefix> <since_iso>

Print the verdict of the LATEST arch-reviewer `verification` event whose topic starts with
<topic_prefix> and whose ts >= <since_iso>. Prints "" (empty) + exit 1 when there is none.

Why read the BUS instead of the pipeline's own stdout (2026-08-11, kb/coding_guidelines.md
§26): wags_autofix.sh derives the verdict by parsing the stdout of `wags_autofix.sh
--review-topic`, a channel that has been polluted for real before — 2026-07-08, notify_thread.sh
printed {"status":"sent"} into it and two FAKE `wags-fix-not-confirmed` questions were filed
while arch-reviewer had actually said CONFIRMED; the same shape recurred 2026-07-22T05:55Z
(question INCONCLUSIVE, closed 8 days later as FALSE_ALARM against the real arch_review log).
_arch_review() writes its verdict to the bus deterministically (outside the agent, one
append_event.sh call) — that record is the artifact; stdout is a self-report that passes
through pipes. Same principle as wags_risk_tier.py: verify the artifact, not the report.

Deliberately requires an explicit since_iso (never "N hours ago") — a stale CONFIRMED from
an earlier run with the same daily label must NOT self-heal today's run. Same discipline as
mike_json.py has-event.
"""
import json
import sys


def main():
    if len(sys.argv) != 4:
        print("")
        return 1
    inbox, prefix, since_iso = sys.argv[1], sys.argv[2], sys.argv[3]
    verdict = ""
    try:
        with open(inbox, encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    e = json.loads(ln)
                except Exception:
                    continue
                if e.get("event_type") != "verification":
                    continue
                if not str(e.get("topic") or "").startswith(prefix):
                    continue
                if str(e.get("ts") or "") < since_iso:
                    continue
                payload = e.get("payload")
                if isinstance(payload, str):
                    try:
                        payload = json.loads(payload)
                    except Exception:
                        payload = None
                if isinstance(payload, dict) and payload.get("verdict"):
                    verdict = str(payload["verdict"])
    except OSError:
        print("")
        return 1
    print(verdict)
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
