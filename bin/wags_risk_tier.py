#!/usr/bin/env python3
"""wags_risk_tier.py <bus_inbox_wags.jsonl> <topic_substr>

Cost-optimization #2 (2026-07-17): arch-reviewer's adversarial audit is correctly
mandatory for anything that could affect the LIVE trading day (dispatch.sh core,
hooks that every session bootstraps through) — but was ALSO being run, at full
cost, for purely cosmetic fixes (a stray notification string, a doc typo) that have
near-zero operational consequence if imperfect. Classify risk from the files Wags
itself reports changing, not from Wags's own risk opinion (that would let a
chronically-wrong Wags just self-declare "low risk" to dodge review — the same
"verify the artifact, not the self-report" principle used elsewhere in this fleet).

Reads the LATEST Wags finding whose topic+payload contains <topic_substr>, checks
its "files_changed" list (Wags is instructed to report this explicitly) against a
short, conservative low-risk allowlist. ANY of these makes the whole fix "high"
(fail-safe default): the finding/field is missing, or any changed file falls
outside the allowlist. Only prints "low" when every single changed file is a known
zero/near-zero-blast-radius path.

Prints exactly one line: "low" or "high".
"""
import json
import re
import sys

# Conservative — err toward "high" (mandatory review) for anything not explicitly
# listed here. Extend only when a path is genuinely inert if the fix is wrong (no
# other agent's dispatch depends on it, no cron execution path touches it).
LOW_RISK_PATTERNS = [
    r"^kb/.*\.md$",
    r"^MIKE\.md$",
    r"^agents/[^/]+/CLAUDE\.md$",
    r"^bin/notify\.sh$",
    r"^bin/notify_thread\.sh$",
    r"^bin/wags_autofix\.sh$",
    r"^bin/ops_autofix\.sh$",
    r"^bin/jobs\.sh$",
]


def main():
    if len(sys.argv) != 3:
        print("high")  # fail-safe on malformed invocation too
        return
    inbox, substr = sys.argv[1], sys.argv[2]
    pick = None
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
                if e.get("event_type") != "finding":
                    continue
                blob = e.get("topic", "") + json.dumps(e.get("payload", ""))
                if substr.lower() not in blob.lower():
                    continue
                pick = e
    except FileNotFoundError:
        print("high")
        return

    if pick is None:
        print("high")  # no matching finding -> can't classify -> mandatory review
        return

    payload = pick.get("payload")
    files = payload.get("files_changed") if isinstance(payload, dict) else None
    if not files or not isinstance(files, list):
        print("high")  # Wags didn't report files_changed -> can't verify -> mandatory
        return

    for f in files:
        if not isinstance(f, str) or not any(re.match(p, f) for p in LOW_RISK_PATTERNS):
            print("high")
            return

    print("low")


if __name__ == "__main__":
    main()
